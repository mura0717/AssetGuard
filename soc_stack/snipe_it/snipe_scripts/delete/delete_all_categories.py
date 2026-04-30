""" Removes all categories for a clean start. """

import os
import sys
import urllib3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Suppress InsecureRequestWarning from urllib3 - unverified HTTPS requests 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

def delete_all_categories():
    print("\n" + "=" * 50)
    print("DELETING ALL CATEGORIES")
    print("=" * 50)
    
    count = CrudBaseService.bulk_delete_all_categories()
    
    if count > 0:
        print(f"\n✓ Soft-deleted {count} categories")
        print("\n--- Purging soft-deleted records ---")
        CrudBaseService.purge_deleted_via_db()
    else:
        print("No categories to delete.")
    
    print("=" * 50 + "\n")


if __name__ == "__main__":
    delete_all_categories()
 