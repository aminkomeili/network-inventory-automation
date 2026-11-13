import csv
import json

from exporters import export_json, export_csv


def sample_devices():

    return [
        {
            "device_name": "router-01",
            "host": "192.168.77.2",
            "collection_time": "2026-11-13T10:00:00+00:00",
            "status": "success",

            "summary": {
                "hostname": "R1",
                "model": "7206VXR (NPE400)",
                "ios_version": "15.2(4)S6",
                "serial_number": "4279256517",
                "uptime": "45 minutes",
                "interface_count": 2,
                "route_count": 2,
            },

            "data": {
                "interfaces": [
                    {
                        "name": "FastEthernet0/0",
                        "ip_address": "192.168.77.2",
                        "status": "up",
                        "protocol": "up",
                    },
                    {
                        "name": "FastEthernet0/1",
                        "ip_address": "unassigned",
                        "status": "administratively down",
                        "protocol": "down",
                    },
                ],

                "routing": [
                    {
                        "code": "C",
                        "network": "192.168.77.0/24",
                        "details": "directly connected",
                    },
                    {
                        "code": "S*",
                        "network": "0.0.0.0/0",
                        "details": "directly connected",
                    },
                ],

                "inventory": [
                    {
                        "name": "Chassis",
                        "description": "Cisco 7206VXR",
                        "pid": "CISCO7206VXR",
                        "vid": "V06",
                        "serial_number": "4279256517",
                    }
                ],
            },

            "errors": [],
        },

        {
            "device_name": "router-02",
            "host": "192.168.77.3",
            "collection_time": "2026-11-13T10:01:00+00:00",
            "status": "partial",

            "summary": {
                "hostname": "R2",
                "model": "7206VXR",
                "ios_version": "15.2(4)S6",
                "serial_number": None,
                "uptime": "30 minutes",
                "interface_count": 0,
                "route_count": 0,
            },

            "data": {
                "interfaces": [],
                "routing": [],
                "inventory": [],
            },

            "errors": [
                {
                    "section": "inventory",
                    "command": "show inventory",
                    "error": "Command failed",
                }
            ],
        },
    ]


def test_export_json(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    devices = sample_devices()

    export_json(devices, "devices.json")

    output_file = tmp_path / "output" / "devices.json"

    assert output_file.exists()

    with open(output_file, encoding="utf-8") as file:
        result = json.load(file)

    assert len(result) == 2
    assert result[0]["device_name"] == "router-01"
    assert result[0]["summary"]["hostname"] == "R1"
    assert result[1]["status"] == "partial"


def test_export_csv_creates_all_files(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    output_dir = tmp_path / "output"

    expected_files = [
        "devices.csv",
        "interfaces.csv",
        "routing.csv",
        "hardware_inventory.csv",
        "errors.csv",
    ]

    for filename in expected_files:
        assert (output_dir / filename).exists()


def test_devices_csv_content(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    filepath = tmp_path / "output" / "devices.csv"

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert rows[0]["device_name"] == "router-01"
    assert rows[0]["hostname"] == "R1"
    assert rows[0]["model"] == "7206VXR (NPE400)"
    assert rows[0]["serial_number"] == "4279256517"

    assert rows[1]["status"] == "partial"


def test_interfaces_csv_content(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    filepath = tmp_path / "output" / "interfaces.csv"

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert rows[0]["interface"] == "FastEthernet0/0"
    assert rows[0]["ip_address"] == "192.168.77.2"
    assert rows[0]["status"] == "up"

    assert rows[1]["status"] == "administratively down"


def test_routing_csv_content(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    filepath = tmp_path / "output" / "routing.csv"

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2

    assert rows[0]["code"] == "C"
    assert rows[0]["network"] == "192.168.77.0/24"

    assert rows[1]["code"] == "S*"
    assert rows[1]["network"] == "0.0.0.0/0"


def test_hardware_inventory_csv_content(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    filepath = tmp_path / "output" / "hardware_inventory.csv"

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1

    assert rows[0]["name"] == "Chassis"
    assert rows[0]["pid"] == "CISCO7206VXR"
    assert rows[0]["serial_number"] == "4279256517"


def test_errors_csv_content(monkeypatch, tmp_path):

    monkeypatch.chdir(tmp_path)

    export_csv(sample_devices())

    filepath = tmp_path / "output" / "errors.csv"

    with open(filepath, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1

    assert rows[0]["device_name"] == "router-02"
    assert rows[0]["section"] == "inventory"
    assert rows[0]["command"] == "show inventory"
    assert rows[0]["error"] == "Command failed"
