"""
Snipe-IT Custom Field and Fieldset Definitions for SOC Asset Management
"""

# Define Custom Fields
CUSTOM_FIELDS = {
    # Identity / IDs
    'azure_ad_id': {"name": "Azure AD Device ID", "element": "text", "format": "ANY", "help_text": "Unique Identifier from Microsoft Entra ID (formerly Azure AD)"},
    'intune_device_id': {"name": "Intune Device ID", "element": "text", "format": "ANY", "help_text": "Unique Identifier from Intune"},
    'primary_user_id': {"name": "Primary User ID", "element": "text", "format": "ANY", "help_text": "Intune/AAD user object ID for the primary user"},
    'device_enrollment_type': {"name": "Device Enrollment Type", "element": "text", "format": "ANY", "help_text": "Type of device enrollment"},
    'device_registration_state': {"name": "Device Registration State", "element": "text", "format": "ANY", "help_text": "State of device registration"},
    'device_category_display_name': {"name": "Device Category Display Name", "element": "text", "format": "ANY", "help_text": "Display name of the device category"},
    'device_type': {"name": "Device Type", "element": "text", "format": "ANY", "help_text": "Type: Computer, Switch, Router, Printer, IoT, etc."},
    'udid': {"name": "UDID", "element": "text", "format": "ANY", "help_text": "Unique Device Identifier"},
    'serial_number': {"name": "Serial Number", "element": "text", "format": "ANY", "help_text": "Serial number of the device"},
    
    # Entra ID Specifics
    'entra_object_id': {"name": "Entra Object ID", "element": "text", "format": "ANY", "help_text": "Unique Object ID from Entra ID"},
    'entra_trust_type': {"name": "Entra Trust Type", "element": "text", "format": "ANY", "help_text": "Trust Type (e.g. Workplace, AzureAd)"},
    'entra_join_type': {"name": "Entra Join Type", "element": "text", "format": "ANY", "help_text": "Mapped Join Type (e.g. Azure AD Joined)"},
    'entra_profile_type': {"name": "Entra Profile Type", "element": "text", "format": "ANY", "help_text": "Profile Type"},
    'entra_account_enabled': {"name": "Entra Account Enabled", "element": "text", "format": "BOOLEAN", "help_text": "Is the account enabled in Entra ID?"},
    'entra_is_compliant': {"name": "Entra Compliant", "element": "text", "format": "BOOLEAN", "help_text": "Is the device compliant in Entra ID?"},
    'entra_is_managed': {"name": "Entra Managed", "element": "text", "format": "BOOLEAN", "help_text": "Is the device managed in Entra ID?"},
    'entra_mdm_app_id': {"name": "Entra MDM App ID", "element": "text", "format": "ANY", "help_text": "MDM Application ID"},
    'entra_last_sign_in': {"name": "Entra Last Sign-In", "element": "text", "format": "ANY", "help_text": "Approximate last sign-in timestamp"},
    'entra_registration_date': {"name": "Entra Registration Date", "element": "text", "format": "ANY", "help_text": "Date of registration in Entra ID"},
    'entra_on_prem_synced': {"name": "Entra On-Prem Synced", "element": "text", "format": "BOOLEAN", "help_text": "Is synced from on-premises AD?"},
    'entra_on_prem_last_sync': {"name": "Entra On-Prem Last Sync", "element": "text", "format": "ANY", "help_text": "Last sync time from on-premises AD"},
    
    # Teams Specific Fields
    'teams_device_id': {"name": "Teams Device ID", "element": "text", "format": "ANY", "help_text": "Unique Identifier from Microsoft Teams"},
    'teams_device_type': {"name": "Teams Device Type", "element": "text", "format": "ANY", "help_text": "Type of Teams device (e.g., collaborationBar, teamsRoom)"},
    'teams_health_status': {"name": "Teams Health Status", "element": "text", "format": "ANY", "help_text": "Health status reported by Teams (e.g., Healthy, Non-urgent)"},
    'teams_activity_state': {"name": "Teams Activity State", "element": "text", "format": "ANY", "help_text": "Activity state reported by Teams (e.g., Idle, InUse)"},
    'teams_last_modified': {"name": "Teams Last Modified", "element": "text", "format": "ANY", "help_text": "Last modified timestamp from Teams (ISO 8601)"},
    'teams_created_date': {"name": "Teams Created Date", "element": "text", "format": "ANY", "help_text": "Creation timestamp from Teams (ISO 8601)"},
    'teams_last_modified_by_id': {"name": "Teams Last Modified By ID", "element": "text", "format": "ANY", "help_text": "AAD User ID of the person who last modified the device in Teams"},
    'teams_last_modified_by_name': {"name": "Teams Last Modified By Name", "element": "text", "format": "ANY", "help_text": "Display name of the person who last modified the device in Teams"},

    # Enrollment / Management
    'intune_managed': {"name": "Intune Managed", "element": "text", "format": "BOOLEAN", "help_text": "Is this device managed by Intune?"},
    'intune_registered': {"name": "Intune Registered", "element": "text", "format": "BOOLEAN", "help_text": "Device is registered with Intune"},
    'intune_enrollment_date': {"name": "Intune Enrollment Date", "element": "text", "format": "ANY", "help_text": "Enrollment timestamp from Intune (ISO 8601)"},
    'intune_last_sync': {"name": "Intune Last Sync", "element": "text", "format": "ANY", "help_text": "Last check-in timestamp from Intune (ISO 8601)"},
    'managed_by': {"name": "Managed By", "element": "text", "format": "ANY", "help_text": "Management authority (e.g., Intune, Co-managed, ConfigMgr)"},
    'management_name': {"name": "Management Name", "element": "text", "format": "ANY", "help_text": "MDM management instance/name"},
    'intune_category': {"name": "Intune Category", "element": "text", "format": "ANY", "help_text": "Intune device category"},
    'ownership': {"name": "Ownership", "element": "text", "format": "ANY", "help_text": "Corporate or Personal ownership"},
    'device_state': {"name": "Device State", "element": "text", "format": "ANY", "help_text": "State reported by Intune (e.g., Active)"},
    'management_state': {"name": "Management State", "element": "text", "format": "ANY", "help_text": "Device's management state (e.g., managed, pending)"},
    'intune_compliance': {"name": "Intune Compliance", "element": "text", "format": "ANY", "help_text": "Compliance state (Compliant/Noncompliant/Unknown)"},
    'compliance_grace_expiration': {"name": "Compliance Grace Expiration", "element": "text", "format": "ANY", "help_text": "Compliance grace period expiration (ISO 8601)"},
    'management_cert_expiration': {"name": "Management Cert Expiration", "element": "text", "format": "ANY", "help_text": "Management certificate expiration date (ISO 8601)"},
    'enrollment_profile_name': {"name": "Enrollment Profile Name", "element": "text", "format": "ANY", "help_text": "Name of the enrollment profile used"},
    'require_user_enrollment_approval': {"name": "Require User Enrollment Approval", "element": "text", "format": "BOOLEAN", "help_text": "Indicates if user enrollment approval is required"},
    'activation_lock_bypass_code': {"name": "Activation Lock Bypass Code", "element": "text", "format": "ANY", "help_text": "Bypass code for activation lock"},

    # OS / Platform
    'os_platform': {"name": "OS Platform", "element": "text", "format": "ANY", "help_text": "Operating system platform (e.g., Windows, macOS, iOS)"},
    'os_version': {"name": "OS Version", "element": "text", "format": "ANY", "help_text": "Specific OS version/build"},
    'sku_family': {"name": "SKU Family", "element": "text", "format": "ANY", "help_text": "OS SKU family/edition"},
    'join_type': {"name": "Join Type", "element": "text", "format": "ANY", "help_text": "AAD join type (AzureADJoined/Hybrid/Workgroup)"},
    'product_name': {"name": "Product Name", "element": "text", "format": "ANY", "help_text": "Product or OS name as reported"},
    'processor_architecture': {"name": "Processor Architecture", "element": "text", "format": "ANY", "help_text": "CPU architecture (x64, ARM64, etc.)"},
    'security_patch_level': {"name": "Security Patch Level", "element": "text", "format": "ANY", "help_text": "OS security patch level"},
    'encrypted': {"name": "Encrypted", "element": "text", "format": "BOOLEAN", "help_text": "Device encryption status"},
    'supervised': {"name": "Supervised", "element": "text", "format": "BOOLEAN", "help_text": "Supervised status (iOS/macOS)"},
    'jailbroken': {"name": "Jailbroken/Rooted", "element": "text", "format": "BOOLEAN", "help_text": "Device jailbreak/root status"},
    'azure_ad_registered': {"name": "Azure AD Registered", "element": "text", "format": "BOOLEAN", "help_text": "Registered in Azure AD"},
    'bios_version': {"name": "System Management BIOS Version", "element": "text", "format": "ANY", "help_text": "SMBIOS/Firmware version"},
    'tpm_manufacturer_id': {"name": "TPM Manufacturer ID", "element": "text", "format": "ANY", "help_text": "TPM manufacturer ID"},
    'tpm_manufacturer_version': {"name": "TPM Manufacturer Version", "element": "text", "format": "ANY", "help_text": "TPM manufacturer version"},
    'android_security_patch_level': {"name": "Android Security Patch Level", "element": "text", "format": "ANY", "help_text": "Security patch level for Android devices"},
    'model': {"name": "Model", "element": "text", "format": "ANY", "help_text": "Device model"},
    'manufacturer': {"name": "Manufacturer", "element": "text", "format": "ANY", "help_text": "Device manufacturer"},

    # User
    'primary_user_upn': {"name": "Primary User UPN", "element": "text", "format": "ANY", "help_text": "User Principal Name of the primary user"},
    'primary_user_email': {"name": "Primary User Email", "element": "text", "format": "ANY", "help_text": "Primary user's email address"},
    'primary_user_display_name': {"name": "Primary User Display Name", "element": "text", "format": "ANY", "help_text": "Primary user's display name"},
    'managed_device_name': {"name": "Managed Device Name", "element": "text", "format": "ANY", "help_text": "The name of the device in Intune"},
    'identity_type': {'name': 'Identity Type', 'element': 'text', 'format': 'ANY', 'help_text': 'User identity type (e.g., aadUser)'},
    'user_display_name': {"name": "User Display Name", "element": "text", "format": "ANY", "help_text": "Display name of the user"},

    # Software Inventory
    'installed_software': {"name": "Installed Software", "element": "textarea", "format": "ANY", "help_text": "JSON list of installed applications from Intune"},
    'software_count': {"name": "Software Count", "element": "text", "format": "ANY", "help_text": "Total number of installed applications"},
    'last_software_scan': {"name": "Last Software Scan", "element": "text", "format": "ANY", "help_text": "Timestamp of last software inventory scan"},
    'configuration_manager_client_enabled_features': {"name": "Configuration Manager Client Enabled Features", "element": "text", "format": "ANY", "help_text": "Enabled features for Configuration Manager client"},

    # Networking
    'dns_hostname': {"name": "DNS Hostname", "element": "text", "format": "ANY", "help_text": "Hostname from DNS or discovery"},
    'mac_addresses': {"name": "MAC Addresses", "element": "textarea", "format": "ANY", "help_text": "Newline-separated list of all MACs (Wi-Fi/Ethernet)"},
    'last_seen_ip': {"name": "Last Seen IP", "element": "text", "format": "ANY", "help_text": "Last observed IP on the network"},
    'wifi_subnet_id': {"name": "WiFi Subnet ID", "element": "text", "format": "ANY", "help_text": "WiFi subnet ID reported by Intune"},
    'wifi_mac': {"name": "WiFi MAC Address", "element": "text", "format": "ANY", "help_text": "MAC address for WiFi interface"},
    'ethernet_mac': {"name": "Ethernet MAC Address", "element": "text", "format": "ANY", "help_text": "MAC address for Ethernet interface"},
    'wifi_ipv4': {"name": "WiFi IPv4 Address", "element": "text", "format": "ANY", "help_text": "IPv4 address assigned to the WiFi interface"},
    'wifi_subnet': {"name": "WiFi Subnet", "element": "text", "format": "ANY", "help_text": "Subnet information for the WiFi interface"},

    # Network Device Information (SNMP)
    'snmp_location': {"name": "SNMP Location", "element": "text", "format": "ANY", "help_text": "Physical location from SNMP"},
    'snmp_contact': {"name": "SNMP Contact", "element": "text", "format": "ANY", "help_text": "Contact person from SNMP"},
    'snmp_uptime': {"name": "SNMP Uptime", "element": "text", "format": "ANY", "help_text": "Device uptime from SNMP"},
    'switch_port_count': {"name": "Switch Port Count", "element": "text", "format": "ANY", "help_text": "Number of ports (for switches)"},
    'firmware_version': {"name": "Firmware Version", "element": "text", "format": "ANY", "help_text": "Firmware/IOS version for network devices"},

    # Cellular / Device comms
    'phone_number': {"name": "Phone Number", "element": "text", "format": "ANY", "help_text": "Device phone number (if available)"},
    'imei': {"name": "IMEI", "element": "text", "format": "ANY", "help_text": "International Mobile Equipment Identity"},
    'iccid': {"name": "ICCID", "element": "text", "format": "ANY", "help_text": "SIM card ICCID"},
    'meid': {"name": "MEID", "element": "text", "format": "ANY", "help_text": "Mobile Equipment Identifier"},
    'eid': {"name": "EID (eSIM)", "element": "text", "format": "ANY", "help_text": "Embedded SIM EID"},
    'subscriber_carrier': {"name": "Subscriber Carrier", "element": "text", "format": "ANY", "help_text": "Mobile carrier"},
    'cellular_technology': {"name": "Cellular Technology", "element": "text", "format": "ANY", "help_text": "e.g., LTE, 5G"},

    # Storage
    'total_storage': {"name": "Total Storage", "element": "text", "format": "ANY", "help_text": "Total device storage (bytes)"},
    'free_storage': {"name": "Free Storage", "element": "text", "format": "ANY", "help_text": "Free device storage (bytes)"},
    'physical_memory_in_bytes': {"name": "Physical Memory (Bytes)", "element": "text", "format": "ANY", "help_text": "Total physical memory in bytes"},

    # EAS (Exchange ActiveSync)
    'eas_activation_id': {"name": "EAS Activation ID", "element": "text", "format": "ANY", "help_text": "EAS activation ID"},
    'eas_activated': {"name": "EAS Activated", "element": "text", "format": "BOOLEAN", "help_text": "EAS activation status"},
    'eas_activation_date': {"name": "EAS Activation Date", "element": "text", "format": "ANY", "help_text": "EAS activation timestamp (ISO 8601)"},
    'eas_last_sync': {"name": "EAS Last Sync", "element": "text", "format": "ANY", "help_text": "Last EAS sync time (ISO 8601)"},
    'eas_reason': {"name": "EAS Reason", "element": "text", "format": "ANY", "help_text": "EAS status reason"},
    'eas_status': {"name": "EAS Status", "element": "text", "format": "ANY", "help_text": "EAS status"},
    'exchange_last_successful_sync_date_time': {"name": "Exchange Last Successful Sync DateTime", "element": "text", "format": "ANY", "help_text": "Date and time of the last successful Exchange sync"},
    'exchange_access_state': {"name": "Exchange Access State", "element": "text", "format": "ANY", "help_text": "Current state of Exchange access"},
    'exchange_access_state_reason': {"name": "Exchange Access State Reason", "element": "text", "format": "ANY", "help_text": "Reason for the current Exchange access state"},
    'remote_assistance_session_url': {"name": "Remote Assistance Session URL", "element": "text", "format": "ANY", "help_text": "URL for remote assistance session"},
    'remote_assistance_session_error_details': {"name": "Remote Assistance Session Error Details", "element": "text", "format": "ANY", "help_text": "Error details for remote assistance session"},

    # Nmap discovery
    'first_seen_date': {"name": "First Seen Date", "element": "text", "format": "ANY", "help_text": "Timestamp when first discovered (ISO 8601)"},
    'nmap_last_scan': {"name": "Nmap Last Scan", "element": "text", "format": "ANY", "help_text": "Timestamp of last nmap scan (ISO 8601)"},
    'nmap_os_guess': {"name": "Nmap OS Guess", "element": "text", "format": "ANY", "help_text": "Nmap's OS fingerprint guess"},
    'os_accuracy': {"name": "OS Accuracy", "element": "text", "format": "ANY", "help_text": "Nmap's confidence level in the OS guess (percentage)"},
    'nmap_open_ports': {"name": "Nmap Open Ports", "element": "textarea", "format": "ANY", "help_text": "Newline or comma-separated list of open ports"},
    'open_ports_hash': {"name": "Open Ports Hash", "element": "text", "format": "ANY", "help_text": "Hash of open ports list to detect changes"},
    'discovery_note': {"name": "Discovery Note", "element": "textarea", "format": "ANY", "help_text": "Notes about discovery (VLAN, location, etc.)"},
    'nmap_discovered_services': {"name": "Nmap Services", "element": "textarea", "format": "ANY", "help_text": "List of discovered service names from Nmap"},
    'nmap_script_output': {"name": "Nmap Script Output", "element": "textarea", "format": "ANY", "help_text": "Output from Nmap NSE scripts (e.g., vuln, http-title)"},

    # Data hygiene
    'last_update_source': {"name": "Last Update Source", "element": "text", "format": "ANY", "help_text": "Which system updated last (Intune/Nmap/Azure)"},
    'last_update_at': {"name": "Last Update At", "element": "text", "format": "ANY", "help_text": "Timestamp of last update (ISO 8601)"},
    'device_action_results': {"name": "Device Action Results", "element": "textarea", "format": "ANY", "help_text": "Results of device actions performed"},
    'device_health_attestation_state': {"name": "Device Health Attestation State", "element": "text", "format": "ANY", "help_text": "State of device health attestation"},
    'partner_reported_threat_state': {"name": "Partner Reported Threat State", "element": "text", "format": "ANY", "help_text": "Threat state reported by partner"},
    'notes': {"name": "Notes", "element": "textarea", "format": "ANY", "help_text": "Additional notes about the device"},

    # Vulnerability Information
    'vulnerability_scan_date': {"name": "Last Vulnerability Scan", "element": "text", "format": "ANY", "help_text": "Date of last vulnerability scan"},
    'critical_vulns': {"name": "Critical Vulnerabilities", "element": "text", "format": "ANY", "help_text": "Count of critical vulnerabilities"},
    'high_vulns': {"name": "High Vulnerabilities", "element": "text", "format": "ANY", "help_text": "Count of high vulnerabilities"},
    'vulnerability_score': {"name": "Vulnerability Score", "element": "text", "format": "ANY", "help_text": "Overall vulnerability score (0-10)"},

    # Certificate Management
    'certificates': {"name": "Certificates", "element": "textarea", "format": "ANY", "help_text": "JSON list of certificates and expiry dates"},
    'cert_expiry_warning': {"name": "Certificate Expiry Warning", "element": "text", "format": "ANY", "help_text": "Earliest certificate expiry date"},

    # Cloud Resource Information
    'cloud_provider': {"name": "Cloud Provider", "element": "text", "format": "ANY", "help_text": "Cloud provider (Azure, AWS, GCP, On-Premise)"},
    'azure_resource_id': {"name": "Azure Resource ID", "element": "text", "format": "ANY", "help_text": "ARM resource ID"},
    'azure_subscription_id': {"name": "Azure Subscription ID", "element": "text", "format": "ANY", "help_text": "Subscription GUID"},
    'azure_resource_group': {"name": "Azure Resource Group", "element": "text", "format": "ANY", "help_text": "Resource group name"},
    'azure_region': {"name": "Azure Region", "element": "text", "format": "ANY", "help_text": "Azure location/region"},
    'azure_tags_json': {"name": "Azure Tags (JSON)", "element": "textarea", "format": "ANY", "help_text": "JSON-encoded Azure tags"},
    
    # Cybersec Tags
    'cybersec_risk_level': {'name': 'Security Risk Level', 'element': 'listbox', "format": "ANY", 'field_values': 'Low\nMedium\nHigh\nCritical', "help_text": "Security risk level of the device"},
    'cybersec_needs_investigation': {'name': 'Needs Security Investigation', 'element': 'text', "format": "BOOLEAN", "help_text": "Flag to indicate if the device needs security investigation"},
    'cybersec_last_seen': {'name': 'Last Security Scan','element': 'text', 'format': 'ANY', "help_text": "Th last scan that the device was seen."},
    
    # Criticality Tag
    'business_criticality': {'name': 'Business Criticality', 'element': 'listbox', "format": "ANY", 'field_values': 'Low\nMedium\nHigh\nMission Critical', "help_text": "Impact on operations if this asset fails."}
}

