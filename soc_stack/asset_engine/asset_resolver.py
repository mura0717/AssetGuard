"""
Asset Resolver
Enriches and normalizes scan data into canonical format.
"""
import os
from dataclasses import dataclass
from typing import Dict, List
from soc_stack.config.network_config import STATIC_IP_MAP
from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.asset_engine.asset_categorizer import AssetCategorizer

@dataclass
class ResolvedAsset:
    canonical_data: Dict
    source: str

class AssetResolver:
    STATIC_OVERRIDE_FIELDS = {'name', 'asset_tag', 'serial', 'manufacturer', 'model'}
    STATIC_FILL_FIELDS = {'location', 'category', 'device_type'}
    
    def __init__(self):
        self.debug = os.getenv('ASSET_RESOLVER_DEBUG', '0') == '1'
        
    def resolve(self, scan_source: str, scan_data: List[Dict]) -> List[ResolvedAsset]:
        resolved_assets = []
        for raw_asset in scan_data:
            # Create a copy to avoid mutating the original scanner data
            asset_data = raw_asset.copy()
            
            asset_data['_source'] = scan_source
            self._enrich_with_static_map(asset_data)
            self._cleanup_generic_name(asset_data)
            self._apply_categorization(asset_data)
            
            if self.debug:
                debug_logger.log_parsed_asset_data(scan_source, asset_data)
            
            resolved_assets.append(ResolvedAsset(asset_data, scan_source))
            
        if self.debug:
            print(f"[Resolver] Resolved {len(resolved_assets)} assets from {scan_source}")
        return resolved_assets
    
    def _apply_categorization(self, asset_data: Dict) -> None:
        """Run categorization to populate device_type, category, etc."""
        categorization = AssetCategorizer.categorize(asset_data)
        asset_data.update(categorization)
    
    def _enrich_with_static_map(self, asset_data: Dict) -> None:
        ip = asset_data.get('last_seen_ip')
        if not ip or ip not in STATIC_IP_MAP: return
        
        static_data = STATIC_IP_MAP[ip]
        for key, value in static_data.items():
            if not value: continue
            current = asset_data.get(key)
            
            if key in self.STATIC_OVERRIDE_FIELDS:
                if self._is_generic_value(key, current) or not current:
                    asset_data[key] = value
            elif key in self.STATIC_FILL_FIELDS or not current:
                asset_data[key] = value
    
    def _is_generic_value(self, key: str, value) -> bool:
        if not value: return True
        if key == 'name':
            name = str(value).lower()
            return name.startswith('device-') or name.startswith('unknown') or name == '_gateway'
        return False
    
    def _cleanup_generic_name(self, asset_data: Dict) -> None:
        name = asset_data.get('name', '')
        if not self._is_generic_value('name', name): return
        
        # Try alternatives
        alternatives = [asset_data.get('dns_hostname'), asset_data.get('host_name'), asset_data.get('intune_device_name')]
        for alt in alternatives:
            if alt and not self._is_generic_value('name', alt):
                asset_data['name'] = alt
                return