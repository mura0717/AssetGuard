#!/usr/bin/env python3

"""
Test New Asset Logger.
"""

import sys
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.loggers.new_asset_logger import NewAssetsLogger

def test_new_asset_logging():
    print("=== Testing New Asset Logger ===")
    
    logger = NewAssetsLogger()
    print(f"Log File Path: {logger.filepath}")
    
    # Prepare dummy data matching NewAssetsLogger expectations
    asset_data = {
        "name": "TEST-ASSET-001",
        "last_seen_ip": "192.168.1.100",
        "mac_addresses": ["AA:BB:CC:DD:EE:FF"],
        "manufacturer": "TestCorp",
        "model": "Model-X",
        "_source": "debug_test"
    }
    category = "Workstation"
    # Note: 'action' is not passed because NewAssetsLogger implies 'create'
    
    print(f"Logging new asset: {asset_data['name']}...")
    logger.log_new_asset(asset_data, category)
    
    if not logger.filepath.exists():
        print(f"✗ Error: Log file not found at {logger.filepath}")
        return False
        
    print(f"✓ Log file exists at {logger.filepath}")
    
    try:
        with open(logger.filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if not rows:
                print("✗ Error: CSV file is empty")
                return False
                
            last_row = rows[-1]
            
            # Expected columns: timestamp, name, ip, mac, manufacturer, model, source, category
            logged_name = last_row[1]
            logged_ip = last_row[2]
            logged_category = last_row[7]
            
            # Verify the data matches what we sent
            if logged_name == asset_data['name'] and logged_ip == asset_data['last_seen_ip'] and logged_category == category:
                print(f"✓ Verification successful!")
                print(f"  Last Entry: {last_row}")
                return True
            else:
                print(f"✗ Error: Content mismatch.")
                print(f"  Expected: {asset_data['name']} / {asset_data['last_seen_ip']} / {category}")
                print(f"  Got:      {logged_name} / {logged_ip} / {logged_category}")
                return False
                
    except Exception as e:
        print(f"✗ Exception reading log file: {e}")
        return False

if __name__ == "__main__":
    test_new_asset_logging()
