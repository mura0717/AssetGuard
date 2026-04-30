#!/usr/bin/env python3

"""
Test WazuhDispatcher file write.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from soc_stack.dispatchers.wazuh_dispatcher import WazuhDispatcher
from soc_stack.builders.base_builder import BuildResult
from soc_stack.config.hydra_settings import WAZUH

def test_wazuh_write():
    print("=== Testing Wazuh Dispatcher File Write ===")
    print(f"Configured Log Path: {WAZUH.event_log}")
    
    dispatcher = WazuhDispatcher()
    
    test_payload = {
        "timestamp": datetime.now().isoformat(),
        "hydra_event_type": "TEST_VERIFICATION",
        "event_action": "create",
        "asset": {
            "name": "TEST-WRITE-VERIFICATION",
            "description": "This is a test event to verify file permissions and path."
        }
    }
    
    result = BuildResult(
        payload=test_payload,
        asset_id="TEST-001",
        action="create",
        metadata={}
    )
    
    print("\nAttempting to write test event...")
    try:
        stats = dispatcher.sync([result])
        print(f"Sync result: {stats}")
        
        if WAZUH.event_log.exists():
            print(f"✓ File exists: {WAZUH.event_log}")
            
            with open(WAZUH.event_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    if "TEST-WRITE-VERIFICATION" in last_line:
                        print("✓ Content verification passed (found test event).")
                    else:
                        print("? File exists but test event not found at end.")
                else:
                    print("? File exists but is empty.")
        else:
            print(f"✗ File was NOT created at: {WAZUH.event_log}")
            
    except Exception as e:
        print(f"✗ Error writing to file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wazuh_write()
