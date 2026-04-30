#!/usr/bin/env python3
"""
Deletes a specific category from Snipe-IT.

This script is designed for cleanup and maintenance. It will prompt for
confirmation before deleting any assets.
"""

import urllib3

from soc_stack.snipe_it.snipe_api.services.fieldsets import FieldsetService
from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

# Suppress InsecureRequestWarning for self-signed certs if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def delete_fieldset(fieldset_name: str):
        
    fieldset_service = FieldsetService()
    
    print(f"Searching for fieldset: '{fieldset_name}'...")
    fieldset = fieldset_service.get_by_name(fieldset_name)

    if not fieldset:
        print(f"✗ fieldset '{fieldset_name}' not found. Nothing to do.")
        return

    print(f"✓ Found fieldset '{fieldset_name}' (ID: {fieldset['id']}).")

    if fieldset_service.delete(fieldset['id']) or fieldset_service.delete_by_name(fieldset_name):
        print(f"✓ Successfully soft-deleted fieldset: '{fieldset_name}'")
        print("\n--- Purging soft-deleted record from the database ---")
        CrudBaseService.purge_deleted_via_db()
        print("Purging completed.")
    else:
        print(f"✗ Failed to delete fieldset '{fieldset_name}'. It might be protected if assets are still assigned to it.")

if __name__ == "__main__":
    TARGET_FIELDSET = "Managed Assets (Intune+Nmap)"
    delete_fieldset(TARGET_FIELDSET)
