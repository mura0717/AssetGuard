#!/usr/bin/env python3
"""
Teams Integration.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.config.ms365_service import Microsoft365Service
from soc_stack.debug.categorize_from_logs.teams_categorize_from_logs import teams_debug_categorization
from soc_stack.utils.mac_utils import combine_macs, macs_from_string

class TeamsScanner:
    """Teams sync service."""
    
    def __init__(self):
        self.ms365_service = Microsoft365Service()
    
    def get_teams_assets(self) -> List[Dict]:
        """Fetch devices."""
        access_token = self.ms365_service.get_access_token()
        return self.ms365_service.get_assets(access_token, "teamwork/devices", "teams")
            
    def normalize_asset(self, teams_asset: Dict) -> Dict:
        """Transform asset."""
        current_time = datetime.now(timezone.utc).isoformat()
        hardware_details = teams_asset.get('hardwareDetail', {})
        current_user = teams_asset.get('currentUser', {})
        last_modified_by_user = (teams_asset.get('lastModifiedBy') or {}).get('user', {})
        serial_raw = hardware_details.get("serialNumber") or ""
        serial = serial_raw.upper() if serial_raw else None
        all_macs = []
        for raw_mac in (hardware_details.get('macAddresses') or []):
            extracted = macs_from_string(str(raw_mac))
            all_macs.extend(extracted)
        
        transformed = {
            
            'teams_device_id': teams_asset.get('id'),
            'teams_device_type': teams_asset.get('deviceType'),
            'teams_health_status': teams_asset.get('healthStatus'),
            'teams_activity_state': teams_asset.get('activityState'),
            'teams_last_modified': teams_asset.get('lastModifiedDateTime'),
            'teams_created_date': teams_asset.get('createdDateTime'),
            'teams_last_modified_by_id': last_modified_by_user.get('id'),
            'teams_last_modified_by_name': last_modified_by_user.get('displayName'),
            
            'asset_tag': teams_asset.get('companyAssetTag'),
            'name': teams_asset.get('displayName') or teams_asset.get('hostname') or current_user.get('displayName'),
            'serial': serial,
            'notes': teams_asset.get('notes'),
            
            'manufacturer': hardware_details.get('manufacturer'),
            'model': hardware_details.get('model'),
            
            'mac_addresses': combine_macs(all_macs),
            
            'last_update_source': 'teams',
            'last_update_at': current_time,
            
            'primary_user_id': current_user.get('id'),
            'primary_user_display_name': current_user.get('displayName'),
            'identity_type': current_user.get('userIdentityType'),
        }

        return {k: v for k, v in transformed.items() if v is not None and v != ""}

    def write_to_logs(self, raw_assets: List[Dict], transformed_assets: List[Dict]):
        """Log raw assets."""
        for raw_asset, transformed_asset in zip(raw_assets, transformed_assets):
            asset_id = raw_asset.get('id', 'Unknown')
            debug_logger.log_raw_host_data('teams', asset_id, raw_asset)
            debug_logger.log_parsed_asset_data('teams', transformed_asset)

    def get_transformed_assets(self) -> tuple[List[Dict], List[Dict]]:
        """Fetch and transform."""
        if teams_debug_categorization.debug:
            print("Running Teams categorization from existing logs...")
            teams_debug_categorization.write_teams_assets_to_logfile()
            return [], [] # Return empty lists as no new scan was performed

        print("Fetching and transforming Teams assets...")
        raw_assets = self.get_teams_assets()
        transformed_assets = [self.normalize_asset(asset) for asset in raw_assets]

        if debug_logger.teams_debug:
            debug_logger.clear_logs('teams')
            self.write_to_logs(raw_assets, transformed_assets)

        return raw_assets, transformed_assets

def main():
    if teams_debug_categorization.debug:
        print("Running Teams categorization from existing logs...")
        teams_debug_categorization.write_teams_assets_to_logfile()
        return
    print("This script is not intended to be run directly. Use ms365_sync.py instead.")

if __name__ == "__main__":
    main()
