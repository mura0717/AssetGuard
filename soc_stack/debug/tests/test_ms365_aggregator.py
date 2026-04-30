#!/usr/bin/env python3
"""
Test MS365 Aggregator using data from existing debug logs.
"""

import json
import os
import sys
from pathlib import Path


# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.scanners.ms365_aggregator import Microsoft365Aggregator
from soc_stack.scanners.intune_scanner import IntuneScanner
from soc_stack.scanners.teams_scanner import TeamsScanner
from soc_stack.scanners.entra_scanner import EntraScanner
from soc_stack.debug.tools.asset_debug_logger import debug_logger

def get_latest_dump_from_log():
    """
    Parses the ms365_raw_data.log to find the latest raw_dump entry.
    """
    log_path = debug_logger.log_files['ms365']['raw']
    path = Path(log_path)
    
    if not path.exists():
        print(f"  [!] Log file not found: {path}")
        print("      Run 'python3 soc_stack/scanners/ms365_aggregator.py' with MS365_DEBUG=1 first.")
        return None

    print(f"  [+] Reading log at: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # The logger appends entries. We want the last "raw_dump".
        marker = "--- RAW DATA | Host: raw_dump ---"
        parts = content.split(marker)
        
        if len(parts) < 2:
            print("  [!] No raw_dump found in log file.")
            return None
            
        # Take the last part
        last_entry = parts[-1]
        
        # Strip the footer separator if present
        separator = "-" * 50
        if separator in last_entry:
            last_entry = last_entry.split(separator)[0]
            
        data = json.loads(last_entry.strip())
        return data
        
    except Exception as e:
        print(f"  [!] Error parsing log: {e}")
        return None

def test_aggregator_logic():
    print("=" * 60)
    print("TESTING MS365 AGGREGATOR (UNION-FIND LOGIC)")
    print("=" * 60)

    # 1. Load Data
    print("\n1. Loading Data from Debug Logs...")
    dump_data = get_latest_dump_from_log()
    
    if not dump_data:
        return

    raw_intune = dump_data.get('intune', [])
    raw_teams = dump_data.get('teams', [])
    raw_entra = dump_data.get('entra', [])
    
    print(f"  > Intune Assets (Raw): {len(raw_intune)}")
    print(f"  > Teams Assets (Raw):  {len(raw_teams)}")
    print(f"  > Entra Assets (Raw):  {len(raw_entra)}")

    # 2. Transform Data
    print("\n2. Transforming Data...")
    intune_scanner = IntuneScanner()
    teams_scanner = TeamsScanner()
    entra_scanner = EntraScanner()
    
    trans_intune = [intune_scanner.normalize_asset(a) for a in raw_intune]
    trans_teams = [teams_scanner.normalize_asset(a) for a in raw_teams]
    trans_entra = [entra_scanner.normalize_asset(a) for a in raw_entra]

    # 3. Run Aggregator
    print("\n3. Running Aggregator Merge Logic...")
    aggregator = Microsoft365Aggregator()
    
    # Display Filter Configuration
    print(f"   [Config] Filter Stale Days: {aggregator.FILTER_STALE_DAYS}")
    print(f"   [Config] Drop Disabled:     {aggregator.DROP_DISABLED_ACCOUNTS}")
    print(f"   [Config] Drop No OS/HW:     {aggregator.DROP_NO_OS_NO_HARDWARE}")

    # Enable debug output for the aggregator
    debug_logger.ms365_debug = True
    
    merged_assets = aggregator.merge_data(
        intune_data=trans_intune,
        teams_data=trans_teams,
        entra_data=trans_entra
    )
    
    # 4. Analyze Results
    print("\n4. Merge Results Analysis")
    print("-" * 30)
    print(f"Total Merged Assets: {len(merged_assets)}")
    
    sources = {}
    for asset in merged_assets:
        src = asset.get('_source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
        
    for src, count in sorted(sources.items()):
        print(f"  - {src}: {count}")

    # 5. Verify Union-Find Behavior
    print("\n5. Verifying Transitive Merges")
    
    # Check for assets that combined multiple sources
    multi_source = [a for a in merged_assets if '+' in a.get('_source', '')]
    print(f"  > Multi-source Assets: {len(multi_source)}")
    
    if multi_source:
        print("    Sample Merges:")
        for i, asset in enumerate(multi_source[:5]):
            print(f"    {i+1}. {asset.get('name')} [{asset.get('_source')}]")
            print(f"       IDs: Azure={asset.get('azure_ad_id')} | Serial={asset.get('serial')}")
    
    print("\nTest Complete.")

if __name__ == "__main__":
    test_aggregator_logic()
