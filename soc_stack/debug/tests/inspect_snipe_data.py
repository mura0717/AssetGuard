#!/usr/bin/env python3

"""
Inspect Snipe-IT assets and API.
"""

from soc_stack.config.hydra_settings import SNIPE
from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient

def snipeit_api_debug():
    print("=== Snipe-IT Asset Debug ===")
    client = SnipeClient()
    
    print("1. Testing API connection...")
    try:
        response = client.make_api_request("GET", "/api/v1/statuslabels")
        if response and response.status_code == 200:
            print("✓ API connection successful")
        else:
            print(f"✗ API connection failed: {response.status_code}")
            return
    except Exception as e:
        print(f"✗ API connection error: {e}")
        return
    
    print("\n2. Checking total assets...")
    try:
        response = client.make_api_request("GET", "/api/v1/hardware?limit=1")
        if response and response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"Total assets in system: {total}")
        else:
            print(f"Failed to get asset count: {response.status_code}")
    except Exception as e:
        print(f"Error getting asset count: {e}")
    
    print("\n3. Checking recent assets...")
    try:
        response = client.make_api_request("GET", "/api/v1/hardware?limit=100&sort=created_at&order=desc")
        if response and response.status_code == 200:
            data = response.json()
            assets = data.get('rows', [])
            print(f"Found {len(assets)} assets in API response")
            
            if assets:
                print("\nRecent assets:")
                for i, asset in enumerate(assets[:10]):  # Show first 10
                    print(f"  {i+1}. {asset.get('name', 'Unknown')} - {asset.get('asset_tag', 'No tag')} - ID: {asset.get('id')}")
            else:
                print("No assets found in API response")
                
        else:
            print(f"Failed to get assets: {response.status_code}")
    except Exception as e:
        print(f"Error getting assets: {e}")
    
    print("\n4. Checking custom fields...")
    try:
        response = client.make_api_request("GET", "/api/v1/fields")
        if response and response.status_code == 200:
            data = response.json()
            fields = data.get('rows', [])
            print(f"Custom fields configured: {len(fields)}")
        else:
            print(f"Failed to get custom fields: {response.status_code}")
    except Exception as e:
        print(f"Error checking custom fields: {e}")

if __name__ == "__main__":
    snipeit_api_debug()