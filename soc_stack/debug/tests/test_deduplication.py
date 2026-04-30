#!/usr/bin/env python3

"""
Deduplication Logic Test
"""

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.states.wazuh_state import WazuhStateManager
from soc_stack.states.zabbix_state import ZabbixStateManager
from soc_stack.states.snipe_state import SnipeStateManager

def print_result(test_name: str, passed: bool, details: str = ""):
    symbol = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{symbol}{reset}] {test_name}")
    if details:
        print(f"    {details}")

def test_wazuh_deduplication():
    print("\n=== Testing Wazuh Deduplication ===")
    with TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "wazuh_state.json"
        state = WazuhStateManager(state_file)
        
        asset_a = {
            "name": "Device-A",
            "mac_addresses": "AA:BB:CC:DD:EE:FF",
            "last_seen_ip": "192.168.1.50"
        }
        res_a = state.check(asset_a)
        state.record(res_a.asset_id, asset_a, 'create')
        
        asset_b = {
            "name": "Device-A",
            "mac_addresses": ["aabbccddeeff"], # Different format, same MAC
            "last_seen_ip": "192.168.1.50"
        }
        res_b = state.check(asset_b)
        
        print_result(
            "Wazuh: Matches String vs List MAC",
            res_b.action != 'create',
            f"ID A: {res_a.asset_id} | ID B: {res_b.asset_id}"
        )
        
        print_result(
            "Wazuh: IDs are identical",
            res_a.asset_id == res_b.asset_id,
            f"Expected: {res_a.asset_id}"
        )

def test_zabbix_deduplication():
    print("\n=== Testing Zabbix Deduplication ===")
    class MockZabbixState(ZabbixStateManager):
        def _load_all_hosts(self):
            self._index_by_mac = {
                "AABBCCDDEEFF": {"hostid": "1001", "host": "ExistingHost"}
            }
            self._cache_loaded = True
            
    state = MockZabbixState()
    
    asset = {
        "name": "NewDevice",
        "mac_addresses": "aa:bb:cc:dd:ee:ff\n11:22:33:44:55:66",
        "last_seen_ip": "10.0.0.1",
        "device_type": "Server"
    }
    
    res = state.check(asset)
    
    print_result(
        "Zabbix: Finds existing by MAC (Normalized)",
        res.action == 'update',
        f"Found HostID: {res.existing['hostid'] if res.existing else 'None'}"
    )

def test_snipe_deduplication():
    print("\n=== Testing Snipe-IT Deduplication ===")
    class MockSnipeState(SnipeStateManager):
        def _load_all_assets(self):
            self._index_by_mac = {
                "AABBCCDDEEFF": {"id": 500, "name": "Existing Asset"}
            }
            self._index_by_serial = {}
            self._index_by_asset_tag = {}
            self._index_by_name = {}
            self._cache_loaded = True
            
    state = MockSnipeState()
    
    asset = {
        "name": "Scanned Device",
        "mac_addresses": ["AA-BB-CC-DD-EE-FF"],
        "serial": None
    }
    
    res = state.check(asset)
    
    print_result(
        "Snipe: Finds existing by MAC (List Input)",
        res.action == 'update',
        f"Found Asset ID: {res.asset_id}"
    )

if __name__ == "__main__":
    test_wazuh_deduplication()
    test_zabbix_deduplication()
    test_snipe_deduplication()
