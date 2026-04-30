"""CRUD service for Snipe-IT locations"""

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

class LocationService(CrudBaseService):
    """Service for managing locations"""
    
    def __init__(self):
        super().__init__('/api/v1/locations', 'location')