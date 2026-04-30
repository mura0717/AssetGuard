"""
Merges Intune, Teams, and Entra ID data using Transitive Graph Logic with SOC-Optimized Filtering.
"""

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Optional

from soc_stack.config.ms365_service import Microsoft365Service
from soc_stack.scanners.intune_scanner import IntuneScanner
from soc_stack.scanners.teams_scanner import TeamsScanner
from soc_stack.scanners.entra_scanner import EntraScanner
from soc_stack.utils.mac_utils import macs_from_string
from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.config.mac_config import CTP18

class Microsoft365Aggregator:    
    """
    Aggregates MS365 assets.
    1. EXTRACTS keys (Serial, AzureID, MAC)
    2. MERGES using Union-Find (Graph Clustering)
    3. FILTERS out non-physical/stale noise
    """
    
    SOURCE_PRIORITY: Dict[str, int] = {
        'intune': 3, 
        'teams': 2,
        'entra': 1,
    }
    
    # Garbage serials to ignore to prevent false merges
    INVALID_SERIALS: Set[str] = frozenset({
        'unknown', 'none', 'n/a', 'na', 'null', 'undefined',
        '0', '000000', '123456', 'to be filled', 'system serial number',
        'default string', 'chassis serial number', 'not specified',
        'to be filled by o.e.m.', 'no serial', 'serial',
    })
    
    # Filtering Configuration for Entra-only devices
    FILTER_STALE_DAYS = 180       # Drop Entra-only devices unseen for 6 months
    DROP_DISABLED_ACCOUNTS = True # Drop if Entra account is disabled
    DROP_AZURE_VMS = False        # KEEP Azure VMs (Monitorable by Zabbix/Wazuh)
    DROP_OTHER_VMS = True         # Drop non-Azure VMs
    DROP_NO_OS_NO_HARDWARE = True # Drop devices with no OS AND no manufacturer
    DROP_NO_ACTIVITY_DATES = True # Drop if no sign-in AND no registration date

    def __init__(self):
        self.microsoft365 = Microsoft365Service()
        self.intune_sync = IntuneScanner()
        self.teams_sync = TeamsScanner()
        self.entra_sync = EntraScanner()

  
    def _extract_matching_keys(self, asset: Dict) -> Set[str]:
        """
        Generates unique keys to link assets across sources.
        """
        keys: Set[str] = set()
        
        # 1. Serial Number (Strongest Hardware Link / Connects: Intune <-> Teams)
        serial = asset.get('serial')
        if serial:
            clean_serial = str(serial).strip().upper()
            if len(clean_serial) > 3 and clean_serial.lower() not in self.INVALID_SERIALS:
                keys.add(f"serial:{clean_serial}")
        
        # 2. Azure AD Device ID (Strongest Identity Link / Connects: Intune <-> Entra)
        azure_id = asset.get('azure_ad_id')
        if azure_id:
            keys.add(f"azure:{str(azure_id).strip().lower()}")
        
        # 3. MAC Addresses (Strong Hardware Link)
        mac_fields = ['mac_addresses', 'wifi_mac', 'ethernet_mac']
        for field in mac_fields:
            value = asset.get(field)
            if value:
                for mac in macs_from_string(str(value)):
                    keys.add(f"mac:{mac}")
        
        # 4. Source Specific IDs (Self-Deduplication)
        if asset.get('intune_device_id'):
            keys.add(f"intune:{str(asset['intune_device_id']).strip().lower()}")
        if asset.get('teams_device_id'):
            keys.add(f"teams:{str(asset['teams_device_id']).strip().lower()}")
        if asset.get('entra_object_id'):
            keys.add(f"entra:{str(asset['entra_object_id']).strip().lower()}")
            
        return keys


    def merge_data(
        self, 
        intune_data: Optional[List[Dict]] = None, 
        teams_data: Optional[List[Dict]] = None,
        entra_data: Optional[List[Dict]] = None
    ) -> List[Dict]:

        # --- A. Fetch Data if missing ---
        if intune_data is None: _, intune_data = self.intune_sync.get_transformed_assets()
        if teams_data is None: _, teams_data = self.teams_sync.get_transformed_assets()
        if entra_data is None: _, entra_data = self.entra_sync.get_transformed_assets()
        
        if debug_logger.ms365_debug:
            print(f"Aggregating: Intune({len(intune_data)}) Teams({len(teams_data)}) Entra({len(entra_data)})")

        # --- B. Tag and Flatten (Safe Copy) ---
        all_assets: List[Dict] = []
        
        # Helper to safely tag assets
        def add_source(data_list, origin_name):
            for a in data_list:
                tagged = a.copy()
                tagged['_origin'] = origin_name
                all_assets.append(tagged)

        add_source(intune_data, 'intune')
        add_source(teams_data, 'teams')
        add_source(entra_data, 'entra')

        if not all_assets: 
            return []

        # --- C. Build Graph (Union-Find via DFS) ---
        
        index_map: Dict[str, List[int]] = defaultdict(list)
        asset_keys_cache: List[Set[str]] = []

        for idx, asset in enumerate(all_assets):
            keys = self._extract_matching_keys(asset)
            asset_keys_cache.append(keys)
            for key in keys:
                index_map[key].append(idx)

        visited: Set[int] = set()
        groups: List[Set[int]] = []

        for i in range(len(all_assets)):
            if i in visited: continue
            
            stack = [i]
            group = set()
            
            while stack:
                curr_idx = stack.pop()
                if curr_idx in visited: continue
                
                visited.add(curr_idx)
                group.add(curr_idx)
                
                # Check all keys belonging to this asset
                for key in asset_keys_cache[curr_idx]:
                    for neighbor_idx in index_map[key]:
                        if neighbor_idx not in visited:
                            stack.append(neighbor_idx)
            groups.append(group)

        # --- D. Merge Components ---
        merged_results: List[Dict] = []
        for group_indices in groups:
            group_assets = [all_assets[i] for i in group_indices]
            merged_asset = self._merge_asset_group(group_assets)
            merged_results.append(merged_asset)

        # --- E. Final Enrichment ---
        self._enrich_assets_with_static_macs(merged_results)
        self._set_final_metadata(merged_results)
        
        # --- F. Filter Noise ---
        final_inventory = self._filter_noise(merged_results)
        
        return final_inventory

    def _merge_asset_group(self, assets: List[Dict]) -> Dict:
        if len(assets) == 1:
            res = assets[0].copy()
            res['_source'] = res.pop('_origin', 'unknown')
            return res

        # Sort: Low Priority -> High Priority (so High overwrites Low)
        assets.sort(key=lambda x: self.SOURCE_PRIORITY.get(x.get('_origin', ''), 0))

        merged: Dict = {}
        sources: Set[str] = set()

        for asset in assets:
            origin = asset.get('_origin', 'unknown')
            sources.add(origin)
            
            for k, v in asset.items():
                if k == '_origin': continue
                if v in (None, "", [], {}, "Unknown", "unknown"): continue
                
                # Name Protection: Don't overwrite specific name with generic one
                if k == 'name':
                    existing_name = merged.get('name', '')
                    if self._is_generic_name(v) and not self._is_generic_name(existing_name):
                        continue
                
                merged[k] = v

        merged['_source'] = "+".join(sorted(sources))
        
        # Debug Log for merges
        if debug_logger.ms365_debug and len(assets) > 1:
             origins = [a.get('_origin') for a in assets]
             name = merged.get('name', merged.get('serial', 'N/A'))
             print(f"  ✓ Merged {origins} -> {name}") # Optional verbose log

        return merged

    def _set_final_metadata(self, assets: List[Dict]) -> None:
        """Sets management flags and timestamps."""
        current_time = datetime.now(timezone.utc).isoformat()
        
        for asset in assets:
            src = asset.get('_source', '')
            
            if 'intune' in src:
                asset['management_status'] = 'Managed (Intune)'
                asset['intune_managed'] = True
                asset['last_update_source'] = 'intune'
            elif 'teams' in src:
                asset['management_status'] = 'Teams Device'
                asset['intune_managed'] = False
                asset['last_update_source'] = 'teams'
            elif 'entra' in src:
                asset['management_status'] = 'Unmanaged (Entra Only)'
                asset['intune_managed'] = False
                asset['last_update_source'] = 'entra'
            else:
                asset['management_status'] = 'Unknown'
                asset['intune_managed'] = False
                asset['last_update_source'] = 'unknown'
            
            if not asset.get('last_update_at'):
                asset['last_update_at'] = current_time
                

    def _enrich_assets_with_static_macs(self, merged_assets: List[Dict]) -> None:
        static_mac_map = {
            d['serial']: d['mac_address'] 
            for d in CTP18.values() 
            if 'serial' in d and 'mac_address' in d
        }
        
        for asset in merged_assets:
            serial = asset.get('serial')
            if serial and serial in static_mac_map:
                current_set = set(macs_from_string(asset.get('mac_addresses', '')))
                static_set = set(macs_from_string(static_mac_map[serial]))
                combined = current_set | static_set
                if combined:
                    asset['mac_addresses'] = ';'.join(sorted(combined))


    # Post-Merge Filtering for Entra-only Assets
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Safely parse datetime strings from MS Graph API."""
        if not dt_string:
            return None
        try:
            clean = dt_string.replace('Z', '+00:00')
            # Handle milliseconds: 2023-01-01T12:00:00.000+00:00
            if '.' in clean:
                base, rest = clean.split('.', 1)
                # Find the timezone part
                for sep in ['+', '-']:
                    if sep in rest:
                        tz_part = sep + rest.split(sep, 1)[1]
                        clean = base + tz_part
                        break
            return datetime.fromisoformat(clean)
        except (ValueError, AttributeError):
            return None

    def _get_last_activity_date(self, asset: Dict) -> Optional[datetime]:
        """
        Get the most recent activity date for an asset.
        Priority: last_sign_in > registration_date
        """
        last_seen = self._parse_datetime(asset.get('entra_last_sign_in'))
        if last_seen:
            return last_seen
        
        # Fallback to registration date
        return self._parse_datetime(asset.get('entra_registration_date'))

    def _filter_noise(self, assets: List[Dict]) -> List[Dict]:
        """
        Removes 'Entra Only' assets that are stale, virtual, disabled, or ghost records.
        
        Devices from Intune or Teams are IMMUNE - they represent managed/known hardware.
        Only Entra-only devices go through the filtering gauntlet.
        """
        clean_inventory: List[Dict] = []
        dropped_stats: Dict[str, int] = defaultdict(int)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.FILTER_STALE_DAYS)

        for asset in assets:
            source = asset.get('_source', '')
            
            # IMMUNITY: Managed devices always kept
            if 'intune' in source or 'teams' in source:
                clean_inventory.append(asset)
                continue
            
            # 1. Disabled Accounts (Security)
            if self.DROP_DISABLED_ACCOUNTS and asset.get('entra_account_enabled') is False:
                dropped_stats['disabled'] += 1
                continue

            # 2. Virtual Machines
            model = str(asset.get('model', '')).lower()
            mfr = str(asset.get('manufacturer', '')).lower()
            
            is_azure_vm = 'microsoft corporation' in mfr and 'virtual machine' in model
            is_other_vm = ('virtual machine' in model or 'vmware' in mfr) and not is_azure_vm
            
            if self.DROP_AZURE_VMS and is_azure_vm:
                dropped_stats['azure_vm'] += 1
                continue
            if self.DROP_OTHER_VMS and is_other_vm:
                dropped_stats['other_vm'] += 1
                continue
            
            # 3. No OS AND No Hardware Info (Ghost/App Registration)
            os_platform = str(asset.get('os_platform', '')).lower()
            if self.DROP_NO_OS_NO_HARDWARE and not os_platform and not mfr:
                dropped_stats['no_os_hardware'] += 1
                continue

            # 4. Activity Date Check (Robust Staleness)
            last_activity = self._get_last_activity_date(asset)
            
            if last_activity:
                # Has date - check if stale
                if last_activity < cutoff_date:
                    dropped_stats['stale'] += 1
                    continue
            else:
                # No dates at all - drop based on policy
                if self.DROP_NO_ACTIVITY_DATES:
                    dropped_stats['no_dates'] += 1
                    continue

            # Survived the gauntlet → valid unmanaged device
            clean_inventory.append(asset)

        # Report filtering results
        total_dropped = sum(dropped_stats.values())
        if total_dropped > 0:
            print(f"  [Filter] Dropped {total_dropped} Entra-only noise records:")
            for reason, count in sorted(dropped_stats.items(), key=lambda x: -x[1]):
                print(f"    - {reason}: {count}")

        return clean_inventory

    @staticmethod
    def _is_generic_name(name: Optional[str]) -> bool:
        if not name: return True
        lower = name.lower()
        return lower.startswith('device-') or lower.startswith('unknown') or lower == '_gateway' or len(lower) < 3

    
    # Public method to run the full collection process
    def collect_assets(self) -> List[Dict]:
        print("Starting Microsoft 365 asset collection (Transitive)...")
        if debug_logger.ms365_debug: debug_logger.clear_logs('ms365')
        
        assets = self.merge_data()
        self._print_summary(assets)
        
        if debug_logger.ms365_debug:
            for a in assets: debug_logger.log_parsed_asset_data('ms365', a)
            
        return assets

    def _print_summary(self, assets: List[Dict]) -> None:
        print(f"\n{'='*50}\nMicrosoft 365 Collection Summary\n{'='*50}")
        print(f"Total Inventory Assets: {len(assets)}")
        
        counts: Dict[str, int] = defaultdict(int)
        for a in assets:
            counts[a.get('_source', 'unknown')] += 1
        
        print(f"\nBy Source:")
        for src, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  - {src}: {count}")
        
        status_counts: Dict[str, int] = defaultdict(int)
        for a in assets:
            status_counts[a.get('management_status', 'Unknown')] += 1
        
        print(f"\nBy Management Status:")
        for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
            print(f"  - {status}: {count}")
        
        print(f"{'='*50}\n")

    def sync_to_logs(self):
        """For debugging."""
        print("Running Debug Sync...")
        raw_intune, trans_intune = self.intune_sync.get_transformed_assets()
        raw_teams, trans_teams = self.teams_sync.get_transformed_assets()
        raw_entra, trans_entra = self.entra_sync.get_transformed_assets()
        
        debug_logger.clear_logs('ms365')
        debug_logger.log_raw_host_data('ms365', 'raw_dump', {
            'intune': raw_intune, 
            'teams': raw_teams, 
            'entra': raw_entra
        })
        
        merged = self.merge_data(trans_intune, trans_teams, trans_entra)
        for m in merged:
            debug_logger.log_parsed_asset_data('ms365', m)
        
        print(f"Logged {len(merged)} merged assets.")

def main():
    agg = Microsoft365Aggregator()
    if debug_logger.ms365_debug:
        agg.sync_to_logs()
    else:
        agg.collect_assets()

if __name__ == "__main__":
    main()