# Define Custom Fieldsets
CUSTOM_FIELDSETS = {
    # This is the primary, comprehensive fieldset for all managed endpoints (Laptops, Desktops, etc.).
    # It includes fields from all key data sources: Microsoft 365 (Intune + Teams) and Nmap.
    "Managed and Discovered Assets": [
        # Identity / IDs
        'azure_ad_id', 'business_criticality', 'intune_device_id', 'primary_user_id', 'device_enrollment_type', 'device_registration_state', 'device_category_display_name', 'udid', 'serial_number',
        
        # Entra ID
        'entra_object_id', 'entra_trust_type', 'entra_join_type', 'entra_profile_type', 'entra_account_enabled',
        'entra_is_compliant', 'entra_is_managed', 'entra_mdm_app_id', 'entra_last_sign_in', 'entra_registration_date',
        'entra_on_prem_synced', 'entra_on_prem_last_sync',

        # Enrollment / Management
        'intune_managed', 'intune_registered', 'intune_enrollment_date', 'intune_last_sync',
        'managed_by', 'management_name', 'intune_category', 'ownership', 'device_state', 'management_state',
        'intune_compliance', 'compliance_grace_expiration', 'management_cert_expiration', 'enrollment_profile_name', 
        'require_user_enrollment_approval', 'activation_lock_bypass_code',
        
        # Teams Specific Fields
        'teams_device_id', 'teams_device_type', 'teams_health_status', 'teams_activity_state',
        'teams_last_modified', 'teams_created_date', 'teams_last_modified_by_id', 'teams_last_modified_by_name',
        
        # User Identity Type
        'identity_type',

        # OS / Platform
        'os_platform', 'os_version', 'sku_family', 'join_type', 'product_name',
        'processor_architecture', 'security_patch_level', 'encrypted', 'supervised',
        'jailbroken', 'azure_ad_registered', 'bios_version',
        'tpm_manufacturer_id', 'tpm_manufacturer_version', 'android_security_patch_level', 'model', 'manufacturer',

        # User
        'primary_user_upn', 'primary_user_email', 'primary_user_display_name', 'managed_device_name', 'user_display_name',

        # Software Inventory
        'installed_software', 'software_count', 'last_software_scan', 'configuration_manager_client_enabled_features',

        # Networking
        'dns_hostname', 'device_type', 'mac_addresses', 
        'wifi_mac', 'ethernet_mac', 'last_seen_ip', 'wifi_subnet_id', 'wifi_ipv4', 'wifi_subnet',

        # Cellular / Device comms
        'phone_number', 'imei', 'iccid', 'meid', 'eid', 'subscriber_carrier', 'cellular_technology',

        # Storage
        'total_storage', 'free_storage', 'physical_memory_in_bytes',

        # EAS
        'eas_activation_id', 'eas_activated', 'eas_activation_date', 'eas_last_sync', 
        'eas_reason', 'eas_status', 'exchange_access_state', 'exchange_access_state_reason',

        # Nmap
        'first_seen_date', 'nmap_last_scan', 'nmap_os_guess', 'os_accuracy', 'nmap_open_ports',
        'open_ports_hash', 'nmap_discovered_services', 'nmap_script_output',

        # Hygiene
        'last_update_source', 'last_update_at', 'device_action_results', 'device_health_attestation_state', 'partner_reported_threat_state',

        # Cybersec
        'cybersec_risk_level', 'cybersec_needs_investigation', 'cybersec_last_seen',

        # Notes
        'discovery_note', 'notes',
        
        # Criticality
        'business_criticality'
        
    ],

    # Software inventory details
    "Software and Applications": [
        'installed_software', 'software_count', 'last_software_scan', 'configuration_manager_client_enabled_features'
    ],

    # Vulnerability and certificate details
    "Security and Vulnerabilities": [
        'vulnerability_scan_date', 'critical_vulns', 'high_vulns', 'vulnerability_score',
        'certificates', 'cert_expiry_warning', 'security_patch_level', 'encrypted',
        'cybersec_risk_level', 'cybersec_needs_investigation', 'cybersec_last_seen'
    ],

    # Network devices and infrastructure
    "Network Infrastructure": [
        'device_type', 'dns_hostname', 'mac_addresses', 'last_seen_ip',
        'snmp_location', 'snmp_contact', 'snmp_uptime', 'switch_port_count', 'firmware_version',
        'model', 'manufacturer',
        'first_seen_date', 'last_update_source', 'last_update_at',
        'nmap_last_scan', 'nmap_os_guess', 'os_accuracy', 
        'nmap_open_ports', 'open_ports_hash', 'nmap_discovered_services', 'nmap_script_output',
        'discovery_note', 'business_criticality'
    ],
    
    # Cellular and mobile device specifics (Phones, Tablets)
    "Mobile Devices": [
        'imei', 'meid', 'phone_number', 'iccid', 'eid', 'subscriber_carrier',
        'cellular_technology', 'supervised', 'jailbroken', 'business_criticality',
        'azure_ad_id', 'intune_device_id', 'primary_user_id', 'primary_user_upn',
        'entra_object_id', 'entra_trust_type', 'entra_join_type', 'entra_profile_type', 'entra_account_enabled',
        'entra_is_compliant', 'entra_is_managed', 'entra_mdm_app_id', 'entra_last_sign_in', 'entra_registration_date',
        'entra_on_prem_synced', 'entra_on_prem_last_sync',
        'primary_user_email', 'managed_by', 'intune_managed', 'intune_compliance', 
        'device_enrollment_type', 'device_registration_state', 'model', 'manufacturer',
        'last_seen_ip', 'mac_addresses'
    ],

    # Nmap-discovered assets
    "Discovered Assets (Nmap Only)": [
        'dns_hostname', 'mac_addresses', 'last_seen_ip',
        'model', 'manufacturer',
        'first_seen_date', 'last_update_source', 'last_update_at','nmap_last_scan', 'nmap_os_guess', 'os_accuracy', 
        'nmap_open_ports', 'open_ports_hash', 'nmap_discovered_services', 'nmap_script_output', 'discovery_note', 'device_type',
        'business_criticality'
    ],

    # Cloud resources
    "Cloud Resources (Azure)": [
        'cloud_provider', 'azure_resource_id', 'azure_subscription_id', 'azure_resource_group',
        'azure_region', 'azure_tags_json', 'last_update_source', 'last_update_at', 'business_criticality',
        'entra_object_id', 'entra_trust_type', 'entra_join_type', 'entra_account_enabled',
        'entra_is_compliant', 'entra_is_managed', 'entra_last_sign_in',
        'entra_profile_type', 'entra_mdm_app_id', 'entra_registration_date',
        'entra_on_prem_synced', 'entra_on_prem_last_sync'
    ],
    
    # All network identifiers for easy reference
    "All Network Identifiers": [
        'dns_hostname', 'wifi_mac', 'ethernet_mac', 'mac_addresses', 'wifi_ipv4',
        'wifi_subnet', 'last_seen_ip'
    ],
    
    # Exchange and Remote Assistance
    "Exchange and Remote Assistance": [
        'eas_activation_date',
        'exchange_last_successful_sync_date_time',
        'exchange_access_state',
        'exchange_access_state_reason',
        'remote_assistance_session_url',
        'remote_assistance_session_error_details'
    ]
}

