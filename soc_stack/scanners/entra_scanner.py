#!/usr/bin/env python3
"""
Entra ID Integration.
"""

from datetime import datetime, timezone
from typing import Dict, List

from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.debug.categorize_from_logs.entra_categorize_from_logs import entra_debug_categorization
from soc_stack.config.ms365_service import Microsoft365Service

class EntraScanner:
    """Entra ID sync service."""
    
    DEVICE_FIELDS = [
        "id",
        "deviceId",
        "displayName",
        "accountEnabled",
        "trustType",
        "profileType",
        "isCompliant",
        "isManaged",
        "approximateLastSignInDateTime",
        "registrationDateTime",         
        "onPremisesSyncEnabled",
        "onPremisesLastSyncDateTime",     
        "operatingSystem",
        "operatingSystemVersion",
        "manufacturer",
        "model",
        "mdmAppId",
    ]
    
    def __init__(self):
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.ms365_service = Microsoft365Service()
    
    def get_entra_devices(self) -> List[Dict]:
        """Fetch devices."""
        access_token = self.ms365_service.get_access_token()
        select_fields = ",".join(self.DEVICE_FIELDS)
        return self.ms365_service.get_assets(
            access_token=access_token,
            endpoint=f"devices?$select={select_fields}",
            source="entra"
        )
    
    def normalize_asset(self, entra_device: Dict) -> Dict:
        current_time = datetime.now(timezone.utc).isoformat()
        trust_type = entra_device.get('trustType', '')
        
        transformed = {
            'name': entra_device.get('displayName'),
            'azure_ad_id': entra_device.get('deviceId'),
            'entra_object_id': entra_device.get('id'),
            
            'entra_trust_type': trust_type,
            'entra_join_type': self._map_trust_type(trust_type),
            'entra_profile_type': entra_device.get('profileType'),      
            'entra_account_enabled': entra_device.get('accountEnabled'),
            'entra_is_compliant': entra_device.get('isCompliant'),
            'entra_is_managed': entra_device.get('isManaged'),
            'entra_mdm_app_id': entra_device.get('mdmAppId'),          
            
            'entra_last_sign_in': entra_device.get('approximateLastSignInDateTime'),
            'entra_registration_date': entra_device.get('registrationDateTime'), 
            
            'entra_on_prem_synced': entra_device.get('onPremisesSyncEnabled', False), 
            'entra_on_prem_last_sync': entra_device.get('onPremisesLastSyncDateTime'), 
            
            'os_platform': entra_device.get('operatingSystem'),
            'os_version': entra_device.get('operatingSystemVersion'),
            'manufacturer': entra_device.get('manufacturer'),
            'model': entra_device.get('model'),
            
            'last_update_source': 'entra',
            'last_update_at': current_time,
        }
        
        return {k: v for k, v in transformed.items() if v is not None and v != ""}
    
    def _map_trust_type(self, trust_type: str) -> str:
        mapping = {
            'AzureAd': 'Azure AD Joined',
            'ServerAd': 'Hybrid Azure AD Joined',
            'Workplace': 'Azure AD Registered (BYOD)',
        }
        return mapping.get(trust_type, trust_type or 'Unknown')
    
    def write_to_logs(self, raw_assets: List[Dict], transformed_assets: List[Dict]):
        """Log raw assets."""
        for raw_asset, transformed_asset in zip(raw_assets, transformed_assets):
            asset_id = raw_asset.get('id', 'Unknown')
            debug_logger.log_raw_host_data('entra', asset_id, raw_asset)
            debug_logger.log_parsed_asset_data('entra', transformed_asset)

    def get_transformed_assets(self) -> tuple[List[Dict], List[Dict]]:
        if entra_debug_categorization.debug:
            print("Running Entra categorization from existing logs...")
            entra_debug_categorization.write_managed_assets_to_logfile()
            return [], []

        print("Fetching Entra ID devices...")
        raw_devices = self.get_entra_devices()
        print(f"  Found {len(raw_devices)} devices in Entra ID")
        
        transformed = [self.normalize_asset(d) for d in raw_devices]
        
        if debug_logger.entra_debug:
            debug_logger.clear_logs('entra')
            self.write_to_logs(raw_devices, transformed)
            
        return raw_devices, transformed

def main():
    if entra_debug_categorization.debug:
        print("Running Entra categorization from existing logs...")
        entra_debug_categorization.write_managed_assets_to_logfile()
        return
    print("This script is not intended to be run directly. Use ms365_sync.py or hydra_orchestrator.py instead.")

if __name__ == "__main__":
    main()