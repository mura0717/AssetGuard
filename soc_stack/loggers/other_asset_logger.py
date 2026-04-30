"""
Other Assets Logger for Checking
"""

import os
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

OTHER_ASSETS_LOG_PATH = os.getenv('OTHER_ASSETS_LOG_PATH', 'logs/other_asset_logs/other_assets.csv')

class OtherAssetLogger:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[2]
        
        path = Path(OTHER_ASSETS_LOG_PATH)
        if path.is_absolute():
            self.filepath = path
        else:
            self.filepath = self.base_dir / path
            
        self.log_dir = self.filepath.parent
        self._ensure_log_dir()
        self._ensure_header()
        
    def _ensure_log_dir(self):
        if not self.log_dir.exists():
            os.makedirs(self.log_dir, exist_ok=True)
    
    def _ensure_header(self):
        if not self.filepath.exists():
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "name", "ip", "mac", "manufacturer", "model", "source", "category"])
    
    def log_other_asset(self, asset_data: Dict[str, Any], category: str):
        """Log an asset categorized as 'Other' to the CSV."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            name = asset_data.get('name', 'Unknown')
            ip = asset_data.get('last_seen_ip', 'N/A')
            
            # Handle MACs which might be a list or string
            macs = asset_data.get('mac_addresses', 'N/A')
            if isinstance(macs, list):
                macs = "; ".join(str(m) for m in macs)
            
            mfr = asset_data.get('manufacturer', 'Unknown')
            model = asset_data.get('model', 'Unknown')
            source = asset_data.get('_source', 'unknown')

            with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, name, ip, macs, mfr, model, source, category])
                
        except Exception as e:
            print(f"Error writing to other assets log: {e}")

    