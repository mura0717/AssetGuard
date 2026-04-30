""" Removes all assets for a clean start. """

import urllib3

# Suppress InsecureRequestWarning from urllib3 - unverified HTTPS requests 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

def delete_all_assets():
    print("\n" + "=" * 50)
    print("DELETING ALL ASSETS")
    print("=" * 50)
    
    # Method 1: Direct DB (fastest, recommended for reset)
    count = CrudBaseService.bulk_delete_all_assets()
    
    if count > 0:
        print(f"\n✓ Soft-deleted {count} assets")
        print("\n--- Purging soft-deleted records ---")
        CrudBaseService.purge_deleted_via_db()
    else:
        print("No assets to delete.")
    
    print("=" * 50 + "\n")
    
if __name__ == "__main__":
    delete_all_assets()

 