from datetime import datetime, timezone

from parsers import (
    parse_version,
    parse_inventory,
    parse_interfaces,
    parse_routes,
)
import logging

logger = logging.getLogger("network_inventory.collectors")


COMMANDS = {
    "version": "show version",
    "inventory": "show inventory",
    "interfaces": "show ip interface brief",
    "routing": "show ip route",
}


PARSERS = {
    "version": parse_version,
    "inventory": parse_inventory,
    "interfaces": parse_interfaces,
    "routing": parse_routes,
}


def collect_device_data(connection, device):

    result = {
        "device_name": device["name"],
        "host": device["host"],
        "collection_time": datetime.now(timezone.utc).isoformat(),
        "status": "success",
        "data": {},
        "errors": [],
    }

    for section, command in COMMANDS.items():

        try:
            logger.info(
                "Executing command '%s' on %s",
                command,
                device["name"]
            )
            output = connection.send_command(
                command,
                read_timeout=30
            )

            parser = PARSERS[section]
            result["data"][section] = parser(output)

        except Exception as error:

            logger.exception(
                "Failed to collect section '%s' from %s",
                section,
                device["name"]
            )

            result["errors"].append({
                "section": section,
                "command": command,
                "error": str(error),
            })

    if result["errors"]:
        result["status"] = (
            "partial" if result["data"] else "failed"
        )

    # استخراج اطلاعات کلیدی از داده‌های جمع‌آوری‌شده
    version_data = result["data"].get("version", {})
    inventory_data = result["data"].get("inventory", [])

    chassis = next(
        (
            item for item in inventory_data
            if item.get("name", "").lower() == "chassis"
        ),
        None
    )

    result["summary"] = {
        "hostname": version_data.get("hostname"),
        "model": version_data.get("model"),
        "ios_version": version_data.get("ios_version"),
        "uptime": version_data.get("uptime"),
        "serial_number": (
            chassis.get("serial_number") if chassis else None
        ),
        "processor_board_serial": version_data.get(
            "processor_board_serial"
        ),
        "interface_count": len(
            result["data"].get("interfaces", [])
        ),
        "route_count": len(
            result["data"].get("routing", [])
        ),
    }

    return result