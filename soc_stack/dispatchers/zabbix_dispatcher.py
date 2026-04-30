import os
import json
from typing import List, Dict

from soc_stack.zabbix.zabbix_api.zabbix_client import ZabbixClient
from soc_stack.dispatchers.base_dispatcher import BaseDispatcher
from soc_stack.builders.base_builder import BuildResult
from soc_stack.loggers.failure_logger import FailureLogger

class ZabbixDispatcher(BaseDispatcher):
    """Dispatches hosts to Zabbix."""
    
    def __init__(self):
        self.debug = os.getenv('ZABBIX_DISPATCHER_DEBUG', '0') == '1'
        self._group_cache: Dict[str, str] = {}
        self.client = ZabbixClient()
        self.failure_logger = FailureLogger()

    def _handle_dispatch_error(self, item: BuildResult, results: Dict, status: str, error_msg: str):
        results[status] += 1
        item.metadata['dispatch_ok'] = False
        self.failure_logger.log_failure(item.payload, item.action, error_msg)
        if self.debug:
            print(f"  ✗ {status.capitalize()}: {item.payload.get('name', 'Unknown')} - {error_msg}")

    def sync(self, build_results: List[BuildResult]) -> Dict[str, int]:
        results = {"created": 0, "updated": 0, "skipped": 0, "failed": 0}
        print(f"\n[ZABBIX] Syncing {len(build_results)} hosts...")
        
        if not self.client.auth:
            print("[ZABBIX] Not authenticated. Skipping all.")
            results["failed"] = len(build_results)
            return results

        for item in build_results:
            try:
                new_ip = item.payload.get('interfaces', [{}])[0].get('ip')
                
                if not new_ip:
                    self._handle_dispatch_error(item, results, 'skipped', "Missing IP address")
                    continue
                
                group_name = item.metadata.get('group_name') or "Discovered Hosts"
                group_id = self._get_or_create_group(group_name)
                
                if not group_id:
                    self._handle_dispatch_error(item, results, 'failed', f"Failed to get or create group '{group_name}'")
                    continue
                    
                item.payload['groups'] = [{"groupid": group_id}]
                
                if item.action == 'update':
                    hostid = item.metadata.get('hostid')
                    
                    if not hostid:
                        self._handle_dispatch_error(item, results, 'failed', "Missing hostid for update")
                        continue
                    
                    update_payload = {
                        "hostid": hostid,
                        "inventory": item.payload['inventory'],
                        "tags": item.payload['tags']
                    }
                    self.client.call("host.update", update_payload)
                    
                    if new_ip:
                        try:
                            interfaces = self.client.call("hostinterface.get", {
                                "hostids": hostid,
                                "output": ["interfaceid", "ip"]
                            })
                            
                            if interfaces:
                                main_interface = interfaces[0]
                                if main_interface.get('ip') != new_ip:
                                    self.client.call("hostinterface.update", {
                                        "interfaceid": main_interface['interfaceid'],
                                        "ip": new_ip
                                    })
                                    if self.debug:
                                        print(f"    ↻ Updated IP: {main_interface['ip']} → {new_ip}")
                        except Exception as e:
                            self.failure_logger.log_failure(item.payload, 'update_ip', str(e))
                            if self.debug:
                                print(f"    ⚠️ Could not update interface IP: {e}")
                    
                    item.metadata['dispatch_ok'] = True
                    results['updated'] += 1
                    if self.debug:
                        print(f"  ✓ Updated: {item.payload.get('name')} (ID: {hostid})")
                        
                else: 
                    result = self.client.call("host.create", item.payload)
                    item.metadata['dispatch_ok'] = True
                    results['created'] += 1
                    
                    if self.debug:
                        new_id = result.get('hostids', ['?'])[0] if result else '?'
                        print(f"  ✓ Created: {item.payload.get('name')} (ID: {new_id})")
                        
            except Exception as e:
                self._handle_dispatch_error(item, results, 'failed', str(e))
                    
        if self.debug and build_results:
            last_payload = build_results[-1].payload if build_results else {}
            print(f"  LOG (last): {json.dumps(last_payload, default=str)[:100]}...")
                    
        print(f"[ZABBIX] Done: {results['created']} created, {results['updated']} updated, "
              f"{results['skipped']} skipped, {results['failed']} failed")
        return results

    def _get_or_create_group(self, name):
        if name in self._group_cache: return self._group_cache[name]
        try:
            groups = self.client.call("hostgroup.get", {"filter": {"name": [name]}, "output": ["groupid"]})
            if groups: gid = groups[0]['groupid']
            else: gid = self.client.call("hostgroup.create", {"name": name})['groupids'][0]
            self._group_cache[name] = gid
            return gid
        except Exception as e:
            if self.debug:
                print(f"[ZABBIX] ✗ Group '{name}' get or create error: {e}")
            return None