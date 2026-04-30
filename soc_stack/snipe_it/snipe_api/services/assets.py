"""CRUD service for Snipe-IT assets"""

from typing import Dict, Optional, List

from soc_stack.snipe_it.snipe_api.services.crudbase import CrudBaseService


class AssetService(CrudBaseService):
    """Service for managing categories"""
    
    def __init__(self):
        super().__init__('/api/v1/hardware', 'hardware')
        
    def search_by_serial(self, serial: str) -> Optional[Dict]:
        resp = self.client.make_api_request("GET", f"{self.endpoint}/byserial/{serial}")
        if not resp:
            return None
        js = resp.json()
        if isinstance(js, dict):
            if js.get("rows"):
                return js["rows"][0]
            if js.get("id"):
                return js
        return None
    
    def search_by_asset_tag(self, asset_tag: str) -> Optional[Dict]:
        """Search for asset by asset tag"""
        response = self.client.make_api_request("GET", f"{self.endpoint}/bytag/{asset_tag}")
        if response and response.json().get("id"):
            return response.json()
        return None
    
    def get_all(self, limit: int = 10000, refresh_cache: bool = True) -> List[Dict]:
        """Get all assets, with optional cache refresh"""
        response = self.client.make_api_request("GET", f"{self.endpoint}?limit={limit}&refresh_cache={'true' if refresh_cache else 'false'}")
        if response:
            return response.json().get("rows", []) if response else []
        return []