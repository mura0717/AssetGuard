"""
Integration Pipeline
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from soc_stack.asset_engine.asset_resolver import ResolvedAsset
from soc_stack.states.base_state import BaseStateManager
from soc_stack.builders.base_builder import BasePayloadBuilder
from soc_stack.dispatchers.base_dispatcher import BaseDispatcher


BASE_DIR = Path(__file__).resolve().parents[2]
DRY_RUN_DIR = BASE_DIR / "logs" / "dry_runs"


@dataclass
class PipelineResult:
    """Result of running a pipeline."""
    created: int
    updated: int
    skipped: int
    failed: int
    integration: str
    heartbeat: int = 0


class IntegrationPipeline:
    """Coordinates state, builder, and dispatcher."""
    
    def __init__(
        self,
        name: str,
        state: BaseStateManager,
        builder: BasePayloadBuilder,
        dispatcher: BaseDispatcher,
        dry_run: bool = False
    ):
        self.name = name
        self.state = state
        self.builder = builder
        self.dispatcher = dispatcher
        self.dry_run = dry_run
        self.debug = os.getenv(f'{name.upper().replace("-", "_")}_PIPELINE_DEBUG', '0') == '1'
        if hasattr(self.builder, 'dry_run'):
            self.builder.dry_run = dry_run
            
    def process(self, assets: List[ResolvedAsset]) -> PipelineResult:
        """Process assets through the pipeline."""
        results = {'created': 0, 'updated': 0, 'skipped': 0, 'failed': 0, 'heartbeat': 0}
        to_dispatch: List[tuple] = []
        skipped_details: List[tuple] = []
        failed_details: List[tuple] = []
        
        print(f"\n[{self.name}] Processing {len(assets)} assets...")
        
        for asset in assets:
            state_result = self.state.check(asset.canonical_data)
            
            if state_result.action == 'skip':
                results['skipped'] += 1
                skipped_details.append((asset, state_result.reason))
                if self.debug:
                    print(f"  ─ Skip: {asset.canonical_data.get('name')} ({state_result.reason})")
                continue
            
            try:
                build_result = self.builder.build(asset.canonical_data, state_result)
                to_dispatch.append((asset, state_result, build_result))
                
                if self.debug:
                    symbol = "+" if state_result.action == 'create' else "↻"
                    print(f"  {symbol} {state_result.action}: {asset.canonical_data.get('name')}")
                
            except Exception as e:
                results['failed'] += 1
                failed_details.append((asset, str(e)))
                if self.debug:
                    print(f"  ✗ Build failed: {asset.canonical_data.get('name')} - {e}")
        
        if self.dry_run:
            self._handle_dry_run(to_dispatch, results, skipped_details, failed_details)
        else:
            self._handle_dispatch(to_dispatch, results)
        
        if not self.dry_run and hasattr(self.state, "save"):
            self.state.save()
            if self.debug: print(f"[{self.name}] State saved.")
        
        self._print_summary(results)
        
        return PipelineResult(
            created=results['created'],
            updated=results['updated'],
            skipped=results['skipped'],
            failed=results['failed'],
            heartbeat=results['heartbeat'],
            integration=self.name
        )
    
    def _handle_dry_run(self, to_dispatch: List[tuple], results: Dict, skipped_details: Optional[List[tuple]] = None, failed_details: Optional[List[tuple]] = None):
        """Handle dry run."""
        skipped_details = skipped_details or []
        failed_details = failed_details or []
        
        print(f"\n[{self.name}] DRY RUN - No changes will be made")
        
        dry_run_data = []
        for asset, state_result, build_result in to_dispatch:
            entry = {
                'action': state_result.action,
                'asset_id': state_result.asset_id,
                'name': asset.canonical_data.get('name', 'Unknown'),
                'source': asset.source,
                'canonical_data': asset.canonical_data,
                'payload': build_result.payload,
                'metadata': build_result.metadata,
            }
            dry_run_data.append(entry)
            
            if state_result.action == 'create':
                results['created'] += 1
            elif state_result.action == 'heartbeat':
                results['heartbeat'] += 1
            else:
                results['updated'] += 1
        
        DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self.name.lower().replace('-', '_').replace(' ', '_')
        dry_run_file = DRY_RUN_DIR / f"dry_run_{safe_name}_{timestamp}.json"
        
        with open(dry_run_file, "w") as f:
            json.dump(dry_run_data, f, indent=2, default=str)
        
        print(f"[{self.name}] Payloads written to: {dry_run_file}")
        
        print(f"\n[{self.name}] Would process {len(dry_run_data)} assets:")
        creates = [d for d in dry_run_data if d['action'] == 'create']
        updates = [d for d in dry_run_data if d['action'] == 'update']
        
        if creates:
            print(f"\n  CREATE ({len(creates)}):")
            for entry in creates[:5]:
                print(f"    + {entry['name']}")
            if len(creates) > 5:
                print(f"    ... and {len(creates) - 5} more")
        
        if updates:
            print(f"\n  UPDATE ({len(updates)}):")
            for entry in updates[:5]:
                print(f"    ↻ {entry['name']} (ID: {entry['asset_id']})")
            if len(updates) > 5:
                print(f"    ... and {len(updates) - 5} more")
        
        if skipped_details:
            print(f"\n  SKIPPED ({len(skipped_details)}):")
            for asset, reason in skipped_details[:5]:
                print(f"    ─ {asset.canonical_data.get('name', 'Unknown')} ({reason})")
        
        if failed_details:
            print(f"\n  FAILED ({len(failed_details)}):")
            for asset, error in failed_details[:5]:
                print(f"    ✗ {asset.canonical_data.get('name', 'Unknown')} ({error})")
    
    def _handle_dispatch(self, to_dispatch: List[tuple], results: Dict):
        """Handle dispatch."""
        if not to_dispatch:
            return
        
        build_results = [br for _, _, br in to_dispatch]
        dispatch_results = self.dispatcher.sync(build_results)
        
        results['created'] = dispatch_results.get('created', 0)
        results['updated'] = dispatch_results.get('updated', 0)
        results['skipped'] += dispatch_results.get('skipped', 0)
        results['failed'] += dispatch_results.get('failed', 0)
        results['heartbeat'] += dispatch_results.get('heartbeat', 0)
        
        for asset, state_result, build_result in to_dispatch:
            if build_result.metadata.get("dispatch_ok", False) is True:
                actual_id = str(build_result.snipe_id) if build_result.snipe_id else state_result.asset_id
                self.state.record(
                    actual_id,
                    asset.canonical_data,
                    state_result.action
                )
            elif self.debug:
                print(f"  ⚠ Not recording state for failed dispatch: {asset.canonical_data.get('name')}")
    
    def _print_summary(self, results: Dict):
        mode = "[DRY RUN] " if self.dry_run else ""
        print(f"\n[{self.name}] {mode}Complete: "
              f"{results['created']} created, "
              f"{results['updated']} updated, "
              f"{results['heartbeat']} heartbeats, "
              f"{results['skipped']} skipped, "
              f"{results['failed']} failed")