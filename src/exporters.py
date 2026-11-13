import csv
import json
import os
import logging


logger = logging.getLogger("network_inventory.exporters")


def export_json(data, filename):

    os.makedirs("output", exist_ok=True)

    filepath = os.path.join("output", filename)

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        logger.info("JSON exported successfully: %s", filepath)

    except Exception:
        logger.exception("Failed to export JSON: %s", filepath)
        raise


def write_csv(filename, fieldnames, rows):

    os.makedirs("output", exist_ok=True)

    filepath = os.path.join("output", filename)

    try:
        with open(
            filepath,
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore"
            )

            writer.writeheader()
            writer.writerows(rows)

        logger.info("CSV exported successfully: %s", filepath)

    except Exception:
        logger.exception("Failed to export CSV: %s", filepath)
        raise


def export_csv(devices):

    device_rows = []
    interface_rows = []
    routing_rows = []
    hardware_rows = []
    error_rows = []

    for device in devices:

        summary = device.get("summary", {})
        data = device.get("data", {})

        device_rows.append({
            "device_name": device.get("device_name"),
            "hostname": summary.get("hostname"),
            "host": device.get("host"),
            "model": summary.get("model"),
            "ios_version": summary.get("ios_version"),
            "serial_number": summary.get("serial_number"),
            "uptime": summary.get("uptime"),
            "status": device.get("status"),
            "interface_count": summary.get("interface_count"),
            "route_count": summary.get("route_count"),
            "collection_time": device.get("collection_time"),
        })

        for interface in data.get("interfaces", []):
            interface_rows.append({
                "device_name": device.get("device_name"),
                "hostname": summary.get("hostname"),
                "interface": interface.get("name"),
                "ip_address": interface.get("ip_address"),
                "status": interface.get("status"),
                "protocol": interface.get("protocol"),
            })

        for route in data.get("routing", []):
            routing_rows.append({
                "device_name": device.get("device_name"),
                "hostname": summary.get("hostname"),
                "code": route.get("code"),
                "network": route.get("network"),
                "details": route.get("details"),
            })

        for component in data.get("inventory", []):
            hardware_rows.append({
                "device_name": device.get("device_name"),
                "hostname": summary.get("hostname"),
                "name": component.get("name"),
                "description": component.get("description"),
                "pid": component.get("pid"),
                "vid": component.get("vid"),
                "serial_number": component.get("serial_number"),
            })

        for error in device.get("errors", []):
            error_rows.append({
                "device_name": device.get("device_name"),
                "host": device.get("host"),
                "section": error.get("section"),
                "command": error.get("command"),
                "error": error.get("error"),
            })

    write_csv(
        "devices.csv",
        [
            "device_name", "hostname", "host", "model",
            "ios_version", "serial_number", "uptime",
            "status", "interface_count", "route_count",
            "collection_time"
        ],
        device_rows
    )

    write_csv(
        "interfaces.csv",
        [
            "device_name", "hostname", "interface",
            "ip_address", "status", "protocol"
        ],
        interface_rows
    )

    write_csv(
        "routing.csv",
        [
            "device_name", "hostname", "code",
            "network", "details"
        ],
        routing_rows
    )

    write_csv(
        "hardware_inventory.csv",
        [
            "device_name", "hostname", "name",
            "description", "pid", "vid", "serial_number"
        ],
        hardware_rows
    )

    write_csv(
        "errors.csv",
        [
            "device_name", "host", "section",
            "command", "error"
        ],
        error_rows
    )