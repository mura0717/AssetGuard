#!/usr/bin/env python3

import json

from soc_stack.snipe_it.snipe_api.services.assets import AssetService

def test_get_all_assets():
    print("Testing fetching all assets...")
    
    try:
        asset_service = AssetService()
        assets = asset_service.get_all(limit=10000, refresh_cache=True)
        
        if assets:
            print(f"✓ Successfully fetched {len(assets)} assets.")
            print(json.dumps(assets, indent=2))
        elif len(assets) == 0:
            print("✓ Currently there are 0 assets found in Snipe-IT.")
        else:
            print("✗ No assets returned.")
    
    except Exception as e:
        print(f"✗ Error occurred while fetching assets: {e}")

if __name__ == "__main__":
    test_get_all_assets()