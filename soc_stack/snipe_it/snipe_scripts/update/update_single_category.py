#!/usr/bin/env python3
"""
Updates a specific category from Snipe-IT.
"""

import urllib3

from soc_stack.snipe_it.snipe_api.services.categories import CategoryService
from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

# Suppress InsecureRequestWarning for self-signed certs if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_category(category_name: str, fields_to_update: dict = None):    
    category_service = CategoryService()

    print(f"Searching for category: '{category_name}'...")
    category = category_service.get_by_name(category_name)

    if not category:
        print(f"✗ Category '{category_name}' not found. Nothing to do.")
        return

    print(f"✓ Found category '{category_name}' (ID: {category['id']}).")
    
    payload = fields_to_update or {}
    if not payload:
        print("No fields to update were provided. Nothing to do.")
        return

    if category_service.update(category['id'], payload):
        print(f"✓ Successfully updated category: '{category_name}' to {payload.get('name')}")
    else:
        print(f"✗ Failed to update category '{category_name}'. It might be protected if assets are still assigned to it.")

if __name__ == "__main__":
    TARGET_CATEGORY = "Virtual Machines On-Premises"
    FIELDS_TO_UPDATE = {
        "name": "Virtual Machines",
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False,
        }
    update_category(TARGET_CATEGORY, FIELDS_TO_UPDATE)
