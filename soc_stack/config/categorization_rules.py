"""
Centralized Rule Definitions for Asset Categorization
"""

NIC_VENDORS = {
    'liteon', 'universal global scientific industrial', 'intel', 'realtek', 
    'lcfc(hefei) electronics technology', 'hon hai precision', 'murata', 'azurewave'
}

MANUFACTURER_CLEANUP_RULES = {
    "lcfc(hefei) electronics technology": {
        "target_manufacturer": "Lenovo",
        "remove_from_model": "LCFC HeFei Electronics Technology LENOVO"
    }
    # Add other complex rules here in the future
}

NETWORK_DEVICE_RULES = {
    'Firewall': {
        'vendors': ['cisco', 'meraki', 'fortinet', 'palo alto', 'sonicwall', 'juniper', 'checkpoint', 'sophos'],
        'model_keywords': ['firewall', 'asa', 'srx', 'pa-', 'mx', 'security gateway', 'firepower']
    },
    'Switch': {
        'vendors': ['cisco', 'juniper', 'aruba', 'hp', 'dell', 'meraki', 'ubiquiti', 'd-link', 'netgear', 'tp-link'],
        'model_keywords': ['switch', 'catalyst', 'nexus', 'comware', 'procurve', 'ex', 'ms', 'edgeswitch', 'unifi switch', 'dgs', 'sg', 'usw'],
        'hostname_prefixes': ['sw', 'switch', 'tl', 'tl-', 'tl-sg', 'hp-switch', 'dgs-'] 
    },
    'Router': {
        'vendors': ['cisco', 'juniper', 'mikrotik', 'ubiquiti', 'netgear', 'tp-link'],
        'model_keywords': ['router', 'isr', 'asr', 'edgerouter', 'unifi gateway']
    },
    'Access Point': {
        'vendors': ['cisco', 'meraki', 'aruba', 'ubiquiti', 'ruckus', 'tp-link', 'unifi'],
        'model_keywords': ['access point', 'ap', 'aironet', 'unifi', 'mr', 'wap'],
        'hostname_prefixes': ['ap', 'ap-', 'ap1', 'ap2', 'ap3', 'ap4', 'ap5', 'ap6', 'ap7', 'ap8', 'uap']
    }
}

SERVER_RULES = {
    'os_keywords': ['windows server', 'esxi'],
    'model_keywords': ['server'],
    'hostname_keywords': ['zabbix', 'veeam', 'vcenter', 'esx', 'dc', 'filesrvr', 'terminal', 'consult']
}

VIRTUAL_MACHINE_RULES = {
    'vendors': ['vmware', 'virtualbox', 'qemu', 'microsoft corporation', 'proxmox', 'red hat', 'bochs'],
    'model_keywords': ['virtual machine', 'vm', 'kvm', 'hyper-v', 'virtualbox', 'vmware virtual platform','bochs', 'qemu'],
    'hostname_keywords': ['ubuntu', 'debian', 'centos', 'vm', 'vcenter', 'esx', 'hyperv', 'hyper-v', 'zabbix-proxy.diabetes.local']
}

CONTAINER_RULES = {
    'vendors': ['vmware', 'proxmox', 'docker', 'kubernetes', 'red hat'],
    'model_keywords': ['container', 'lxc', 'docker', 'k8s', 'kubernetes'],
    'hostname_keywords': ['lxc', 'container', 'docker', 'kubernetes', 'k8s']
}

MOBILE_DEVICE_RULES = {
    'vendors': [
        'apple', 'samsung', 'oneplus', 'google', 'huawei', 'xiaomi', 
        'oppo', 'vivo', 'motorola', 'nokia', 'sony', 'fairphone'
    ],
    'phone_keywords': ['phone', 'mobile', 'mobile phone', 'cell', 'smartphone'
    ],
    'phone_models': [
        'iphone', 'galaxy','galaxy s', 'galaxy a', 'galaxy z', 'galaxy note', 'galaxy xcover',
        'sm-s', 'sm-a', 'sm-g', 'sm-f', 'sm-n', 'sm-m', 'samsungSM',
        'googlepixel', 'pixel', 'oneplus', 'cph', 'le2', 'dn2', 'in2', 'kb2', 'gm1', 'hd1',
        'moto g', 'moto e', 'xperia'
    ],
    'tablet_models': [
        'ipad', 'galaxy tab', 'sm-t', 'sm-x', 'sm-p',
        'surface go', 'mediapad', 'matepad'
    ],
}

ANDROID_RULES = {
    'tablet_keywords': ['tablet', 'tab'],
    'tablet_vendors': ['samsung', 'lenovo', 'huawei'],
    'iot_keywords': ['meetingbar', 'roompanel', 'ctp']
}

