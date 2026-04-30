"""Base CRUD service for Snipe-IT entities"""

import os
import subprocess
import time
import threading
import subprocess
from typing import Dict, List, Optional

from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient
from soc_stack.utils.text_utils import normalize_for_comparison, normalize_for_display
from soc_stack.snipe_it.snipe_db.snipe_db_connect import SnipeItDbConnection


class CrudBaseService:
    """Base class for CRUD operations on Snipe-IT entities"""
    
    # Class-level rate limiting
    _rate_lock = threading.Lock()
    _last_request_time = 0.0
    _min_request_interval = 0.5
    
    def __init__(self, endpoint: str, entity_name: str):
        self.client = SnipeClient()
        self.endpoint = endpoint
        self.entity_name = entity_name
        self._cache = {}
        
    # =========================================================================
    # RATE LIMITING
    # =========================================================================
        
    @classmethod
    def set_rate_limit(cls, requests_per_second: float):
        """Configure global rate limit for all CRUD operations."""
        cls._min_request_interval = 1.0 / requests_per_second
    
    @classmethod
    def _wait_for_rate_limit(cls):
        """Enforce rate limiting across all instances."""
        with cls._rate_lock:
            now = time.time()
            elapsed = now - cls._last_request_time
            if elapsed < cls._min_request_interval:
                time.sleep(cls._min_request_interval - elapsed)
            cls._last_request_time = time.time()
    
    # =========================================================================
    # READ OPERATIONS (API)
    # =========================================================================
    
    def get_all(self, limit: int = 500, refresh_cache: bool = False) -> List[Dict]:
        """Get all entities"""
        if not refresh_cache and 'all' in self._cache:
            return self._cache['all']
        all_rows = []
        offset = 0
        
        while True:
            response = self.client.make_api_request(
                "GET", 
                self.endpoint, 
                params={"limit": limit, "offset": offset}
            )
            
            if not response:
                break
                
            try:
                js = response.json()
            except ValueError:
                break

            rows = js.get("rows", [])
            if not rows:
                break
                
            all_rows.extend(rows)
            
            total = js.get("total")
            if total and len(all_rows) >= int(total):
                break
            
            if len(rows) < limit:
                break
                
            offset += limit
            
        self._cache['all'] = all_rows
        return all_rows
    
    def get_by_id(self, entity_id: int) -> Optional[Dict]:
        """Get entity by ID"""
        response = self.client.make_api_request("GET", f"{self.endpoint}/{entity_id}")
        return response.json() if response else None
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """Get entity by name (normalized)"""
        if not name:
            return None
        normalized_search_name = normalize_for_comparison(name)
        all_entities = self.get_all()
        for entity in all_entities:
            entity_name = entity.get('name')
            if not entity_name:
                continue
            normalized_entity_name = normalize_for_comparison(entity_name)
            if normalized_entity_name == normalized_search_name:
                return entity
        return None
    
    def get_map(self, key: str = 'name', value: str = 'id') -> Dict:
        """Get dictionary mapping"""
        all_entities = self.get_all()
        return {entity.get(key): entity.get(value) for entity in all_entities}
    
    # =========================================================================
    # CREATE OPERATIONS (API - Always)
    # =========================================================================
    
    def create(self, data: Dict) -> Optional[Dict]:
        """Create new entity via API"""
        if not data:
            print(f"Cannot create {self.entity_name}: No data provided")
            return None
        if 'name' in data:
            data['name'] = normalize_for_display(data['name'])
        if 'model_number' in data:
            data['model_number'] = normalize_for_display(data['model_number'])
        
        self._wait_for_rate_limit()
        response = self.client.make_api_request("POST", self.endpoint, json=data)
        
        if not response:
            return None
        
        try:
            js = response.json()
            if isinstance(js, dict):
                if js.get("status") == "success":
                    self._cache.clear()
                    return js.get("payload", js)
                elif js.get("status") == "error":
                    print(f"[CREATE ERROR] {self.entity_name}: {js.get('messages')}")
                    self._cache.clear() 
                    return None
            return js
        except Exception as e:
            self._cache.clear() 
            print(f"[CREATE ERROR] Failed to parse response: {e}")
            return None

    def create_if_not_exists(self, data: Dict) -> bool:
        """Create entity only if it doesn't exist"""
        name = data.get('name')
        if not name:
            print(f"Error: No name provided for {self.entity_name}")
            return False
        
        if self.get_by_name(name):
            print(f"{self.entity_name.title()} '{name}' already exists")
            return False
        
        result = self.create(data)
        if result:
            print(f"Created {self.entity_name}: {name}")
            return True
        return False
    
    def get_or_create(self, data: Dict) -> Optional[Dict]:
        """Get or create entity"""
        name = data.get('name')
        if not name:
            print(f"Error: No name provided for {self.entity_name}")
            return None
        
        existing = self.get_by_name(name)
        if existing:
            return existing
        
        return self.create(data)
    
    # =========================================================================
    # UPDATE OPERATIONS (API - Always)
    # =========================================================================
    
    def update(self, entity_id: int, data: Dict) -> Optional[Dict]:
        """Update entity by ID"""
        self._wait_for_rate_limit()
        response = self.client.make_api_request("PATCH", f"{self.endpoint}/{entity_id}", json=data)
        if not response:
            return None
        js = response.json()
        if isinstance(js, dict) and js.get("status") == "error":
            print(f"[UPDATE ERROR] {self.entity_name}: {js.get('messages')}")
            return None
        self._cache.clear()
        return js
    
    # =========================================================================
    # DELETE OPERATIONS - HYBRID APPROACH
    # =========================================================================
    
    def delete(self, entity_id: int, refresh_cache: bool = False) -> bool:
        """Delete entity by ID via API (soft delete)"""
        self._wait_for_rate_limit()
        response = self.client.make_api_request("DELETE", f"{self.endpoint}/{entity_id}")
        if response and response.ok:
            if refresh_cache:
                self._cache.clear()
            return True
        return False
    
    def delete_by_name(self, name: str) -> bool:
        """Delete entity by name"""
        entity = self.get_by_name(name)
        if entity:
            return self.delete(entity['id'])
        return False
    
    def batch_delete_api(self, ids: List[int], 
                         requests_per_second: float = 2.0,
                         show_progress: bool = True) -> int:
        """
        Delete multiple entities via API with rate limiting.
        For bulk/reset operations, use batch_delete_db() instead.
        """
        if not ids:
            return 0
        
        old_interval = self._min_request_interval
        self._min_request_interval = 1.0 / requests_per_second
        
        deleted = 0
        total = len(ids)
        
        print(f"Deleting {total} {self.entity_name}s via API at {requests_per_second} req/s...")
        
        try:
            for i, entity_id in enumerate(ids, 1):
                if self.delete(entity_id, refresh_cache=False):
                    deleted += 1
                
                if show_progress and (i % 50 == 0 or i == total):
                    print(f"  Progress: {i}/{total} ({(i/total)*100:.1f}%)")
        finally:
            self._min_request_interval = old_interval
            self._cache.clear()  # Clear cache once at end
        
        return deleted

    # =========================================================================
    # BULK DELETE OPERATIONS (Direct DB - For Reset/Cleanup)
    # =========================================================================
    
    @staticmethod
    def bulk_soft_delete_table(table_name: str) -> int:
        """
        Soft-delete all records in a table via direct DB - faster than API for bulk operations.
        """
        from datetime import datetime
        
        db_manager = SnipeItDbConnection()
        connection = None
        
        try:
            connection = db_manager.db_connect()
            if not connection:
                print(f"✗ Cannot soft-delete {table_name}: DB connection failed")
                return 0
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with connection.cursor() as cursor:
                # Count existing non-deleted records
                cursor.execute(
                    f"SELECT COUNT(*) as cnt FROM `{table_name}` WHERE deleted_at IS NULL"
                )
                count = cursor.fetchone()['cnt']
                
                if count == 0:
                    print(f"  No {table_name} to delete.")
                    return 0
                
                # Soft-delete all
                cursor.execute(
                    f"UPDATE `{table_name}` SET deleted_at = %s WHERE deleted_at IS NULL",
                    (now,)
                )
                
                connection.commit()
                print(f"  ✓ Soft-deleted {count} records from {table_name}")
                return count
                
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"  ✗ Error soft-deleting {table_name}: {e}")
            return 0
        finally:
            if connection:
                db_manager.db_disconnect(connection)
    
    @staticmethod
    def bulk_delete_all_assets() -> int:
        """Soft-delete all assets via DB. Use for reset scenarios."""
        return CrudBaseService.bulk_soft_delete_table('assets')
    
    @staticmethod
    def bulk_delete_all_models() -> int:
        """Soft-delete all models via DB."""
        return CrudBaseService.bulk_soft_delete_table('models')
    
    @staticmethod
    def bulk_delete_all_categories() -> int:
        """Soft-delete all categories via DB."""
        return CrudBaseService.bulk_soft_delete_table('categories')
    
    @staticmethod
    def bulk_delete_all_manufacturers() -> int:
        """Soft-delete all manufacturers via DB."""
        return CrudBaseService.bulk_soft_delete_table('manufacturers')
    
    @staticmethod  
    def bulk_delete_all_custom_fields() -> int:
        """Soft-delete all custom fields via DB."""
        return CrudBaseService.bulk_soft_delete_table('custom_fields')
    
    @staticmethod
    def bulk_delete_all_custom_fieldsets() -> int:
        """Soft-delete all custom fieldsets via DB."""
        return CrudBaseService.bulk_soft_delete_table('custom_fieldsets')
    
    @staticmethod
    def bulk_delete_all_status_labels() -> int:
        """Soft-delete all status labels via DB."""
        return CrudBaseService.bulk_soft_delete_table('status_labels')
    
    @staticmethod
    def bulk_delete_all_locations() -> int:
        """Soft-delete all locations via DB."""
        return CrudBaseService.bulk_soft_delete_table('locations')
    
    # =========================================================================
    # PURGE & TRUNCATE (Direct DB)
    # =========================================================================
    
    @staticmethod
    def purge_deleted_via_db():
        """
       Purge all soft-deleted records via artisan command.
        """
        snipe_it_path = os.getenv('SNIPE_IT_APP_PATH', '/var/www/snipe-it')
        if not os.path.isdir(snipe_it_path):
            print(f"✗ ERROR: Snipe-IT path '{snipe_it_path}' not found. Running snipeit:purge via SSH.")
            CrudBaseService.purge_deleted_via_db_ssh()
            return

        command = ['php', 'artisan', 'snipeit:purge', '--force']
        
        print(f"-> Running official Snipe-IT purge command: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                cwd=snipe_it_path,
                capture_output=True, text=True, check=True,
                input='yes\n' # We pipe 'yes' to automatically confirm the prompt.
            )
            output = result.stdout.strip()
            if output:
                print(f"  {output.replace(chr(10), chr(10) + '  ')}")
            print("  ✓ Purge completed")
        except FileNotFoundError:
            print("✗ ERROR: 'php' command not found. Trying SSH...")
            CrudBaseService.purge_deleted_via_db_ssh()
        except subprocess.CalledProcessError as e:
            print(f"✗ Purge failed:")
            print(f"  Return Code: {e.returncode}")
            print(f"  Output:\n{e.stdout}")
            print(f"  Error Output:\n{e.stderr}")
            
    @staticmethod
    def purge_deleted_via_db_ssh():
        """Purges soft-deleted records via SSH."""
        db_conn = SnipeItDbConnection()
        
        if not db_conn.db_ssh_user or not db_conn.db_host or not db_conn.db_ssh_key_path:
            print("✗ Cannot purge via SSH: Missing SSH configuration.")
            return

        ssh_cmd = [
            "ssh",
            "-i", db_conn.db_ssh_key_path,
            "-o", "StrictHostKeyChecking=no",
            "-o", "BatchMode=yes",  # Forces immediate failure if auth is missing
            "-o", "ConnectTimeout=10",
            f"{db_conn.db_ssh_user}@{db_conn.db_host}",
            "cd /var/www/snipe-it && php artisan snipeit:purge --force"
        ]
        
        print(f"-> Executing SSH command: {' '.join(ssh_cmd)}")
        
        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True, input='yes\n')
            output = result.stdout.strip()
            if output:
                print(f"  {output.replace(chr(10), chr(10) + '  ')}")
            print("  ✓ Remote purge completed")
        except subprocess.CalledProcessError as e:
            print(f"✗ Remote purge failed:")
            print(f"  Error: {e.stderr}")
        
    @staticmethod
    def _drop_custom_fields_columns(connection, db_name):
        """
        Drops all columns in the 'assets' table that start with '_snipeit_'.
        This cleans up the schema so custom fields can be recreated from ID 1.
        """
        print("  -> Cleaning up 'assets' table schema (dropping '_snipeit_' columns)...")
        try:
            with connection.cursor() as cursor:
                # Find the columns
                # NOTE: We use %% for wildcard because PyMySQL uses % for parameter substitution
                sql_find = """
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_NAME = 'assets' 
                    AND COLUMN_NAME LIKE '_snipeit_%%'
                """
                cursor.execute(sql_find, (db_name,))
                columns = [row['COLUMN_NAME'] for row in cursor.fetchall()]
                
                if not columns:
                    print("    - No ghost columns found.")
                    return

                print(f"    - Found {len(columns)} ghost columns. Dropping...")
                
                for col in columns:
                    cursor.execute(f"ALTER TABLE `assets` DROP COLUMN `{col}`")
                
                print("    - Schema cleanup complete.")
                
        except Exception as e:
            print(f"  ✗ Error dropping custom columns: {e}")
            raise e
        
    @staticmethod
    def truncate_tables(table_names: List[str], force: bool = False) -> bool:
        """
        Truncates tables AND cleans up asset schema.
        """
        if not table_names:
            print("No tables specified for truncation.")
            return False

        db_manager = SnipeItDbConnection()
        connection = None
        
        if not force:
            print(f"\nWARNING: This will permanently delete all data from: {', '.join(table_names)}")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Cancelled.")
                return False

        try:
            connection = db_manager.db_connect()
            if not connection:
                print("✗ Could not proceed due to connection failure.")
                return False

            with connection.cursor() as cursor:
                print("  -> Disabling foreign key checks...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

                for table in table_names:
                    print(f"  -> Truncating table: `{table}`...")
                    cursor.execute(f"TRUNCATE TABLE `{table}`;")
                
                CrudBaseService._drop_custom_fields_columns(connection, db_manager.db_name)

                print("  -> Re-enabling foreign key checks...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            
            connection.commit()
            print("✓ Database truncation and schema cleanup complete.")
            return True
        
        except Exception as e:
            print(f"✗ An unexpected error occurred: {e}")
            return False
        
        finally:
            if connection:
                db_manager.db_disconnect(connection)

    @staticmethod
    def truncate_all(force: bool = False) -> bool:
        """Truncates all relevant tables."""
        all_tables = [
            'assets', 'models', 'manufacturers', 'categories', 'custom_fieldsets',
            'custom_fields', 'status_labels', 'locations', 'accessories',
            'components', 'consumables', 'licenses',
            'custom_field_custom_fieldset', 
            'action_logs',
        ]
        return CrudBaseService.truncate_tables(all_tables, force=force)