# Define Status Labels
STATUS_LABELS = {
    "Managed - Intune": {
        "type": "deployable", 
        "color": "#36a9e0",
        "show_in_nav": False,
        "default_label": False
        },
    "Managed - M365": {
        "type": "deployable",
        "color": "#0078d4",
        "show_in_nav": True,
        "default_label": False
    },
    "Managed - Teams": {
        "type": "deployable",
        "color": "#4b53bc",
        "show_in_nav": True,
        "default_label": False
    },
    "Discovered - Nmap": {
        "type": "deployable", 
        "color": "#f1c40f",
        "show_in_nav": False,
        "default_label": False
        },
    "Discovered - Needs Review": {
        "type": "pending",
        "color": "#d35400",
        "show_in_nav": True,
        "default_label": False
    },
    "Cloud Resource": {
        "type": "deployable", 
        "color": "#9b59b6",
        "show_in_nav": False,
        "default_label": False
    },
    "On-Premise": {
        "type": "deployable", 
        "color": "#008000",
        "show_in_nav": False,
        "default_label": False
    },
    "Off-site": {
        "type": "deployable", 
        "color": "#e67e22",
        "show_in_nav": False,
        "default_label": False
    },
    "Discovered - Unmanaged": {
        "type": "deployable", 
        "color": "#e74c3c",
        "show_in_nav": False,
        "default_label": False
    },
    "Unknown": {
        "type": "deployable", 
        "color": "#95a5a6",
        "show_in_nav": False,
        "default_label": True
    },
    "Missing": {
        "type": "deployable", 
        "color": "#000000",
        "show_in_nav": False,
        "default_label": False
    },
}

