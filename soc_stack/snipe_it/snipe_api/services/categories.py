"""CRUD service for Snipe-IT categories"""

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

class CategoryService(CrudBaseService):
    """Service for managing categories"""
    
    def __init__(self):
        super().__init__('/api/v1/categories', 'category')