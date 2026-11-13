import os
import yaml
import logging
from dotenv import load_dotenv
from datetime import datetime, timezone

from logger import setup_logger
from connection import connect_to_device
from collectors import collect_device_data
from exporters import export_json, export_csv


logger = logging.getLogger("network_inventory.main")


def build_connection_failure_result(device, error):

    return {
        "device_name": device["name"],
        "host": device["host"],
        "collection_time": datetime.now(timezone.utc).isoformat(),
        "status": "unreachable",
        "data": {},
        "errors": [
            {
                "section": "connection",
                "command": "SSH connection",
                "error": str(error),
            }
        ],
        "summary": {
            "hostname": None,
            "model": None,
            "ios_version": None,
            "uptime": None,
            "serial_number": None,
            "processor_board_serial": None,
            "interface_count": 0,
            "route_count": 0,
        },
    }


def main():
    load_dotenv()
    setup_logger()

    logger.info("=" * 60)
    logger.info("Network Inventory Automation started")

    if not os.getenv("SSH_PASSWORD"):
        logger.critical(
            "SSH_PASSWORD environment variable is missing"
        )
        return

    try:
        with open("inventory/devices.yaml", "r") as file:
            inventory = yaml.safe_load(file)

    except Exception:
        logger.exception("Failed to load device inventory")
        return

    devices = inventory.get("devices", [])

    logger.info("Loaded %d devices from inventory", len(devices))

    all_devices = []

    for device in devices:

        logger.info(
            "Starting device processing: %s (%s)",
            device["name"],
            device["host"]
        )

        try:
            connection = connect_to_device(device)

        except Exception as error:

            logger.exception(
                "Connection failed for %s",
                device["name"]
            )

            device_data = build_connection_failure_result(
                device,
                error
            )

            all_devices.append(device_data)

            continue

        try:
            device_data = collect_device_data(
                connection,
                device
            )

            all_devices.append(device_data)

            logger.info(
                "Device collection completed: %s | Status: %s",
                device["name"],
                device_data["status"]
            )

        finally:
            try:
                connection.disconnect()

                logger.info(
                    "Disconnected from %s",
                    device["name"]
                )

            except Exception:
                logger.exception(
                    "Failed to disconnect from %s",
                    device["name"]
                )

    try:
        export_json(all_devices, "devices.json")
        export_csv(all_devices)

        logger.info(
            "Inventory exported successfully: %d devices",
            len(all_devices)
        )

    except Exception:
        logger.exception("Failed to export inventory")
        return

    successful = sum(
        1 for device in all_devices
        if device["status"] == "success"
    )

    unreachable = sum(
        1 for device in all_devices
        if device["status"] == "unreachable"
    )

    logger.info(
        "Execution summary | Total: %d | Successful: %d | Unreachable: %d",
        len(all_devices),
        successful,
        unreachable
    )

    logger.info("Network Inventory Automation finished")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()