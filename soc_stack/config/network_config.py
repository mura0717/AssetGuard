"""
Default Nmap Scan Ranges
A list of CIDR network ranges for the Nmap scanner to use by default.
These should cover all subnets where assets might be found.
"""
NMAP_SCAN_RANGES = [
    "192.168.1.0/24",    # Glostrup Main 
    "192.168.5.0/22",    # Glostrup Extended
    "192.168.200.0/24",  # Odense Main
    "172.20.20.0/24"     # Guest Wifi
]

"""
DHCP Scope for both Glostrup and Odense
"""
DHCP_SCOPES = [
    {
        'start_ip': '192.168.1.50',
        'end_ip': '192.168.1.150',
        'location': 'Glostrup',
        'notes': 'Main client DHCP scope for the Glostrup location.'
    },
    {
        'start_ip': '192.168.4.50',
        'end_ip': '192.168.7.250',
        'location': 'Glostrup',
        'notes': 'Extended client DHCP scope for the Glostrup location.'
    },
    {
        'start_ip': '192.168.200.50',
        'end_ip': '192.168.200.150',
        'location': 'Odense',
        'notes': 'Main client DHCP scope for the Odense location.'
    }
]

"""
Static IP Address Mapping
This is the highest priority mapping. If an asset's IP is found here,
these values will be used for categorization and naming.

Format: 'IP_ADDRESS': {'device_type': '...', 'category': '...', 'host_name': '...', 'services': '...', location': '...', 'placement': '...'}

device_type: Helps the categorizer select the right logic (e.g., 'Switch', 'Printer', 'Server').
category:    The final Snipe-IT category for the asset.
host_name:   The desired host_name for the asset in Snipe-IT.
services:    Services present on the host machine.
location:    The physical location host_name as defined in Snipe-IT.
placement:   Specific placement information (e.g., Rack U23, Room 101).
"""

