#!/usr/bin/env python3

"""
Central API Connectivity Tester
"""

import os
from urllib import response
import urllib3
from pathlib import Path

# Suppress insecure request warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from soc_stack.config.hydra_settings import SNIPE, ZABBIX, WAZUH
from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient
from soc_stack.wazuh.wazuh_api.wazuh_client import WazuhClient
from soc_stack.zabbix.zabbix_api.zabbix_client import ZabbixClient

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "settings.py"

def print_status(service, status, message):
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{symbol}{reset}] {service}: {message}")

def test_snipe():
    print("\n--- Testing Snipe-IT ---")
    print(f"Target URL: {SNIPE.snipe_url}")
    try:
        client = SnipeClient()
        response = client.make_api_request("GET", "/api/v1/users/me", timeout=10)
        if response and response.status_code == 200:
            data = response.json()
            user = data.get('username', 'Unknown')
            print_status("Snipe-IT API", True, f"Connected as '{user}'")
        else:
            status = response.status_code if response else "No Response"
            print_status("Snipe-IT API", False, f"HTTP {status}")
    except Exception as e:
        print_status("Snipe-IT API", False, f"Connection Error: {e}")

def test_zabbix():
    print("\n--- Testing Zabbix ---")
    print(f"Target URL: {ZABBIX.zabbix_url}")
    
    try:
        client = ZabbixClient()
        
        if client.auth:
            print_status("Zabbix Auth", True, "Authentication Successful")
            
            try:
                version = client.call("apiinfo.version", {}, require_auth=False)
                print_status("Zabbix Version", True, f"API Version {version}")
            except Exception as e:
                print_status("Zabbix Version", False, f"Error fetching version: {e}")
        else:
            print_status("Zabbix Auth", False, "Authentication Failed (Check logs/credentials)")

    except Exception as e:
        print_status("Zabbix API", False, f"Connection Error: {e}")

def test_wazuh():
    print("\n--- Testing Wazuh ---")
    print(f"API URL: {WAZUH.wazuh_api_url}")
    print(f"API User: {WAZUH.wazuh_api_user}")
    
    try:
        client = WazuhClient()
        if client.token:
            print_status("Wazuh API", True, "Token Obtained - Authentication Successful")
            try:
                info_data = client.get("/manager/info")
                ver = info_data.get('data', {}).get('version')
                if ver:
                    print(f"    > Manager Version: {ver}")
            except Exception as e:
                print(f"    > Could not fetch manager info: {e}")
        else:
            print_status("Wazuh API", False, "Authentication Failed")
        
            
    except Exception as e:
        print_status("Wazuh API", False, f"Connection Error: {e}")

    print(f"Ingestion Method: Log File + Agent")
    print(f"Log Path: {WAZUH.event_log}")
    
    try:
        log_dir = WAZUH.event_log.parent
        if not log_dir.exists():
             print_status("Wazuh Log", False, f"Directory does not exist: {log_dir}")
             return

        if os.access(log_dir, os.W_OK):
             print_status("Wazuh Log", True, "Log directory is writable")
        else:
             print_status("Wazuh Log", False, "Permission Denied writing to log directory")
             
        print("    ! Note: Direct Indexer connection skipped (Using Log+Agent method)")

    except Exception as e:
        print_status("Wazuh Log", False, f"Error: {e}")

if __name__ == "__main__":
    print("=== Central API Connectivity Test ===")
    print(f"Loaded Settings from: {CONFIG_PATH}")
    
    test_snipe()
    test_zabbix()
    test_wazuh()