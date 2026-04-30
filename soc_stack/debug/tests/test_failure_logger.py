#!/usr/bin/env python3

"""
Test FailureLogger.
"""

import sys
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.loggers.failure_logger import FailureLogger

def test_failure_logging():
    print("=== Testing Failure Logger ===")
    
    logger = FailureLogger()
    print(f"Log File Path: {logger.filepath}")
    
    payload = {
        "name": "TEST-FAIL-LOGGER",
        "serial": "FAIL-001",
        "_source": "debug_test",
        "ip": "127.0.0.1"
    }
    action = "create"
    error_msg = "Simulated error: Connection timeout"
    
    print(f"Logging failure for {payload['name']}...")
    logger.log_failure(payload, action, error_msg)
    
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
            
            logged_name = last_row[1]
            logged_error = last_row[5]
            
            if logged_name == payload['name'] and logged_error == error_msg:
                print(f"✓ Verification successful!")
                print(f"  Last Entry: {last_row}")
                return True
            else:
                print(f"✗ Error: Content mismatch.\n  Expected: {payload['name']} / {error_msg}\n  Got:      {logged_name} / {logged_error}")
                return False
                
    except Exception as e:
        print(f"✗ Exception reading log file: {e}")
        return False

if __name__ == "__main__":
    test_failure_logging()
