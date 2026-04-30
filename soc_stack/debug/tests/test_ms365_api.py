#!/usr/bin/env python3

"""
Test Microsoft365 API connection.
"""

import requests

from soc_stack.config.ms365_service import Microsoft365Service 

class MS365APTConnectionTester:
    """Microsoft Intune synchronization service"""
    
    def __init__(self):
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self.beta_graph_url = "https://graph.microsoft.com/beta"
        self.ms365_service = Microsoft365Service() 
    
    def test_connection(self) -> bool:
        print("Testing connection to Microsoft365 API...")
        headers = self.ms365_service.get_connection()
        
        if not headers:
            print(" ✗ Failed to obtain connection headers (Authentication failed).")
            return False
        
        intune_url = f"{self.graph_url}/deviceManagement/managedDevices"
        teams_url = f"{self.beta_graph_url}/teamwork/devices"
        entra_url = f"{self.graph_url}/devices"
                
        try:
            response = requests.get(intune_url, headers=headers)
            response.raise_for_status()
            print(" ✓ Successfully connected to Intune API.")
            response = requests.get(teams_url, headers=headers)
            response.raise_for_status()
            print(" ✓ Successfully connected to Teams API.")
            response = requests.get(entra_url, headers=headers)
            response.raise_for_status()
            print(" ✓ Successfully connected to Entra ID API.")
            return True
        except requests.exceptions.RequestException as e:
            if 'response' in locals() and response is not None:
                    print(f" ✗ MS365 API Error - Response Status Code: {response.status_code}")
                    print(f" ✗ MS365 API Error - Response Body: {response.text}")
            return False

if __name__ == "__main__":
    ms365tester = MS365APTConnectionTester()
    ms365tester.test_connection()