"""
Main Orchestrator
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict

from soc_stack.scanners.nmap_scanner import NmapScanner
from soc_stack.scanners.ms365_aggregator import Microsoft365Aggregator
from soc_stack.asset_engine.asset_resolver import AssetResolver
from soc_stack.asset_engine.asset_merger import AssetMerger

from soc_stack.states.snipe_state import SnipeStateManager
from soc_stack.states.wazuh_state import WazuhStateManager
from soc_stack.states.zabbix_state import ZabbixStateManager

from soc_stack.builders.snipe_builder import SnipePayloadBuilder
from soc_stack.builders.wazuh_builder import WazuhPayloadBuilder
from soc_stack.builders.zabbix_builder import ZabbixPayloadBuilder

from soc_stack.dispatchers.snipe_dispatcher import SnipeDispatcher
from soc_stack.dispatchers.wazuh_dispatcher import WazuhDispatcher
from soc_stack.dispatchers.zabbix_dispatcher import ZabbixDispatcher

from soc_stack.pipelines.integration_pipeline import IntegrationPipeline, PipelineResult
from soc_stack.config.hydra_settings import WAZUH
from soc_stack.utils.sudo_utils import elevate_to_root
from soc_stack.config.hydra_settings import print_configuration


BASE_DIR = Path(__file__).resolve().parents[1]
DRY_RUN_DIR = BASE_DIR / "logs" / "dry_runs"


class HydraOrchestrator:
    """Main entry point for asset synchronization."""
    
    def __init__(self, dry_run: bool = False, skip_integrations: Optional[List[str]] = None):
        self.resolver = AssetResolver()
        self.dry_run = dry_run
        self.skip_integrations = skip_integrations or []
        self._pipelines = None
    
    @property
    def pipelines(self) -> Dict[str, IntegrationPipeline]:
        """Lazy load pipelines."""
        if self._pipelines is None:
            self._pipelines = self._create_pipelines()
        return self._pipelines
    
    def _create_pipelines(self) -> Dict[str, IntegrationPipeline]:
        """Initialize pipelines."""
        return {
            'snipe': IntegrationPipeline(
                name='Snipe-IT',
                state=SnipeStateManager(),
                builder=SnipePayloadBuilder(dry_run=self.dry_run),
                dispatcher=SnipeDispatcher(),
                dry_run=self.dry_run
            ),
            'wazuh': IntegrationPipeline(
                name='Wazuh',
                state=WazuhStateManager(WAZUH.state_file),
                builder=WazuhPayloadBuilder(),
                dispatcher=WazuhDispatcher(),
                dry_run=self.dry_run
            ),
            'zabbix': IntegrationPipeline(
                name='Zabbix',
                state=ZabbixStateManager(),
                builder=ZabbixPayloadBuilder(),
                dispatcher=ZabbixDispatcher(),
                dry_run=self.dry_run
            ),
        }
    
    def run_full_sync(self, integrations: Optional[List[str]] = None, sources: Optional[List[str]] = None,
        nmap_profile: str = 'discovery') -> Dict[str, PipelineResult]:
        
        """Run complete sync."""
        
        print("=" * 60)
        print("HYDRA ASSET SYNCHRONIZATION PIPELINE")
        if self.dry_run:
            print("MODE: DRY RUN (no changes will be made)")
        print("=" * 60)
        
        print("\n" + "=" * 60)
        print("PHASE 1: COLLECTING DATA FROM SOURCES")
        print("=" * 60)
        
        all_resolved = []
        active_sources = sources or ['all']
        if 'all' in active_sources:
            active_sources = ['nmap', 'ms365']
        raw_data = {}  # Store for dry-run output
        
        if 'nmap' in active_sources:
            print(f"\n[NMAP] Scanning network (Profile: {nmap_profile})...")
            if os.geteuid() != 0:
                try:
                    elevate_to_root()
                except Exception as e:
                    print(f"Failed to elevate to root: {e}")
                    sys.exit(1)
                
            nmap_data = NmapScanner().collect_assets(profile=nmap_profile)
            raw_data['nmap'] = nmap_data
            resolved = self.resolver.resolve('nmap', nmap_data)
            all_resolved.extend(resolved)
            print(f"[NMAP] Found {len(nmap_data)} hosts")
        
        if 'ms365' in active_sources:
            print("\n[MS365] Fetching from Microsoft 365...")
            ms365_data = Microsoft365Aggregator().collect_assets()
            raw_data['ms365'] = ms365_data
            resolved = self.resolver.resolve('microsoft365', ms365_data)
            all_resolved.extend(resolved)
            print(f"[MS365] Found {len(ms365_data)} assets")
        
        print(f"\nTotal resolved assets: {len(all_resolved)}")
        
        print("\nMerging assets from multiple sources...")
        merged_assets = AssetMerger.merge_assets(all_resolved)
        print(f"After merge: {len(merged_assets)} unique assets "
              f"(reduced from {len(all_resolved)})")
        
        if not merged_assets:
            print("\nNo assets found. Nothing to process.")
            return {}
        
        print("\n" + "=" * 60)
        print("PHASE 2: RUNNING INTEGRATION PIPELINES")
        print("=" * 60)
        
        active_integrations = integrations or list(self.pipelines.keys())
        active_integrations = [i for i in active_integrations if i not in self.skip_integrations]
        
        if not active_integrations:
            print("\nNo integrations enabled. Nothing to dispatch.")
            return {}
        
        print(f"\nActive integrations: {', '.join(active_integrations)}")
        
        results = {}
        for name in active_integrations:
            if name in self.pipelines:
                results[name] = self.pipelines[name].process(merged_assets)
        
        self._print_final_summary(results, raw_data if self.dry_run else None)
        
        return results
    
    def _print_final_summary(self, results: Dict[str, PipelineResult], raw_data: Optional[Dict] = None):
        """Print execution summary."""
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        
        if not results:
            print("  No pipelines were run.")
            return
        
        total_created = sum(r.created for r in results.values())
        total_updated = sum(r.updated for r in results.values())
        total_skipped = sum(r.skipped for r in results.values())
        total_failed = sum(r.failed for r in results.values())
        
        for name, result in results.items():
            print(f"\n  {name}:")
            print(f"    Created: {result.created}")
            print(f"    Updated: {result.updated}")
            print(f"    Skipped: {result.skipped}")
            print(f"    Failed:  {result.failed}")
        
        print(f"\n  {'─' * 40}")
        print(f"  TOTAL: {total_created} created, {total_updated} updated, "
              f"{total_skipped} skipped, {total_failed} failed")
        
        if self.dry_run and raw_data:
            self._write_dry_run_summary(raw_data, results)
    
    def _write_dry_run_summary(self, raw_data: Dict, results: Dict[str, PipelineResult]):
        """Save dry-run summary to JSON."""
        DRY_RUN_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = DRY_RUN_DIR / f"dry_run_summary_{timestamp}.json"
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run',
            'sources': {
                source: {
                    'count': len(data),
                    'sample': data[:3] if data else []
                }
                for source, data in raw_data.items()
            },
            'results': {
                name: {
                    'created': r.created,
                    'updated': r.updated,
                    'skipped': r.skipped,
                    'failed': r.failed
                }
                for name, r in results.items()
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n  Dry run summary: {summary_file}")


def parse_args():
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description='Hydra Asset Synchronization Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            %(prog)s                              # Full sync, all sources and integrations
            %(prog)s --dry-run                    # Test run, no changes made
            %(prog)s --dry-run --source nmap      # Dry run with only nmap data
            %(prog)s --skip-zabbix                # Skip Zabbix integration
            %(prog)s --only snipe wazuh           # Only sync to Snipe-IT and Wazuh
            %(prog)s --source ms365 --only snipe  # MS365 data to Snipe-IT only
                    """
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Run without making any changes (writes payloads to log files)'
    )
    
    parser.add_argument(
        '--source', '-s',
        nargs='+',
        choices=['nmap', 'ms365', 'all'],
        default=None,
        help='Data source(s) to collect from (default: all)'
    )
    
    parser.add_argument(
        '--nmap',
        metavar='PROFILE',
        help='Run Nmap scan with specific profile (e.g., discovery, detailed). Implies --source nmap'
    )
    
    parser.add_argument(
        '--ms365',
        action='store_true',
        help='Run Microsoft 365 sync. Implies --source ms365'
    )
    
    parser.add_argument(
        '--only', '-o',
        nargs='+',
        choices=['snipe', 'wazuh', 'zabbix'],
        help='Only run specified integrations'
    )
    
    parser.add_argument(
        '--skip-snipe',
        action='store_true',
        help='Skip Snipe-IT integration'
    )
    
    parser.add_argument(
        '--skip-wazuh',
        action='store_true',
        help='Skip Wazuh integration'
    )
    
    parser.add_argument(
        '--skip-zabbix',
        action='store_true',
        help='Skip Zabbix integration'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run integration tests instead of sync'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.verbose:
        import os
        os.environ['ASSET_RESOLVER_DEBUG'] = '1'
        os.environ['SNIPE_PIPELINE_DEBUG'] = '1'
        os.environ['WAZUH_PIPELINE_DEBUG'] = '1'
        os.environ['ZABBIX_PIPELINE_DEBUG'] = '1'
    
    print_configuration()
    
    skip = []
    if args.skip_snipe:
        skip.append('snipe')
    if args.skip_wazuh:
        skip.append('wazuh')
    if args.skip_zabbix:
        skip.append('zabbix')
    
    sources = []
    if args.nmap:
        sources.append('nmap')
    if args.ms365:
        sources.append('ms365')
    
    if args.source:
        for s in args.source:
            if s not in sources:
                sources.append(s)
    
    if not sources:
        sources = ['all']
    
    integrations = args.only if args.only else None
    
    if args.test:
        print("Running integration tests...")
        try:
            from soc_stack.debug.tests.test_hydra import main as run_tests
            return run_tests()
        except ImportError as e:
            print(f"Could not import test module: {e}")
            return 1
    
    try:
        orchestrator = HydraOrchestrator(
            dry_run=args.dry_run,
            skip_integrations=skip
        )
        
        orchestrator.run_full_sync(
            integrations=integrations,
            sources=sources,
            nmap_profile=args.nmap if args.nmap else 'discovery'
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())