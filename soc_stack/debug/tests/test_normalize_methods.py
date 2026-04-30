#!/usr/bin/env python3

"""
Test text normalization.
"""

import soc_stack.utils.text_utils as text_utils

inputs = ["TL-SG108PE.Diabetes.local"]

for input in range (len(inputs)):
    after_display_normalized = text_utils.normalize_for_display(name=inputs[input])
    print(f"Display normalized: '{after_display_normalized}'")
   
    after_comparison_normalized = text_utils.normalize_for_comparison(text=inputs[input])
    print(f"Comparison normalized: '{after_comparison_normalized}'")
          
