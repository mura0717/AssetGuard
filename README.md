# AssetGuard Documentation

## 1. What the Code Does

AssetGuard is as an automated, centralized asset pipeline (dubbed "Project Hydra") for a basic Security Operations Center (SOC). It gathers, deduplicates, and distributes device data across the network without requiring agent installations for discovery.

**Core Workflow:**

* **Collect:** Gathers asset data from Microsoft 365 (Intune, Teams) and actively scans the local network and remote branches using Nmap.
* **Match & Deduplicate:** Cross-checks the discovered devices against existing inventory using MAC addresses, IP addresses, serial numbers, and hostnames to ensure a single source of truth and avoid duplicates.
* **Dispatch:** Formats and sends the finalized asset data to three open-source SOC tools:
* **Snipe-IT:** For IT Asset Management (ITAM).
* **Zabbix:** For operational and uptime monitoring.
* **Wazuh:** For SIEM (Security Information and Event Management) and vulnerability monitoring.



## 2. Necessary Setup

For the code to function correctly, you need the following prerequisites:

* **Python Environment:** Python 3.x installed along with the required dependencies (found in `requirements.txt`).
* **System Packages:** `nmap` and `git` installed on the host running the script.
* **Privileges:** The user executing the script requires `sudo` privileges to run raw-socket Nmap scans without a password prompt.
* **Active SOC Endpoints:** Running instances of Snipe-IT, Zabbix (v6.0+), and Wazuh.
* **Environment Configuration:** A fully configured `.env` file (based on the provided `env_sample`) placed in the project root containing API keys, database credentials, and IP configurations.
* **Wazuh Agent:** A Wazuh agent installed on the same machine running the script to forward locally generated JSON logs to the Wazuh Manager.

### Wazuh Integration & Custom Alerts Setup

The script does not send data directly to the Wazuh indexer. Instead, it appends event logs to a local file (`/opt/proxmox-basic-soc/logs/wazuh_events.jsonl`).

**Step 1: Configure the Local Agent**
Add the following block to `/var/ossec/etc/ossec.conf` on the machine running the script to ingest the logs:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/opt/proxmox-basic-soc/logs/wazuh_events.jsonl</location>
</localfile>
```

**Step 2: Add Custom Rules on the Wazuh Manager**
To generate alerts from the pipeline's data, add the following custom rules to `/var/ossec/etc/rules/local_rules.xml` on your Wazuh Manager. These rules use the built-in `json` decoder and look for specific event actions:

```xml
<group name="hydra,asset_scan,">
  <rule id="100003" level="3">
    <decoded_as>json</decoded_as>
    <field name="hydra_event_type">hydra_asset_scan</field>
    <description>Hydra: Asset Scan Event</description>
  </rule>

  <rule id="100004" level="5">
    <if_sid>100003</if_sid>
    <field name="event_action">create</field>
    <description>Hydra: New Asset Discovered - $(asset.name)</description>
    <group>hydra_new_asset,</group>
  </rule>

  <rule id="100005" level="4">
    <if_sid>100003</if_sid>
    <field name="event_action">update</field>
    <description>Hydra: Asset Updated - $(asset.name)</description>
    <group>hydra_asset_update,</group>
  </rule>

  <rule id="100006" level="7">
    <if_sid>100003</if_sid>
    <field name="related_agent.status">not_found</field>
    <description>Hydra: Unmanaged Device Detected</description>
    <group>hydra_unmanaged,</group>
  </rule>

  <rule id="100007" level="10">
    <if_sid>100006</if_sid>
    <field name="security.open_ports">22|3389|445</field>
    <description>CRITICAL: Unmanaged device with sensitive ports open - $(asset.name) at $(asset.ip)</description>
    <group>hydra_critical,security_gap,</group>
  </rule>