# Define Categories
CATEGORIES = {
    "Cameras": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Desktops": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Laptops" : {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Tablets" : {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    }, 
    "Mobile Phones" : {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Monitors": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Storage Devices": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Servers": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Firewalls": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Switches": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Routers": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Access Points": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
     "Network Devices": {
        "category_type": "asset",
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
    },
    "Printers": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "IoT Devices": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Virtual Machines": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Containers": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Cloud Resources": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
    "Other Assets": {
        "category_type": "asset", 
        "use_default_eula": False,
        "require_acceptance": False,
        "checkin_email": False
        },
}

# Define Generic Models
MODELS = [
    {'name': 'Generic Camera', 'category': 'Cameras', 'manufacturer': 'Generic'},
    {'name': 'Generic Unknown Device', 'category': 'Other Assets', 'manufacturer': 'Generic'},
    {'name': 'Generic Desktop', 'category': 'Desktops', 'manufacturer': 'Generic'},
    {'name': 'Generic Laptop', 'category': 'Laptops', 'manufacturer': 'Generic'},
    {'name': 'Generic Server', 'category': 'Servers', 'manufacturer': 'Generic'},
    {'name': 'Generic Firewall', 'category': 'Firewalls', 'manufacturer': 'Generic'},
    {'name': 'Generic Switch', 'category': 'Switches', 'manufacturer': 'Generic'},
    {'name': 'Generic Router', 'category': 'Routers', 'manufacturer': 'Generic'},
    {'name': 'Generic Access Point', 'category': 'Access Points', 'manufacturer': 'Generic'},
    {'name': 'Generic Network Device', 'category': 'Network Devices', 'manufacturer': 'Generic'},
    {'name': 'Generic Printer', 'category': 'Printers', 'manufacturer': 'Generic'},
    {'name': 'Generic Mobile Phone', 'category': 'Mobile Phones', 'manufacturer': 'Generic'},
    {'name': 'Generic Tablet', 'category': 'Tablets', 'manufacturer': 'Generic'},
    {'name': 'Generic IoT Device', 'category': 'IoT Devices', 'manufacturer': 'Generic'},
    {'name': 'Generic Storage Device', 'category': 'Storage Devices', 'manufacturer': 'Generic'},
    {'name': 'Generic Virtual Machine', 'category': 'Virtual Machines', 'manufacturer': 'Generic'},
    {'name': 'Generic Container', 'category': 'Containers', 'manufacturer': 'Generic'},
    {'name': 'Generic Cloud Resource', 'category': 'Cloud Resources', 'manufacturer': 'Generic'},    
    {'name': 'Generic Domain Controller', 'category': 'Servers', 'manufacturer': 'Generic'},
    {'name': 'Generic Database Server', 'category': 'Servers', 'manufacturer': 'Generic'},
    {'name': 'Generic Web Server', 'category': 'Servers', 'manufacturer': 'Generic'}
]

#Define Manufacturers
MANUFACTURERS = [
    {'name': 'Generic', 'support_contact': '', 'support_url': ''}
]

# Define Locations
LOCATIONS = [
    "Glostrup",
    "Odense",
    "Off-site",
    "Cloud"
]