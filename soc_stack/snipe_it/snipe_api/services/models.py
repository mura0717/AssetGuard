"""CRUD service for Snipe-IT asset models"""

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

class ModelService(CrudBaseService):
    """Service for managing asset models"""
    
    def __init__(self):
        super().__init__('/api/v1/models', 'model')
        
    
