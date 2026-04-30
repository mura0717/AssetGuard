"""
Implements logic to categorize assets based on various data points.
"""

from typing import Dict, List, Optional
from ipaddress import ip_address, AddressValueError

from soc_stack.debug.tools.asset_debug_logger import debug_logger
from soc_stack.config import categorization_rules
from soc_stack.utils.text_utils import normalize_for_comparison
from soc_stack.config import network_config

class AssetCategorizer:

    def __init__(self):
        pass
    
    @classmethod
    def _is_static_ip(cls, ip_address: str) -> bool:
        return ip_address in network_config.STATIC_IP_MAP

    @classmethod
    def _categorize_by_static_ip(cls, ip_address: Optional[str]) -> Optional[Dict]:
        if not ip_address:
            return None
        return network_config.STATIC_IP_MAP.get(ip_address)
    
    @classmethod
    def _normalize_hardware_identity(cls, manufacturer: str, model: str) -> tuple[str, str]:
        """Fixes manufacturer data when a NIC vendor is mistakenly identified."""
        mfr_lower = manufacturer.lower()
        model_lower = model.lower()

        # Complex cleanup rules
        for rule_mfr, rule_data in categorization_rules.MANUFACTURER_CLEANUP_RULES.items():
            if rule_mfr in mfr_lower:
                new_mfr = rule_data["target_manufacturer"]
                new_model = model.replace(rule_data["remove_from_model"], "").strip()
                return new_mfr, new_model

        # NIC vendor cleanup
        if any(nic in mfr_lower for nic in categorization_rules.NIC_VENDORS):
            if 'lenovo' in model_lower:
                return 'Lenovo', model
            if 'dell' in model_lower:
                return 'Dell', model
            if 'hp' in model_lower or 'hewlett' in model_lower:
                return 'HP', model
            return 'Generic', model
        
        return manufacturer, model
    
    @classmethod
    def _categorize_network_device(cls, model: str, manufacturer: str, device_name: str) -> str | None:
        priority_order = ['Firewall', 'Switch', 'Router', 'Access Point']
        clean_device_name = normalize_for_comparison(device_name)

        # Hostname prefix
        for device_type in priority_order:
            rules = categorization_rules.NETWORK_DEVICE_RULES.get(device_type, {})
            if any(clean_device_name.startswith(prefix) for prefix in rules.get('hostname_prefixes', [])):
                return device_type

        # Vendor and model
        for device_type in priority_order:
            rules = categorization_rules.NETWORK_DEVICE_RULES.get(device_type, {})
            
            vendor_match = any(vendor in manufacturer for vendor in rules.get('vendors', []))
            if vendor_match and model and any(keyword in model for keyword in rules.get('model_keywords', [])):
                return device_type

        return None
    
    @classmethod
    def _categorize_by_services(cls, services: List[str]) -> str | None:
        if not services:
            return None

        service_str = normalize_for_comparison(' '.join(services))
        
        if all(kw in service_str for kw in categorization_rules.SERVICE_RULES['Domain Controller']['service_keywords']):
            return 'Domain Controller'
        if any(svc in service_str for svc in categorization_rules.SERVICE_RULES['Printer']['service_keywords']):
            return 'Printer'
        if any(db in service_str for db in categorization_rules.SERVICE_RULES['Database Server']['service_keywords']):
            return 'Database Server'
        if any(svc in service_str for svc in categorization_rules.SERVICE_RULES['Storage Device']['service_keywords']):
            return 'Storage Device'
        if any(svc in service_str for svc in categorization_rules.SERVICE_RULES['Web Server']['service_keywords']):
            return 'Web Server'
        if any(svc in service_str for svc in categorization_rules.SERVICE_RULES['Network Device']['service_keywords']):
            return 'Network Device'
        return None
    
    @classmethod
    def _categorize_vm(cls, manufacturer: str, model: str, device_name: str) -> Optional[str]:
        if (any(vendor in manufacturer for vendor in categorization_rules.VIRTUAL_MACHINE_RULES['vendors']) and \
           any(kw in model for kw in categorization_rules.VIRTUAL_MACHINE_RULES['model_keywords'])) or \
           any(kw in device_name for kw in categorization_rules.VIRTUAL_MACHINE_RULES.get('hostname_keywords', [])):
            return 'Virtual Machine'
        return None
    
    @classmethod
    def _categorize_container(cls, manufacturer: str, model: str, device_name: str) -> Optional[str]:
        if (any(vendor in manufacturer for vendor in categorization_rules.CONTAINER_RULES['vendors']) and \
           any(kw in model for kw in categorization_rules.CONTAINER_RULES['model_keywords'])) or \
           any(kw in device_name for kw in categorization_rules.CONTAINER_RULES.get('hostname_keywords', [])):
            return 'Container'
        return None

    @classmethod
    def _categorize_server(cls, os_type: str, model: str, device_name: str) -> Optional[str]:
        if any(kw in os_type for kw in categorization_rules.SERVER_RULES['os_keywords']) or \
           any(kw in model for kw in categorization_rules.SERVER_RULES['model_keywords']):
            return 'Server'
        clean_name = normalize_for_comparison(device_name)
        if any(kw in clean_name for kw in categorization_rules.SERVER_RULES.get('hostname_keywords', [])):
            return 'Server'
        return None

    @classmethod
    def _categorize_mobile_device(cls, device_type: Optional[str], model: str, manufacturer: str, os_type: str, device_name: str) -> Optional[str]:
        
        # Type check
        if device_type and device_type.lower() in categorization_rules.MOBILE_DEVICE_RULES['phone_keywords']:
            return 'Mobile Phone'
        
        # Model check
        if any(kw in model for kw in categorization_rules.MOBILE_DEVICE_RULES['tablet_models']):
            return 'Tablet'
        if any(kw in model for kw in categorization_rules.MOBILE_DEVICE_RULES['phone_models']):
            return 'Mobile Phone'
        
        # Name check
        if any(kw in device_name.lower() for kw in categorization_rules.MOBILE_DEVICE_RULES['tablet_models']):
            return 'Tablet'
        if any(kw in device_name for kw in categorization_rules.MOBILE_DEVICE_RULES['phone_models']):
            return 'Mobile Phone'

        # OS check
        if 'ipados' in os_type:
            return 'Tablet'
        if 'ios' in os_type or 'iphone' in os_type:
            if 'ipad' in model or 'ipad' in device_name:
                return 'Tablet'
            return 'Mobile Phone'
        
        if 'android' in os_type:
            if any(kw in model for kw in categorization_rules.ANDROID_RULES.get('tablet_keywords', [])):
                return 'Tablet'
            if any(kw in model for kw in categorization_rules.ANDROID_RULES.get('iot_keywords', [])):
                return 'IoT Device' #Safe guard against miscategorization of Android-based IoT devices
            return 'Mobile Phone'
        
        # 3. Safe Vendor Fallback
        if any(mfr in manufacturer for mfr in categorization_rules.MOBILE_DEVICE_RULES['vendors']):
            # Use weak indicators to confirm it's actually a phone/tablet
            keywords = categorization_rules.MOBILE_DEVICE_RULES.get('phone_keywords', [])
            if any(x in model for x in keywords) or any(x in device_name.lower() for x in keywords):
                return 'Mobile Phone'

        return None

    @classmethod
    def _categorize_computer(cls, os_type: str, model: str, manufacturer: str, device_name: str) -> Optional[str]:

        # Hostname
        if any(kw in device_name for kw in categorization_rules.COMPUTER_RULES['laptop_hostname_keywords']):
            return 'Laptop'
        if any(kw in device_name for kw in categorization_rules.COMPUTER_RULES['desktop_hostname_keywords']):
            return 'Desktop'

        # Vendor prefix
        vendor_result = cls._check_vendor_model_prefix(manufacturer, model)
        if vendor_result:
            return vendor_result

        # Model keyword
        if any(marker in model for marker in categorization_rules.COMPUTER_RULES['laptop_keywords']):
            return 'Laptop'
        if any(marker in model for marker in categorization_rules.COMPUTER_RULES['desktop_keywords']):
            return 'Desktop'

        # OS check 
        if 'windows' in os_type or 'mac' in os_type:
             if any(kw in os_type for kw in categorization_rules.COMPUTER_RULES['desktop_os_keywords']):
                return 'Desktop'
             return 'Desktop'

        return None

    @classmethod
    def _categorize_printer(cls, model: str, manufacturer: str, device_name: str) -> Optional[str]:
        clean_name = normalize_for_comparison(device_name)
        
        # Model keywords
        if any(kw in model for kw in categorization_rules.PRINTER_RULES['model_keywords']):
            return 'Printer'
        
        # Vendor check (requires secondary confirmation to avoid false positives like HP laptops)
        if any(mfr in manufacturer for mfr in categorization_rules.PRINTER_RULES['vendors']):
            if 'printer' in model or any(kw in clean_name for kw in categorization_rules.PRINTER_RULES['hostname_keywords']):
                return 'Printer'

        # Hostname contains Vendor AND Model keyword
        if any(mfr in clean_name for mfr in categorization_rules.PRINTER_RULES['vendors']) and \
           any(kw in clean_name for kw in categorization_rules.PRINTER_RULES['model_keywords']):
            return 'Printer'
            
        # Explicit "Printer" in name
        if 'printer' in clean_name:
            return 'Printer'
            
        return None
    
    @classmethod
    def _categorize_generic_os_device(cls, os_type: str, model: str) -> Optional[str]:
        """Categorize a device based on generic OS and inferred model."""
        if 'windows server' in model or 'linux server' in model:
            return 'Server'
        if 'windows workstation' in model or 'linux workstation' in model or 'macos device' in model:
            return 'Desktop'
        if 'windows' in os_type or 'mac' in os_type or 'linux' in os_type:
            return 'Desktop'
        return None

    @classmethod
    def _categorize_iot(cls, model: str, manufacturer: str, os_type: str, device_name: str) -> Optional[str]:
        
        # Manufacturer check
        if any(kw in manufacturer for kw in categorization_rules.IOT_RULES.get('manufacturer_keywords', [])):
            return 'IoT Device'
        
        # Model keywords
        if any(kw in model for kw in categorization_rules.IOT_RULES.get('model_keywords', [])):
            return 'IoT Device'
        
        # OS keywords
        if any(kw in os_type for kw in categorization_rules.IOT_RULES.get('os_keywords', [])):
            return 'IoT Device'
        
        # Hostname keywords
        for kw in categorization_rules.IOT_RULES.get('hostname_keywords', []):
            if kw in device_name:
                return 'IoT Device'
        
        return None

    @classmethod
    def _categorize_camera(cls, manufacturer: str, model: str, device_name: str) -> Optional[str]:
        clean_name = normalize_for_comparison(device_name)
        if any(vendor in manufacturer for vendor in categorization_rules.CAMERA_RULES.get('vendors', [])):
            return 'Camera'
        if any(kw in model for kw in categorization_rules.CAMERA_RULES.get('model_keywords', [])):
            return 'Camera'
        if any(kw in clean_name for kw in categorization_rules.CAMERA_RULES.get('hostname_keywords', [])):
            return 'Camera'
        return None

    @classmethod
    def _determine_cloud_provider(cls, intune_device: Dict) -> str | None: 
        raw_manufacturer = intune_device.get('manufacturer') or ''
        if isinstance(raw_manufacturer, dict):
            raw_manufacturer = raw_manufacturer.get('name', '') or ''
        manufacturer = raw_manufacturer.lower()
    
        raw_model = intune_device.get('model') or ''
        if isinstance(raw_model, dict):
            raw_model = raw_model.get('name', '') or raw_model.get('model_number', '') or ''
        model = raw_model.lower()
        if 'yealink' in manufacturer:
            return None
        if 'microsoft corporation' in manufacturer and 'virtual machine' in model: 
            return 'Azure'
        if 'amazon' in manufacturer or 'aws' in manufacturer or 'amazon ec2' in model: 
            return 'AWS'
        return 'On-Premise'
    
    @classmethod
    def _determine_business_criticality(cls, device_category: str) -> str | None:
        """Assign business criticality based on device category."""
        if not device_category:
            return None
            
        for criticality, rule in categorization_rules.BUSINESS_CRITILCALITY_RULES.items():
            if device_category in rule.get('categories', []):
                return criticality
        return None

    
    @classmethod
    def _check_vendor_model_prefix(cls, manufacturer: str, model: str) -> Optional[str]:
        """Check vendor-specific model number prefixes."""
        mfr_lower = manufacturer.lower()
        
        if 'lenovo' in mfr_lower:
            model_parts = model.split()
            model_number = None
            for part in model_parts:
                if part.upper() == 'LENOVO': continue
                if part and len(part) >= 2:
                    model_number = part
                    break
            
            if not model_number: model_number = model
            
            laptop_prefixes = categorization_rules.COMPUTER_RULES.get('laptop_vendor_prefixes', {}).get('lenovo', [])
            for prefix in laptop_prefixes:
                if model_number.startswith(prefix): return 'Laptop'
            
            desktop_prefixes = categorization_rules.COMPUTER_RULES.get('desktop_vendor_prefixes', {}).get('lenovo', [])
            for prefix in desktop_prefixes:
                if model_number.startswith(prefix): return 'Desktop'
        
        return None
    
    @classmethod
    def _get_location_from_dhcp_scope(cls, ip: Optional[str]) -> Optional[Dict]:
        if not ip:
            return None

        try:
            target_addr = ip_address(ip)
            for scope in network_config.DHCP_SCOPES:
                start_addr = ip_address(scope['start_ip'])
                end_addr = ip_address(scope['end_ip'])
                if start_addr <= target_addr <= end_addr:
                    return scope
        except (AddressValueError, KeyError):
            return None
        return None
    
    @classmethod
    def categorize(cls, device_data: Dict) -> Dict[str, str]:
 
        # --- 1. Initialization ---
        source = device_data.get('_source', 'unknown')
        ip_address = device_data.get('last_seen_ip')
        nmap_services = device_data.get('nmap_discovered_services', [])

        # --- 2. Static IP Mapping ---
        static_info = None
        if ip_address and cls._is_static_ip(ip_address):
            static_info = cls._categorize_by_static_ip(ip_address)
            
        if static_info:
            device_data.update(static_info)
            static_services_str = static_info.get('services', '')    
            if static_services_str:
                static_services_list = [s.strip() for s in static_services_str.split(',')]
                nmap_services = list(dict.fromkeys(static_services_list + nmap_services))
        
        # --- 3. DHCP Scope Fallback ---        
        if 'location' not in device_data:
            dhcp_info = cls._get_location_from_dhcp_scope(ip_address)
            if dhcp_info and dhcp_info.get('location'):
                device_data['location'] = dhcp_info['location']
        
        # --- 4. Data Normalization ---    
        raw_name = (device_data.get('name') or device_data.get('deviceName') or '')
        raw_os = (device_data.get('os_platform') or device_data.get('operatingSystem') or '')
        
        raw_model = device_data.get('model') or ''
        if isinstance(raw_model, dict):
            raw_model = raw_model.get('name', '') or raw_model.get('model_number', '') or ''
        
        raw_mfr = device_data.get('manufacturer') or ''
        if isinstance(raw_mfr, dict):
            raw_mfr = raw_mfr.get('name', '') or ''
        
        # Hardware Normalization
        norm_mfr, norm_model = cls._normalize_hardware_identity(str(raw_mfr), str(raw_model))
        
        if norm_mfr != raw_mfr:
            device_data['manufacturer'] = norm_mfr
        if norm_model != raw_model:
            device_data['model'] = norm_model
        
        device_name = raw_name.lower()
        os_type = raw_os.lower()
        model = norm_model.lower()
        manufacturer = norm_mfr.lower()
        cloud_provider = cls._determine_cloud_provider(device_data)
        
        raw_serial = (device_data.get('serial') or '')
        log_entry = (
            f"--- Device: {raw_name or 'Unknown'} ---\n"
            f"  Serial:       {raw_serial}\n"
            f"  OS Type:      {raw_os}\n"
            f"  Model:        {raw_model}\n"
            f"  Manufacturer: {raw_mfr}\n"
            f"  Nmap Discovered Services: {', '.join(nmap_services) if nmap_services else 'None'}\n"
            f"  Cloud Provider: {cloud_provider}\n"
            f"{'-'*50}\n"
        )
        debug_logger.log_categorization(source, log_entry)
        
        # --- 5. Categorization ---
        device_type = device_data.get('device_type')
        if not device_type:
            if os_type == 'printer':
                device_type = 'Printer'
            else:
                device_type = (
                    cls._categorize_container(manufacturer, model, device_name) or
                    cls._categorize_vm(manufacturer, model, device_name) or
                    cls._categorize_camera(manufacturer, model, device_name) or
                    cls._categorize_printer(model, manufacturer, device_name) or
                    cls._categorize_iot(model, manufacturer, os_type, device_name) or
                    cls._categorize_network_device(model, manufacturer, device_name) or
                    cls._categorize_mobile_device(device_type, model, manufacturer, os_type, device_name) or
                    cls._categorize_server(os_type, model, device_name) or
                    cls._categorize_computer(os_type, model, manufacturer, device_name) or
                    (cls._categorize_by_services(nmap_services) if nmap_services else None) or
                    cls._categorize_generic_os_device(os_type, model) or
                    'Other Device'
                )

        # --- 6. Category Mapping ---
        category = device_data.get('category') or categorization_rules.CATEGORY_MAP.get(device_type, 'Other Assets')
        if cloud_provider in ['Azure', 'AWS', 'GCP']:
            category = 'Cloud Resources'
            
        business_criticality = cls._determine_business_criticality(category)

        return {
            'device_type': device_type, 
            'category': category, 
            'cloud_provider': cloud_provider,
            'business_criticality': business_criticality
        }