STATIC_IP_MAP = {
    # --- Glostrup Location ---
    '192.168.1.1': {'device_type': 'Firewall', 'category': 'Firewalls', 'host_name': 'Meraki MX85 Gateway', 'manufacturer': 'Cisco', 'model': 'Meraki MX85', 'services': 'default gateway', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.2.1': {'device_type': 'Firewall', 'category': 'Firewalls', 'host_name': 'Meraki MX85 DMZ Gateway', 'manufacturer': 'Cisco', 'model': 'Meraki MX85', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.2': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Core switch Aruba 2930', 'manufacturer': 'HPE Aruba', 'model': '2930', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.9': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Server switch HP 1910-24G', 'manufacturer': 'HP', 'model': '1910-24G', 'services': 'HP 1910-24G', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.10': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G - 1', 'manufacturer': 'HP', 'model': '1920-24G', 'services': 'HP 1920-24G - 1', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.11': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G - 2', 'manufacturer': 'HP', 'model': '1920-24G', 'services': 'HP 1920-24G - 2', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.12': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G POE', 'manufacturer': 'HP', 'model': '1920-24G POE', 'services': 'HP 1920-24G POE', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.13': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G POE (2)', 'manufacturer': 'HP', 'model': '1920-24G POE', 'services': 'HP 1920-24G POE', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.14': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G - 3', 'manufacturer': 'HP', 'model': '1920-24G', 'services': 'HP 1920-24G - 3', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.15': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-24G - 4', 'manufacturer': 'HP', 'model': '1920-24G', 'services': 'HP 1920-24G - 4', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.20': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1920-48G POE', 'manufacturer': 'HP', 'model': '1920-48G POE', 'services': 'HP 1920-48G POE', 'location': 'Glostrup', 'placement': 'Mellem X felt'},
    '192.168.1.22': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS-1100-08P IT', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': 'D-Link DGS-1100-08P', 'location': 'Glostrup', 'placement': 'IT Department'},
    '192.168.1.23': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS-1100-08P Serverrum', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': 'D-Link DGS-1100-08P', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.25': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch Unify Ubiquiti USW-24-PoE', 'manufacturer': 'Ubiquiti', 'model': 'USW-24-PoE', 'services': 'Unify Ubiquiti USW-24-PoE', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.26': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch Unify Ubiquiti USW-24-PoE Kantine', 'manufacturer': 'Ubiquiti', 'model': 'USW-24-PoE', 'services': 'Unify Ubiquiti USW-24-PoE', 'location': 'Glostrup', 'placement': 'Canteen'},
    '192.168.1.27': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch Unify Ubiquiti USW-24-PoE Lille X felt', 'manufacturer': 'Ubiquiti', 'model': 'USW-24-PoE', 'services': 'Unify Ubiquiti USW-24-PoE', 'location': 'Glostrup', 'placement': 'Lille X felt'},
    '192.168.4.1': {'device_type': 'Firewall', 'category': 'Firewalls', 'host_name': 'Gateway', 'manufacturer': 'Generic', 'model': 'Gateway', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.5.2': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch 3560', 'manufacturer': 'Cisco', 'model': '3560', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.5.7': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS 1100-08P', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': '', 'location': 'Glostrup', 'placement': 'Consultation Room'},
    '192.168.5.8': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS-1100-08P', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': '', 'location': 'Glostrup', 'placement': 'Accounting'},

    # Routers
    '192.168.1.30': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 1)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.31': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 2)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.32': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 3)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Glostrup', 'placement': ''},

    # Printers
    '192.168.1.42': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Printer C4510', 'manufacturer': 'Develop', 'model': 'ineo+ 4510', 'services': '', 'location': 'Glostrup', 'placement': 'Reception Desk'},
    '192.168.1.43': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Printer C4510 (2)', 'manufacturer': 'Develop', 'model': 'ineo+ 4510', 'services': '', 'location': 'Glostrup', 'placement': 'Hallway - Foran Krogh'},
    '192.168.1.45': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Printer ZD421 Test', 'manufacturer': 'Zebra', 'model': 'ZD421', 'services': '', 'location': 'Glostrup', 'placement': 'Test - will be moved to Odense'},

    # Servers & Virtual Machines
    '192.168.1.170': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'Vcenter01', 'manufacturer': 'VMware', 'model': 'vCenter Server', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.171': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IMM 1', 'manufacturer': 'Lenovo', 'model': 'Integrated Management Module', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.172': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IMM 2', 'manufacturer': 'Lenovo', 'model': 'Integrated Management Module', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.173': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'Esx06', 'manufacturer': 'VMware', 'model': 'ESXi Hypervisor', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.174': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'Esx07', 'manufacturer': 'VMware', 'model': 'ESXi Hypervisor', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.175': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'res 1 - MDL-Laptop7.Diabetes.local', 'manufacturer': 'NetApp', 'model': 'FAS Series', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.176': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'res 2 - ?', 'manufacturer': 'NetApp', 'model': 'FAS Series', 'services': 'NetApp', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.181': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'DC03', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.186': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Filesrvr04', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.196': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IMM 3', 'manufacturer': 'Lenovo', 'model': 'Integrated Management Module', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.197': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IMM 4', 'manufacturer': 'Lenovo', 'model': 'Integrated Management Module', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.198': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'Esx04', 'manufacturer': 'VMware', 'model': 'ESXi Hypervisor', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.199': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'Esx05', 'manufacturer': 'VMware', 'model': 'ESXi Hypervisor', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.222': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Visma01', 'manufacturer': 'Visma', 'model': 'Application Server', 'services': 'sql', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.228': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Consult05', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.229': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'DC02', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.230': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Terminal02', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': 'rdp', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.232': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Veeam01', 'manufacturer': 'Veeam', 'model': 'Backup & Replication', 'services': 'veeam backup(not in domain)', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.234': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Filesrvr03', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': 'radius', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.235': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Scribe01', 'manufacturer': 'TIBCO', 'model': 'Scribe Insight', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.236': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Consult06', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.237': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Netmonitor', 'manufacturer': 'Generic', 'model': 'Monitoring Server', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.239': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Consult04', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': 'print, azure ad connect, terminal radius', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.240': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Consult07', 'manufacturer': 'Microsoft', 'model': 'Windows Server', 'services': 'azure ad connect', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.242': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Fotostation01', 'manufacturer': 'FotoWare', 'model': 'FotoStation', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.244': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Visma05 (TEST)', 'manufacturer': 'Visma', 'model': 'Application Server', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.246': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'Backup02', 'manufacturer': 'Generic', 'model': 'Backup Server', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.1.247': {'device_type': 'Virtual Machine', 'category': 'Virtual Machines', 'host_name': 'APC Powerchute', 'manufacturer': 'APC', 'model': 'PowerChute', 'services': 'https', 'location': 'Glostrup', 'placement': ''},
    '192.168.2.15': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IntegrationPROD', 'manufacturer': 'Generic', 'model': 'Application Server', 'services': '', 'location': 'Glostrup', 'placement': ''},
    '192.168.2.20': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'IntegrationTEST', 'manufacturer': 'Generic', 'model': 'Application Server', 'services': '', 'location': 'Glostrup', 'placement': ''},
    
    # Nodes (Hosts)
    '192.168.1.161': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'HQ-SCAN', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M720q', 'services': 'Proxmox', 'location': 'Glostrup', 'placement': 'IT Department'},
    '192.168.1.162': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'HQ-WAZUH', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M720q', 'services': 'Proxmox', 'location': 'Glostrup', 'placement': 'IT Department'},
    '192.168.1.163': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'HQ-ZABBIX', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M720q', 'services': 'Proxmox', 'location': 'Glostrup', 'placement': 'IT Department'},
    '192.168.1.164': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'HQ-SNIPE', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M720q', 'services': 'Proxmox', 'location': 'Glostrup', 'placement': 'IT Department'},
    '192.168.1.165': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'HQ-BACKUP', 'manufacturer': 'Lenovo', 'model': 'ThinkCentre M720q', 'services': 'Proxmox', 'location': 'Glostrup', 'placement': 'IT Department'},

    # LXC Containers
    '192.168.1.201': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-scan', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'Nmap', 'location': 'Glostrup', 'placement': 'HQ-SCAN'},
    '192.168.1.191': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-revproxy', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'Nginx', 'location': 'Glostrup', 'placement': 'HQ-SCAN'},
    '192.168.1.202': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-wazuh', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'Wazuh', 'location': 'Glostrup', 'placement': 'HQ-WAZUH'},
    '192.168.1.203': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-zabbix', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'Zabbix', 'location': 'Glostrup', 'placement': 'HQ-ZABBIX'},
    '192.168.1.204': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-snipe', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'Snipe-IT', 'location': 'Glostrup', 'placement': 'HQ-SNIPE'},
    '192.168.1.205': {'device_type': 'Container', 'category': 'Containers', 'host_name': 'lxc-backup', 'manufacturer': 'Proxmox', 'model': 'LXC Container', 'services': 'PBS', 'location': 'Glostrup', 'placement': 'HQ-BACKUP'},
    
    # Storage Devices
    '192.168.1.185': {'device_type': 'Storage Device', 'category': 'Storage Devices', 'host_name': 'BackupNAS02 Synology RS815RP+', 'manufacturer': 'Synology', 'model': 'RS815RP+', 'services': '', 'location': 'Glostrup', 'placement': '3. floor X felt'},
    '192.168.1.226': {'device_type': 'Storage Device', 'category': 'Storage Devices', 'host_name': 'Synology NAS', 'manufacturer': 'Synology', 'model': 'NAS', 'services': '', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.251': {'device_type': 'Storage Device', 'category': 'Storage Devices', 'host_name': 'BackupNAS03 Synology RS820RP+', 'manufacturer': 'Synology', 'model': 'RS820RP+', 'services': '', 'location': 'Glostrup', 'placement': ''},

    # Other Infrastructure
    '192.168.1.3': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'Zyxel Guest WiFi Router', 'os': 'HP ProCurve Secure Router 7102dl', 'manufacturer': 'Zyxel', 'model': 'Guest WiFi', 'services': 'http', 'location': 'Glostrup', 'placement': 'Server Room'},
    '192.168.1.209': {'device_type': 'Server', 'category': 'Servers', 'host_name': 'APC Management Card', 'os':'APC 7940 or 7723 Network Management Card (AOS 3.7.3 - 3.7.4)', 'manufacturer': 'APC', 'model': 'Network Management Card', 'services': 'ftp', 'location': 'Glostrup', 'placement': 'Server Room'},

    # --- Odense Location ---
    '192.168.200.1': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'MPLS Gateway', 'manufacturer': 'Generic', 'model': 'MPLS Gateway', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.3': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 1)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.4': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 2)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.5': {'device_type': 'Router', 'category': 'Routers', 'host_name': 'NiaNet MPLS (Reserved 3)', 'manufacturer': 'NiaNet', 'model': 'MPLS Router', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.10': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch HP 1910-24 POE', 'manufacturer': 'HP', 'model': '1910-24 POE', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.11': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS-1100-08P', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': '', 'location': 'Odense', 'placement': 'Logistics Area - forsendelse'},
    '192.168.200.12': {'device_type': 'Switch', 'category': 'Switches', 'host_name': 'Switch D-Link DGS-1100-08P', 'manufacturer': 'D-Link', 'model': 'DGS-1100-08P', 'services': '', 'location': 'Odense', 'placement': 'Logistics - Skrabelod'},
    '192.168.200.15': {'device_type': 'Storage Device', 'category': 'Storage Devices', 'host_name': 'BackupNAS04-Ode', 'manufacturer': 'Synology', 'model': 'NAS', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.201': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Ricoh IM C300', 'manufacturer': 'Ricoh', 'model': 'IM C300', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.206': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Ricoh c5100', 'manufacturer': 'Ricoh', 'model': 'c5100', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.207': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Ricoh Ferry', 'manufacturer': 'Ricoh', 'model': 'Ferry', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.208': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'HP LaserJet Pro M402dw', 'manufacturer': 'HP', 'model': 'LaserJet Pro M402dw', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.209': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Ricoh SP 4520DN', 'manufacturer': 'Ricoh', 'model': 'SP 4520DN', 'services': '', 'location': 'Odense', 'placement': ''},
    '192.168.200.210': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Zebra GK420D', 'manufacturer': 'Zebra', 'model': 'GK420D', 'services': 'Label Printer', 'location': 'Odense', 'placement': ''},
    '192.168.200.211': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'HP Pagewide 477DW', 'manufacturer': 'HP', 'model': 'Pagewide 477DW', 'services': '', 'location': 'Odense', 'placement': 'Logistics - 1. floor'},
    '192.168.200.212': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Zebra ZD421', 'manufacturer': 'Zebra', 'model': 'ZD421', 'services': 'Label Printer ', 'location': 'Odense', 'placement': ''},
    '192.168.200.213': {'device_type': 'Printer', 'category': 'Printers', 'host_name': 'Brother HL-L6415DN', 'manufacturer': 'Brother', 'model': 'HL-L6415DN', 'services': 'Fakturaprinter', 'location': 'Odense', 'placement': ''},
}
