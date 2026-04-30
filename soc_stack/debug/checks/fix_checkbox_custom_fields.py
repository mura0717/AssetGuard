#!/usr/bin/env python3

"""Fix checkbox fields to proper BOOLEAN format if they are not already."""

from soc_stack.snipe_it.snipe_api.services.fields import FieldService

# The checkbox fields that need to be fixed
CHECKBOX_FIELDS = [
    'Intune Managed',
    'Intune Registered',
    'Encrypted',
    'Supervised',
    'EAS Activated',
    'Jailbroken/Rooted',
    'Azure AD Registered',
    'Require User Enrollment Approval'
]

field_service = FieldService()
all_fields = field_service.get_all(refresh_cache=True)

print("="*80)
print("CHANGING CHECKBOX FIELDS TO TEXT")
print("="*80)

fixed_count = 0
already_correct = 0

for field in all_fields:
    if field.get('name') in CHECKBOX_FIELDS:
        field_id = field.get('id')
        field_name = field.get('name')
        
        current_element = field.get('type')
        current_format = field.get('format')
        current_values = field.get('field_values', '')
        
        needs_fix = (
            current_element != 'text' or 
            current_format != 'BOOLEAN' or 
            (current_values and current_values.strip())
        )
        
        if not needs_fix:
            print(f"✓ {field_name} - Already correct")
            already_correct += 1
            continue
        
        print(f"\n→ Fixing: {field_name}")
        print(f"  Current Element: '{current_element}'")
        print(f"  Current Format: {current_format}")
        print(f"  Current Values: '{current_values}'")
        
        # The fix payload
        update_payload = {
            'element': 'text',
            'format': 'BOOLEAN',
            'field_values': ''  # Remove any dropdown options
        }
        
        result = field_service.update(field_id, update_payload)
        
        if result:
            print(f"  ✓ Successfully updated to 'text' element")
            fixed_count += 1
        else:
            print(f"  ✗ Failed to update")

print("\n" + "="*80)
print(f"Summary: {fixed_count} fields fixed, {already_correct} already correct")
print("="*80)