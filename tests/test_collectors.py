from collectors import collect_device_data


class MockConnection:
    """
    شبیه‌ساز اتصال SSH به روتر Cisco
    """

    def __init__(self, fail_commands=None):
        self.fail_commands = fail_commands or []

        self.outputs = {
            "show version": """
R1 uptime is 45 minutes
Cisco IOS Software, Version 15.2(4)S6,
Cisco 7206VXR (NPE400) processor
Processor board ID 4279256517
""",

            "show inventory": """
NAME: "Chassis", DESCR: "Cisco 7206VXR"
PID: CISCO7206VXR, VID: V06, SN: 4279256517

NAME: "Power Supply 1", DESCR: "AC Power Supply"
PID: PWR-7200-AC, VID: V01, SN: PS123456
""",

            "show ip interface brief": """
Interface              IP-Address      OK? Method Status                Protocol
FastEthernet0/0        192.168.77.2    YES NVRAM  up                    up
FastEthernet0/1        unassigned      YES unset  administratively down down
FastEthernet1/0        unassigned      YES unset  administratively down down
FastEthernet1/1        unassigned      YES unset  administratively down down
""",

            "show ip route": """
S* 0.0.0.0/0 [1/0] is directly connected, FastEthernet0/0
C 192.168.77.0/24 is directly connected, FastEthernet0/0
L 192.168.77.2/32 is directly connected, FastEthernet0/0
"""
        }

    def send_command(self, command, read_timeout=30):

        if command in self.fail_commands:
            raise Exception(f"Simulated failure: {command}")

        return self.outputs[command]


# اطلاعات دستگاه آزمایشگاهی
DEVICE = {
    "name": "router-01",
    "host": "192.168.77.2"
}


def test_collect_device_data_success():

    connection = MockConnection()

    result = collect_device_data(connection, DEVICE)

    assert result["status"] == "success"
    assert result["device_name"] == "router-01"

    # بررسی Summary
    assert result["summary"]["hostname"] == "R1"
    assert result["summary"]["model"] == "7206VXR (NPE400)"
    assert result["summary"]["ios_version"] == "15.2(4)S6"
    assert result["summary"]["serial_number"] == "4279256517"

    # بررسی تعداد اطلاعات جمع‌آوری‌شده
    assert result["summary"]["interface_count"] == 4
    assert result["summary"]["route_count"] == 3

    assert len(result["errors"]) == 0


def test_collect_device_data_partial_failure():

    connection = MockConnection(
        fail_commands=["show inventory"]
    )

    result = collect_device_data(connection, DEVICE)

    assert result["status"] == "partial"

    # سه بخش دیگر باید با موفقیت جمع‌آوری شده باشند
    assert "version" in result["data"]
    assert "interfaces" in result["data"]
    assert "routing" in result["data"]

    # Inventory نباید در داده‌های موفق باشد
    assert "inventory" not in result["data"]

    assert len(result["errors"]) == 1
    assert result["errors"][0]["command"] == "show inventory"


def test_collect_device_data_total_failure():

    connection = MockConnection(
        fail_commands=[
            "show version",
            "show inventory",
            "show ip interface brief",
            "show ip route"
        ]
    )

    result = collect_device_data(connection, DEVICE)

    assert result["status"] == "failed"
    assert len(result["data"]) == 0
    assert len(result["errors"]) == 4


def test_collect_device_data_summary_without_inventory():

    connection = MockConnection(
        fail_commands=["show inventory"]
    )

    result = collect_device_data(connection, DEVICE)

    assert result["summary"]["hostname"] == "R1"
    assert result["summary"]["serial_number"] is None
    assert result["summary"]["interface_count"] == 4
    assert result["summary"]["route_count"] == 3
