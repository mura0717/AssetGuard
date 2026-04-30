"""
Utility for finding existing assets in Snipe-IT using various strategies.
"""

from typing import Dict, List, Optional

from soc_stack.snipe_it.snipe_api.services.assets import AssetService
from soc_stack.config import network_config
from soc_stack.config.snipe_schema import CUSTOM_FIELDS
from soc_stack.utils.mac_utils import macs_from_keys, macs_from_any, intersect_mac_sets

class AssetFinder:
    """
    A helper class to find assets in Snipe-IT using a prioritized set of matching strategies.
    """
    def __init__(self, asset_service: AssetService):
        self.asset_service = asset_service
        self._all_assets_cache: Optional[List[Dict]] = None

    def _get_all_assets(self) -> List[Dict]:
        """Lazily fetches all assets from the API, caching the result for the lifetime of the instance."""
        if self._all_assets_cache is None:
            print("  -> Fetching all assets for matching...")
            self._all_assets_cache = self.asset_service.get_all()
        return self._all_assets_cache

    def _get_custom_field(self, existing_asset: Dict, key: str) -> Optional[str]:
        """Helper to safely retrieve a custom field value from an asset dictionary."""
        field_def = CUSTOM_FIELDS.get(key)
        if not field_def:
            return None
        label = field_def['name']
        return (existing_asset.get('custom_fields', {})
                            .get(label, {})
                            .get('value'))

    def _has_sufficient_match_data(self, asset_data: Dict) -> bool:
        """
        Internal check to ensure incoming data has at least one strong identifier
        before attempting to match against existing assets. This prevents updates
        based on low-quality data.
        """
        if asset_data.get('serial'):
            return True
        if asset_data.get('mac_addresses') or asset_data.get('wifi_mac') or asset_data.get('ethernet_mac'):
            return True
        if asset_data.get('intune_device_id') or asset_data.get('azure_ad_id'):
            return True
        dns_hostname = asset_data.get('dns_hostname', '')
        if dns_hostname and not dns_hostname.startswith('Device-') and dns_hostname not in ['', '_gateway']:
            return True
        name = (asset_data.get('name') or '').strip()
        if name and not name.lower().startswith('device-'):
            return True
        return bool(asset_data.get('asset_tag'))

    def by_serial(self, serial: Optional[str]) -> Optional[Dict]:
        """Strategy 1: Find by serial number (fast API search)."""
        if not serial:
            return None
        existing = self.asset_service.search_by_serial(serial)
        if existing:
            print(f"  ✓ Found by serial: {serial} (ID: {existing.get('id')})")
        return existing

    def by_asset_tag(self, asset_tag: Optional[str]) -> Optional[Dict]:
        """Strategy 2: Find by asset tag (fast API search)."""
        if not asset_tag:
            return None
        existing = self.asset_service.search_by_asset_tag(asset_tag)
        if existing:
            print(f"  ✓ Found by asset_tag: {asset_tag} (ID: {existing.get('id')})")
        return existing
    
    def by_static_mapping(self, ip_address: Optional[str]) -> Optional[Dict]:
        """Strategy 3: Find by trusted hostname from the static IP map."""
        if not ip_address:
            return None

        static_info = network_config.STATIC_IP_MAP.get(ip_address)
        if not static_info or not static_info.get('host_name'):
            return None
        
        trusted_hostname = static_info['host_name']
        print(f"  Static IP mapping found for {ip_address}. Searching for trusted hostname: '{trusted_hostname}'")

        # Search for an asset with this exact name
        for asset in self._get_all_assets():
            asset_name = asset.get('name')
            if isinstance(asset_name, str) and trusted_hostname.lower() == asset_name.lower():
                print(f"  ✓ Found by static map hostname: '{trusted_hostname}' (ID: {asset.get('id')})")
                return asset
        return None
    
    def by_mac_address(self, asset_data: Dict) -> Optional[Dict]:
        """Strategy 4: Find by MAC address (requires full asset list)."""
        if not self._has_sufficient_match_data(asset_data):
            return None

        mac_fields = ('mac_addresses', 'wifi_mac', 'ethernet_mac', 'mac_address')
        new_macs = macs_from_keys(asset_data, mac_fields)

        if not new_macs:
            return None

        for asset in self._get_all_assets():
            # Also check wifi_mac and ethernet_mac custom fields on existing assets
            existing_set = macs_from_any(asset.get('mac_address'))
            existing_set |= macs_from_any(self._get_custom_field(asset, 'mac_addresses'))
            existing_set |= macs_from_any(self._get_custom_field(asset, 'wifi_mac')) # From Intune
            existing_set |= macs_from_any(self._get_custom_field(asset, 'ethernet_mac')) # From Intune

            hit = intersect_mac_sets(new_macs, existing_set)
            if hit:
                print(f"  ✓ Found by MAC: {hit} (ID: {asset.get('id')})")
                return asset
        return None

    def by_hostname(self, asset_data: Dict) -> Optional[Dict]:
        """Strategy 5: Find by hostname (requires full asset list)."""
        if not self._has_sufficient_match_data(asset_data):
            return None

        # Prioritize the trusted 'host_name' from static map, then fall back to others.
        dns_hostname = asset_data.get('host_name') or asset_data.get('dns_hostname') or asset_data.get('name')
        if not isinstance(dns_hostname, str) or dns_hostname.startswith('Device-'):
            return None

        clean_hostname = dns_hostname.split('.')[0].lower()
        for asset in self._get_all_assets():
            # Check asset name
            asset_name = asset.get('name')
            if isinstance(asset_name, str) and clean_hostname == asset_name.split('.')[0].lower():
                print(f"  ✓ Found by hostname: '{dns_hostname}' -> '{asset_name}' (ID: {asset.get('id')})")
                return asset
            # Check custom field for hostname
            cf_host = self._get_custom_field(asset, 'dns_hostname')
            if isinstance(cf_host, str) and clean_hostname == cf_host.split('.')[0].lower():
                print(f"  ✓ Found by DNS hostname custom field: {dns_hostname} (ID: {asset.get('id')})")
                return asset
        return None

    def by_partial_hostname(self, asset_data: Dict) -> Optional[Dict]:
        pass

    def by_ip_address(self, ip_address: Optional[str]) -> Optional[Dict]:
        """Strategy 6: Find by last seen IP address (requires full asset list)."""
        if not ip_address: # IP is considered a weak identifier, so we don't check for sufficient data
            return None

        for asset in self._get_all_assets():
            if self._get_custom_field(asset, 'last_seen_ip') == ip_address:
                print(f"  ✓ Found by IP: {ip_address} (ID: {asset.get('id')})")
                return asset
        return None

    def by_model_manufacturer_ip(self, asset_data: Dict) -> Optional[Dict]:
        pass
    
    def by_fallback_identifiers(self, asset_data: Dict) -> Optional[Dict]:
        """Strategy 7: Find by other unique identifiers in custom fields."""
        if not self._has_sufficient_match_data(asset_data):
            return None

        identifiers_to_check = ['intune_device_id', 'azure_ad_id', 'teams_device_id', 'entra_object_id']
        for key in identifiers_to_check:
            new_value = asset_data.get(key)
            if not new_value:
                continue

            for asset in self._get_all_assets():
                existing_value = self._get_custom_field(asset, key)
                if existing_value and existing_value.strip().lower() == str(new_value).strip().lower():
                    print(f"  ✓ Found by fallback identifier '{key}': {new_value} (ID: {asset.get('id')})")
                    return asset
        return None