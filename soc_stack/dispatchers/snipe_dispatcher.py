import os
import requests
from typing import List, Dict, Optional

from soc_stack.dispatchers.base_dispatcher import BaseDispatcher
from soc_stack.builders.base_builder import BuildResult
from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient
from soc_stack.loggers.failure_logger import FailureLogger


class SnipeDispatcher(BaseDispatcher):
    """Dispatches assets to Snipe-IT."""
    
    def __init__(self):
        self.client = SnipeClient()
        self.failure_logger = FailureLogger()
        self.debug = os.getenv('SNIPE_DISPATCHER_DEBUG', '0') == '1'
        
    def _send(self, method: str, endpoint: str, payload: Dict = None) -> Optional[requests.Response]:
        return self.client.make_api_request(method, f"/api/v1/{endpoint}", json=payload if payload is not None else None)

    def sync(self, build_results: List[BuildResult]) -> Dict[str, int]:
        results = {"created": 0, "updated": 0, "skipped": 0, "failed": 0}
        print(f"\n[SNIPE-IT] Syncing {len(build_results)} assets...")
        
        for build_result in build_results:
            try:
                payload = build_result.payload
                name = payload.get('name', 'Unknown')
                action = build_result.action
                
                method = None
                endpoint = None
                
                if action == 'create':
                    method = 'POST'
                    endpoint = 'hardware'
                elif action == 'update':
                    if not build_result.snipe_id:
                        build_result.metadata['dispatch_ok'] = False
                        results["skipped"] += 1
                        self.failure_logger.log_failure(payload, 'update', 'Missing snipe_id for update')
                        if self.debug:
                            print(f"  ✗ Update skipped (missing snipe_id): {name}")
                        continue
                    method = 'PATCH'
                    endpoint = f'hardware/{build_result.snipe_id}'
                
                if not method:
                    continue

                resp = self._send(method, endpoint, payload)
                
                if resp is None:
                    build_result.metadata['dispatch_ok'] = False
                    build_result.metadata['error'] = 'No response after retries'
                    results["failed"] += 1
                    self.failure_logger.log_failure(payload, action, 'No response after retries')
                    if self.debug:
                        print(f"  ✗ {action.capitalize()} failed: {name} - No response from API")
                    continue
                
                try:
                    body = resp.json()
                except (ValueError, AttributeError):
                    body = {}

                if resp.status_code in (200, 201) and body.get('status') == 'success':
                    build_result.metadata['dispatch_ok'] = True
                    if action == 'create':
                        new_id = body.get('payload', {}).get('id')
                        if new_id:
                            build_result.snipe_id = new_id
                        results["created"] += 1
                        if self.debug:
                            print(f"  ✓ Created: {name} (ID: {new_id})")
                    else:
                        results["updated"] += 1
                        if self.debug:
                            print(f"  ✓ Updated: {name}")
                else:
                    build_result.metadata["dispatch_ok"] = False
                    results["failed"] += 1
                    err_msg = body.get('messages') or (resp.text[:100] if resp.text else "No response")
                    self.failure_logger.log_failure(payload, action, err_msg)
                    if self.debug:
                        print(f"  ✗ {action.capitalize()} failed: {name} - Status: {resp.status_code} - {err_msg}")
            
            except Exception as e:
                build_result.metadata['dispatch_ok'] = False
                results["failed"] += 1
                self.failure_logger.log_failure(payload, build_result.action, str(e))
                if self.debug:
                    print(f"  ✗ Error: {build_result.payload.get('name', 'Unknown')} - {e}")

        print(f"[SNIPE-IT] Done: {results['created']} created, {results['updated']} updated, {results['skipped']} skipped, {results['failed']} failed")
        return results