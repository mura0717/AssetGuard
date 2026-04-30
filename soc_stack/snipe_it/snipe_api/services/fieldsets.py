"""CRUD service for Snipe-IT fieldsets"""

from typing import List, Dict

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService
from soc_stack.snipe_it.snipe_api.services.fields import FieldService

class FieldsetService(CrudBaseService):
    """Service for managing fieldsets"""
    
    def __init__(self):
        super().__init__('/api/v1/fieldsets', 'fieldset')
        self.field_service = FieldService()
    
    def get_fields(self, fieldset_id: int) -> List[Dict]:
        """Get all fields in a fieldset"""
        response = self.client.make_api_request("GET", f"{self.endpoint}/{fieldset_id}/fields")
        if response:
            return response.json().get("rows", [])
        return []
    
    def setup_fieldset_associations(self, fieldset_name: str, field_keys: List[str], 
                                   field_definitions: Dict) -> int:
        """Setup all field associations for a fieldset"""
        fieldset = self.get_by_name(fieldset_name)
        if not fieldset:
            print(f"Warning: Fieldset '{fieldset_name}' not found")
            return 0
        
        fieldset_id = fieldset['id']
        all_fields = self.field_service.get_map()
        associations_made = 0
        
        for field_key in field_keys:
            field_def = field_definitions.get(field_key, {})
            field_name = field_def.get('name')
            
            if not field_name:
                continue
            
            field_id = all_fields.get(field_name)
            if not field_id:
                continue
            
            if self.field_service.associate_to_fieldset(field_id, fieldset_id):
                associations_made += 1
        
        return associations_made