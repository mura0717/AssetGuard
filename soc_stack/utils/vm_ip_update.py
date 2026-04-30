#!/usr/bin/env python3

"""
A utility script to update the IP address for the Snipe-IT application
in the Nginx configuration and .env files after a VM reboot.

This is useful for development environments on a VM where the IP may
change after a reboot.

This script requires sudo privileges to modify system files and restart services.
It will prompt for a password if not run as root.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

# --- Configuration ---
NGINX_CONF_FILE = os.getenv("NGINX_CONF_FILE") or "/etc/nginx/sites-available/snipe-it"
APACHE_CONF_FILE = os.getenv("APACHE_CONF_FILE") or "/etc/apache2/sites-available/snipe-it.conf"
SNIPE_IT_ENV_FILE = os.getenv("SNIPE_IT_ENV_FILE") or "/var/www/snipe-it/.env"
SNIPE_IT_DIR = os.getenv("SNIPE_IT_DIR") or "/var/www/snipe-it"

# --- Sudo Elevation ---
# If the script is not run as root, re-launch it with sudo.
if os.geteuid() != 0:
    print("Root privileges are required. Attempting to elevate...")
    try:
        # Re-execute the script with sudo
        args = ['sudo', sys.executable] + sys.argv
        subprocess.run(args, check=True)
        # Exit the non-privileged script
        sys.exit(0)
    except subprocess.CalledProcessError:
        print("Failed to elevate privileges. Please run with 'sudo'.")
        sys.exit(1)

def get_ip_address() -> str:
    """Gets the primary IP address of the machine."""
    try:
        # 'hostname -I' can return multiple IPs, we want the first one.
        result = subprocess.run(
            ['hostname', '-I'],
            capture_output=True,
            text=True,
            check=True
        )
        ip_address = result.stdout.strip().split()[0]
        print(f"✓ Detected IP Address: {ip_address}")
        return ip_address
    except (subprocess.CalledProcessError, IndexError) as e:
        print(f"✗ ERROR: Could not determine IP address. {e}")
        sys.exit(1)

def run_command(command, description):
    """Runs a command and prints status."""
    print(f"-> {description}...")
    try:
        # The commands are constructed internally, so it's safe here.
        subprocess.run(command, shell=True, check=True, capture_output=True)
        print(f"  ✓ Success")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ FAILED: {description}")
        print(f"    Error: {e.stderr.decode() if e.stderr else e}")
        sys.exit(1)

def update_config_file(file_path: str, new_ip: str):
    """Updates the APP_URL/SNIPE_URL in a .env file or server_name in Nginx config."""
    if not os.path.exists(file_path):
        print(f"  ! Skipping: File not found at {file_path}")
        return

    # This sed command finds a line with APP_URL, SNIPE_URL, or server_name and replaces
    # the IP address or domain with the new IP. It's safe to run multiple times.
    # It handles both http:// and https:// prefixes.
    sed_command = (
        fr"sed -i -E "
        f"'s|(APP_URL=https?://)[^/]+|\\1{new_ip}|g; "
        f"s|(server_name )[^;]+;|\\1{new_ip};|g; "
        f"s|(ServerName\\s+)[^\\s]+|\\1{new_ip}|g; "
        f"s|(SNIPE_URL=https?://)[^/]+|\\1{new_ip}|g' "
        f"{file_path}"
    )
    run_command(sed_command, f"Updating IP in {os.path.basename(file_path)}")

def main():
    """Main execution function."""
    ip_address = get_ip_address()

    print("\n--- Updating Configuration Files ---")
    update_config_file(NGINX_CONF_FILE, ip_address)
    update_config_file(APACHE_CONF_FILE, ip_address)
    update_config_file(SNIPE_IT_ENV_FILE, ip_address)

    print("\n--- Restarting Services ---")
    if os.path.exists("/etc/nginx/sites-enabled/snipe-it"):
        run_command("systemctl restart nginx", "Restarting Nginx")
    if os.path.exists("/etc/apache2/sites-enabled/snipe-it.conf"):
        run_command("systemctl restart apache2", "Restarting Apache")

    print("\n--- Clearing Snipe-IT Caches ---")
    # Run artisan commands as the 'www-data' user from the correct directory.
    run_command(f"cd {SNIPE_IT_DIR} && sudo -u www-data php artisan cache:clear", "Clearing application cache")
    run_command(f"cd {SNIPE_IT_DIR} && sudo -u www-data php artisan view:clear", "Clearing view cache")
    run_command(f"cd {SNIPE_IT_DIR} && sudo -u www-data php artisan config:clear", "Clearing config cache")

    print("\n✅ IP Address update process completed successfully!")

if __name__ == "__main__":
    main()
