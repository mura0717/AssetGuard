"""
Snipe-IT API Client
"""

import urllib3
import json
import time
import requests

from soc_stack.config.hydra_settings import SNIPE

# To suppress unverified HTTPS requests - Only when self-signed certs are used.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SnipeClient:
    """
    Client for interacting with the Snipe-IT API.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SNIPE.headers)
        self.session.verify = SNIPE.verify_ssl
    
    def make_api_request(self, method, endpoint, max_retries=3, timeout=30, **kwargs):
        """
        Make API request with retry logic
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/api/v1/fields")
            max_retries: Number of retries for failed requests
            **kwargs: Additional arguments for requests
        """
        
        url = f"{SNIPE.snipe_url}{endpoint}" if not endpoint.startswith(SNIPE.snipe_url) else endpoint
        total_attempts = max_retries + 1
        
        for attempt in range(total_attempts): # +1 to include initial attempt
            attempt_num = attempt + 1
            
            try:
                response = self.session.request(method, url, timeout=timeout, **kwargs)
                if response.status_code == 429:
                    if attempt < max_retries:
                        try:
                            error_data = response.json()
                            retry_after = int(error_data.get("retryAfter", 15)) + 1
                        except (ValueError, json.JSONDecodeError):
                            retry_after = 15
                        print(f"-> Rate limited on {method} {url}. "
                            f"Retrying in {retry_after}s... (Attempt {attempt_num}/{total_attempts})")
                        time.sleep(retry_after)
                        continue
                    else:
                        print(f"-> Max retries exceeded for {method} {url}. Returning 429 response.")
                        return response

                response.raise_for_status()
                return response

            except requests.exceptions.HTTPError as e:
                # Only retry on 5xx Server Errors
                if 500 <= e.response.status_code < 600 and attempt < max_retries:
                    print(f"-> Server error ({e.response.status_code}). "
                      f"Retrying in 10s... (Attempt {attempt_num}/{total_attempts})")
                    time.sleep(10)
                    continue
                raise

            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    print(f"-> Network error ({type(e).__name__}). "
                        f"Retrying in 10s... (Attempt {attempt_num}/{total_attempts})")
                    time.sleep(10)
                else:
                    print(f"-> Persistent network error after {total_attempts} attempts. Aborting.")
                    raise
    
        return None