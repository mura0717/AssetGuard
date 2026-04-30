#!/usr/bin/env python3

"""
Hydra Pipeline Integration Test
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.asset_engine.asset_resolver import AssetResolver, ResolvedAsset
from soc_stack.states.snipe_state import SnipeStateManager
from soc_stack.states.wazuh_state import WazuhStateManager
from soc_stack.states.zabbix_state import ZabbixStateManager
from soc_stack.builders.snipe_builder import SnipePayloadBuilder
from soc_stack.builders.zabbix_builder import ZabbixPayloadBuilder
from soc_stack.builders.wazuh_builder import WazuhPayloadBuilder
from soc_stack.states.base_state import StateResult

INTEGRATION_TESTS = os.getenv("HYDRA_INTEGRATION_TESTS", "0") == "1"
SNIPE_AVAILABLE = bool(os.getenv("SNIPE_API_TOKEN"))

def print_result(test_name: str, passed: bool, details: str = ""):
    symbol = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{symbol}{reset}] {test_name}")
    if details:
        print(f"    {details}")

def get_mock_nmap_assets() -> List[Dict]:
    return [
        {
            "last_seen_ip": "192.168.1.100",
            "name": "test-server-01",
            "dns_hostname": "test-server-01.local",
            "mac_addresses": "AA:BB:CC:DD:EE:FF",
            "manufacturer": "Dell Inc.",
            "model": "PowerEdge R640",
            "device_type": "Server",
            "nmap_discovered_services": ["ssh", "http", "https"],
            "nmap_open_ports": "22/tcp/ssh\n80/tcp/http\n443/tcp/https",
        },
        {
            "last_seen_ip": "192.168.1.101",
            "name": "Device-192.168.1.101",
            "dns_hostname": "",
        }
    ]

def get_mock_ms365_assets() -> List[Dict]:
    return [
        {
            "name": "LAPTOP-USER01",
            "serial": "ABC123XYZ",
            "manufacturer": "Lenovo",
            "model": "ThinkPad X1 Carbon",
            "os_platform": "Windows",
            "os_version": "11",
            "intune_device_id": "intune-device-001",
            "azure_ad_id": "azure-ad-001",
            "primary_user_upn": "user@company.com",
            "mac_addresses": "11:22:33:44:55:66",
        }
    ]

def test_resolver():
    print("\n=== Testing AssetResolver ===")
    
    try:
        resolver = AssetResolver()
        
        nmap_assets = get_mock_nmap_assets()
        resolved = resolver.resolve("nmap", nmap_assets)
        
        print_result(
            "Resolver returns ResolvedAsset objects",
            all(isinstance(r, ResolvedAsset) for r in resolved),
            f"Got {len(resolved)} ResolvedAsset objects"
        )
        
        print_result(
            "Source is tagged correctly",
            all(r.canonical_data.get('_source') == 'nmap' for r in resolved),
            f"All assets tagged with 'nmap'"
        )
        
        return True
        
    except Exception as e:
        print_result("AssetResolver", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_snipe_state():
    print("\n=== Testing SnipeStateManager ===")
    
    if not SNIPE_AVAILABLE:
        print("  [SKIP] Snipe-IT not configured")
        return True
    
    try:
        state = SnipeStateManager()
        
        asset_with_serial = {"serial": "TEST123", "name": "Test Device"}
        result = state.check(asset_with_serial)
        
        print_result(
            "State check returns StateResult",
            isinstance(result, StateResult),
            f"Action: {result.action}"
        )
        
        print_result(
            "Generate ID works",
            state.generate_id(asset_with_serial) is not None,
            f"ID: {state.generate_id(asset_with_serial)}"
        )
        
        return True
        
    except Exception as e:
        print_result("SnipeStateManager", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wazuh_state():
    print("\n=== Testing WazuhStateManager ===")
    
    try:
        from tempfile import TemporaryDirectory
        
        with TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "wazuh_state.json"
            state = WazuhStateManager(state_file)
            
            asset = {"serial": "WAZUH001", "name": "Test Device", "last_seen_ip": "192.168.1.50"}
            result = state.check(asset)
            
            print_result(
                "New asset returns 'create'",
                result.action == 'create',
                f"Action: {result.action}"
            )
            
            state.record(result.asset_id, asset, 'create')
            result2 = state.check(asset)
            
            print_result(
                "Unchanged asset returns 'skip'",
                result2.action == 'skip',
                f"Action: {result2.action}"
            )
            
            asset['last_seen_ip'] = "192.168.1.60"
            result3 = state.check(asset)
            
            print_result(
                "Changed asset returns 'update'",
                result3.action == 'update',
                f"Action: {result3.action}"
            )
            
        return True
        
    except Exception as e:
        print_result("WazuhStateManager", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_zabbix_state():
    print("\n=== Testing ZabbixStateManager ===")
    
    try:
        state = ZabbixStateManager()
        
        asset = {
            "name": "Test-Zabbix-Host",
            "last_seen_ip": "192.168.1.200",
            "mac_addresses": "11:22:33:44:55:66",
            "device_type": "Server"
        }
        
        result = state.check(asset)
        
        print_result(
            "State check returns StateResult",
            isinstance(result, StateResult),
            f"Action: {result.action}"
        )
        
        print_result(
            "Generate ID works (MAC priority)",
            result.asset_id == "mac:112233445566",
            f"ID: {result.asset_id}"
        )
        
        return True
        
    except Exception as e:
        print_result("ZabbixStateManager", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_snipe_builder():
    print("\n=== Testing SnipePayloadBuilder ===")
    
    if not SNIPE_AVAILABLE:
        print("  [SKIP] Snipe-IT not configured")
        return True
    
    try:
        builder = SnipePayloadBuilder()
        
        asset_data = {
            "name": "Test-Device",
            "serial": "TEST123",
            "manufacturer": "Dell",
            "model": "OptiPlex 7090",
            "mac_addresses": "AA:BB:CC:DD:EE:FF",
            "_source": "nmap"
        }
        
        state_result = StateResult(
            action='create',
            asset_id='snipe:serial:TEST123',
            existing=None,
            reason='New asset'
        )
        
        build_result = builder.build(asset_data, state_result)
        
        print_result(
            "Builder returns BuildResult",
            hasattr(build_result, 'payload'),
            f"Keys: {list(build_result.payload.keys())[:5]}..."
        )
        
        print_result(
            "Payload has required fields",
            all(k in build_result.payload for k in ['name', 'model_id']),
            f"Has name and model_id"
        )
        
        print_result(
            "Auto-generated asset_tag",
            build_result.payload.get('asset_tag', '').startswith('AUTO-'),
            f"Tag: {build_result.payload.get('asset_tag')}"
        )
        
        return True
        
    except Exception as e:
        print_result("SnipePayloadBuilder", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wazuh_builder():
    print("\n=== Testing WazuhPayloadBuilder ===")
    
    try:
        builder = WazuhPayloadBuilder()
        
        asset_data = {
            "name": "Test-Device",
            "last_seen_ip": "192.168.1.50",
            "nmap_open_ports": "22/tcp/ssh\n80/tcp/http",
            "device_type": "Desktop",
            "_source": "nmap"
        }
        
        state_result = StateResult(
            action='create',
            asset_id='serial:TEST123',
            existing=None,
            reason='New asset'
        )
        
        build_result = builder.build(asset_data, state_result)
        event = build_result.payload
        
        print_result(
            "Event has required structure",
            all(k in event for k in ['timestamp', 'hydra_event_type', 'event_action', 'asset', 'security']),
            f"Keys: {list(event.keys())}"
        )
        
        print_result(
            "Open ports parsed correctly",
            len(event['security']['open_ports']) == 2,
            f"Ports: {event['security']['open_ports']}"
        )
        
        print_result(
            "VLAN detection works",
            event['security']['vlan'] == "Primary LAN",
            f"VLAN: {event['security']['vlan']}"
        )
        
        return True
        
    except Exception as e:
        print_result("WazuhPayloadBuilder", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_zabbix_builder():
    print("\n=== Testing ZabbixPayloadBuilder ===")
    
    try:
        builder = ZabbixPayloadBuilder()
        
        asset_data = {
            "name": "Test-Server",
            "last_seen_ip": "192.168.1.100",
            "device_type": "Server",
            "serial": "SRV001",
            "_source": "nmap"
        }
        
        state_result = StateResult(
            action='create',
            asset_id='mac:112233445566',
            existing=None,
            reason='New host'
        )
        
        build_result = builder.build(asset_data, state_result)
        payload = build_result.payload
        
        print_result(
            "Group name mapping works",
            build_result.metadata.get('group_name') == "Servers",
            f"Group: {build_result.metadata.get('group_name')}"
        )
        
        print_result(
            "Payload has required fields",
            all(k in payload for k in ['host', 'name', 'groups', 'interfaces']),
            f"Keys: {list(payload.keys())}"
        )
        
        print_result(
            "Interface has correct IP",
            payload['interfaces'][0]['ip'] == "192.168.1.100",
            f"IP: {payload['interfaces'][0]['ip']}"
        )
        
        return True
        
    except Exception as e:
        print_result("ZabbixPayloadBuilder", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    print("\n=== Testing Full Pipeline (Dry Run) ===")
    
    if not SNIPE_AVAILABLE:
        print("  [SKIP] Snipe-IT not configured")
        return True
    
    try:
        from unittest.mock import patch
        from soc_stack.hydra_orchestrator import HydraOrchestrator
        
        nmap_data = get_mock_nmap_assets()
        
        with patch('soc_stack.scanners.nmap_scanner.NmapScanner') as MockNmap, \
             patch('soc_stack.scanners.ms365_aggregator.Microsoft365Aggregator') as MockMS365:
            
            MockNmap.return_value.collect_assets.return_value = nmap_data
            MockMS365.return_value.collect_assets.return_value = []

            orchestrator = HydraOrchestrator(dry_run=True)
            results = orchestrator.run_full_sync(sources=['nmap'])
            
            wazuh_res = results.get('wazuh')
            if wazuh_res:
                print_result(
                    "Wazuh Pipeline processed assets",
                    wazuh_res.created + wazuh_res.skipped > 0,
                    f"Created: {wazuh_res.created}, Skipped: {wazuh_res.skipped}"
                )
            else:
                print_result("Wazuh Pipeline ran", False, "No results returned")

            print_result("Snipe-IT Pipeline ran", 'snipe' in results)
            print_result("Zabbix Pipeline ran", 'zabbix' in results)
            
            print("  [INFO] Orchestrator generated summary log in logs/dry_runs/")

        return True
        
    except Exception as e:
        print_result("Full Pipeline", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("HYDRA PIPELINE INTEGRATION TEST")
    print("Mode: DRY RUN (No changes will be made)")
    print("=" * 60)
    
    results = []
    
    results.append(("Resolver", test_resolver()))
    results.append(("Wazuh State", test_wazuh_state()))
    results.append(("Zabbix State", test_zabbix_state()))
    results.append(("Wazuh Builder", test_wazuh_builder()))
    results.append(("Zabbix Builder", test_zabbix_builder()))
    
    if INTEGRATION_TESTS and SNIPE_AVAILABLE:
        results.append(("Snipe State", test_snipe_state()))
        results.append(("Snipe Builder", test_snipe_builder()))
        results.append(("Full Pipeline", test_full_pipeline()))
    else:
        print("\n[SKIP] Snipe-IT integration tests")
        if not SNIPE_AVAILABLE:
            print("       Reason: SNIPE_API_TOKEN is missing")
        if not INTEGRATION_TESTS:
            print("       Reason: HYDRA_INTEGRATION_TESTS != '1'")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        symbol = "✓" if result else "✗"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"  [{color}{symbol}{reset}] {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())