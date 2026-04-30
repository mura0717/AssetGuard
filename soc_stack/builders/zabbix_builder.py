"""
Zabbix Payload Builder Module
"""

import os
from typing import Dict

from soc_stack.builders.base_builder import BasePayloadBuilder, BuildResult
from soc_stack.states.base_state import StateResult
from soc_stack.utils.mac_utils import normalize_mac_semicolon


class ZabbixPayloadBuilder(BasePayloadBuilder):
    """
    Transforms canonical asset data into Zabbix Host JSON-RPC payloads.
    """
    
    GROUP_MAPPING = {
        "switch": "Network/Switches",
        "router": "Network/Routers",
        "firewall": "Network/Firewalls",
        "access point": "Network/Access Points",
        "network device": "Network/Devices",
        "server": "Servers",
        "printer": "Printers",
        "camera": "IoT/Cameras",
        "desktop": "Workstations",
        "storage": "Storage Devices",
    }
    
    def __init__(self):
        self.debug = os.getenv('ZABBIX_BUILDER_DEBUG', '0') == '1'

    def build(self, asset_data: Dict, state_result: StateResult) -> BuildResult:
        hostname = (asset_data.get("name") or "Unknown").strip()
        ip = asset_data.get("last_seen_ip", "")
        device_type = asset_data.get("device_type", "")
        
        zabbix_host = self._sanitize_hostname(hostname)
        group_name = self._get_group_name(device_type)
        
        # Robust MAC handling (Handle list or string)
        raw_macs = asset_data.get("mac_addresses")
        mac_list = []
        if isinstance(raw_macs, list):
            mac_list = raw_macs
        elif isinstance(raw_macs, str) and raw_macs:
            mac_list = [m.strip() for m in raw_macs.split('\n') if m.strip()]
            
        # Normalize and extract up to 2 MACs
        valid_macs = [m for m in (normalize_mac_semicolon(str(x)) for x in mac_list) if m]
        mac_a = valid_macs[0] if len(valid_macs) > 0 else ""
        mac_b = valid_macs[1] if len(valid_macs) > 1 else ""
        
        payload = {
            "host": zabbix_host,
            "name": hostname,
            "groups": [{"name": group_name}],  # Resolved to ID by dispatcher
            "interfaces": [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "10050"
            }],
            "inventory_mode": 1,
            "inventory": {
                # THE KEY: Store our asset_key for future lookups
                "asset_tag": state_result.asset_id,
                
                "serialno_a": asset_data.get("serial") or "",
                "macaddress_a": mac_a,
                "macaddress_b": mac_b,
                "vendor": asset_data.get("manufacturer") or "",
                "model": asset_data.get("model") or "",
                "os": asset_data.get("os_platform") or asset_data.get("nmap_os_guess") or "",
                "notes": f"Managed by Hydra | Source: {asset_data.get('_source', 'unknown')}"
            },
            "tags": [
                {"tag": "source", "value": asset_data.get("_source", "hydra")},
                {"tag": "device_type", "value": device_type or "unknown"},
                {"tag": "hydra_managed", "value": "true"}
            ]
        }
        
        if self.debug:
                print(f"\n[Zabbix Builder] Built payload for asset_id={state_result.asset_id} action={state_result.action}")
                print(f"  Host: {zabbix_host}, Group: {group_name}, IP: {ip}")
                print(f"  Payload: {payload}\n")
        
        return BuildResult(
            payload=payload,
            asset_id=state_result.asset_id,
            action=state_result.action,
            metadata={
                "group_name": group_name,
                "hostid": state_result.existing['hostid'] if state_result.existing else None
            }           
        )     
        
           

    def _sanitize_hostname(self, name: str) -> str:
        clean = name.replace(" ", "_").replace("/", "-")
        return "".join(c for c in clean if c.isalnum() or c in "._-")[:64]

    def _get_group_name(self, dtype: str) -> str:
        dt = (dtype or "").lower()
        for key, group in self.GROUP_MAPPING.items():
            if key in dt:
                return group
        return "Discovered hosts"