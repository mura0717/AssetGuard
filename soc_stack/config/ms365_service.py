# Configuration and constants for Microsoft365 setup

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# Configuration
AZURE_TENANT_ID= os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID= os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET= os.getenv("AZURE_CLIENT_SECRET")
AZURE_DEBUG = os.getenv('AZURE_DEBUG', '0') == '1'

if not AZURE_TENANT_ID or not AZURE_CLIENT_ID or not AZURE_CLIENT_SECRET:
    raise RuntimeError("Azure credentials not configured in environment.")

if AZURE_DEBUG:
    masked_secret = AZURE_CLIENT_SECRET[:5] + "..." if AZURE_CLIENT_SECRET else "None"
    print(f"[DEBUG] AZURE_TENANT_ID: {AZURE_TENANT_ID} " + f"AZURE_CLIENT_ID: {AZURE_CLIENT_ID} " + f"AZURE_CLIENT_SECRET: {masked_secret}")

import os
import sys
from msal import ConfidentialClientApplication

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Microsoft365Service:
    """Microsoft365 API service"""
    
    def __init__(self):
        self.tenant_id = AZURE_TENANT_ID
        self.client_id = AZURE_CLIENT_ID
        self.client_secret = AZURE_CLIENT_SECRET
        
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Azure credentials not configured in environment")
        
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.beta_graph_url = "https://graph.microsoft.com/beta"
        self.access_token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API"""
        try:
            app = ConfidentialClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_silent(
                ["https://graph.microsoft.com/.default"],
                account=None
            )
            
            if not result:
                result = app.acquire_token_for_client(
                    scopes=["https://graph.microsoft.com/.default"]
                )
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
            else:
                print(f"Authentication failed: {result.get('error_description')}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
        
    def get_access_token(self) -> Optional[str]:
        """Ensure valid access token."""
        if not self.access_token:
            if not self.authenticate():
                print("Authentication failed via Microsoft365 helper.")
                return None
        return self.access_token

    def get_connection(self, access_token: Optional[str] = None) -> Optional[Dict]:
        """Create connection headers."""
        token = access_token or self.get_access_token()
        if not token:
            print("No access token available.")
            return None
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_assets(self, access_token: Optional[str], endpoint: str, source: str) -> List[Dict]:
        """Fetch assets from Microsoft Graph."""
        headers = self.get_connection(access_token)
        if not headers:
            print(f"Cannot fetch {source} assets: No connection.")
            return []

        assets = []
        if source == "teams":
            endpoint = f"{self.beta_graph_url}/{endpoint}"
        else:
            endpoint = f"{self.graph_url}/{endpoint}"
        
        while endpoint:
            try:
                response = requests.get(endpoint, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('value'):
                    print(f"DEBUG: API call to {endpoint} returned an empty 'value' array.")
                    print(f"DEBUG: Full API Response: {json.dumps(data, indent=2)}")

                assets.extend(data.get('value', []))
                endpoint = data.get('@odata.nextLink')  # Handle pagination
                
            except requests.exceptions.RequestException as e:
                if 'response' in locals() and response is not None:
                    print(f"{source.capitalize()} API Error - Response Status Code: {response.status_code}")
                    print(f"{source.capitalize()} API Error - Response Body: {response.text}")
                print(f"Error fetching assets: {e}")
                break

        return assets