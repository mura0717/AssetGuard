"""
Snipe-IT State Manager
Handles asset existence checks against Snipe-IT API with caching.
"""

import os
from typing import Dict, Optional, List

from soc_stack.states.base_state import BaseStateManager, StateResult
from soc_stack.asset_engine.asset_finder import AssetFinder
from soc_stack.snipe_it.snipe_api.services.assets import AssetService
from soc_stack.config.network_config import STATIC_IP_MAP
from soc_stack.utils.mac_utils import normalize_mac_semicolon, get_primary_mac_address


class SnipeStateManager(BaseStateManager):
    """
    Manages asset state against Snipe-IT with caching to avoid rate limiting.
    """
    
    IDENTITY_PRIORITY = ('serial', 'asset_tag', 'mac_addresses', 'intune_device_id')
    
    def __init__(self):
        self.service = AssetService()
        self.finder = AssetFinder(self.service)
        self._match_cache: Dict[str, Dict] = {}
        self._all_assets: Optional[List[Dict]] = None
        self._cache_loaded = False
        self.debug = os.getenv('SNIPE_STATE_DEBUG', '0') == '1'

    def _load_all_assets(self) -> None:
        """Load all assets from Snipe-IT once for matching."""
        if self._cache_loaded:
            return
            
        print("  [Snipe State] Loading all assets for matching...")
        try:
            self._all_assets = self.service.get_all() or []
            self._cache_loaded = True
            print(f"  [Snipe State] Loaded {len(self._all_assets)} existing assets")
            
            # Build lookup indexes
            self._index_by_serial = {}
            self._index_by_mac = {}
            self._index_by_asset_tag = {}
            self._index_by_name = {}
            self._index_by_intune_id = {}
            self._index_by_aad_id = {}      
            
            for asset in self._all_assets:
                # Index by serial (normalized)
                serial = asset.get('serial')
                if serial:
                    self._index_by_serial[self._normalize_serial(serial)] = asset
                
                # Index by asset tag
                tag = asset.get('asset_tag')
                if tag:
                    self._index_by_asset_tag[tag] = asset
                
                # Index by MAC (standard field)
                standard_mac = asset.get('mac_address')
                if standard_mac:
                    norm = normalize_mac_semicolon(standard_mac)
                    if norm:
                        mac_key = norm.replace(':', '').upper()
                        if mac_key not in self._index_by_mac:
                            self._index_by_mac[mac_key] = asset
                        else:
                            # Prefer most recently updated asset if duplicate MAC exists
                            existing = self._index_by_mac[mac_key]
                            existing_updated = existing.get('updated_at', {})
                            if isinstance(existing_updated, dict):
                                existing_updated = existing_updated.get('datetime', '')
                            current_updated = asset.get('updated_at', {})
                            if isinstance(current_updated, dict):
                                current_updated = current_updated.get('datetime', '')
                            
                            if str(current_updated) > str(existing_updated):
                                if self.debug:
                                    print(f"    Duplicate MAC {mac_key}: preferring ID {asset['id']} "
                                        f"over {existing['id']} (more recent)")
                                self._index_by_mac[mac_key] = asset
                
                # Index by MAC (from custom fields) - MUST BE INSIDE THE LOOP
                for cf_name, cf_data in asset.get('custom_fields', {}).items():
                    if 'mac' in cf_name.lower():
                        mac = cf_data.get('value', '') if isinstance(cf_data, dict) else cf_data
                        if mac:
                            for m in str(mac).replace(',', '\n').replace(';', '\n').split('\n'):
                                m = m.strip()
                                if not m:
                                    continue
                                norm = normalize_mac_semicolon(m)
                                if norm:
                                    mac_key = norm.replace(':', '').upper()
                                    if mac_key not in self._index_by_mac:
                                        self._index_by_mac[mac_key] = asset
                
                # Index by name (exact match)
                name = asset.get('name')
                if name:
                    self._index_by_name[name.lower()] = asset
                
                # Index by Intune Device ID (from custom fields)
                intune_id = None
                aad_id = None
                for cf_name, cf_data in asset.get('custom_fields', {}).items():
                    cf_name_lower = cf_name.lower()
                    val = cf_data.get('value', '') if isinstance(cf_data, dict) else cf_data
                    if not val:
                        continue
                    if 'intune device id' in cf_name_lower or 'intune_device_id' in cf_name_lower:
                        intune_id = str(val).strip().lower()
                    elif 'azure ad device id' in cf_name_lower or 'azure_ad_id' in cf_name_lower:
                        aad_id = str(val).strip().lower()
                
                if intune_id:
                    self._index_by_intune_id[intune_id] = asset
                if aad_id:
                    self._index_by_aad_id[aad_id] = asset
                    
        except Exception as e:
            print(f"  [Snipe State] Error loading assets: {e}")
            self._all_assets = []
            self._cache_loaded = True

    def generate_id(self, asset_data: Dict) -> Optional[str]:
        """Generate unique identifier from asset data."""
        for field in self.IDENTITY_PRIORITY:
            value = asset_data.get(field)
            if value:
                return f"snipe:{field}:{value}"
        return None

    def check(self, asset_data: Dict) -> StateResult:
        """Check if asset exists in Snipe-IT and determine action."""
        # Ensure cache is loaded
        self._load_all_assets()
        
        asset_id = self.generate_id(asset_data)
        
        # Check cache first
        cache_key = self._get_cache_key(asset_data)
        if cache_key and cache_key in self._match_cache:
            existing = self._match_cache[cache_key]
            return StateResult(
                action='update',
                asset_id=str(existing['id']),
                existing=existing,
                reason=f"Cached match: Snipe ID {existing['id']}"
            )
        
        # Find existing asset using indexes (fast, no API calls)
        existing = self._find_existing_cached(asset_data)
        
        if existing:
            # Cache the match
            if cache_key:
                self._match_cache[cache_key] = existing
            
            return StateResult(
                action='update',
                asset_id=str(existing['id']),
                existing=existing,
                reason=f"Found existing Snipe-IT asset ID: {existing['id']}"
            )
            
        if self._has_sufficient_data(asset_data):
            return StateResult(
                action='create',
                asset_id=asset_id or '',
                existing=None,
                reason='New asset with sufficient data'
            )

        return StateResult(
            action='skip',
            asset_id=asset_id or '',
            existing=None,
            reason='Insufficient data for creation'
        )

    def _normalize_serial(self, serial: str) -> str:
        """Normalize serial number for consistent comparison."""
        if not serial:
            return ''
        # Remove whitespace, hyphens, normalize case
        return serial.strip().upper().replace(' ', '').replace('-', '').replace('_', '')
    
    def _get_cache_key(self, asset_data: Dict) -> Optional[str]:
        """Generate cache key from asset identifiers."""
        if asset_data.get('serial'):
            return f"serial:{self._normalize_serial(asset_data['serial'])}"
        if asset_data.get('mac_addresses'):
            mac = get_primary_mac_address(asset_data['mac_addresses'])
            if mac:
                norm = normalize_mac_semicolon(mac)
                if norm:
                    return f"mac:{norm.replace(':', '').upper()}"
        if asset_data.get('asset_tag'):
            return f"tag:{asset_data['asset_tag']}"
        return None

    def _find_existing_cached(self, asset_data: Dict) -> Optional[Dict]:
        """Find existing asset using cached indexes (no API calls)."""
        
        # 1. By serial (most reliable)
        serial = asset_data.get('serial')
        if serial:
            match = self._index_by_serial.get(self._normalize_serial(serial))
            if match:
                if self.debug:
                    print(f"    Match by serial: {serial} -> ID {match['id']}")
                return match
        
        # 2. By asset tag
        tag = asset_data.get('asset_tag')
        if tag:
            match = self._index_by_asset_tag.get(tag)
            if match:
                if self.debug:
                    print(f"    Match by asset_tag: {tag} -> ID {match['id']}")
                return match
        
        # 3. By MAC address
        macs = self._extract_all_macs(asset_data)
        for mac_key in macs:
            match = self._index_by_mac.get(mac_key)
            if match:
                if self.debug:
                    print(f"    Match by MAC: {mac_key} -> ID {match['id']}")
                return match
        
        # 4. By exact name match (for static IP devices)
        name = asset_data.get('name')
        if name and not name.lower().startswith('device-'):
            match = self._index_by_name.get(name.lower())
            if match:
                # Validate: if new asset has serial, existing must match or be empty
                new_serial = asset_data.get('serial')
                existing_serial = match.get('serial')
                
                if new_serial and existing_serial:
                    if self._normalize_serial(new_serial) != self._normalize_serial(existing_serial):
                        if self.debug:
                            print(f"    Name match REJECTED (serial conflict): {name} "
                                f"(new: {new_serial}, existing: {existing_serial})")
                        return None
                
                # Additional check: if MACs exist on both, they should overlap
                new_macs = self._extract_all_macs(asset_data)
                existing_macs = self._extract_all_macs_from_existing(match)
                
                if new_macs and existing_macs:
                    if not new_macs.intersection(existing_macs):
                        if self.debug:
                            print(f"    Name match REJECTED (no MAC overlap): {name}")
                        return None
                
                if self.debug:
                    print(f"    Match by name: {name} -> ID {match['id']}")
                return match

        # 5. By Intune Device ID
        intune_id = asset_data.get('intune_device_id')
        if intune_id:
            match = self._index_by_intune_id.get(str(intune_id).strip().lower())
            if match:
                if self.debug:
                    print(f"    Match by Intune ID: {intune_id} -> ID {match['id']}")
                return match

        # 6. By Azure AD ID
        aad_id = asset_data.get('azure_ad_id')
        if aad_id:
            match = self._index_by_aad_id.get(str(aad_id).strip().lower())
            if match:
                if self.debug:
                    print(f"    Match by AAD ID: {aad_id} -> ID {match['id']}")
                return match
        
        return None

    def _extract_all_macs(self, asset_data: Dict) -> set:
        """Extract all MAC addresses from asset data as normalized set."""
        macs = set()
        for key in ['mac_addresses', 'wifi_mac', 'ethernet_mac']:
            val = asset_data.get(key)
            if val:
                if isinstance(val, list):
                    for m in val:
                        norm = normalize_mac_semicolon(str(m).strip())
                        if norm:
                            macs.add(norm.replace(':', '').upper())
                else:
                    for m in str(val).replace(',', '\n').split('\n'):
                        norm = normalize_mac_semicolon(m.strip())
                        if norm:
                            macs.add(norm.replace(':', '').upper())
        return macs

    def _extract_all_macs_from_existing(self, asset: Dict) -> set:
        """Extract all MACs from existing Snipe-IT asset."""
        macs = set()
        # Standard field
        if asset.get('mac_address'):
            norm = normalize_mac_semicolon(asset['mac_address'])
            if norm:
                macs.add(norm.replace(':', '').upper())
        # Custom fields
        for cf_name, cf_data in asset.get('custom_fields', {}).items():
            if 'mac' in cf_name.lower():
                val = cf_data.get('value') if isinstance(cf_data, dict) else cf_data
                if val:
                    for m in str(val).replace(',', '\n').replace(';', '\n').split('\n'):
                        norm = normalize_mac_semicolon(m.strip())
                        if norm:
                            macs.add(norm.replace(':', '').upper())
        return macs

    def record(self, asset_id: str, asset_data: Dict, action: str) -> None:
        """
        Update internal indexes after a successful create to prevent duplicates
        within the same run.
        """
        cache_key = self._get_cache_key(asset_data)
        
        if action == 'create':
            # Create a stub representing the just-created asset
            # Use the actual Snipe ID if provided by dispatcher
            snipe_id = int(asset_id) if asset_id and str(asset_id).isdigit() else None
            
            if snipe_id:
                created_stub = {
                    "id": snipe_id, 
                    "name": asset_data.get("name"),
                    "serial": asset_data.get("serial"),
                    "asset_tag": asset_data.get("asset_tag"),
                    "mac_address": asset_data.get("mac_addresses", "").split('\n')[0] if asset_data.get("mac_addresses") else None,
                    "custom_fields": {}
                }
            else:
                # Mark as pending to prevent duplicate create attempts
                created_stub = {"id": "PENDING", "name": asset_data.get("name")}
            
            # Update match cache
            if cache_key:
                self._match_cache[cache_key] = created_stub
            
            # Update indexes to prevent duplicate creation in same run
            serial = asset_data.get('serial')
            if serial:
                self._index_by_serial[self._normalize_serial(serial)] = created_stub
            
            tag = asset_data.get('asset_tag')
            if tag:
                self._index_by_asset_tag[tag] = created_stub
            
            mac_val = asset_data.get('mac_addresses') or asset_data.get('wifi_mac') or asset_data.get('ethernet_mac')
            if mac_val:
                mac = get_primary_mac_address(mac_val)
                if mac:
                    norm = normalize_mac_semicolon(mac)
                    if norm:
                        self._index_by_mac[norm.replace(':', '').upper()] = created_stub
            
            name = asset_data.get('name')
            if name and not name.lower().startswith('device-'):
                self._index_by_name[name.lower()] = created_stub
        
        elif action == 'update' and cache_key:
            # For updates, just ensure cache is populated
            if cache_key not in self._match_cache:
                self._match_cache[cache_key] = {"id": asset_id}

    def _has_sufficient_data(self, asset_data: Dict) -> bool:
        """Check if asset has enough data to create a new record."""
        if asset_data.get('last_seen_ip') in STATIC_IP_MAP:
            return True
        if asset_data.get('serial'):
            return True
        if any(asset_data.get(k) for k in ('mac_addresses', 'wifi_mac', 'ethernet_mac')):
            return True
        if asset_data.get('asset_tag'):
            return True
        if asset_data.get('intune_device_id') or asset_data.get('azure_ad_id'):
            return True
        
        name = (asset_data.get('name') or '').strip()
        dns = asset_data.get('dns_hostname', '')
        if name and not name.lower().startswith('device-') and dns not in ('', '_gateway'):
            return True
        
        return False