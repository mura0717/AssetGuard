#!/usr/bin/env python3
"""
Test Teams data fetch.
"""
import os
import sys
from pathlib import Path

# Set debug flag BEFORE importing modules that initialize the logger
os.environ['INTUNE_DEBUG'] = '1'

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.scanners.intune_scanner import IntuneScanner
from soc_stack.debug.tools.asset_debug_logger import debug_logger

def test_intune_fetch():
    print("=== Testing Intune Raw Data Fetch ===")
    print("Initializing IntuneScanner...")
    scanner = IntuneScanner()
    
    print("Fetching assets...")
    raw, transformed = scanner.get_transformed_assets()
    
    print(f"\n✓ Fetched {len(raw)} raw assets.")
    print(f"✓ Transformed {len(transformed)} assets.")
    
    raw_log = debug_logger.log_files['teams']['raw']
    parsed_log = debug_logger.log_files['teams']['parsed']
    
    print(f"\nLogs generated:")
    print(f"  Raw Data:    {raw_log}")
    print(f"  Parsed Data: {parsed_log}")
    
    if raw:
        print("\nSample Raw Asset Keys:")
        print(list(raw[0].keys()))
        
    if transformed:
        print("\nSample Transformed Asset Keys:")
        print(list(transformed[0].keys()))

if __name__ == "__main__":
    test_intune_fetch()