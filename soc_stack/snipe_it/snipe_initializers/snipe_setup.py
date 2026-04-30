#!/usr/bin/env python3
"""
Snipe-IT Setup Script
Initializes Snipe-IT with custom fields, fieldsets, status labels, categories, and locations
"""

import argparse
import time

from soc_stack.snipe_it.snipe_initializers.snipe_reset_utility import SnipeResetManager
from soc_stack.snipe_it.snipe_api.services.fields import FieldService
from soc_stack.snipe_it.snipe_api.services.fieldsets import FieldsetService
from soc_stack.snipe_it.snipe_api.services.manufacturers import ManufacturerService
from soc_stack.snipe_it.snipe_api.services.models import ModelService
from soc_stack.snipe_it.snipe_api.services.status_labels import StatusLabelService
from soc_stack.snipe_it.snipe_api.services.categories import CategoryService
from soc_stack.snipe_it.snipe_api.services.locations import LocationService
from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService
from soc_stack.config.snipe_schema import CUSTOM_FIELDS, CUSTOM_FIELDSETS, STATUS_LABELS, CATEGORIES, MANUFACTURERS, MODELS, LOCATIONS

class SnipeITSetup:
    """Main setup class for Snipe-IT configuration"""
    
    def __init__(self):
        self.field_service = FieldService()
        self.fieldset_service = FieldsetService()
        self.status_service = StatusLabelService()
        self.category_service = CategoryService()
        self.model_service = ModelService()
        self.manufacture_service = ManufacturerService()
        self.location_service = LocationService()
    
    def setup_all(self):
        """Run complete setup"""
        print("=" * 60)
        print("Starting Snipe-IT Setup")
        print("=" * 60)
        
        self.setup_status_labels()
        self.setup_categories()
        self.setup_locations()
        self.setup_manufacturers()
        
        self.setup_fields()
        self.setup_fieldsets()
        self.associate_fields_to_fieldsets()
        
        self.setup_models()
        
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
    
    def setup_status_labels(self):
        """Create all status labels"""
        print("\n--- Setting up Status Labels ---")
        created, skipped = 0, 0
        
        for label_name, config in STATUS_LABELS.items():
            payload = {
                "name": label_name,
                "color": config.get("color", "#FFFFFF"),
                "type": config.get("type", "deployable"),
                "show_in_nav": config.get("show_in_nav", False),
                "default_label": config.get("default_label", False)
            }
            result = self.status_service.create_if_not_exists(payload)
            if result:
                created += 1
            else:
                skipped += 1
        
        print(f"✓ Status Labels: {created} created, {skipped} already existed")
    
    def setup_categories(self):
        """Create all categories"""
        print("\n--- Setting up Categories ---")
        created, skipped = 0, 0
        
        for category_name, config in CATEGORIES.items():
            payload = {
                "name": category_name,
                "category_type": config.get("category_type", "asset"),
                "use_default_eula": config.get("use_default_eula", False),
                "require_acceptance": config.get("require_acceptance", False),
                "checkin_email": config.get("checkin_email", False)
            }
            result = self.category_service.create_if_not_exists(payload)
            if result:
                created += 1
            else:
                skipped += 1
        
        print(f"✓ Categories: {created} created, {skipped} already existed")
    
    def setup_locations(self):
        """Create all locations"""
        print("\n--- Setting up Locations ---")
        created, skipped = 0, 0
        
        for location_name in LOCATIONS:
            result = self.location_service.create_if_not_exists({"name": location_name})
            if result:
                created += 1
            else:
                skipped += 1
        
        print(f"✓ Locations: {created} created, {skipped} already existed")
    
    def setup_manufacturers(self):
        """Create all common manufacturers"""
        print("\n--- Setting up Manufacturers ---")
        created, skipped = 0, 0
        for manufacturer_data in MANUFACTURERS:
            result = self.manufacture_service.create_if_not_exists({"name": manufacturer_data['name']})
            if result:
                created += 1
            else:
                skipped += 1
                
        print(f"✓ Manufacturers: {created} created, {skipped} already existed")
        
    def setup_models(self):
        """Create default model if not exists"""
        print("\n--- Setting up Default Models ---")
        created, skipped = 0, 0
        
        for model_data in MODELS:
            mfr = self.manufacture_service.get_by_name(model_data['manufacturer'])
            cat = self.category_service.get_by_name(model_data['category'])
            
            if mfr and cat:
                fieldset = self._determine_fieldset_for_category(model_data['category'])
                
                payload = {
                    "name": model_data['name'],
                    "manufacturer_id": mfr['id'],
                    "category_id": cat['id'],
                    "model_number": model_data.get('model_number', ''),
                }
                
                if fieldset:
                    payload['fieldset_id'] = fieldset['id']
                else:
                    print(f"  ⚠ Warning: Could not find target fieldset for model {model_data['name']}")

                result = self.model_service.create_if_not_exists(payload)
                if result:
                    created += 1
                else:
                    skipped += 1
            else:
                if not mfr:
                    print(f"  ✗ Manufacturer '{model_data['manufacturer']}' not found for model '{model_data['name']}'.")
                if not cat:
                    print(f"  ✗ Category '{model_data['category']}' not found for model '{model_data['name']}'.")
                
        print(f"✓ Models: {created} created, {skipped} already existed")
    
    def _determine_fieldset_for_category(self, category_name: str) -> dict:
        """Helper: Map category name to fieldset object"""
        fieldset_name = "Managed and Discovered Assets" # Default
        
        if category_name in ['Switches', 'Routers', 'Firewalls', 'Access Points', 'Cameras', 'Network Devices']:
            fieldset_name = "Network Infrastructure"
        elif category_name == 'Printers':
            fieldset_name = "Discovered Assets (Nmap Only)"
        elif category_name == 'Cloud Resources':
            fieldset_name = "Cloud Resources (Azure)"
        elif category_name in ['Mobile Phones', 'Tablets']:
            fieldset_name = "Mobile Devices"
            
        return self.fieldset_service.get_by_name(fieldset_name)
    
    def setup_fields(self):
        """Create all custom fields"""
        print("\n--- Setting up Custom Fields ---")
        created, skipped = 0, 0
        
        for field_key, field_data in CUSTOM_FIELDS.items():
            result = self.field_service.create_if_not_exists(field_data)
            if result:
                created += 1
            else:
                skipped += 1
        
        print(f"✓ Fields: {created} created, {skipped} already existed")
    
    def setup_fieldsets(self):
        """Create all fieldsets"""
        print("\n--- Setting up Fieldsets ---")
        created, skipped = 0, 0
        
        for fieldset_name in CUSTOM_FIELDSETS.keys():
            result = self.fieldset_service.create_if_not_exists({"name": fieldset_name})
            if result:
                created += 1
            else:
                skipped += 1
        
        print(f"✓ Fieldsets: {created} created, {skipped} already existed")
    
    def associate_fields_to_fieldsets(self):
        """Associate fields with their fieldsets"""
        print("\n--- Associating Fields with Fieldsets ---")
        total_associations = 0
        
        for fieldset_name, field_keys in CUSTOM_FIELDSETS.items():
            associations = self.fieldset_service.setup_fieldset_associations(
                fieldset_name, field_keys, CUSTOM_FIELDS
            )
            total_associations += associations
            print(f"  ✓ {fieldset_name}: {associations} fields associated")
        
        print(f"✓ Total associations created: {total_associations}")
    
    
    def cleanup_all(self):
        """Remove all custom configuration using efficient DB methods."""
        print("=" * 60)
        print("Starting Cleanup (DB Method)")
        print("=" * 60)
        
        SnipeResetManager.full_reset(skip_confirmation=True)
        
        print("\n" + "=" * 60)
        print("Cleanup Complete!")
        print("=" * 60)
    
    def cleanup_assets(self):
        """Delete all assets using DB method."""
        print("\n--- Cleaning up Assets ---")
        deleted = CrudBaseService.bulk_delete_all_assets()
        print(f"✓ Deleted {deleted} assets")
        return deleted
    
    def cleanup_fields(self):
        """Delete all custom fields"""
        print("\n--- Cleaning up Custom Fields ---")
        deleted = CrudBaseService.bulk_delete_all_custom_fields()
        print(f"✓ Deleted {deleted} fields")
        return deleted
    
    def cleanup_fieldsets(self):
        """Delete all fieldsets"""
        print("\n--- Cleaning up Fieldsets ---")
        deleted = CrudBaseService.bulk_delete_all_custom_fieldsets()
        print(f"✓ Deleted {deleted} fieldsets")
        return deleted
        
    def cleanup_manufacturers(self):
        """Delete all manufacturers"""
        print("\n--- Cleaning up Manufacturers ---")
        deleted = CrudBaseService.bulk_delete_all_manufacturers()
        print(f"✓ Deleted {deleted} manufacturers")
        return deleted
    
    def cleanup_models(self):
        """Delete all models"""
        print("\n--- Cleaning up Models ---")
        deleted = CrudBaseService.bulk_delete_all_models()
        print(f"✓ Deleted {deleted} models")
        return deleted
    
    def cleanup_status_labels(self):
        """Delete all status labels"""
        print("\n--- Cleaning up Status Labels ---")
        deleted = CrudBaseService.bulk_delete_all_status_labels()
        print(f"✓ Deleted {deleted} status labels")
        return deleted
    
    def cleanup_categories(self):
        """Delete all categories"""
        print("\n--- Cleaning up Categories ---")
        deleted = CrudBaseService.bulk_delete_all_categories()
        print(f"✓ Deleted {deleted} categories")
        return deleted
    
    def cleanup_locations(self):
        """Delete all locations"""
        print("\n--- Cleaning up Locations ---")
        deleted = CrudBaseService.bulk_delete_all_locations()
        print(f"✓ Deleted {deleted} locations")
        return deleted
        
    def purge_all(self):
        """
        Purges all soft-deleted records by calling the official Snipe-IT artisan command.
        This should be run AFTER all cleanup operations.
        """
        print("\n--- Purging all deleted ---")
        CrudBaseService.purge_deleted_via_db()
        print(f"✓ Purged all deleted records")
        

def main():
    parser = argparse.ArgumentParser(description='Snipe-IT Setup Tool')
    parser.add_argument('action', 
                        choices=['setup', 'cleanup', 'reset'],
                        nargs='?', 
                        default='reset',
                        help='Action to perform (defaults to "reset")')
    args = parser.parse_args()
    
    setup = SnipeITSetup()
    
    if args.action == 'setup':
        # To prevent issues, a setup should always start from a clean slate.
        # We will run the same logic as 'reset'.
        print("INFO: 'setup' action runs a full reset to ensure a clean environment.")
        setup.cleanup_all()
        setup.purge_all()
        setup.setup_all()
    elif args.action == 'cleanup':
        setup.cleanup_all()
    elif args.action == 'reset':
        setup.cleanup_all()
        setup.purge_all()
        print("\n" + "=" * 60)
        print("Waiting before setup...")
        print("=" * 60)
        time.sleep(3)
        setup.setup_all()

if __name__ == "__main__":
    main()