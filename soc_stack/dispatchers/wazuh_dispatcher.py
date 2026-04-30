import os
import json
from typing import List, Dict

from soc_stack.config.hydra_settings import WAZUH
from soc_stack.dispatchers.base_dispatcher import BaseDispatcher
from soc_stack.builders.base_builder import BuildResult
from soc_stack.loggers.failure_logger import FailureLogger

class WazuhDispatcher(BaseDispatcher):
    """Dispatches events to Wazuh logs."""
    
    def __init__(self):
        self.debug = os.getenv('WAZUH_DISPATCHER_DEBUG', '0') == '1'
        self.failure_logger = FailureLogger()

    def sync(self, build_results: List[BuildResult]) -> Dict[str, int]:
        results = {"created": 0, "updated": 0, "heartbeat": 0, "failed": 0}
        print(f"\n[WAZUH] Writing {len(build_results)} events...")
        
        WAZUH.event_log.parent.mkdir(parents=True, exist_ok=True)

        with open(WAZUH.event_log, 'a') as f:
            for build_result in build_results:
                try:
                    f.write(json.dumps(build_result.payload) + "\n")
                    build_result.metadata['dispatch_ok'] = True
                    if build_result.action == 'create':
                        results["created"] += 1
                    elif build_result.action == 'heartbeat':
                        results["heartbeat"] += 1
                    else:
                        results["updated"] += 1
                        
                    if self.debug:
                        name = build_result.payload.get('asset', {}).get('name', 'Unknown')
                        print(f"  ✓ {build_result.action}: {name}")
                        
                except Exception as e:
                    results["failed"] += 1
                    build_result.metadata["dispatch_ok"] = False
                    self.failure_logger.log_failure(build_result.payload, build_result.action, str(e))
                    if self.debug:
                        print(f"  ✗ Failed to write event: {e}")

        print(f"[WAZUH] Done: {results['created']} created, {results['updated']} updated, {results['heartbeat']} heartbeats, {results['failed']} failed")
        return results