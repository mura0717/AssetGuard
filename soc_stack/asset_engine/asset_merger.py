"""
Asset Merger
Merges assets from multiple sources using Union-Find on shared identifiers.
"""

from typing import List, Dict, Set, Optional
from collections import defaultdict
from soc_stack.asset_engine.asset_resolver import ResolvedAsset
from soc_stack.utils.mac_utils import macs_from_string


class AssetMerger:
    """Merges resolved assets based on shared identifiers."""
    
    # Source priority for merge conflicts (higher = preferred)
    SOURCE_PRIORITY = {
        'microsoft365': 4,
        'intune': 3,
        'teams': 3,
        'nmap': 2,
        'unknown': 1,
    }
    
    @classmethod
    def merge_assets(cls, assets: List[ResolvedAsset]) -> List[ResolvedAsset]:
        """
        Merges assets based on shared identifiers using Union-Find approach.
        """
        if not assets:
            return []
        
        # 1. Pre-compute keys for all assets (do this ONCE)
        keys_cache = [cls._extract_keys(asset.canonical_data) for asset in assets]
        
        # 2. Build index: Map every identifier to list of asset indices
        index_map: Dict[str, List[int]] = defaultdict(list)
        
        for idx, keys in enumerate(keys_cache):
            for key in keys:
                index_map[key].append(idx)
        
        # 3. Find connected components using DFS
        visited: Set[int] = set()
        groups: List[Set[int]] = []
        
        for i in range(len(assets)):
            if i in visited:
                continue
            
            # Start new group with DFS
            group: Set[int] = set()
            stack = [i]
            
            while stack:
                curr = stack.pop()
                if curr in visited:
                    continue
                    
                visited.add(curr)
                group.add(curr)
                
                # Find all assets sharing any key with current asset
                curr_keys = keys_cache[curr]  # ← Use pre-computed cache
                for key in curr_keys:
                    for neighbor_idx in index_map[key]:
                        if neighbor_idx not in visited:
                            stack.append(neighbor_idx)
            
            groups.append(group)
        
        # 4. Merge each group into single asset
        merged_results = []
        for group_indices in groups:
            group_assets = [assets[i] for i in group_indices]
            merged = cls._merge_group(group_assets)
            merged_results.append(merged)
        
        return merged_results
    
    @classmethod
    def _extract_keys(cls, data: Dict) -> Set[str]:
        """Extract all identifier keys from asset data."""
        keys: Set[str] = set()
        
        # High-priority identifiers
        if data.get('serial'):
            keys.add(f"serial:{data['serial'].strip().upper()}")
        
        if data.get('intune_device_id'):
            keys.add(f"intune:{str(data['intune_device_id']).strip().lower()}")
        
        if data.get('azure_ad_id'):
            keys.add(f"azure:{str(data['azure_ad_id']).strip().lower()}")
        
        if data.get('entra_object_id'):
            keys.add(f"entra:{str(data['entra_object_id']).strip().lower()}")
        
        if data.get('teams_device_id'):
            keys.add(f"teams:{str(data['teams_device_id']).strip().lower()}")
        
        # MAC addresses (can have multiple)
        mac_sources = ['mac_addresses', 'wifi_mac', 'ethernet_mac']
        for field in mac_sources:
            value = data.get(field)
            if value:
                for mac in macs_from_string(str(value)):
                    keys.add(f"mac:{mac}")
        
        # Hostnames (lower priority, only use if meaningful)
        hostname = data.get('dns_hostname') or data.get('name') or ''
        if hostname and not hostname.lower().startswith('device-') and hostname.lower() not in ('unknown', '_gateway', ''):
            # Use short hostname for matching
            short_name = hostname.split('.')[0].lower()
            if len(short_name) > 3:  # Avoid matching on very short names
                keys.add(f"hostname:{short_name}")
        
        return keys
    
    @classmethod
    def _merge_group(cls, group: List[ResolvedAsset]) -> ResolvedAsset:
        """Merge multiple assets into one, respecting source priority."""
        if len(group) == 1:
            return group[0]
        
        def _get_asset_source(a: ResolvedAsset) -> str:
            return (a.canonical_data.get("_source") or a.source or "unknown")
        
        # Sort by source priority (ascending, so highest priority processed last)
        group.sort(key=lambda x: cls.SOURCE_PRIORITY.get(_get_asset_source(x), 1))
        
        # Start with lowest priority, overlay higher priority data
        merged_data: Dict = {}
        sources: Set[str] = set()
        
        for asset in group:
            src = _get_asset_source(asset)
            sources.add(src)
            
            for key, value in asset.canonical_data.items():
                if value in (None, '', [], {}, 'Unknown'):
                    continue
                
                # Special handling for names - don't overwrite good names with generic
                if key == 'name':
                    existing = merged_data.get('name', '')
                    if cls._is_generic_name(value) and not cls._is_generic_name(existing):
                        continue
                
                # Special handling for _source - will be set at the end
                if key == '_source':
                    continue
                
                merged_data[key] = value
        
        # Determine primary (highest priority) source
        primary = max(sources, key=lambda s: cls.SOURCE_PRIORITY.get(s, 1))

        merged_data['_source'] = primary
        merged_data['_sources'] = sorted(sources)  # optional provenance

        return ResolvedAsset(
            canonical_data=merged_data,
            source=primary
        )
    
    @staticmethod
    def _is_generic_name(name: Optional[str]) -> bool:
        """Check if name is generic/placeholder."""
        if not name:
            return True
        lower = name.lower()
        return (
            lower.startswith('device-') or
            lower.startswith('unknown') or
            lower == '_gateway' or
            len(lower) < 3
        )