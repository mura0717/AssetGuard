#!/usr/bin/env python3
"""
Snipe-IT DB connection.
"""

import os
import pymysql
from pathlib import Path
import paramiko

def _patch_paramiko_compatibility():
    #Patches paramiko.DSSKey if missing to prevent sshtunnel crashes.
    if not hasattr(paramiko, 'DSSKey'):
        class DSSKey:
            @classmethod
            def from_private_key_file(cls, filename, password=None):
                raise paramiko.SSHException("DSSKey not supported")
        paramiko.DSSKey = DSSKey

_patch_paramiko_compatibility()

from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
ENV_PATH = BASE_DIR / '.env'

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()

class SnipeItDbConnection():
    
    def __init__(self):
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_pass = os.getenv("DB_PASS")
        self.db_name = os.getenv("DB_NAME")
        self.db_port = int(os.getenv("DB_PORT", 3306))
        self.db_ssh_user = os.getenv("DB_SSH_USER")
        self.db_ssh_key_path = os.getenv("DB_SSH_KEY_PATH")
        self.db_ssh_port = int(os.getenv("DB_SSH_PORT", 22))
        self.tunnel = None
        self.connection = None

    def db_connect(self):
        """Establishes and returns a database connection via SSH tunnel if not local."""
        connection = None
        print("Attempting to connect to Snipe-IT database...")
        try:
            if self.db_ssh_user and self.db_ssh_key_path:
                print("Using SSH tunnel for database connection...")
                self.tunnel = SSHTunnelForwarder(
                    (self.db_host, self.db_ssh_port),
                    ssh_username=self.db_ssh_user,
                    ssh_pkey=self.db_ssh_key_path,
                    remote_bind_address=('127.0.0.1', self.db_port)
                )
                self.tunnel.start()
                print(f"-> Tunnel established! Forwarding localhost:{self.tunnel.local_bind_port} -> {self.db_host}:{self.db_port}")
                connection = pymysql.connect(host='127.0.0.1', user=self.db_user, password=self.db_pass, database=self.db_name, port=self.tunnel.local_bind_port, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
                print("✓ Database connection successful")
                return connection
            else:
                print("Using local database connection...")
                connection = pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass, database=self.db_name, port=self.db_port, connect_timeout=5, cursorclass=pymysql.cursors.DictCursor)
                print("✓ Database connection successful")
                return connection
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            self.close_tunnel()
            return None
    
    def db_disconnect(self, connection):
        """Closes the database connection."""
        if connection:
            try:
                if connection.open:
                    connection.close()
                    print("✓ Database connection closed")
                else:
                    print("-> Database connection was already closed")
            except Exception as e:
                print(f"-> Warning: Error closing connection: {e}")
        self.close_tunnel()
        

    def close_tunnel(self):
        """Safely closes the SSH tunnel."""
        if self.tunnel:
            self.tunnel.stop()
            self.tunnel = None
            print("-> SSH Tunnel closed")