"""
Zabbix State Manager
Handles host existence checks against Zabbix API.
"""

import os
from typing import Dict, Optional

from soc_stack.states.base_state import BaseStateManager, StateResult
from soc_stack.zabbix.zabbix_api.zabbix_client import ZabbixClient
from soc_stack.config.network_config import STATIC_IP_MAP
from soc_stack.utils.mac_utils import normalize_mac_no_semicolon, get_primary_mac_address

class ZabbixStateManager(BaseStateManager):
    
    IDENTITY_PRIORITY = [
        ('serial', 'serial'),
        ('intune_device_id', 'intune'),
        ('azure_ad_id', 'azure'),
        ('mac_addresses', 'mac'),
    ]
    
    def __init__(self):
        self._cache_loaded = False
        self.debug = os.getenv('ZABBIX_STATE_DEBUG', '0') == '1'
        self.api = None
        
        self._index_by_asset_key: Dict[str, Dict] = {}
        self._index_by_mac: Dict[str, Dict] = {}
        self._index_by_serial: Dict[str, Dict] = {}
        self._index_by_name: Dict[str, Dict] = {}
    
    def _load_all_hosts(self):
        if self._cache_loaded:
            return

        self.api = ZabbixClient()
        if not getattr(self.api, 'auth', None):
            print("  [Zabbix State] ⚠️ Authentication failed. Skipping Zabbix state load.")
            self._cache_loaded = True
            return
        
        print("  [Zabbix State] Loading existing hosts...")
        try:
            hosts = self.api.call("host.get", {
                "output": ["hostid", "host", "name"],
                "selectInventory": ["asset_tag", "serialno_a", "macaddress_a", "macaddress_b"],
                "selectInterfaces": ["ip"]
            }) or []
            
            print(f"  [Zabbix State] Loaded {len(hosts)} existing hosts")
            
            for host in hosts:
                inv = host.get('inventory') or {}
                
                # Index by asset_key
                key = inv.get('asset_tag', '')
                if key and key.startswith(('serial:', 'intune:', 'azure:', 'mac:')):
                    self._index_by_asset_key[key] = host
                
                # Index by serial
                serial = inv.get('serialno_a')
                if serial:
                    self._index_by_serial[serial.upper()] = host
                
                # Index by MAC
                for f in ['macaddress_a', 'macaddress_b']:
                    mac = inv.get(f)
                    if mac:
                        self._index_by_mac[normalize_mac_no_semicolon(mac)] = host
                
                # Index by name
                name = host.get('host', '').lower()
                if name:
                    self._index_by_name[name] = host
            
            if self.debug:
                print(f"    Indexed: {len(self._index_by_asset_key)} keys, "
                      f"{len(self._index_by_serial)} serials, "
                      f"{len(self._index_by_mac)} MACs")
                
            self._cache_loaded = True
            
        except Exception as e:
            print(f"  [Zabbix State] Load failed: {e}")
            self._cache_loaded = True
        
    def generate_id(self, asset_data: Dict) -> Optional[str]:
        for field, prefix in self.IDENTITY_PRIORITY:
            value = asset_data.get(field)
            if value:
                if field == 'mac_addresses':
                    # Use robust helper then strip colons
                    mac = get_primary_mac_address(value)
                    value = mac.replace(':', '') if mac else None
                elif field == 'serial':
                    value = value.upper().strip()
                else:
                    value = str(value).strip()
                
                if value:
                    return f"{prefix}:{value}"
        
        name = asset_data.get('name', '')
        if name and not name.lower().startswith('device-'):
            return f"name:{name.lower()}"
            
        return None
    
    def check(self, asset_data: Dict) -> StateResult:
        self._load_all_hosts()
        asset_key = self.generate_id(asset_data)
        
        if not asset_key:
            return StateResult(
                action='skip',
                asset_id='',
                existing=None,
                reason='No suitable identifier'
            )
            
        if not self._is_monitorable(asset_data):
            return StateResult(
                action='skip',
                asset_id=asset_key,
                existing=None,
                reason='Not monitorable (endpoint or no IP)'
            )
            
        existing = self._find_existing(asset_key, asset_data)
        
        if existing:
            return StateResult(
                action='update',
                asset_id=asset_key,
                existing=existing,
                reason=f"Found host {existing['hostid']}"
            )
            
        return StateResult(
            action='create',
            asset_id=asset_key,
            existing=None,
            reason='New infrastructure host'
        )
    
    def _find_existing(self, asset_key: str, asset_data: Dict) -> Optional[Dict]:
        # 1. By asset_key (our stored key)
        if asset_key in self._index_by_asset_key:
            if self.debug:
                print(f"    ✓ Match by asset_key: {asset_key}")
            return self._index_by_asset_key[asset_key]
        
        # 2. By serial
        serial = asset_data.get('serial')
        if serial and serial.upper() in self._index_by_serial:
            if self.debug:
                print(f"    ✓ Match by serial: {serial}")
            return self._index_by_serial[serial.upper()]
        
        # 3. By MAC
        mac_val = asset_data.get("mac_addresses")
        if mac_val:
            mac = get_primary_mac_address(mac_val)
            norm = mac.replace(":", "") if mac else ""
            if norm and norm in self._index_by_mac:
                if self.debug:
                    print(f"    ✓ Match by MAC: {norm}")
                return self._index_by_mac[norm]
        
        # 4. By hostname
        name = asset_data.get('name', '').lower()
        if name and name in self._index_by_name:
            if self.debug:
                print(f"    ✓ Match by name: {name}")
            return self._index_by_name[name]
        
        return None
    
    def _is_monitorable(self, asset_data: Dict) -> bool:
        """Determine if asset should be monitored in Zabbix."""
        # Must have an IP address
        if not asset_data.get('last_seen_ip'):
            return False
        
        # Skip certain device types
        device_type = asset_data.get('device_type', '').lower()
        if device_type in ('mobile phone', 'tablet', 'laptop', 'other assets', 'cloud resources', 'monitors', 'desktop'):
            return False
        if device_type in ('server', 'network device', 'access point', 'switch', 'router', 'firewall'):
            return True
        
        # Include Static IPs (Known Infrastructure)
        if asset_data.get('last_seen_ip') in STATIC_IP_MAP:
            return True
        
        return False

    def record(self, asset_id: str, asset_data: Dict, action: str) -> None:
        pass
