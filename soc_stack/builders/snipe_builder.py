"""
Snipe-IT Payload Builder Module
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional, Set 
from datetime import datetime

from soc_stack.builders.base_builder import BasePayloadBuilder, BuildResult
from soc_stack.states.base_state import StateResult
from soc_stack.snipe_it.snipe_api.services.categories import CategoryService
from soc_stack.snipe_it.snipe_api.services.manufacturers import ManufacturerService
from soc_stack.snipe_it.snipe_api.services.models import ModelService
from soc_stack.snipe_it.snipe_api.services.status_labels import StatusLabelService
from soc_stack.snipe_it.snipe_api.services.locations import LocationService
from soc_stack.snipe_it.snipe_api.services.fields import FieldService
from soc_stack.snipe_it.snipe_api.services.fieldsets import FieldsetService
from soc_stack.asset_engine.asset_categorizer import AssetCategorizer
from soc_stack.loggers.other_asset_logger import OtherAssetLogger
from soc_stack.loggers.new_asset_logger import NewAssetsLogger
from soc_stack.config.snipe_schema import CUSTOM_FIELDS, MODELS, CUSTOM_FIELDSETS
from soc_stack.utils.mac_utils import normalize_mac_semicolon
from soc_stack.utils.text_utils import normalize_for_comparison


class SnipePayloadBuilder(BasePayloadBuilder):
    """
    Handles all Snipe-IT specific payload formatting.
    """
    
    _custom_field_map: Dict[str, str] = {}
    _hydrated = False
    
    # Hierarchy to prevent downgrading models (higher = more capabilities)
    FIELDSET_RANK = {
        'Discovered Assets (Nmap Only)': 1,
        'Network Infrastructure': 2,
        'Cloud Resources (Azure)': 2,
        'Mobile Devices': 2,
        'Managed and Discovered Assets': 3,  # The Superset (Ceiling)
    }
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.status_service = StatusLabelService()
        self.category_service = CategoryService()
        self.manufacturer_service = ManufacturerService()
        self.model_service = ModelService()
        self.location_service = LocationService()
        self.field_service = FieldService()
        self.fieldset_service = FieldsetService()
        self.debug = os.getenv('SNIPE_BUILDER_DEBUG', '0') == '1'
        self._allowed_custom_fields: Optional[Set[str]] = None
        self.other_assets_logger = OtherAssetLogger()
        self.new_assets_logger = NewAssetsLogger()
        
        if not SnipePayloadBuilder._hydrated:
            self._hydrate_field_map()
    
    def build(self, asset_data: Dict, state_result: StateResult) -> BuildResult:
        """Build the final Snipe-IT JSON payload."""
        is_update = state_result.action == 'update'
        
        # Reset allowed fields for this build
        self._allowed_custom_fields = None
        
        # Merge with existing data if updating
        if is_update and state_result.existing:
            working_data = self._merge_with_existing(
                state_result.existing, 
                asset_data, 
                asset_data.get('_source', 'unknown')
            )
        else:
            working_data = asset_data.copy()
        
        # Name Priority
        if working_data.get('host_name'):
            working_data['name'] = working_data['host_name']

        payload = {}
        
        if self.dry_run:
            self._build_dry_run_payload(payload, working_data, is_update)
        else:    
            self._assign_model_manufacturer_category(payload, working_data)
            self._populate_standard_fields(payload, working_data, is_update)
            self._populate_custom_fields(payload, working_data)
            
            if state_result.action == 'create':
                cat_val = working_data.get('category')
                cat_name = cat_val.get('name') if isinstance(cat_val, dict) else str(cat_val)
                self.new_assets_logger.log_new_asset(working_data, cat_name)
        
        return BuildResult(
            payload=payload,
            asset_id=state_result.asset_id,
            action=state_result.action,
            snipe_id=int(state_result.asset_id) if state_result.action == 'update' and state_result.asset_id.isdigit() else None,
            metadata={
                'source': asset_data.get('_source'),
                'name': payload.get('name'),
            }
        )
        
    def _build_dry_run_payload(self, payload: Dict, asset_data: Dict, is_update: bool):
        """Build a simplified payload for dry run without API calls."""
        payload['name'] = asset_data.get('name', 'Unknown Device')
        
        if asset_data.get('serial'):
            payload['serial'] = asset_data['serial']
        
        if asset_data.get('asset_tag'):
            payload['asset_tag'] = asset_data['asset_tag']
        elif not is_update:
            payload['asset_tag'] = self._generate_asset_tag(asset_data)
        
        if asset_data.get('mac_addresses'):
            macs = asset_data['mac_addresses']
            if isinstance(macs, list):
                first_mac = macs[0] if macs else None
            elif isinstance(macs, str):
                first_mac = macs.split('\n')[0]
            else:
                first_mac = str(macs)
            if first_mac:
                payload['mac_address'] = normalize_mac_semicolon(first_mac.strip())
        
        payload['_dry_run'] = True
        payload['_manufacturer'] = asset_data.get('manufacturer', 'Unknown')
        payload['_model'] = asset_data.get('model', 'Unknown')
        payload['_category'] = asset_data.get('category') or asset_data.get('device_type', 'Unknown')
        payload['_source'] = asset_data.get('_source', 'unknown')
        payload['_last_seen_ip'] = asset_data.get('last_seen_ip')
        
        source = asset_data.get('_source', 'unknown')
        if source == 'nmap':
            payload['_status_name'] = 'Discovered - Nmap'
        elif source in ['microsoft365', 'intune']:
            payload['_status_name'] = 'Managed - M365'
        elif source == 'teams':
            payload['_status_name'] = 'Managed - Teams'
        else:
            payload['_status_name'] = 'Unknown'

        # Include what the real sync would resolve to
        payload['_status_would_resolve'] = f"Status label lookup for: {payload['_status_name']}"
        
        for key in ['intune_device_id', 'azure_ad_id', 'teams_device_id', 'primary_user_upn']:
            if asset_data.get(key):
                payload[f'_{key}'] = asset_data[key]

    def _set_allowed_fields_from_fieldset(self, fieldset_name: Optional[str]) -> None:
        """Set allowed custom fields based on fieldset name."""
        if fieldset_name and fieldset_name in CUSTOM_FIELDSETS:
            self._allowed_custom_fields = set(CUSTOM_FIELDSETS[fieldset_name])
            if self.debug:
                print(f"  [Builder] Fieldset '{fieldset_name}' limits to {len(self._allowed_custom_fields)} fields")
        else:
            # Fallback to comprehensive fieldset
            self._allowed_custom_fields = set(CUSTOM_FIELDSETS.get('Managed and Discovered Assets', []))
            if self.debug:
                print(f"  [Builder] Using default fieldset (no match for '{fieldset_name}')")

    def _get_fieldset_name_for_model(self, model: Dict) -> Optional[str]:
        """Get the fieldset name directly from a model object."""
        fieldset = model.get('fieldset')
        if isinstance(fieldset, dict):
            return fieldset.get('name')
        return None

    def _get_fieldset_name_for_category(self, category_obj: Optional[Dict], asset_data: Dict) -> str:
        """Map Category to Fieldset Name."""
        # Priority: Assets with Cloud Identity must use a supporting fieldset
        if asset_data.get('azure_ad_id') or asset_data.get('entra_object_id'):
            cat_name = category_obj.get('name') if isinstance(category_obj, dict) else str(category_obj)
            
            if cat_name in ['Mobile Phones', 'Tablets']:
                return 'Mobile Devices'
            
            return 'Managed and Discovered Assets'

        # Fallback: Category-based rules
        if not category_obj:
            return 'Managed and Discovered Assets'
        
        cat_name = category_obj.get('name') if isinstance(category_obj, dict) else str(category_obj)
        
        if cat_name in ['Switches', 'Routers', 'Firewalls', 'Access Points', 'Cameras', 'Network Devices']:
            return 'Network Infrastructure'
        elif cat_name == 'Printers':
            return 'Discovered Assets (Nmap Only)'
        elif cat_name == 'Cloud Resources':
            return 'Cloud Resources (Azure)'
        elif cat_name in ['Mobile Phones', 'Tablets']:
            return 'Mobile Devices'
        return 'Managed and Discovered Assets'

    def _ensure_model_fieldset_compliance(self, model: Dict, target_fieldset: Optional[Dict]) -> None:
        """Upgrade Model fieldset if current is insufficient."""
        if not model or not target_fieldset:
            return

        current_fs = model.get('fieldset')
        current_name = current_fs.get('name') if isinstance(current_fs, dict) else None
        target_name = target_fieldset.get('name')

        current_rank = self.FIELDSET_RANK.get(current_name, 0)
        target_rank = self.FIELDSET_RANK.get(target_name, 0)

        # Only update if target rank is higher
        if target_rank > current_rank:
            if self.debug:
                print(f"  [Builder] UPGRADING Model '{model.get('name')}' fieldset: "
                      f"'{current_name}' ({current_rank}) -> '{target_name}' ({target_rank})")

            try:
                self.model_service.update(model['id'], {'fieldset_id': target_fieldset['id']})
                model['fieldset'] = target_fieldset
            except Exception as e:
                print(f"  [Builder] Warning: Failed to auto-heal model fieldset: {e}")

    def _ensure_fieldset_filtering(self, model: Optional[Dict], category_obj: Optional[Dict], asset_data: Dict) -> None:
        """Ensure fieldset filtering is set (Model > Category > Default)."""
        if model:
            actual_fieldset = self._get_fieldset_name_for_model(model)
            if actual_fieldset:
                self._set_allowed_fields_from_fieldset(actual_fieldset)
                return
            
            # If model has no fieldset, disable custom fields to prevent rejection
            if 'fieldset' in model and model['fieldset'] is None:
                if self.debug:
                    print(f"  [Builder] Model '{model.get('name')}' has no fieldset. Disabling custom fields.")
                self._allowed_custom_fields = set()
                return
        
        fieldset_name = self._get_fieldset_name_for_category(category_obj, asset_data)
        self._set_allowed_fields_from_fieldset(fieldset_name)

    def _assign_model_manufacturer_category(self, payload: Dict, asset_data: Dict):
        category_obj = self._determine_category(asset_data)
        
        self._ensure_fieldset_filtering(None, category_obj, asset_data)
        mfr_name, model_name = self._extract_mfr_and_model_names(asset_data)

        if self.debug:
            print(f"Processing model for asset '{asset_data.get('name', 'Unknown')}'. "
                  f"Manufacturer: '{mfr_name}', Model: '{model_name}'")

        is_generic = normalize_for_comparison(model_name) in [
            normalize_for_comparison(m['name']) for m in MODELS if 'Generic' in m['name']
        ]

        if mfr_name and model_name and not is_generic:
            self._handle_specific_model(payload, asset_data, mfr_name, model_name, category_obj)
        else:
            self._assign_generic_model(payload, asset_data, category_obj)

        if category_obj and 'category_id' not in payload:
            payload['category_id'] = category_obj['id']
        
        # Ensure filtering is set before populating custom fields
        if self._allowed_custom_fields is None:
            self._ensure_fieldset_filtering(None, category_obj, asset_data)

    def _handle_specific_model(self, payload: Dict, asset_data: Dict, mfr_name: str, 
                                model_name: str, category_obj: Dict):
        manufacturer = self.manufacturer_service.get_or_create({'name': mfr_name})
        if not manufacturer or not category_obj:
            return
        
        payload['manufacturer_id'] = manufacturer['id']
        payload['category_id'] = category_obj['id']
        fieldset = self._determine_fieldset(category_obj, asset_data)

        full_model_name = self._build_full_model_name(mfr_name, model_name)
        model = self._get_or_create_model(full_model_name, manufacturer, category_obj, fieldset)

        if model:
            payload['model_id'] = model['id']
            self._ensure_fieldset_filtering(model, category_obj, asset_data)

    def _assign_generic_model(self, payload: Dict, asset_data: Dict, category_obj: Optional[Dict] = None):
        if 'model_id' in payload:
            return
        
        device_type = str(asset_data.get('device_type') or '').lower()
        generic_name = self._determine_model_name(device_type)
        generic_model = self.model_service.get_by_name(generic_name)
        
        target_fieldset = self._determine_fieldset(category_obj, asset_data)
        
        if not generic_model and category_obj:
            if self.debug:
                print(f"[_assign_generic_model] Creating missing generic model: '{generic_name}'")
            
            generic_mfr = self.manufacturer_service.get_or_create({'name': 'Generic'})
            generic_model = self._create_model_internal(
                name=generic_name,
                mfr=generic_mfr,
                cat=category_obj,
                fieldset=target_fieldset
            )
        
        if generic_model:
            # Ensure generic model is capable enough
            self._ensure_model_fieldset_compliance(generic_model, target_fieldset)

            payload['model_id'] = generic_model['id']
            self._ensure_fieldset_filtering(generic_model, category_obj, asset_data)
            
            if category_obj:
                payload['category_id'] = category_obj['id']
            elif 'category_id' not in payload and generic_model.get('category'):
                payload['category_id'] = generic_model.get('category', {}).get('id')
        else:
            fallback = self.model_service.get_by_name('Generic Unknown Device')
            if fallback:
                payload['model_id'] = fallback['id']
                self._ensure_fieldset_filtering(fallback, category_obj, asset_data)
            else:
                self._ensure_fieldset_filtering(None, category_obj, asset_data)

    def _determine_category(self, asset_data: Dict) -> Dict:
        """Determine category/device_type with anti-downgrade protection."""
        existing_type = asset_data.get('device_type')
        existing_cat = asset_data.get('category')
        if isinstance(existing_cat, dict):
            existing_cat = existing_cat.get('name')

        # Recalculate on clean copy using only hardware facts
        temp_data = asset_data.copy()
        temp_data.pop('device_type', None)
        temp_data.pop('category', None)
        
        classification = AssetCategorizer.categorize(temp_data)
        
        fresh_type = classification.get('device_type')
        fresh_cat = classification.get('category')

        GENERIC_TYPES = frozenset({
            'Other Device', 'other device', 
            'Unknown', 'unknown', 
            'Generic Unknown Device',
            '', None
        })
        
        old_is_specific = existing_type and existing_type not in GENERIC_TYPES
        new_is_generic = fresh_type in GENERIC_TYPES
        
        final_cat_name = None

        if old_is_specific and new_is_generic:
            if self.debug:
                print(f"[_determine_category] PREVENTED DOWNGRADE '{asset_data.get('name')}': "
                      f"Kept '{existing_type}' instead of '{fresh_type}'")
            asset_data['device_type'] = existing_type
            asset_data['category'] = existing_cat
            final_cat_name = existing_cat
        else:
            if self.debug and existing_type != fresh_type:
                arrow = "->" if existing_type else "NEW"
                print(f"[_determine_category] CLASSIFICATION {arrow} '{asset_data.get('name')}': "
                      f"'{existing_type}' -> '{fresh_type}'")
            
            asset_data['device_type'] = fresh_type
            asset_data['category'] = fresh_cat
            final_cat_name = fresh_cat

        final_cat_name = final_cat_name or 'Other Assets'

        # Log suspicious/uncategorized assets
        if final_cat_name in ['Other Assets', 'Other Device', 'Unknown', 'Generic']:
            self.other_assets_logger.log_other_asset(asset_data, final_cat_name)
        
        return self.category_service.get_or_create({
            'name': final_cat_name, 
            'category_type': 'asset'
        })

    def _determine_model_name(self, device_type: str) -> str:
        device_type = device_type.lower()
        model_map = {
            'server': 'Generic Server', 
            'camera': 'Generic Camera', 
            'desktop': 'Generic Desktop', 
            'laptop': 'Generic Laptop', 
            'switch': 'Generic Switch', 
            'router': 'Generic Router',
            'firewall': 'Generic Firewall', 
            'access point': 'Generic Access Point', 
            'printer': 'Generic Printer', 
            'virtual machine': 'Generic Virtual Machine', 
            'container': 'Generic Container',
            'iot device': 'Generic IoT Device',
            'mobile phone': 'Generic Mobile Phone',
            'tablet': 'Generic Tablet',
            'network device': 'Generic Network Device',
            'storage device': 'Generic Storage Device'
        }
        for key, name in model_map.items():
            if key in device_type:
                return name
        return 'Generic Unknown Device'

    def _determine_fieldset(self, category_obj: Dict, asset_data: Dict) -> Optional[Dict]:
        fieldset_name = self._get_fieldset_name_for_category(category_obj, asset_data)
        return self.fieldset_service.get_by_name(fieldset_name)

    def _build_full_model_name(self, mfr: str, model: str) -> str:
        if normalize_for_comparison(model).startswith(normalize_for_comparison(mfr)):
            return model
        return f"{mfr} {model}"

    def _get_or_create_model(self, name: str, mfr: Dict, cat: Dict, 
                              fieldset: Optional[Dict]) -> Optional[Dict]:
        model = self.model_service.get_by_name(name)
        if model:
            # Check existing models for compliance
            self._ensure_model_fieldset_compliance(model, fieldset)
            return model
        
        return self._create_model_internal(name, mfr, cat, fieldset)

    def _create_model_internal(self, name: str, mfr: Dict, cat: Dict, fieldset: Optional[Dict]) -> Optional[Dict]:
        data = {
            'name': name, 
            'manufacturer_id': mfr['id'], 
            'category_id': cat['id'], 
            'model_number': name
        }
        if fieldset:
            data['fieldset_id'] = fieldset['id']
        
        return self.model_service.create(data)    
    
    def _merge_with_existing(self, existing: Dict, new_data: Dict, scan_type: str) -> Dict:
        """Merge new scan data with existing asset data."""
        merged = self._flatten_existing_asset(existing)
        
        sources = new_data.get("_sources") or [scan_type]
        sources = [s for s in sources if s]

        priority_map = {
            'nmap': ['last_seen_ip', 'nmap_last_scan', 'nmap_open_ports', 
                     'nmap_discovered_services', 'nmap_os_guess', 'open_ports_hash'],
            'microsoft365': ['intune_last_sync', 'intune_compliance', 
                            'primary_user_upn', 'primary_user_email'],
            'intune': ['intune_last_sync', 'intune_compliance', 
                       'primary_user_upn', 'primary_user_email'],
        }

        priority_fields = set()
        for s in sources:
            priority_fields.update(priority_map.get(s, []))
        
        GENERIC_VALUES = frozenset({
            'generic', 'unknown', 'other', 'other device', 'other assets',
            'generic unknown device', '', 'none', 'n/a'
        })
        
        def _is_generic(v) -> bool:
            if v is None: return True
            s = str(v).strip().lower()
            if key == 'name' and (s.startswith('device-') or s.startswith('unknown')):
                return True
            return s in GENERIC_VALUES
        
        # Fields to always upgrade if existing value is generic
        ALWAYS_UPGRADE = {
            'manufacturer', 'model', 'os_platform', 'device_type', 
            'category', 'serial', 'name'
        }

        for key, value in new_data.items():
            if value in (None, '', []):
                continue
            
            existing_val = merged.get(key)

            # Allow overwriting "Generic" values
            if key in ALWAYS_UPGRADE and _is_generic(existing_val) and not _is_generic(value):
                merged[key] = value
                continue

            if key in priority_fields or not existing_val:
                merged[key] = value
        
        merged['_source'] = scan_type
        return merged

    def _flatten_existing_asset(self, existing: Dict) -> Dict:
        """Flatten Snipe-IT API response to simple key-value pairs."""
        flattened = {}
        
        for key, value in existing.items():
            if key == 'custom_fields':
                continue
            elif isinstance(value, dict):
                flattened[key] = value.get('name') or value.get('id')
            else:
                flattened[key] = value
        
        for label, field_data in existing.get('custom_fields', {}).items():
            value = field_data.get('value') if isinstance(field_data, dict) else field_data
            for key, field_def in CUSTOM_FIELDS.items():
                if field_def.get('name') == label:
                    flattened[key] = value
                    break
        
        return flattened
    
    def _extract_mfr_and_model_names(self, asset_data: Dict) -> tuple:
        mfr = asset_data.get('manufacturer')
        model = asset_data.get('model')
        mfr_str = mfr.get('name') if isinstance(mfr, dict) else mfr
        model_str = model.get('name') if isinstance(model, dict) else model
        return str(mfr_str or '').strip(), str(model_str or '').strip()

    def _populate_standard_fields(self, payload: Dict, asset_data: Dict, is_update: bool):
        for field in ['name', 'asset_tag', 'serial', 'notes']:
            if asset_data.get(field):
                payload[field] = asset_data[field]
            
        if asset_data.get('mac_addresses'):
            macs = asset_data['mac_addresses']
            if isinstance(macs, list):
                first_mac = macs[0] if macs else None
            elif isinstance(macs, str):
                first_mac = macs.split('\n')[0]
            else:
                first_mac = str(macs)
                
            if first_mac:
                payload['mac_address'] = normalize_mac_semicolon(first_mac.strip())
            
        if not is_update and 'asset_tag' not in payload:
            payload['asset_tag'] = self._generate_asset_tag(asset_data)
            
        self._assign_location(payload, asset_data)
        self._determine_status(payload, asset_data)

    def _determine_status(self, payload: Dict, asset_data: Dict):
        if 'status_id' in payload:
            return
        source = asset_data.get('_source', 'unknown')
        status_name = 'Discovered - Nmap' if source == 'nmap' else 'Unknown'
        if source in ['microsoft365', 'intune']:
            status_name = 'Managed - M365'
        
        status = self.status_service.get_by_name(status_name)
        if status:
            payload['status_id'] = status['id']

    def _assign_location(self, payload: Dict, asset_data: Dict):
        loc_name = asset_data.get('location')
        if not loc_name:
            return
        if isinstance(loc_name, dict):
            loc_name = loc_name.get('name')
        
        location = self.location_service.get_by_name(loc_name)
        if not location:
            location = self.location_service.create({'name': loc_name})
        if location:
            payload['location_id'] = location['id']

    def _generate_asset_tag(self, asset_data: Dict) -> str:
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = json.dumps(asset_data, sort_keys=True, default=str)
        hash_part = hashlib.md5(hash_input.encode()).hexdigest()[:6].upper()
        return f"AUTO-{ts}-{hash_part}"

    def _populate_custom_fields(self, payload: Dict, asset_data: Dict):
        if not SnipePayloadBuilder._hydrated:
            self._hydrate_field_map()
        
        fields_added = 0
        fields_skipped = 0
        
        for field_key, field_def in CUSTOM_FIELDS.items():
            # Skip fields not in current fieldset
            if self._allowed_custom_fields is not None:
                if field_key not in self._allowed_custom_fields:
                    fields_skipped += 1
                    continue
            
            val = asset_data.get(field_key)
            db_key = SnipePayloadBuilder._custom_field_map.get(field_key)
            
            if val is not None and db_key:
                if isinstance(val, str) and not val.strip():
                    continue
                formatted = self._format_custom_value(field_key, val, field_def)
                if formatted is not None:
                    payload[db_key] = formatted
                    fields_added += 1
        
        if self.debug:
            print(f"  [Builder] Custom fields: {fields_added} added, {fields_skipped} filtered out")

    def _hydrate_field_map(self):
        if SnipePayloadBuilder._hydrated:
            return
        
        config_map = {normalize_for_comparison(v['name']): k for k, v in CUSTOM_FIELDS.items()}
        server_fields = self.field_service.get_all(refresh_cache=True) or []
        
        for field in server_fields:
            name = normalize_for_comparison(field.get('name', ''))
            key = config_map.get(name)
            if key and field.get('db_column_name'):
                SnipePayloadBuilder._custom_field_map[key] = field['db_column_name']
        
        if self.debug:
            print(f"[DEBUG] Hydrated {len(SnipePayloadBuilder._custom_field_map)} custom field mappings.")
            if len(SnipePayloadBuilder._custom_field_map) < len(CUSTOM_FIELDS):
                missing = [k for k in CUSTOM_FIELDS if k not in SnipePayloadBuilder._custom_field_map]
                print(f"[WARNING] Could not find server mapping for keys: {missing}")
        
        SnipePayloadBuilder._hydrated = True

    def _format_custom_value(self, key: str, val: Any, field_def: Dict) -> Optional[str]:
        if field_def.get('format') == 'BOOLEAN':
            return "1" if str(val).lower() in ('true', '1', 'yes', 'on') else "0"
        if isinstance(val, (dict, list)):
            return json.dumps(val, indent=2) if field_def.get('element') == 'textarea' else str(val)
        return str(val)