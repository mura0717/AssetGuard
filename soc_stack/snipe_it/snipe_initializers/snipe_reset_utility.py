#!/usr/bin/env python3
"""
snipe_reset.py - Efficient Snipe-IT Reset Utility

Provides fast bulk operations using direct DB access where appropriate,
with proper dependency ordering.
"""

import time
from typing import List, Callable
from dataclasses import dataclass

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService


@dataclass
class ResetStep:
    """Represents a single reset operation."""
    name: str
    delete_fn: Callable[[], int]
    purge_after: bool = True


class SnipeResetManager:
    """
    Manages Snipe-IT reset operations with proper dependency ordering.
    
    Deletion Order (respects foreign keys):
    1. Assets (depends on models)
    2. Models (depends on categories, manufacturers, fieldsets)
    3. Fieldsets + Field associations
    4. Custom Fields
    5. Categories, Manufacturers, Status Labels, Locations
    """
    
    # Ordered steps for full reset
    RESET_STEPS: List[ResetStep] = [
        ResetStep("Assets", CrudBaseService.bulk_delete_all_assets, purge_after=True),
        ResetStep("Models", CrudBaseService.bulk_delete_all_models, purge_after=True),
        ResetStep("Fieldsets", CrudBaseService.bulk_delete_all_custom_fieldsets, purge_after=False),
        ResetStep("Custom Fields", CrudBaseService.bulk_delete_all_custom_fields, purge_after=True),
        ResetStep("Categories", CrudBaseService.bulk_delete_all_categories, purge_after=False),
        ResetStep("Manufacturers", CrudBaseService.bulk_delete_all_manufacturers, purge_after=False),
        ResetStep("Status Labels", CrudBaseService.bulk_delete_all_status_labels, purge_after=False),
        ResetStep("Locations", CrudBaseService.bulk_delete_all_locations, purge_after=True),
    ]
    
    @classmethod
    def full_reset(cls, skip_confirmation: bool = False) -> dict:
        """
        Perform a complete reset of all Snipe-IT entities.
        
        Returns: {"total_deleted": n, "steps": [...]}
        """
        if not skip_confirmation:
            print("\n" + "!" * 60)
            print("WARNING: This will DELETE ALL data in Snipe-IT!")
            print("!" * 60)
            confirm = input("\nType 'DELETE ALL' to confirm: ")
            if confirm != 'DELETE ALL':
                print("Cancelled.")
                return {"total_deleted": 0, "cancelled": True}
        
        print("\n" + "=" * 60)
        print("SNIPE-IT FULL RESET")
        print("=" * 60)
        
        start_time = time.time()
        results = {"total_deleted": 0, "steps": []}
        
        for step in cls.RESET_STEPS:
            print(f"\n[Step] Deleting {step.name}...")
            
            try:
                count = step.delete_fn()
                results["steps"].append({"name": step.name, "deleted": count})
                results["total_deleted"] += count
                
                if step.purge_after and count > 0:
                    print(f"  Purging {step.name.lower()}...")
                    CrudBaseService.purge_deleted_via_db()
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results["steps"].append({"name": step.name, "error": str(e)})
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"RESET COMPLETE in {elapsed:.1f}s")
        print(f"Total records deleted: {results['total_deleted']}")
        print("=" * 60)
        
        return results
    
    @classmethod
    def delete_assets_only(cls) -> int:
        """Quick method to delete just assets."""
        print("\n--- Deleting all assets (DB method) ---")
        count = CrudBaseService.bulk_delete_all_assets()
        if count > 0:
            CrudBaseService.purge_deleted_via_db()
        return count
    
    @classmethod
    def delete_configuration_only(cls) -> dict:
        """
        Delete configuration (models, categories, etc.) but NOT assets.
        Useful for reconfiguring without losing asset data.
        """
        print("\n--- Deleting configuration entities ---")
        
        # Skip assets, start from models
        config_steps = cls.RESET_STEPS[1:]  
        
        results = {"deleted": 0}
        for step in config_steps:
            count = step.delete_fn()
            results["deleted"] += count
            if step.purge_after and count > 0:
                CrudBaseService.purge_deleted_via_db()
        
        return results

# Convenience functions for scripts
def reset_all(skip_confirmation: bool = False):
    """Full reset - delete everything."""
    return SnipeResetManager.full_reset(skip_confirmation)


def reset_assets():
    """Delete all assets only."""
    return SnipeResetManager.delete_assets_only()


def reset_configuration():
    """Delete configuration only (preserves assets)."""
    return SnipeResetManager.delete_configuration_only()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Snipe-IT Reset Utility')
    parser.add_argument('mode', choices=['all', 'assets', 'config'],
                        help='What to reset')
    parser.add_argument('--force', '-f', action='store_true',
                        help='Skip confirmation prompt')
    args = parser.parse_args()
    
    if args.mode == 'all':
        reset_all(skip_confirmation=args.force)
    elif args.mode == 'assets':
        reset_assets()
    elif args.mode == 'config':
        reset_configuration()