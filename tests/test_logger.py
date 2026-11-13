import logging

from logger import setup_logger


def test_log_rotation(tmp_path):

    log_file = tmp_path / "automation.log"

    logger = setup_logger(
        name="test_rotation_logger",
        log_file=str(log_file),
        level=logging.INFO,
        max_bytes=200,
        backup_count=2,
    )

    # Prevent test messages from flooding the console
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.FileHandler
        ):
            handler.setLevel(logging.CRITICAL)

    try:
        # Generate enough log messages to trigger rotation
        for i in range(20):
            logger.info("Log rotation test message number %d", i)

        # Check current log file
        assert log_file.exists()

        # Check rotated files
        assert (tmp_path / "automation.log.1").exists()
        assert (tmp_path / "automation.log.2").exists()

        # Check that rotation limit is respected
        assert not (tmp_path / "automation.log.3").exists()

        # Check file sizes
        for filename in [
            "automation.log",
            "automation.log.1",
            "automation.log.2",
        ]:
            assert (tmp_path / filename).stat().st_size <= 200

    finally:
        # Close and remove handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
