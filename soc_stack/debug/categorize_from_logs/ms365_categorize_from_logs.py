#!/usr/bin/env python3
"""
Debug MS365 categorization.
"""

import os
import json
from typing import List, Dict

from soc_stack.asset_engine.asset_categorizer import AssetCategorizer
from soc_stack.debug.tools.asset_debug_logger import debug_logger

class Microsoft365DebugCategorization:
    """Debug MS365 categorization."""
    def __init__(self):
        self.debug = os.getenv('MS365_CATEGORIZATION_DEBUG', '0') == '1'
        self.raw_log_path = debug_logger.log_files['ms365']['parsed']
        self.categorization_log_path = debug_logger.log_files['ms365']['categorization']

    def get_raw_ms365_assets_from_log(self) -> List[Dict]:
        """Fetch MS365 assets from log."""
        if not os.path.exists(self.raw_log_path):
            print(f"Error: Log file not found at {self.raw_log_path}")
            print("Please run a Microsoft 365 sync with MS365_DEBUG=1 first.")
            return []

        try:
            with open(self.raw_log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            marker = "--- PARSED ASSET DATA ---"
            marker_pos = content.find(marker)
            
            if marker_pos == -1:
                print("Error: Could not find PARSED ASSET DATA marker in log.")
                return []

            array_start = content.find('[', marker_pos)
            array_end = content.rfind(']')

            if array_start == -1 or array_end == -1 or array_end <= array_start:
                print("Error: Could not find JSON array brackets after marker.")
                return []

            json_str = content[array_start:array_end + 1]

            assets = json.loads(json_str)

            print(f"Successfully loaded {len(assets)} merged assets from MS365 parsed log.")
            return assets

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Extracted JSON string starts with: {json_str[:200]}...")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def write_m365_assets_to_logfile(self):
        """Categorize MS365 assets."""
        merged_assets = self.get_raw_ms365_assets_from_log()
        print(f"Loaded {len(merged_assets)} merged assets from Microsoft 365 log.")

        output_path = self.categorization_log_path
        with open(output_path, 'w', encoding='utf-8') as f:
            for asset in merged_assets:
                categorization = AssetCategorizer.categorize(asset)
                out = {
                    "name": asset.get("name"),
                    "serial": asset.get("serial"),
                    "manufacturer": asset.get("manufacturer"),
                    "model": asset.get("model"),
                    "os_platform": asset.get("os_platform"),
                    "last_update_source": asset.get("last_update_source"),
                    "device_type": categorization.get("device_type"),
                    "category": categorization.get("category"),
                }
                f.write(json.dumps(out, indent=2) + "\n")
        print(f"Wrote categorized results to {output_path}")

ms365_debug_categorization = Microsoft365DebugCategorization()

if __name__ == "__main__":
    if ms365_debug_categorization.debug:
        from debug.tools.asset_debug_logger import debug_logger
        ms365_debug_categorization.write_m365_assets_to_logfile()
    else:
        print("To debug categorization, set MS365_CATEGORIZATION_DEBUG=1 and run this script.")
