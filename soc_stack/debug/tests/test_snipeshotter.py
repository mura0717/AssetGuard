#!/usr/bin/env python3

from pathlib import Path
from soc_stack.snipe_it.snipe_api.services.assets import AssetService

BASE_DIR = Path(__file__).resolve().parents[3]

def test_snipeshot():
    print("Taking snapshot of current Snipe-IT assets...")
    assets = []
    
    try:
        assets = AssetService().get_all(limit=10000, refresh_cache=True)
    except Exception as e:
        print(f"Error fetching all assets: {e}")
        return None
    
    for asset in assets:
        print(asset)
    
    if len(assets) == 0 or assets == []:
        print("No assets found in Snipe-IT.")
        return None
    
    print("Snapshot complete.")
    print(f"[Snapshot] Would be saved {len(assets)} assets to log.")
    return 

if __name__ == "__main__":
    test_snipeshot()