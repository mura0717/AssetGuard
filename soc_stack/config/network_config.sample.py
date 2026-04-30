"""
Default Nmap Scan Ranges
A list of CIDR network ranges for the Nmap scanner to use by default.
These should cover all subnets where assets might be found.
"""

NMAP_SCAN_RANGES = [
    # Example Scan Range - 
    #"192.168.1.0/24",    # Main Office
    #"10.10.0.0/22",      # Branch Office
    #"172.16.20.0/24"     # Guest Wifi
]

"""
DHCP Scope for Locations
"""
DHCP_SCOPES = [
    # Example DHCP Scope config:
    # {
    #     'start_ip': '192.168.1.100',
    #     'end_ip': '192.168.1.200',
    #     'location': 'HQ',
    #     'notes': 'Main client DHCP scope for the HQ location.'
    # },
]

"""
Physical Locations for Snipe-IT
These locations will be automatically populated in Snipe-IT during setup.
"""
LOCATIONS = [
    # "HQ",
    # "Branch Office"
]

"""
Static IP Address Mapping
This is the highest priority mapping. If an asset's IP is found here,
these values will be used for categorization and naming.
"""

STATIC_IP_MAP = {
    # Example Static IP MAP:
    # Routers
    #'192.168.1.1': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'ISP Router', 'manufacturer': 'Generic', 'model': 'Router', 'services': '', 'location': 'HQ', 'placement': 'Server Room'},

    # Servers & Virtual Machines
    #'192.168.1.100': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Domain Controller', 'manufacturer': 'Generic', 'model': 'Virtual Server', 'services': 'Active Directory, DNS', 'location': 'HQ', 'placement': 'Hypervisor Cluster'},
}