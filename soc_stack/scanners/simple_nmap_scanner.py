#!/usr/bin/env python3
"""
Simple Nmap scanner for testing.
"""

import os
import sys
import nmap
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from soc_stack.utils.sudo_utils import elevate_to_root

class SimpleNmapScanner:

    def __init__(self):
        elevate_to_root()
        self.nm = nmap.PortScanner()
        self.log_files = {}
        self.logging_enabled_sources = []

    def log_result(self, data: list, log_file: str = 'simple_nmap_scan_result.log'):
        """Log result."""
        log_dir = os.path.join(BASE_DIR, "debug", "debug_logs", "nmap_logs")
        full_log_path = os.path.join(log_dir, log_file)

        timestamp = datetime.now().isoformat()
        message = (
            f"\n--- SCAN RESULT ---\n"
            f"{json.dumps(data, indent=2)}\n"
            f"{'-'*50}"
        )
        log_entry = f"[{timestamp}] {message}"
 
        try:
            os.makedirs(log_dir, exist_ok=True)
            with open(full_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
            print(f"Scan results logged to {full_log_path}")
        except IOError as e:
            print(f"Warning: Could not write to log file {full_log_path}: {e}")

    def run_scan(self, scan_type: str, targets: str):

        scan_profiles = {
            'discovery': {
                'args': '-sn',  # Ping scan
                'ports': None
            },
            'detailed': {
                'args': '-v -sS -sV -O -A --osscan-guess',
                'ports': '1-1024'
            }
        }

        profile = scan_profiles.get(scan_type)
        if not profile:
            print(f"ERROR: Invalid scan type '{scan_type}'. Available types are: {list(scan_profiles.keys())}")
            return []

        print(f"Starting Nmap '{scan_type}' scan on {targets}...")
        try:
            self.nm.scan(hosts=targets, ports=profile['ports'], arguments=profile['args'])
        except nmap.PortScannerError as e:
            print(f"ERROR: Nmap scan failed: {e}")
            return []

        assets = []
        for host in self.nm.all_hosts():
            if self.nm[host].state() != 'up':
                continue

            vendor_dict = self.nm[host].get('vendor', {})
            manufacturer = list(vendor_dict.values())[0] if vendor_dict else 'Unknown'

            if scan_type == 'discovery':
                asset = {
                    'ip': host,
                    'hostname': self.nm[host].hostname() or 'Unknown',
                    'mac': self.nm[host]['addresses'].get('mac', 'Unknown'),
                    'state': self.nm[host].state(),
                    'manufacturer': manufacturer
                }
                assets.append(asset)

            elif scan_type == 'detailed':
                os_match = self.nm[host].get('osmatch', [])
                asset = {
                    'ip': host,
                    'hostname': self.nm[host].hostname() or 'Unknown',
                    'os': os_match[0]['name'] if os_match else 'Unknown',
                    'mac': self.nm[host]['addresses'].get('mac', 'Unknown'),
                    'state': self.nm[host].state(),
                    'manufacturer': manufacturer,
                    'protocols': {},
                }
                for proto in self.nm[host].all_protocols():
                    asset['protocols'][proto] = []
                    for port, port_info in self.nm[host][proto].items():
                        asset['protocols'][proto].append({
                            'port': port,
                            'state': port_info.get('state', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', ''),
                            'extrainfo': port_info.get('extrainfo', '')
                        })
                assets.append(asset)

        print("\nScan Info:", self.nm.scaninfo())
        return assets

if __name__ == "__main__":

    SCAN_TYPE_TO_RUN = 'detailed'
    IP_RANGE_TO_SCAN = '192.168.200.221'

    scanner = SimpleNmapScanner()
    found_assets = scanner.run_scan(scan_type=SCAN_TYPE_TO_RUN, targets=IP_RANGE_TO_SCAN)

    scanner.log_result(found_assets)
    print(f"\nAssets found: {len(found_assets)}")
    for asset_data in found_assets:
        print(json.dumps(asset_data, indent=2))
    print("\nAll scanned hosts:", scanner.nm.all_hosts())