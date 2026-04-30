#!/usr/bin/env python3
"""
Debug Intune categorization.
"""

import os
import json
from typing import List, Dict

from soc_stack.asset_engine.asset_categorizer import AssetCategorizer
from soc_stack.debug.tools.asset_debug_logger import debug_logger

class IntuneDebugCategorization:
    """Debug Intune categorization.""" 
    def __init__(self):
        self.debug = os.getenv('INTUNE_CATEGORIZATION_DEBUG', '0') == '1'
        self.raw_log_path = debug_logger.log_files['intune']['raw']
        self.categorization_log_path = debug_logger.log_files['intune']['categorization']
    
    def get_raw_intune_assets_from_log(self) -> List[Dict]:
        """Fetch Intune assets from log."""
        if not os.path.exists(self.raw_log_path):
            print(f"Error: Log file not found at {self.raw_log_path}")
            print("Please run an Intune sync with INTUNE_DEBUG=1 first.")
            return []
            
        assets = []
        decoder = json.JSONDecoder()
        try:
            with open(self.raw_log_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            chunks = content.split('--- RAW DATA | Host:')
            
            for chunk in chunks[1:]:
                try:
                    json_start = chunk.find('{')
                    if json_start == -1: continue
                    asset, _ = decoder.raw_decode(chunk, json_start)
                    assets.append(asset)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to decode a JSON chunk. Error: {e}")
                    continue
        except Exception as e:
            print(f"Error reading or parsing log file: {e}")
        
        return assets
    
    def write_managed_assets_to_logfile(self):
        from scanners.intune_scanner import IntuneScanner
        sync = IntuneScanner()
        raw_assets = self.get_raw_intune_assets_from_log()
        print(f"Loaded {len(raw_assets)} raw assets from log.")

        output_path = self.categorization_log_path
        with open(output_path, 'w', encoding='utf-8') as f:
            for asset in raw_assets:
                transformed = sync.normalize_asset(asset)
                categorization = AssetCategorizer.categorize(transformed)
                out = {
                    "name": transformed.get("name"),
                    'serial': transformed.get('serial'),
                    "manufacturer": transformed.get("manufacturer"),
                    "model": transformed.get("model"),
                    "os_platform": transformed.get("os_platform"),
                    "device_type": categorization.get("device_type"),
                    "category": categorization.get("category"),
                    "nmap services": categorization.get("nmap_discovered_services"),
                    "cloud provider": categorization.get("cloud_provider"),
                }
                f.write(json.dumps(out, indent=2) + "\n")
        print(f"Wrote categorized results to {output_path}")

intune_debug_categorization = IntuneDebugCategorization()