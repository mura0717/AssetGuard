#!/usr/bin/env python3
"""
Deletes a specific category from Snipe-IT.

This script is designed for cleanup and maintenance. It will prompt for
confirmation before deleting any assets.
"""

import os
import sys
import urllib3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from soc_stack.snipe_it.snipe_api.services.categories import CategoryService
from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

# Suppress InsecureRequestWarning for self-signed certs if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def delete_category(category_name: str):
    
    category_service = CategoryService()

    print(f"Searching for category: '{category_name}'...")
    category = category_service.get_by_name(category_name)

    if not category:
        print(f"✗ Category '{category_name}' not found. Nothing to do.")
        return

    print(f"✓ Found category '{category_name}' (ID: {category['id']}).")

    if category_service.delete(category['id']) or category_service.delete_by_name(category_name):
        print(f"✓ Successfully soft-deleted category: '{category_name}'")
        print("\n--- Purging soft-deleted record from the database ---")
        CrudBaseService.purge_deleted_via_db()
        print("Purging completed.")
    else:
        print(f"✗ Failed to delete category '{category_name}'. It might be protected if assets are still assigned to it.")

if __name__ == "__main__":
    TARGET_CATEGORY = "Software Licenses"
    delete_category(TARGET_CATEGORY)
