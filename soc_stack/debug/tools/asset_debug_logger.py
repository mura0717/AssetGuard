import os
import json
from pathlib import Path
from datetime import datetime

from soc_stack.config.hydra_settings import BASE_DIR

class AssetDebugLogger:
    """Debug logger for asset processing."""
    
    def __init__(self):
        # Granular debug flags (can be set independently)
        self.intune_debug = os.getenv('INTUNE_DEBUG', '0') == '1'
        self.nmap_debug = os.getenv('NMAP_DEBUG', '0') == '1'
        self.teams_debug = os.getenv('TEAMS_DEBUG', '0') == '1'
        self.entra_debug = os.getenv('ENTRA_DEBUG', '0') == '1'
        self.ms365_debug = os.getenv('MS365_DEBUG', '0') == '1'
        
        # Master flag
        self.is_enabled = any([
            self.intune_debug, 
            self.nmap_debug, 
            self.teams_debug, 
            self.entra_debug,
            self.ms365_debug,
        ])
        
        if self.is_enabled:
            print(f"[DEBUG_LOGGER]: Initializing... ")
            if self.intune_debug:
                print(f"INTUNE_DEBUG={os.getenv('INTUNE_DEBUG', '0')} (internal: {self.intune_debug}).")
            elif self.nmap_debug:
                print(f"NMAP_DEBUG={os.getenv('NMAP_DEBUG', '0')} (internal: {self.nmap_debug}).")
            elif self.teams_debug:
                print(f"TEAMS_DEBUG={os.getenv('TEAMS_DEBUG', '0')} (internal: {self.teams_debug}).")
            elif self.entra_debug:
                print(f"ENTRA_DEBUG={os.getenv('ENTRA_DEBUG', '0')} (internal: {self.entra_debug}).")
            elif self.ms365_debug:
                print(f"MS365_DEBUG={os.getenv('MS365_DEBUG', '0')} (internal: {self.ms365_debug}).")
            else:
                print(f"Any enabled: {self.is_enabled}.")

        # Create log directory
        base_log_dir = os.path.join(BASE_DIR, "soc_stack", "debug", "debug_logs")
        os.makedirs(base_log_dir, exist_ok=True)
        
        # Purpose-based log files
        self.log_files = {
            'intune': {
                'raw': os.path.join(base_log_dir, 'intune_logs', 'intune_raw_data.log'),
                'parsed': os.path.join(base_log_dir, 'intune_logs', 'intune_parsed_data.log'),
                'categorization': os.path.join(base_log_dir, 'intune_logs', 'intune_categorization_details.log'),
            },
            'teams': {
                'raw': os.path.join(base_log_dir, 'teams_logs', 'teams_raw_data.log'),
                'parsed': os.path.join(base_log_dir, 'teams_logs', 'teams_parsed_data.log'),
                'categorization': os.path.join(base_log_dir, 'teams_logs', 'teams_categorization_details.log'),
            },
            'entra': {
                'raw': os.path.join(base_log_dir, 'entra_logs', 'entra_raw_data.log'),
                'parsed': os.path.join(base_log_dir, 'entra_logs', 'entra_parsed_data.log'),
                'categorization': os.path.join(base_log_dir, 'entra_logs', 'entra_categorization_details.log'),
            },
            'nmap': {
                'raw': os.path.join(base_log_dir, 'nmap_logs', 'nmap_raw_data.log'),
                'parsed': os.path.join(base_log_dir, 'nmap_logs', 'nmap_parsed_data.log'),
                'categorization': os.path.join(base_log_dir, 'nmap_logs', 'nmap_categorization_details.log'),
                'summary': os.path.join(base_log_dir, 'nmap_logs', 'nmap_summary.log'),
                'final_payload': os.path.join(base_log_dir, 'nmap_logs', 'nmap_final_payload.log'),
            },
            'ms365': {
                'raw': os.path.join(base_log_dir, 'ms365_logs', 'ms365_raw_data.log'),
                'parsed': os.path.join(base_log_dir, 'ms365_logs', 'ms365_parsed_data.log'),
                'categorization': os.path.join(base_log_dir, 'ms365_logs', 'ms365_categorization_details.log'),
                'summary': os.path.join(base_log_dir, 'ms365_logs', 'ms365_summary.log'),
                'final_payload': os.path.join(base_log_dir, 'ms365_logs', 'ms365_final_payload.log'),
            }
        }
        # Create all necessary subdirectories
        for source_logs in self.log_files.values():
            for log_path in source_logs.values():
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    def _get_log_path(self, source: str, purpose: str) -> str | None:
        """Helper to get the correct log file path for a source and purpose."""  
        log_path = self.log_files.get(source.lower(), {}).get(purpose)
        return log_path
    
    
    def _should_log(self, source: str) -> bool:
        """Check if logging is enabled for the given source."""
        source_lower = source.lower()
        if source_lower == 'intune': result = self.intune_debug
        elif source_lower == 'nmap': result = self.nmap_debug
        elif source_lower == 'teams': result = self.teams_debug
        elif source_lower == 'entra': result = self.entra_debug
        elif source_lower == 'ms365': result = self.ms365_debug
        else: result = False
        return result
    
    def clear_logs(self, source: str):
        """Clears all log files for a specific source."""
        if not self._should_log(source): return
        
        source_files = self.log_files.get(source.lower(), {})
        for file_path in source_files.values():
            with open(file_path, "w", encoding="utf-8") as f: f.write("")
        
    def log_raw_host_data(self, source: str, host_identifier: str, data: dict):
        if not self._should_log(source): return
        log_path = self._get_log_path(source, 'raw')
        if not log_path: return
        
        message = f"\n--- RAW DATA | Host: {host_identifier} ---\n" + \
                  json.dumps(data, indent=2, default=str) + "\n" + "-"*50
        self._write_log(message, log_path)

    def log_parsed_asset_data(self, source: str, data: list):
        if not self._should_log(source): return
        log_path = self._get_log_path(source, 'parsed')
        if not log_path: return
        
        payload, header = (data, f"Found {len(data)} assets.\n") if isinstance(data, list) else (data, "Found 1 asset.\n")
        
        message = f"\n--- PARSED ASSET DATA ---\n" + \
                  f"{header}\n" + \
                  json.dumps(payload, indent=2, default=str) + "\n" + "-"*50
        self._write_log(message, log_path)
        
    def log_categorization(self, source: str, log_entry: str):
        if not self._should_log(source): return
        log_path = self._get_log_path(source, 'categorization')
        if not log_path: return
        self._write_log(log_entry, log_path)
        
    def log_sync_summary(self, source: str, results: dict):
        if not self._should_log(source): return
        log_path = self._get_log_path(source, 'summary')
        if not log_path: return
        
        message = f"\n--- SYNC SUMMARY ---\n" + \
                  f"Created: {results.get('created', 0)}\n" + \
                  f"Updated: {results.get('updated', 0)}\n" + \
                  f"Failed:  {results.get('failed', 0)}\n" + "-"*50
        self._write_log(message, log_path)

    def log_final_payload(self, scan_type: str, action: str, asset_name: str, payload: dict):
        """Log final payload."""
        if not self._should_log(scan_type): return
        log_path = self._get_log_path(scan_type, 'final_payload')
        if not log_path: return

        message = f"\n--- FINAL PAYLOAD | Action: {action.upper()} | Asset: {asset_name} ---\n" + \
                  json.dumps(payload, indent=2, default=str) + "\n" + "-"*50
        self._write_log(message, log_path)

    def _write_log(self, message: str, log_file: str):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        try:
            with open(log_file, "a", encoding="utf-8") as f: f.write(log_entry + "\n")
        except IOError as e:
            print(f"Warning: Could not write to log file {log_file}: {e}")

debug_logger = AssetDebugLogger()