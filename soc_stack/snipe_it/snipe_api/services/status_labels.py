"""CRUD service for Snipe-IT status labels"""

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService

class StatusLabelService(CrudBaseService):
    """Service for managing status labels"""
    
    def __init__(self):
        super().__init__('/api/v1/statuslabels', 'status label')