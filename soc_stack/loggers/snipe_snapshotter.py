"""
Snipe-IT Snapshotter
"""

import json
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

from soc_stack.snipe_it.snipe_api.services.assets import AssetService

BASE_DIR = Path(__file__).resolve().parents[2]

class SnipeSnapshotter:

    def __init__(self):
        self.asset_service = AssetService()
        self.snapshot_dir = BASE_DIR / "logs" / "snipe_snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def take_snapshot(self) -> Optional[Path]:
        """Save all assets to JSON."""
        print("Taking snapshot of current Snipe-IT assets...")
        try:
            assets = self.asset_service.get_all(limit=10000, refresh_cache=True)
        except Exception as e:
            print(f"Error fetching all assets: {e}")
            return None
       
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snipe_snapshot_{timestamp}.log"
        filepath = self.snapshot_dir / filename
        
        snapshot_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "count": len(assets)
            },
            "assets": assets
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2)
        
        print(f"[Snapshot] Saved {len(assets)} assets to {filepath}")
        return filepath

    def cleanup_old_snapshots(self, retention_days: int = 90):
        """Delete old snapshots."""
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        for snapshot_file in self.snapshot_dir.glob("snipe_snapshot_*.log"):
            file_mtime = datetime.fromtimestamp(snapshot_file.stat().st_mtime)
            if file_mtime < cutoff_time:
                try:
                    snapshot_file.unlink()
                    print(f"[Cleanup] Deleted old snapshot: {snapshot_file.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"[Cleanup] Error deleting {snapshot_file.name}: {e}")
        
        if deleted_count > 0:
            print(f"[Cleanup] Total deleted: {deleted_count}")

if __name__ == "__main__":
    snapshotter = SnipeSnapshotter()
    snapshotter.take_snapshot()
    snapshotter.cleanup_old_snapshots()
