#!/usr/bin/env python3
"""
Test Entra ID data fetch.
"""
import os
import sys
from pathlib import Path

# Set debug flag BEFORE importing modules that initialize the logger
os.environ['ENTRA_DEBUG'] = '1'

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.scanners.entra_scanner import EntraScanner
from soc_stack.debug.tools.asset_debug_logger import debug_logger

def test_entra_fetch():
    print("=== Testing Entra ID Raw Data Fetch ===")
    print("Initializing EntraScanner...")
    scanner = EntraScanner()
    
    print("Fetching assets...")
    raw, transformed = scanner.get_transformed_assets()
    
    print(f"\n✓ Fetched {len(raw)} raw assets.")
    print(f"✓ Transformed {len(transformed)} assets.")
    
    raw_log = debug_logger.log_files['entra']['raw']
    parsed_log = debug_logger.log_files['entra']['parsed']
    
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
    test_entra_fetch()