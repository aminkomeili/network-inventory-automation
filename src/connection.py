import os
import logging

from netmiko import ConnectHandler


logger = logging.getLogger("network_inventory.connection")


def connect_to_device(device):

    connection_params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": device["username"],
        "password": os.getenv("SSH_PASSWORD"),
        "timeout": 15,
        "fast_cli": False,
    }

    logger.info(
        "Attempting SSH connection to %s (%s)",
        device["name"],
        device["host"]
    )

    connection = ConnectHandler(**connection_params)

    logger.info(
        "Successfully connected to %s",
        device["name"]
    )

    return connection