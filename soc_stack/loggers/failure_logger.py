"""
Failure Logger
"""

import os
import csv
from datetime import datetime
from pathlib import Path


FAILURE_LOG_PATH = os.getenv('FAILURE_LOG_PATH', 'logs/fail_logs/fails.csv')

class FailureLogger:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[2]
        
        path = Path(FAILURE_LOG_PATH)
        if path.is_absolute():
            self.filepath = path
        else:
            self.filepath = self.base_dir / path
            
        self.log_dir = self.filepath.parent
        self._ensure_log_dir()
        self._ensure_header()
        
    def _ensure_log_dir(self):
        if not self.log_dir.exists():
            os.makedirs(self.log_dir, exist_ok=True)
    
    def _ensure_header(self):
        if not self.filepath.exists():
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "name", "serial", "source", "action", "error_message"])
    
    def log_failure(self, payload: dict, action: str, error_msg: str):
        """Log failure to CSV."""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            name = payload.get('name', 'Unknown')
            serial = payload.get('serial', 'N/A')
            source = payload.get('_source', 'unknown')
            clean_error = str(error_msg).replace('\n', ' ')[:1000]

            with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, name, serial, source, action, clean_error])
                
        except Exception as e:
            print(f"Error writing to failure log: {e}")

    