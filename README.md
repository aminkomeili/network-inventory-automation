# Network Inventory Automation

A Python-based network inventory automation tool designed to collect, parse, and export operational information from Cisco IOS devices over SSH.

The project provides structured network inventory data in JSON and CSV formats, with built-in error handling, logging, and automated tests.

It is designed as a practical Network Automation / NetDevOps portfolio project.

## Features

- SSH connectivity using Netmiko.
- Automated information collection from Cisco IOS devices.
- Structured parsing of CLI command outputs.
- Device identification and hardware inventory collection.
- Interface and routing table discovery.
- Per-device and per-section error handling.
- JSON and CSV data exports.
- Centralized application logging.
- Log rotation using `RotatingFileHandler`.
- Environment-based credential management.
- Automated unit tests using Pytest.

## Architecture

The application follows a modular structure to separate connectivity, data collection, parsing, logging, and exporting responsibilities.

```text
network-inventory-automation/
│
├── inventory/
│   └── devices.yaml
│
├── src/
│   ├── main.py
│   ├── connection.py
│   ├── collectors.py
│   ├── parsers.py
│   ├── exporters.py
│   └── logger.py
│
├── output/
├── logs/
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | Application entry point and workflow orchestration |
| `connection.py` | SSH connection management |
| `collectors.py` | CLI command execution and data collection |
| `parsers.py` | Parsing raw CLI output into structured Python objects |
| `exporters.py` | JSON and CSV report generation |
| `logger.py` | Application logging and log rotation |

## Data Collection

The application executes the following read-only commands on each device:

| Command | Collected Information |
|---|---|
| `show version` | Hostname, IOS version, model, uptime, processor board serial |
| `show inventory` | Hardware components, PID, VID, serial numbers |
| `show ip interface brief` | Interface names, IP addresses, status, protocol |
| `show ip route` | Routing table entries |

All commands are operational `show` commands.

**The application does not modify device configurations.**

## Data Processing

Raw CLI outputs are processed using dedicated parsing functions.

The collected information is organized into structured sections:

- Version information
- Hardware inventory
- Interface information
- Routing information

A summary is also generated for each device, including:

- Hostname
- Device model
- IOS version
- Uptime
- Serial number
- Processor board serial
- Interface count
- Route count

## Error Handling

The application handles failures at multiple levels.

### Connection Failures

If an SSH connection fails, the device is recorded as `unreachable`.

The application continues processing the remaining devices.

### Collection Failures

Each collection section is handled independently.

A failure in one command does not prevent the application from attempting the remaining commands.

Device collection statuses:

| Status | Description |
|---|---|
| `success` | All collection sections completed successfully |
| `partial` | Some sections succeeded while others failed |
| `failed` | No collection section produced usable data |
| `unreachable` | SSH connection could not be established |

Errors are recorded in the inventory data and exported separately.

## Output Files

The application generates the following files inside the `output/` directory:

| File | Description |
|---|---|
| `devices.json` | Complete structured inventory data |
| `devices.csv` | Device summary information |
| `interfaces.csv` | Interface inventory |
| `routing.csv` | Routing table information |
| `hardware_inventory.csv` | Hardware component inventory |
| `errors.csv` | Collection and connection errors |

JSON is used for structured data storage, while CSV files provide a convenient format for reporting and further analysis.

CSV files are written using UTF-8 with BOM encoding for improved compatibility with spreadsheet applications.

## Logging

Application events are recorded in:

```text
logs/automation.log
```

The logging system supports:

- Console logging
- File logging
- Configurable logging levels
- Timestamped log records
- Exception tracebacks
- Automatic log rotation

Log rotation is implemented using Python's `RotatingFileHandler`.

Default configuration:

| Parameter | Value |
|---|---|
| Maximum log file size | 5 MB |
| Backup files | 5 |
| Encoding | UTF-8 |

When the active log file reaches its configured size, it is rotated automatically.

## Requirements

- Python 3.12
- SSH access to target devices
- Cisco IOS devices
- Network connectivity between the automation host and target devices

Python dependencies are listed in `requirements.txt`.

Main libraries:

- Netmiko
- Paramiko
- PyYAML
- python-dotenv
- ntc-templates
- Pytest

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd network-inventory-automation
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Configure Device Inventory

Edit:

```text
inventory/devices.yaml
```

Example:

```yaml
devices:
  - name: router-01
    host: "192.0.2.10"
    device_type: "cisco_ios"
    username: "automation_user"

  - name: router-02
    host: "192.0.2.11"
    device_type: "cisco_ios"
    username: "automation_user"
```

Each device requires:

| Parameter | Description |
|---|---|
| `name` | Unique device identifier |
| `host` | Management IP address or hostname |
| `device_type` | Netmiko device type |
| `username` | SSH username |

### 2. Configure SSH Credentials

Create a local environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SSH_PASSWORD=your_ssh_password
```

The application loads environment variables using `python-dotenv`.

**Security note:** The `.env` file is excluded from Git through `.gitignore`. Never commit real credentials to the repository.

## Usage

Run the application from the project root:

```bash
python src/main.py
```

The application will:

1. Load environment variables.
2. Initialize logging.
3. Load the device inventory.
4. Establish SSH connections.
5. Execute collection commands.
6. Parse command outputs.
7. Record collection results and errors.
8. Export JSON and CSV reports.
9. Display an execution summary.

Generated reports are stored in `output/`, and execution logs are stored in `logs/`.

## Running Tests

Run the automated test suite:

```bash
PYTHONPATH=src pytest -v
```

The test suite covers:

- CLI output parsers
- Device data collection
- Partial and total collection failures
- JSON and CSV exporters
- CSV content validation
- Connection failure handling
- Log rotation

Current test results:

**18 tests passed.**

## Security and Operational Considerations

- SSH credentials are stored in environment variables rather than device inventory files.
- The local `.env` file is excluded from version control.
- Device interaction is read-only.
- Connection and collection failures are logged.
- SSH compatibility settings should be evaluated carefully when working with legacy devices.

For legacy laboratory equipment, older SSH algorithms may require compatibility adjustments. Such adjustments should be restricted to the relevant lab environment and should not weaken production-wide SSH security policies.

## Current Scope and Limitations

This version is an initial implementation focused on Cisco IOS inventory collection.

Current scope:

- Cisco IOS devices
- SSH-based connectivity
- Sequential device processing
- CLI-based information collection
- JSON and CSV exports

The following capabilities are not currently implemented:

- Multi-vendor device support
- Parallel device collection
- Database integration
- REST API
- Web dashboard
- Configuration management
- Automated configuration changes

These are potential directions for future development.

## Future Improvements

Potential enhancements include:

- Multi-vendor support for Cisco IOS-XE, NX-OS, and MikroTik.
- Parallel device collection.
- Historical inventory tracking.
- Database integration.
- REST API for inventory access.
- Web-based reporting dashboard.
- Scheduled inventory collection.
- CI/CD integration.

## Project Goals

This project demonstrates practical skills in:

- Network automation with Python
- SSH-based network device management
- Cisco IOS operational commands
- Structured data processing
- Error handling and logging
- Software modularity
- Automated testing
- Secure credential management

---

**Project Category:** Network Automation / NetDevOps
**Language:** Python
**Primary Platform:** Cisco IOS