</group>
```


## 3. How to Use the Code

The pipeline is executed via the main orchestrator script. It offers multiple command-line arguments to customize runs, test data, and target specific integrations.

**Basic Execution (Full Sync):**
Runs data collection from all sources and dispatches to all integrations.

```bash
python -m proxmox_soc.hydra_orchestrator
```

**Dry Run Mode:**
Executes the entire pipeline without making actual API calls or changes. It writes the generated payloads to local log files for review.

```bash
python -m proxmox_soc.hydra_orchestrator --dry-run
```

**Source-Specific Options:**
Target specific data sources instead of running everything.

* Run only Nmap scans: `python -m proxmox_soc.hydra_orchestrator --source nmap`
* Run Nmap with a specific profile (e.g., discovery, detailed): `python -m proxmox_soc.hydra_orchestrator --nmap discovery`
* Run only Microsoft 365 (Intune/Teams): `python -m proxmox_soc.hydra_orchestrator --ms365`

**Integration-Specific Options:**
Include or exclude specific target destinations.

* Run *only* specific integrations: `python -m proxmox_soc.hydra_orchestrator --only snipe wazuh`
* Exclude specific integrations:
* `python -m proxmox_soc.hydra_orchestrator --skip-zabbix`
* `python -m proxmox_soc.hydra_orchestrator --skip-snipe`
* `python -m proxmox_soc.hydra_orchestrator --skip-wazuh`



**Testing & Debugging Options:**

* Run system tests instead of a sync: `python -m proxmox_soc.hydra_orchestrator --test`
* Enable verbose output for detailed troubleshooting: `python -m proxmox_soc.hydra_orchestrator --verbose`


## 4. Debugging and Logging Tools

The project includes several utilities to help monitor, troubleshoot, and test the pipeline safely.

### Categorize from Logs

Located in `proxmox_soc/debug/categorize_from_logs/`, these scripts allow you to test the categorization logic (device types, models, manufacturers) against offline JSON dumps without hitting live APIs.

* Available scripts: `intune_categorize_from_logs.py`, `ms365_categorize_from_logs.py`, `nmap_categorize_from_logs.py`, `teams_categorize_from_logs.py`.
* **Usage:** Run them to see exactly how raw data is parsed and labeled by the engine before it reaches Snipe-IT.

### Integration Tests

Located in `proxmox_soc/debug/tests/`, these scripts verify the health and logic of individual components.

* `test_api_connections.py`: Verifies authentication and connectivity to Snipe-IT, Zabbix, and Wazuh APIs.
* `test_deduplication.py` / `test_ms365_merge.py`: Tests the logic that merges redundant assets.
* `test_hydra.py`: Runs a mock integration test.

### Snipe Snapshotter

Located at `proxmox_soc/snipe_it/snipe_scripts/log/snipe_snapshotter.py`.

* **Purpose:** Before running massive updates or tests, this script takes a snapshot of the current Snipe-IT asset inventory and saves it locally. It acts as a fail-safe allowing you to review the original state if the pipeline overwrites something unexpectedly.

### Asset Loggers

The pipeline uses specialized loggers to record specific actions into organized files:

* `new_asset_logger`: Records details of completely newly discovered devices that are being created for the first time.
* `other_asset_logger`: Records devices that are merely being updated (e.g., an IP change) or skipped (because no data changed).
* `failure_logger`: Catches and logs instances where an asset fails to sync due to missing fields, API timeouts, or validation errors.

### Debug Logs (Verbose Mode)

When running the orchestrator with the `--verbose` (or `-v`) flag, the system prints deep debug logs. These logs show:

* The final resolved URLs being targeted (useful for verifying proxy vs. direct IP routing).
* The raw HTTP responses and status codes from the SOC endpoints.
* The exact, formatted JSON payloads being dispatched to Snipe-IT, Zabbix, and Wazuh just before transmission.


## 5. Proxmox LXC Project Setup (Reference Architecture)

This architecture details a "Zero Budget" multi-node Proxmox Virtual Environment (VE) setup. It utilizes 4 physical nodes configured as a single cluster, running Debian Linux Containers (LXC).

### Infrastructure Layout

* **Node 1 (Scanner / "The Hydra" / Nginx Reverse Proxy):** Runs the Python pipeline, Nmap, and reverse proxy.
* **Node 2 (Wazuh AIO):** Wazuh Manager, Indexer, and Dashboard.
* **Node 3 (Zabbix):** Zabbix Server and database.
* **Node 4 (Snipe-IT):** Apache, PHP, and MariaDB.

### Network Configuration (VLAN-Aware Bridge)

To allow the scanner (Node 1) to perform Layer 2 ARP scans across multiple subnets and bypass inter-VLAN firewalls:




1. **Physical Switch:** The physical port connected to Node 1 is configured as a **Trunk** port (e.g., allowing your primary management VLAN and any specific target VLANs to be scanned).
2. **Proxmox Bridge:** The virtual bridge (`vmbr0`) on Node 1 is set to **VLAN Aware**.
3. **Scanner LXC (Multi-Homed):** The scanner container is assigned multiple virtual network interfaces directly connected to target VLANs. **These should be customized to match your specific network topography.** For example:


* `eth0`: Your Management VLAN (e.g., VLAN 10 - provides Internet access and Gateway for Layer 3 routed scans).
* `eth1`: Target Subnet A (e.g., VLAN 20 - Corporate/Client devices, no gateway).
* `eth2`: Target Subnet B (e.g., VLAN 30 - Guest WiFi or IoT network, no gateway).



### Key Security & Operational Configurations

* **Snipe-IT Database (SSH Tunneling):** Instead of opening MariaDB to the network (port 3306), MariaDB is bound strictly to `127.0.0.1`. The Python scanner establishes an automated SSH tunnel to the Snipe-IT container to perform administrative database tasks securely.
* **Scanner Sudo Privileges:** A dedicated user runs the Python script. To allow Nmap to perform OS fingerprinting and ARP pings, passwordless sudo is configured strictly for the Python executable in the sudoers file.
* **Zabbix Agent 2 Systemd Fix (Debian LXC):**
  If the Zabbix agent fails to start after a container reboot due to a missing `/run/zabbix` PID folder, a systemd override ensures the directory is created:

```ini
# sudo systemctl edit zabbix-agent2
[Service]
RuntimeDirectory=zabbix
RuntimeDirectoryMode=0755
```


* **Logging Fix for Debian 13 LXC:**
  In Debian 13 containers, `systemd-journald` often fails due to namespace restrictions. To ensure the script's `logger` commands function correctly:




1. Mask `systemd-journald` services.
2. Create a systemd override for `rsyslog` setting sandboxing features (`PrivateDevices`, `ProtectSystem`, etc.) to `no`.
3. Configure the `imuxsock` module in `/etc/rsyslog.d/00-imuxsock.conf` to create the `/dev/log` socket directly.



## 6. Appendix: Resource Allocation & ZRAM Settings

For environments with strict hardware limitations (e.g., 8GB RAM or less per node), ZRAM can be used to prevent containers—especially Java-heavy services like Wazuh—from crashing.

### ZRAM Configuration Steps




1. Install `zram-tools` on all nodes (`apt install zram-tools`).
2. Configure the settings in `/etc/default/zramswap`.
3. Adjust the OS swappiness in `/etc/sysctl.conf`.
4. Apply using `service zramswap reload` and `sysctl -p`.

### Recommended Node Settings

| Node | Role | RAM Allocation | ZRAM Algorithm | ZRAM Percent | Swappiness | Note |
|----|----|----|----|----|----|----|
| **Node 1** | Hydra Scanner | 2 GB | `lz4` | 40% | Default (60) | `lz4` saves CPU cycles for intensive Nmap scanning. |
| **Node 2** | Wazuh AIO | 6 GB | `zstd` | 75% | 10 | High capacity buffer; low swappiness prevents the Java Heap from swapping to disk and crashing. |
| **Node 3** | Zabbix | 4 GB | `zstd` | 60% | 60 | Balanced for database caching. |
| **Node 4** | Snipe-IT | 2 GB | `zstd` | 60% | 60 | Balanced for Web/DB operations. |


