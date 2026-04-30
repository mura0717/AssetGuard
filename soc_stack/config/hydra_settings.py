"""
Centralized Configuration for Hydra
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

HYDRA_SETTINGS_DEBUG = os.getenv('HYDRA_SETTINGS_DEBUG', '0') == '1'
USE_PROXY = os.getenv('USE_PROXY', 'False').lower() in ('true', '1', 'yes')
PROXY_HOST = os.getenv('PROXY_HOST')

# Direct backend IPs
HOST_IPS = {
    'snipe': os.getenv('SNIPE_HOST_IP'),
    'zabbix': os.getenv('ZABBIX_HOST_IP'),
    'wazuh': os.getenv('WAZUH_HOST_IP'),
}

# Helper to safely get int ports
def get_port(key):
    val = os.getenv(key)
    return int(val) if val and val.strip().isdigit() else None

# Port mappings
PROXY_PORTS = {
    'snipe': get_port('SNIPE_PROXY_PORT'),
    'zabbix': get_port('ZABBIX_PROXY_PORT'),
    'wazuh_api': get_port('WAZUH_PROXY_API_PORT'),
    'wazuh_indexer': get_port('WAZUH_PROXY_INDEXER_PORT'),
}

DIRECT_PORTS = {
    'snipe': get_port('SNIPE_DIRECT_PORT'),
    'zabbix': get_port('ZABBIX_DIRECT_PORT'),
    'wazuh_api': get_port('WAZUH_DIRECT_API_PORT'),
    'wazuh_indexer': get_port('WAZUH_DIRECT_INDEXER_PORT'),
}

@dataclass
class SnipeConfig:
    snipe_api_key: str = os.getenv("SNIPE_API_TOKEN")
    verify_ssl: bool = os.getenv("VERIFY_SSL", "False").lower() in ('true', '1', 'yes')
    snipe_url: str = field(init=False)
    
    def __post_init__(self):
        if not self.snipe_api_key:
            raise RuntimeError("CRITICAL: SNIPE_API_TOKEN is missing from .env")
        if USE_PROXY:
            host = PROXY_HOST
            port = PROXY_PORTS["snipe"]
        else:
            host = HOST_IPS["snipe"]
            port = DIRECT_PORTS["snipe"]
        
        if not host or not port:
            raise RuntimeError("Snipe host/port not configured (direct/proxy).")
            
        scheme = "https" if self.verify_ssl or port == 443 else "http"
        self.snipe_url = f"{scheme}://{host}:{port}"

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.snipe_api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

@dataclass
class ZabbixConfig:
    zabbix_username: str = os.getenv('ZABBIX_USER')
    zabbix_pass: str = os.getenv('ZABBIX_PASS')
    zabbix_url: str = field(init=False)
    
    def __post_init__(self):
        if USE_PROXY:
            host = PROXY_HOST
            port = PROXY_PORTS["zabbix"]
        else:
            host = HOST_IPS["zabbix"]
            port = DIRECT_PORTS["zabbix"]
            
        self.zabbix_url = f"http://{host}:{port}/zabbix/api_jsonrpc.php"

@dataclass
class WazuhConfig:
    wazuh_api_user: str = os.getenv('WAZUH_API_USER')
    wazuh_api_pass: str = os.getenv('WAZUH_API_PASS')
    event_log: Path = Path(os.getenv('WAZUH_EVENT_LOG_PATH', BASE_DIR / 'logs' / 'wazuh_logs' / 'wazuh_events.jsonl'))
    state_file: Path = Path(os.getenv('WAZUH_STATE_FILE_PATH', BASE_DIR / 'logs' / 'wazuh_logs' / 'wazuh_state.json'))
    wazuh_api_url: str = field(init=False)
    wazuh_indexer_url: str = field(init=False)
    heartbeat_hours: int = 24
    
    def __post_init__(self):
        if USE_PROXY:
            host = PROXY_HOST
            api_port = PROXY_PORTS['wazuh_api']
            idx_port = PROXY_PORTS['wazuh_indexer']
            
            self.wazuh_api_url = f"http://{host}:{api_port}"
            self.wazuh_indexer_url = f"http://{host}:{idx_port}"
        else:
            host = HOST_IPS['wazuh']
            api_port = DIRECT_PORTS['wazuh_api']
            idx_port = DIRECT_PORTS['wazuh_indexer']

            self.wazuh_api_url = f"https://{host}:{api_port}"
            self.wazuh_indexer_url = f"https://{host}:{idx_port}"

# 4. Singleton Instances
SNIPE = SnipeConfig()
ZABBIX = ZabbixConfig()
WAZUH = WazuhConfig()

def print_configuration():
    """Print configuration details if debug is enabled."""
    if HYDRA_SETTINGS_DEBUG:
        mode = "PROXY" if USE_PROXY else "DIRECT"
        masked_snipe_key = SNIPE.snipe_api_key[:5] + "..." if SNIPE.snipe_api_key else "None"
        masked_zabbix_pass = ZABBIX.zabbix_pass[:5] + "..." if ZABBIX.zabbix_pass else "None"
        masked_wazuh_pass = WAZUH.wazuh_api_pass[:5] + "..." if WAZUH.wazuh_api_pass else "None"
        print(f"--- CONFIG LOADED ({mode} MODE) ---")
        print(f"SNIPE_URL: {SNIPE.snipe_url} " + f"SNIPE_API_TOKEN: {masked_snipe_key} " + f"VERIFY_SSL: {SNIPE.verify_ssl}")
        print(f"ZABBIX_URL: {ZABBIX.zabbix_url} " + f"ZABBIX_USER: {ZABBIX.zabbix_username} " + f"ZABBIX_PASS: {masked_zabbix_pass}")
        print(f"WAZUH_API_URL: {WAZUH.wazuh_api_url} " + f"WAZUH_INDEXER_URL: {WAZUH.wazuh_indexer_url} " + f"WAZUH_API_USER: {WAZUH.wazuh_api_user} " + f"WAZUH_API_PASS: {masked_wazuh_pass}")