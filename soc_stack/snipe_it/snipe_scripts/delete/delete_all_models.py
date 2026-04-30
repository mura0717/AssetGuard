""" Removes all models for a clean start. """

import urllib3

# Suppress InsecureRequestWarning from urllib3 - unverified HTTPS requests 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

def delete_all_models():
    print("\n" + "=" * 50)
    print("DELETING ALL MODELS")
    print("=" * 50)
    
    count = CrudBaseService.bulk_delete_all_models()
    
    if count > 0:
        print(f"\n✓ Soft-deleted {count} models")
        print("\n--- Purging soft-deleted records ---")
        CrudBaseService.purge_deleted_via_db()
    else:
        print("No models to delete.")
    
    print("=" * 50 + "\n")


if __name__ == "__main__":
    delete_all_models()
 