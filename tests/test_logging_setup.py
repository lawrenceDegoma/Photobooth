"""Tests for logging setup, particularly RotatingFileHandler configuration
used in production (Milestone 9 — Kiosk Deployment: log rotation)."""
import logging
from logging.handlers import RotatingFileHandler

from app.core.config import LoggingConfig
from app.core.logging_setup import setup_logging


def _reset_root_logger():
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()


def test_creates_log_directory(tmp_path):
    _reset_root_logger()
    log_path = tmp_path / "nested" / "photobooth.log"
    config = LoggingConfig(path=str(log_path))

    setup_logging(config)

    assert log_path.parent.exists()
    _reset_root_logger()


def test_configures_rotating_file_handler_with_given_limits(tmp_path):
    _reset_root_logger()
    log_path = tmp_path / "photobooth.log"
    config = LoggingConfig(path=str(log_path), max_bytes=12345, backup_count=7)

    setup_logging(config)

    root = logging.getLogger()
    rotating_handlers = [h for h in root.handlers if isinstance(h, RotatingFileHandler)]

    assert len(rotating_handlers) == 1
    handler = rotating_handlers[0]
    assert handler.maxBytes == 12345
    assert handler.backupCount == 7
    _reset_root_logger()


def test_log_level_is_applied(tmp_path):
    _reset_root_logger()
    log_path = tmp_path / "photobooth.log"
    config = LoggingConfig(path=str(log_path), level="WARNING")

    setup_logging(config)

    assert logging.getLogger().level == logging.WARNING
    _reset_root_logger()


def test_actual_rotation_occurs_when_size_exceeded(tmp_path):
    _reset_root_logger()
    log_path = tmp_path / "photobooth.log"
    config = LoggingConfig(path=str(log_path), max_bytes=200, backup_count=2)

    setup_logging(config)
    logger = logging.getLogger("test.rotation")

    for i in range(200):
        logger.info("Filler log line number %d to force rotation", i)

    rotated_files = list(tmp_path.glob("photobooth.log.*"))
    assert len(rotated_files) > 0
    _reset_root_logger()
