"""
Utility functions for handling sudo elevation
"""

import os
import sys

def elevate_to_root():
    """
    Auto-elevate the current script to root privileges using sudo.
    Replaces the current process with the elevated one.
    """
    if os.geteuid() != 0:
        print("Root privileges are required. Attempting to elevate...")
        args = ['sudo', sys.executable] + sys.argv
        try:
            os.execvp('sudo', args)
        except OSError as e:
            print(f"ERROR: Failed to elevate privileges: {e}")
            sys.exit(1)
