"""
Wazuh Payload Builder Module
"""

import os
from datetime import datetime, timezone
from typing import Dict, Optional

from soc_stack.builders.base_builder import BasePayloadBuilder, BuildResult
from soc_stack.states.base_state import StateResult
from soc_stack.wazuh.wazuh_api.wazuh_client import WazuhClient

class WazuhPayloadBuilder(BasePayloadBuilder):
    """
    Transforms canonical asset data into Wazuh Log Events.
    """
    
    NETWORK_MAPPING = {
        "192.168.1.": "Primary LAN",
        "192.168.2.": "DMZ",
        "192.168.200.": "Odense Office",
        "172.20.20.": "Guest WiFi",
        "10.255.255.": "Security Cameras",
    }
    EXTENDED_PREFIXES = ("192.168.4.", "192.168.5.", "192.168.6.", "192.168.7.")

    _agent_cache: Optional[Dict[str, Dict]] = None

    def __init__(self):
        self.debug = os.getenv('WAZUH_BUILDER_DEBUG', '0') == '1'
        self._load_agents()


    def _load_agents(self):
        """Load Wazuh agents for correlation."""
        if WazuhPayloadBuilder._agent_cache is not None:
            return
        
        print("  [Wazuh Builder] Loading agents for correlation...")
        try:
            client = WazuhClient()
            # Optimize: Only re-authenticate if init failed (token is None)
            if not client.token and not client._authenticate():
                raise RuntimeError("Authentication failed.")
            print("  [Wazuh Builder] Authenticated successfully.")
            
            # Fetch all agents (adjust limit if you have >10k agents)
            response = client.get("/agents", params={"limit": 10000, "select": "id,name,ip,status,os.name,lastKeepAlive"})
            agents = response.get('data', {}).get('affected_items', [])
        
            # Index by IP for fast lookup
            WazuhPayloadBuilder._agent_cache = {}
            for agent in agents:
                ip = agent.get('ip')
                if ip:
                    WazuhPayloadBuilder._agent_cache[ip] = agent
            
            print(f"  [Wazuh Builder] Cached {len(WazuhPayloadBuilder._agent_cache)} agents")
            
            if self.debug:
                print("  [Wazuh Builder] Agent Cache:")
                for agent in WazuhPayloadBuilder._agent_cache.items():
                    print(f"    {agent}")
                
        except Exception as e:
            print(f"  [Wazuh Builder] ⚠️ Could not load agents (API might be down): {e}")
            WazuhPayloadBuilder._agent_cache = {}


    def build(self, asset_data: Dict, state_result: StateResult) -> BuildResult:
        """Build Wazuh log event from canonical data."""
        
        ports = asset_data.get("nmap_open_ports", [])
        if isinstance(ports, str):
            ports = [p.strip() for p in ports.split('\n') if p.strip()]

        # Ensure MAC addresses are a list for better querying in Wazuh
        macs = asset_data.get("mac_addresses", [])
        if isinstance(macs, str):
            macs = [m.strip() for m in macs.split('\n') if m.strip()]

        # Agent Correlation
        ip = asset_data.get("last_seen_ip")
        agent_info = self._agent_cache.get(ip) if ip and self._agent_cache else None

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hydra_event_type": "hydra_asset_scan",
            "event_action": state_result.action,
            "wazuh_id": state_result.asset_id,
            "source": asset_data.get("_source"),
            "asset": {
                "name": asset_data.get("name"),
                "ip": ip,
                "mac": macs,
                "serial": asset_data.get("serial"),
                "asset_tag": asset_data.get("asset_tag"),
            },
            "classification": {
                "manufacturer": asset_data.get("manufacturer"),
                "model": asset_data.get("model"),
                "category": asset_data.get("category"),
                "device_type": asset_data.get("device_type"),
            },
            "security": {
                "open_ports": ports,
                "os_guess": asset_data.get("nmap_os_guess"),
                "compliance": asset_data.get("intune_compliance"),
                "vlan": self._get_vlan(asset_data.get("last_seen_ip"))
            },
            # Enriched Agent Data
            "related_agent": {
                "id": agent_info.get('id') if agent_info else None,
                "status": agent_info.get('status') if agent_info else "not_found",
                "name": agent_info.get('name') if agent_info else None
            } if agent_info else {
                "id": None,
                "status": "not_found",
                "name": None
            }
        }
        
        return BuildResult(
            payload=event,
            asset_id=state_result.asset_id,
            action=state_result.action,
            metadata={"source": asset_data.get("_source")}
        )


    def _get_vlan(self, ip: str) -> Optional[str]:
        if not ip:
            return None
        for prefix, vlan in self.NETWORK_MAPPING.items():
            if ip.startswith(prefix):
                return vlan
        if ip.startswith(self.EXTENDED_PREFIXES):
            return "Extended"
        return "Unknown"