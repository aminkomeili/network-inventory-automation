import re


def parse_version(output):
    result = {}

    patterns = {
        "hostname": r"^(\S+) uptime is",
        "ios_version": r"Version\s+([^,\s]+)",
        "model": r"Cisco\s+(.+?)\s+processor",
        "processor_board_serial": r"Processor board ID\s+(\S+)",
        "uptime": r"^\S+ uptime is (.+)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.MULTILINE | re.IGNORECASE)

        if match:
            result[key] = match.group(1).strip()

    return result


def parse_inventory(output):
    components = []
    current_name = None
    current_description = None

    for line in output.splitlines():
        name_match = re.search(r'NAME:\s*"([^"]+)"', line)
        if name_match:
            current_name = name_match.group(1).strip()

        desc_match = re.search(r'DESCR:\s*"([^"]+)"', line)
        if desc_match:
            current_description = desc_match.group(1).strip()

        pid_match = re.search(
            r'PID:\s*(.*?)\s*,\s*VID:\s*(.*?)\s*,\s*SN:\s*(.*)',
            line
        )

        if pid_match:
            components.append({
                "name": current_name,
                "description": current_description,
                "pid": pid_match.group(1).strip(),
                "vid": pid_match.group(2).strip(),
                "serial_number": pid_match.group(3).strip(),
            })

    return components


def parse_interfaces(output):
    interfaces = []

    for line in output.splitlines():
        match = re.match(
            r"^(\S+)\s+(\S+)\s+\S+\s+\S+\s+(.*?)\s+(up|down)$",
            line.strip(),
            re.IGNORECASE
        )

        if not match:
            continue

        interfaces.append({
            "name": match.group(1),
            "ip_address": match.group(2),
            "status": match.group(3).strip(),
            "protocol": match.group(4).lower(),
        })

    return interfaces


def parse_routes(output):
    routes = []

    pattern = re.compile(
        r"^([A-Z][A-Z*+%]*)\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3}/\d+)\s+"
        r"(.+)$"
    )

    for line in output.splitlines():
        match = pattern.match(line.strip())

        if match:
            routes.append({
                "code": match.group(1),
                "network": match.group(2),
                "details": match.group(3).strip(),
            })

    return routes