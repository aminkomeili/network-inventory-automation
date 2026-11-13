from parsers import (
    parse_version,
    parse_inventory,
    parse_interfaces,
    parse_routes,
)


def test_parse_version():

    output = """
R1 uptime is 45 minutes
Cisco IOS Software, 7200 Software (C7200-ADVENTERPRISEK9-M),
Version 15.2(4)S6, RELEASE SOFTWARE (fc1)
Cisco 7206VXR (NPE400) processor
Processor board ID 4279256517
"""

    result = parse_version(output)

    assert result["hostname"] == "R1"
    assert result["ios_version"] == "15.2(4)S6"
    assert result["model"] == "7206VXR (NPE400)"
    assert result["processor_board_serial"] == "4279256517"
    assert result["uptime"] == "45 minutes"


def test_parse_inventory():

    output = """
NAME: "Chassis", DESCR: "Cisco 7206VXR, 6-slot chassis"
PID: CISCO7206VXR, VID: , SN: 4279256517

NAME: "NPE400 0", DESCR: "Cisco 7200VXR Network Processing Engine NPE-400"
PID: NPE-400, VID: , SN: 11111111
"""

    result = parse_inventory(output)

    assert len(result) == 2
    assert result[0]["name"] == "Chassis"
    assert result[0]["pid"] == "CISCO7206VXR"
    assert result[0]["serial_number"] == "4279256517"


def test_parse_interfaces():

    output = """
Interface              IP-Address      OK? Method Status                Protocol
FastEthernet0/0        192.168.77.2    YES NVRAM  up                    up
FastEthernet0/1        unassigned      YES NVRAM  administratively down down
FastEthernet1/0        unassigned      YES NVRAM  administratively down down
FastEthernet1/1        unassigned      YES NVRAM  administratively down down
"""

    result = parse_interfaces(output)

    assert len(result) == 4

    assert result[0]["name"] == "FastEthernet0/0"
    assert result[0]["ip_address"] == "192.168.77.2"
    assert result[0]["status"] == "up"
    assert result[0]["protocol"] == "up"

    assert result[1]["status"] == "administratively down"
    assert result[1]["protocol"] == "down"


def test_parse_routes():

    output = """
S*    0.0.0.0/0 is directly connected, FastEthernet0/0
C     192.168.77.0/24 is directly connected, FastEthernet0/0
L     192.168.77.2/32 is directly connected, FastEthernet0/0
"""

    result = parse_routes(output)

    assert len(result) == 3
    assert result[0]["code"] == "S*"
    assert result[0]["network"] == "0.0.0.0/0"
    assert result[1]["code"] == "C"
    assert result[2]["network"] == "192.168.77.2/32"