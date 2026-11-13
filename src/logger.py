import logging
import os

from logging.handlers import RotatingFileHandler


def setup_logger(
    name="network_inventory",
    log_file="logs/automation.log",
    level=logging.INFO,
    max_bytes=5 * 1024 * 1024,
    backup_count=5
):

    # Create log directory
    log_dir = os.path.dirname(log_file)

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)

    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Log format
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()

    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger