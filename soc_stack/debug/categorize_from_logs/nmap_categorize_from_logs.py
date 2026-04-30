#!/usr/bin/env python3
"""
Debug Nmap categorization.
"""

import os
import json
from typing import List, Dict
from datetime import datetime

from soc_stack.asset_engine.asset_categorizer import AssetCategorizer
from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.utils.mac_utils import normalize_mac_semicolon

class NmapDebugCategorization:
    """Test categorization logic for Nmap assets."""
    
    def __init__(self):
        self.debug = os.getenv('NMAP_CATEGORIZATION_DEBUG', '0') == '1'
        self.raw_log_path = debug_logger.log_files['nmap']['raw']
        self.categorization_log_path = debug_logger.log_files['nmap']['categorization']


    def get_raw_nmap_assets_from_log(self) -> List[Dict]:
        """Extract Nmap assets from log."""
        if not os.path.exists(self.raw_log_path):
            print(f"ERROR: {self.raw_log_path} not found!")
            print("Run this first: NMAP_DEBUG=1 python scanners/nmap_scanner.py [profile]")
            return []
        
        assets = []
        try:
            with open(self.raw_log_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            chunks = content.split('--- RAW DATA | Host:')
            
            for chunk in chunks[1:]:
                try:
                    json_start = chunk.find('{')
                    # Find the matching closing brace for the main object
                    json_end = chunk.rfind('}')
                    if json_start == -1 or json_end == -1:
                        continue
                    
                    json_text = chunk[json_start : json_end + 1]
                    assets.append(json.loads(json_text))
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to decode a JSON chunk. Error: {e}")
                    continue
        except Exception as e:
            print(f"Error reading {self.raw_log_path}: {e}")
            return []
        
        return assets
    
    def write_nmap_assets_to_logfile(self):
        """Categorize Nmap assets."""
        raw_assets = self.get_raw_nmap_assets_from_log()
        
        if not raw_assets:
            print("No Nmap assets found in log. Ensure NMAP_DEBUG=1 andyou've run:")
            print("  NMAP_DEBUG=1 python scanners/nmap_scanner.py [profile]")
            print("  Example: NMAP_DEBUG=1 python scanners/nmap_scanner.py discovery")
            return
        
        print(f"Loaded {len(raw_assets)} raw Nmap assets from log.")

        output_path = self.categorization_log_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Nmap Categorization Test Results\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total assets: {len(raw_assets)}\n\n")
            
            for i, raw_asset in enumerate(raw_assets, 1):
                parsed_asset = self._reconstruct_parsed_asset(raw_asset)
                
                categorization = AssetCategorizer.categorize(parsed_asset)
                
                output_data = {
                    "index": i,
                    "name": parsed_asset.get("name"),
                    "last_seen_ip": parsed_asset.get("last_seen_ip"),
                    "dns_hostname": parsed_asset.get("dns_hostname"),
                    "mac_address": parsed_asset.get("mac_addresses"),
                    "manufacturer": parsed_asset.get("manufacturer"),
                    "os_platform": parsed_asset.get("os_platform"),
                    "nmap_os_guess": parsed_asset.get("nmap_os_guess"),
                    "nmap_discovered_services": parsed_asset.get("nmap_discovered_services", []),
                    "scan_profile": parsed_asset.get("nmap_scan_profile"),
                    "device_type": categorization.get("device_type"),
                    "category": categorization.get("category"),
                    "cloud_provider": categorization.get("cloud_provider"),
                }
                
                f.write(json.dumps(output_data, indent=2))
                f.write("\n" + "-"*80 + "\n\n")
               
            print(f"Processed {i}/{len(raw_assets)} assets...")
        
        print(f"\n✅ Wrote categorized results to: {output_path}")
        print(f"📊 Summary:")
        self._print_summary(output_path)

    def _reconstruct_parsed_asset(self, raw_asset: Dict) -> Dict: # type: ignore
        """Reconstruct parsed asset from raw log."""
        asset = {
            'name': raw_asset.get('hostname'),
            'last_seen_ip': raw_asset.get('host'),
            'dns_hostname': raw_asset.get('hostname'),
            'mac_addresses': normalize_mac_semicolon(raw_asset.get('addresses', {}).get('mac', '')),
            'manufacturer': list(raw_asset.get('vendor', {}).values())[0] if raw_asset.get('vendor') else None,
            'os_platform': None,
            'nmap_discovered_services': [],
            '_source': 'nmap'
        }

        if raw_asset.get('osmatch'):
            asset['os_platform'] = raw_asset['osmatch'][0].get('name')

        for proto, ports in raw_asset.get('protocols', {}).items():
            for port, info in ports.items():
                if info.get('state') == 'open':
                    asset['nmap_discovered_services'].append(info.get('name', 'unknown'))
        return {k: v for k, v in asset.items() if v}

    def _print_summary(self, output_path: str):
        
        # Generate summary statistics
        category_stats = {}
        device_type_stats = {}
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Count categories
            for line in content.split('\n'):
                if '"category":' in line:
                    category = line.split('"category": "')[1].split('"')[0]
                    category_stats[category] = category_stats.get(category, 0) + 1
                elif '"device_type":' in line:
                    device_type = line.split('"device_type": "')[1].split('"')[0]
                    device_type_stats[device_type] = device_type_stats.get(device_type, 0) + 1
        
        print("\nAssets by Category:")
        for category, count in sorted(category_stats.items(), key=lambda x: -x[1]):
            print(f"  {category:35} : {count}")
        
        print("\nAssets by Device Type:")
        for device_type, count in sorted(device_type_stats.items(), key=lambda x: -x[1]):
            print(f"  {device_type:35} : {count}")
        
nmap_debug_categorization = NmapDebugCategorization()
