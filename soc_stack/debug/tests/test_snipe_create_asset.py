#!/usr/bin/env python3

"""
Test creating a single asset via API.
"""

import json
from datetime import datetime

from soc_stack.config.hydra_settings import SNIPE
from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient

def get_valid_defaults(client):
    try:
        model_resp = client.make_api_request("GET", "/api/v1/models?limit=1")
        model_id = model_resp.json().get('rows', [{}])[0].get('id', 1) if model_resp and model_resp.status_code == 200 else 1
        
        status_resp = client.make_api_request("GET", "/api/v1/statuslabels?limit=1")
        status_id = status_resp.json().get('rows', [{}])[0].get('id', 1) if status_resp and status_resp.status_code == 200 else 1
        
        category_resp = client.make_api_request("GET", "/api/v1/categories?limit=1")
        category_id = category_resp.json().get('rows', [{}])[0].get('id', 1) if category_resp and category_resp.status_code == 200 else 1
        
        return model_id, status_id, category_id
   
    except Exception as e:
        print(f"Error: {e}")
        return 1, 1, 1

def test_create_asset():
    print("Testing asset creation...")
    client = SnipeClient()
    
    model_id, status_id, category_id = get_valid_defaults(client)
    print(f"Using - Model ID: {model_id}, Status ID: {status_id}, Category ID: {category_id}")
    
    test_asset = {
        "name": "Test-Asset-Debug",
        "asset_tag": f"TEST-{datetime.now().strftime('%H%M%S')}",
        "model_id": model_id, 
        "status_id": status_id,
        "category_id": category_id,  
        "notes": "Test asset for debugging"
    }
  
    print(f"Payload: {json.dumps(test_asset, indent=2)}")
        
    try:
        response = client.make_api_request("POST", "/api/v1/hardware", json=test_asset)
        
        if not response:
            print("✗ Request failed (No response returned)")
            return
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✓ Asset created successfully!")
                print(f"Asset ID: {result.get('payload', {}).get('id')}")
            else:
                print("✗ Asset creation failed with errors:")
                print(result.get('messages', 'Unknown error'))
        else:
            print("✗ Asset creation failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_asset()