# Put this in a shared file, e.g. debug/tools/json_log_parser.py

import os
import json
from typing import List, Dict, Any

def parse_raw_debug_log(filepath: str) -> List[Dict[Any, Any]]:
    """
    Parses any of your raw debug logs (intune, teams, ms365 raw-unmerged, etc.)
    Works reliably even with:
    - Pretty-printed JSON
    - Concatenated objects
    - Timestamps + --- RAW DATA --- separators
    - Windows/Linux line endings
    """
    if not os.path.exists(filepath):
        print(f"Error: Log file not found: {filepath}")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    assets = []
    pos = 0
    length = len(content)

    while pos < length:
        # Find next opening brace
        brace_pos = content.find('{', pos)
        if brace_pos == -1:
            break

        # Find the matching closing brace (handles nested braces and strings properly)
        depth = 1
        i = brace_pos + 1
        in_string = False
        escape = False

        while i < length:
            c = content[i]

            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_string = not in_string
            elif not in_string:
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        # Found complete JSON object
                        try:
                            obj = json.loads(content[brace_pos:i+1])
                            assets.append(obj)
                        except json.JSONDecodeError as e:
                            print(f"Warning: Failed to parse JSON at position {brace_pos}: {e}")
                        pos = i + 1
                        break
            i += 1
        else:
            # Reached EOF without closing brace → broken last object
            break

    print(f"Successfully parsed {len(assets)} assets from {os.path.basename(filepath)}")
    return assets