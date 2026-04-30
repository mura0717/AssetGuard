#!/usr/bin/env python3
"""
Master Reset Script for Snipe-IT Configuration

Now uses efficient DB-based deletion instead of rate-limited API calls.
"""

import os
import sys
import time
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from soc_stack.snipe_it.snipe_initializers.snipe_reset_utility import SnipeResetManager

def print_header(message: str):
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)
    

def main():
    print_header("SNIPE-IT FULL RESET & SETUP")
    
    start_time = time.time()
    
    print_header("STEP 1: Bulk Delete All Entities (DB Method)")
    
    reset_result = SnipeResetManager.full_reset(skip_confirmation=True)
    
    if reset_result.get("cancelled"):
        print("Reset cancelled.")
        sys.exit(0)
    
    print_header("STEP 2: Running Setup")
    
    from soc_stack.snipe_it.snipe_initializers.snipe_setup import SnipeITSetup
    
    setup = SnipeITSetup()
    setup.setup_all()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"✅ FULL RESET COMPLETED in {elapsed:.1f} seconds")
    print("=" * 60)


if __name__ == "__main__":
    main()