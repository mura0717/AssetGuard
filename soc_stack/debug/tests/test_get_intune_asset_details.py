#!/usr/bin/env python3

"""
Fetch single Intune device raw data.
"""

import sys
import requests
import json

from soc_stack.scanners.intune_scanner import IntuneScanner

GRAPH_URL = "https://graph.microsoft.com/v1.0"

def get_device(device_id: str, token: str):
    """Fetch single device from Intune"""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    try:
        response = requests.get(
            f"{GRAPH_URL}/deviceManagement/managedDevices/{device_id}", 
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    sync = IntuneScanner()
    token = sync.get_access_token()
    
    if not token:
        print("ERROR: Set AZURE_BEARER_TOKEN environment variable")
        sys.exit(1)
    
    device_id = None
    if len(sys.argv) >= 2:
        device_id = sys.argv[1]
    else:
        print("No device id provided on command line — attempting to fetch managed devices and auto-select the first one...")
        try:
            managed = sync.get_intune_assets()
        except Exception:
            managed = None

        if managed and isinstance(managed, list) and len(managed) > 0:
            # common Intune field is 'id'
            device_id = managed[0].get('id') or managed[0].get('deviceId') or managed[0].get('intune_device_id')
            if device_id:
                print(f"Auto-selected device id: {device_id}")
        if not device_id:
            print("Usage: python debug/get_intune_device.py <device_id>")
            print("Or run after ensuring IntuneSync.get_managed_assets() returns devices.")
            sys.exit(1)
    
    device = get_device(device_id, token)
    if device:
        print(json.dumps(device, indent=2))