COMPUTER_RULES = {
    'laptop_keywords': {
        'laptop', 'notebook', 'book', 'zenbook', 'vivobook',
        'thinkpad', 'latitude', 'xps', 'precision', 'elitebook',
        'probook', 'spectre', 'envy', 'surface laptop', 'studiobook',
        'proart', 'macbook', 'macbook pro', 'macbook air',
    },
    'laptop_hostname_keywords': {'laptop', 'book', 'mob', 'nb'},
    'laptop_vendor_prefixes': {
        'lenovo': ['20', '21', '40']
    },
    'desktop_keywords': {
        'desktop', 'workstation', 'station', 'studio', 'thinkcentre', 
        'ideacentre', 'thinkstation', 'neo', 'tower', 'sff', 'tiny', 
        'all-in-one', 'aio', 'm70s', 'm70t', 'm70q', 'm90s', 'm90t', 
        'm90q', 'm75s', 'm75t', 'm75q', 'p320', 'p520', 'p360', 'p340',
        'imac', 'mac mini', 'mac studio', 'mac pro', 'zbook', 'z840',
        'z640', 'z440', 'z240', 'z620', 'precision', 'proart station'
    },
    'desktop_hostname_keywords': {'pc', 'desktop', 'wkst', 'workstation'},
    'desktop_vendor_prefixes': {
        'lenovo': ['10', '11', '12', '30']
    },
    'desktop_os_keywords': ['desktop', 'windows workstation', 'linux workstation']
}

IOT_RULES = {
    'manufacturer_keywords': ['yealink'],
    'model_keywords': ['iot', 'meetingbar', 'roompanel', 'ctp', 'ctp18', 'a20', 'a30', 'poly', 'core2kit'],
    'hostname_keywords': ['meetingbar', 'roompanel', 'ctp', 'poly'],
    'os_keywords': ['iot', 'androidaosp']
}

PRINTER_RULES = {
    'vendors': [
        'brother', 'hp', 'hewlett', 'canon', 'epson', 'ricoh', 
        'xerox', 'lexmark', 'kyocera', 'konica', 'sharp', 'develop', 
        'zebra', 'dymo', 'toshiba', 'oki', 'pantum'
    ],
    'model_keywords': [
        'printer', 'laserjet', 'inkjet', 'deskjet', 'officejet', 'pagewide',
        'hl-l', 'mfc-', 'dcp-', 'imageclass', 'pixma', 'workforce', 'ecotank',
        'designjet', 'envy photo', 'im c', 'bizhub', 'imagerunner', 'colorwave', 
        'phaser', 'versalink',
        'zd4', 'zd6', 'zd2', 'gk4', 'gx4', 'zt4', 'zt2', 'zq', 'zd421', 'gk420',
        'l6410', 'l6415', 'l5100'
    ],
    'hostname_keywords': ['printer', 'prn', 'mfp', 'copier', 'print']
}

CAMERA_RULES = {
    'vendors': ['hikvision'],
    'model_keywords': ['camera', 'ipc'],
    'hostname_keywords': ['cam', 'camera']
}

SERVICE_RULES = {
    'Domain Controller': {
        'service_keywords': ['domain', 'ldap', 'kerberos']
    },
    'Printer': {
        'service_keywords': ['ipp', 'jetdirect', 'printer', 'cups', 'lpr']
    },
    'Database Server': {
        'service_keywords': ['mysql', 'mssql', 'postgresql', 'oracle', 'mongodb']
    },
    'Storage Device': {
        'service_keywords': ['nfs', 'smb', 'cifs', 'iscsi', 'netapp', 'synology']
    },
    'Web Server': {
        'service_keywords': ['http', 'https', 'nginx', 'apache', 'iis']
    },
    'Network Device': { 
        'service_keywords': ['snmp']
    }
}

CATEGORY_MAP = {
    'Camera': 'Cameras',
    'Server': 'Servers',
    'Switch': 'Switches',
    'Router': 'Routers',
    'Firewall': 'Firewalls',
    'Access Point': 'Access Points',
    'Printer': 'Printers',
    'Laptop': 'Laptops',
    'Desktop': 'Desktops',
    'Tablet': 'Tablets',
    'Mobile Phone': 'Mobile Phones',
    'Virtual Machine': 'Virtual Machines',
    'Container': 'Containers',
    'IoT Device': 'IoT Devices',
    # Map inferred models to existing categories
    'Windows Server': 'Servers',
    'Linux Server': 'Servers',
    'Windows Workstation': 'Desktops',
    'Linux Workstation': 'Desktops',
    'macOS Device': 'Desktops',
}

BUSINESS_CRITILCALITY_RULES = {
    'Mission Critical': {
        'categories': [ 
            'Servers', 'Firewalls', 'Routers', 'Switches'
        ]
    },
    'High': {
        'categories': [
            'Access Points', 'Storage Devices', 'Network Devices',
            'Cloud Resources'
        ]
    },
    'Medium': {
        'categories': [
            'Laptops', 'Desktops', 'Virtual Machines'
        ]
    },
    'Low': {
        'categories': [
            'Cameras', 'Tablets', 'Mobile Phones', 
            'IoT Devices', 'Monitors', 'Printers', 'Other Assets'
        ]
    }
}