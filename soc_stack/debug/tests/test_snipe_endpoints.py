#!/usr/bin/env python3

"""
Debug API endpoints.
"""

from soc_stack.snipe_it.snipe_api.snipe_client import SnipeClient

endpoints = [
    ('/api/v1/hardware', 'Assets'),
    ('/api/v1/models', 'Models'),
    ('/api/v1/manufacturers', 'Manufacturers'),
    ('/api/v1/statuslabels', 'Status Labels'),
    ('/api/v1/categories', 'Categories'),
    ('/api/v1/locations', 'Locations'),
    ('/api/v1/users', 'Users'),
    ('/api/v1/licenses', 'Licenses'),
    ('/api/v1/fields', 'Fields'),
    ('/api/v1/fieldsets', 'Fieldsets'),
    ('/api/v1/companies', 'Companies'),
    ('/api/v1/accessories', 'Accessories'),
    ('/api/v1/components', 'Components'),
    ('/api/v1/consumables', 'Consumables'),
    ('/api/v1/suppliers', 'Suppliers'),
    ('/api/v1/groups', 'Groups'),
    ('/api/v1/departments', 'Departments'),
    ('/api/v1/reports/activity', 'Reports'),
    ('/api/v1/version', 'Misc'),
    ('/api/v1/settings/backups', 'Settings')
]

positive_results = []
negative_results = []

def check_endpoints():
    print("=== Snipe-IT Endpoint Check ===")
    client = SnipeClient()
    
    print("1. Testing API connections...")
    for endpoint, name in endpoints:
        print(f"Checking {name} endpoint...")    
        try:
            response = client.make_api_request("GET", endpoint)
            if response and response.status_code == 200:
                data = response.json()
                info = "✓"
                if isinstance(data, dict) and 'total' in data:
                    info = f"✓ ({data['total']} items)"
                
                positive_results.append((name, info, response.status_code))
            else:
                negative_results.append((name, "✗ ", response.status_code))
        except Exception as e:
            negative_results.append((name, f"✗ EXCEPTION: {e}", "N/A"))

check_endpoints()
print("Successful Endpoints: ", positive_results)
print("Failed Endpoints: ", negative_results)