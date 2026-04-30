#!/usr/bin/env python3
"""
Nmap Scanner.
"""
import os
import sys
import nmap
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional

from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.config.network_config import NMAP_SCAN_RANGES
from soc_stack.config.nmap_profiles import NMAP_SCAN_PROFILES
from soc_stack.utils.mac_utils import normalize_mac_semicolon
from soc_stack.utils.sudo_utils import elevate_to_root

DNS_SERVERS = os.getenv('NMAP_DNS_SERVERS', '').strip()
DNS_ARGS = f"--dns-servers {DNS_SERVERS} -R" if DNS_SERVERS else "-R"

class NmapScanner:
    """Nmap Scanner."""
    
    def __init__(self, network_ranges: Optional[List[str]] = None):
        self.network_ranges = network_ranges if network_ranges else NMAP_SCAN_RANGES
        self.nm = nmap.PortScanner()
    
    def run_scan(self, profile: str = 'discovery', targets: Optional[List[str]] = None) -> List[Dict]:
        """Run scan."""
        
        if profile not in NMAP_SCAN_PROFILES:
            print(f"Unknown profile: {profile}")
            return []
        
        scan_config = NMAP_SCAN_PROFILES[profile]
        args = scan_config['args']
        if scan_config.get('use_dns'):
            args = f"{args} {DNS_ARGS}"
        scan_targets = ' '.join(targets) if targets else ' '.join(self.network_ranges)
        
        print(f"Running {profile} scan: {scan_config['description']}")
        print(f"Targets: {scan_targets}")
        
        try:
            self.nm.scan(hosts=scan_targets, arguments=args)
            
            assets = []
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    asset = self._parse_host(host, profile, scan_config)
                    assets.append(asset)
            
            return assets
            
        except nmap.PortScannerError as e:
            print(f"Nmap error: {e}")
            return []
        except Exception as e:
            print(f"Scan failed: {e}")
            return []
    
    def _parse_host(self, host: str, profile: str, scan_config: Dict) -> Dict:
        """Parse results."""
        nmap_host = self.nm[host]
        
        raw_host_data = {
            'host': host,
            'hostname': nmap_host.hostname(),
            'state': nmap_host.state(),
            'addresses': nmap_host.get('addresses', {}),
            'vendor': nmap_host.get('vendor', {}),
            'osmatch': nmap_host.get('osmatch', []),
            'protocols': {}
        }
        for proto in nmap_host.all_protocols():
            raw_host_data['protocols'][proto] = nmap_host[proto]
        
        debug_logger.log_raw_host_data('nmap', host, raw_host_data)
        
        asset = {
            'last_seen_ip': host,
            'nmap_last_scan': datetime.now(timezone.utc).isoformat(),
            'nmap_scan_profile': profile,
            'name': nmap_host.hostname() or f"Device-{host}",
            'dns_hostname': nmap_host.hostname(),
            '_source': 'nmap',
            'first_seen_date': datetime.now(timezone.utc).isoformat(),
        }
        
        mac_addresses = []
        if 'mac' in nmap_host.get('addresses', {}):
            raw_mac = nmap_host['addresses']['mac']
            normalized_mac = normalize_mac_semicolon(raw_mac)
            if normalized_mac:
                mac_addresses.append(normalized_mac)
                asset['mac_addresses'] = normalized_mac
                if 'vendor' in nmap_host and nmap_host['vendor']:
                    asset['manufacturer'] = list(nmap_host['vendor'].values())[0]
        
        if scan_config.get('collects_ports') and 'osmatch' in nmap_host and nmap_host['osmatch']:
            os_match = nmap_host['osmatch'][0]
            asset['nmap_os_guess'] = os_match.get('name', '')
            asset['os_accuracy'] = os_match.get('accuracy')
            asset['os_platform'] = os_match.get('name', '')
        
        if scan_config.get('collects_ports'):
            open_ports_list = []
            service_names = []
            
            for proto in nmap_host.all_protocols():
                for port, port_info in nmap_host[proto].items():
                    if port_info.get('state') == 'open':
                        service_name = port_info.get('name', 'unknown')
                        service_names.append(service_name)
                        
                        product = port_info.get('product', '')
                        version = port_info.get('version', '')

                        port_str = f"{port}/{proto}/{service_name} ({product} {version})".strip()
                        open_ports_list.append(port_str)
            
            if open_ports_list:
                asset['nmap_open_ports'] = '\n'.join(sorted(open_ports_list))
                asset['open_ports_hash'] = hashlib.md5(asset['nmap_open_ports'].encode()).hexdigest()
                asset['nmap_discovered_services'] = service_names
                
        return {k: v for k, v in asset.items() if v is not None and v != '' and v != []}
    
    def collect_assets(self, profile: str = 'discovery') -> List[Dict]:
        """Collect assets."""
        print(f"Starting Nmap {profile} scan...")
        
        if debug_logger.nmap_debug:
            debug_logger.clear_logs('nmap')

        assets = self.run_scan(profile)
        
        if not assets:
            print("No hosts found.")
        else:
            print(f"Found {len(assets)} hosts")
            if debug_logger.nmap_debug:
                for asset in assets:
                    debug_logger.log_parsed_asset_data('nmap', asset)
        
        return assets

def main():
    from soc_stack.debug.categorize_from_logs.nmap_categorize_from_logs import nmap_debug_categorization
    
    if nmap_debug_categorization.debug: 
        nmap_debug_categorization.write_nmap_assets_to_logfile()
        return

    command = sys.argv[1] if len(sys.argv) > 1 else 'discovery'
    
    if command == 'list':
        print("\nAvailable scan profiles:")
        for name, config in NMAP_SCAN_PROFILES.items():
            print(f"  {name:12} - {config['description']}")
        return
    
    if command not in NMAP_SCAN_PROFILES:
        print(f"Unknown command: {command}")
        print("Usage: nmap_scanner.py [profile_name|list]")
        return

    elevate_to_root()
    
    scanner = NmapScanner()
    assets = scanner.collect_assets(command)
    
    print(f"\nScan complete. Found {len(assets)} assets.")
    if os.getenv('NMAP_DEBUG', '0') == '1':
        import json
        print(json.dumps(assets, indent=2, default=str))

if __name__ == "__main__":
    main()