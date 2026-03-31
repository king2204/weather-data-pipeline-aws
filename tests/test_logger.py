"""Tests for logging configuration."""
import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.logger import configure_logging, get_logger


class TestConfigureLogging:
    """Test suite for logging configuration."""

    def test_configure_logging_default(self):
        """Test default logging configuration."""
        logger = configure_logging()

        assert logger.name == "weather_etl"
        assert logger.level == logging.INFO

    def test_configure_logging_debug(self):
        """Test logging with DEBUG level."""
        logger = configure_logging(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_configure_logging_error(self):
        """Test logging with ERROR level."""
        logger = configure_logging(level="ERROR")

        assert logger.level == logging.ERROR

    def test_configure_logging_warning(self):
        """Test logging with WARNING level."""
        logger = configure_logging(level="WARNING")

        assert logger.level == logging.WARNING

    def test_configure_logging_critical(self):
        """Test logging with CRITICAL level."""
        logger = configure_logging(level="CRITICAL")

        assert logger.level == logging.CRITICAL

    def test_configure_logging_invalid_level(self):
        """Test logging with invalid level (should default to INFO)."""
        logger = configure_logging(level="INVALID")

        assert logger.level == logging.INFO

    def test_configure_logging_with_file(self):
        """Test logging configuration with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")

            logger = configure_logging(log_file=log_file)

            # Test that file handler is created
            has_file_handler = any(
                isinstance(h, logging.FileHandler) for h in logger.handlers
            )
            assert has_file_handler

    def test_configure_logging_file_directory_creation(self):
        """Test that logging creates parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "nested", "test.log")

            logger = configure_logging(log_file=log_file)

            # Parent directory should be created
            assert os.path.exists(os.path.dirname(log_file))

            # File handler should be added
            has_file_handler = any(
                isinstance(h, logging.FileHandler) for h in logger.handlers
            )
            assert has_file_handler

    def test_configure_logging_console_handler(self):
        """Test that console handler is always added."""
        logger = configure_logging()

        has_console_handler = any(
            isinstance(h, logging.StreamHandler) and
            not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )
        assert has_console_handler

    def test_configure_logging_formatter(self):
        """Test that formatter is properly configured."""
        logger = configure_logging()

        for handler in logger.handlers:
            formatter = handler.formatter
            assert formatter is not None
            assert "%(levelname)s" in formatter._fmt
            assert "%(message)s" in formatter._fmt
            assert "%(asctime)s" in formatter._fmt

    def test_configure_logging_write_to_file(self):
        """Test that logs are actually written to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")

            logger = configure_logging(log_file=log_file)
            logger.info("Test message")

            # Give time for file write
            import time
            time.sleep(0.1)

            # Check that file exists and contains the message
            assert os.path.exists(log_file)
            with open(log_file, "r") as f:
                content = f.read()
                assert "Test message" in content
                assert "INFO" in content

    def test_configure_logging_multiple_calls(self):
        """Test multiple calls to configure_logging."""
        logger1 = configure_logging(level="INFO")
        logger2 = configure_logging(level="DEBUG")

        # Should return same logger instance (same name)
        assert logger1.name == logger2.name == "weather_etl"

    def test_get_logger_default(self):
        """Test getting logger with default name."""
        logger = get_logger()

        assert logger.name == "weather_etl"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_custom_name(self):
        """Test getting logger with custom name."""
        logger = get_logger("custom_logger")

        assert logger.name == "custom_logger"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_existing(self):
        """Test that get_logger returns existing logger."""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")

        assert logger1 is logger2

    def test_configure_logging_level_case_insensitive(self):
        """Test that logging level is case insensitive."""
        logger1 = configure_logging(level="info")
        logger2 = configure_logging(level="INFO")
        logger3 = configure_logging(level="Info")

        # All should have same level
        assert logger1.level == logger2.level == logger3.level == logging.INFO

    def test_configure_logging_file_with_log_level(self):
        """Test file logging with specific log level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")

            # Remove existing handlers first
            logger = logging.getLogger("weather_etl")
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            logger = configure_logging(level="WARNING", log_file=log_file)

            # File handler should have WARNING level
            file_handler = next(
                (h for h in logger.handlers if isinstance(h, logging.FileHandler)),
                None
            )
            assert file_handler is not None
            assert file_handler.level == logging.WARNING

    def test_get_logger_existing_configured_logger(self):
        """Test getting an already configured logger."""
        configure_logging()
        logger = get_logger()

        # Should have handlers since we called configure_logging
        assert len(logger.handlers) > 0
