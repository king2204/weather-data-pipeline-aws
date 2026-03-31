"""Tests for configuration management."""
import os
from unittest.mock import patch

import pytest

from src.utils.config import AppConfig


class TestAppConfig:
    """Test suite for AppConfig."""

    def test_from_env_success(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {
            "WEATHER_API_KEY": "test-key-123",
            "API_TIMEOUT": "20",
            "AWS_REGION": "us-east-1",
            "AWS_S3_BUCKET": "test-bucket",
            "LOG_LEVEL": "DEBUG",
            "MAX_RETRIES": "5",
            "BATCH_SIZE": "100"
        }):
            config = AppConfig.from_env()

            assert config.weather_api_key == "test-key-123"
            assert config.api_timeout == 20
            assert config.aws_region == "us-east-1"
            assert config.aws_s3_bucket == "test-bucket"
            assert config.log_level == "DEBUG"
            assert config.max_retries == 5
            assert config.batch_size == 100

    def test_from_env_defaults(self):
        """Test loading config with default values."""
        with patch.dict(os.environ, {
            "WEATHER_API_KEY": "test-key"
        }, clear=True):
            config = AppConfig.from_env()

            assert config.weather_api_key == "test-key"
            assert config.api_timeout == 10  # default
            assert config.aws_region == "ap-southeast-1"  # default
            assert config.log_level == "INFO"  # default
            assert config.max_retries == 3  # default

    def test_from_env_missing_api_key(self):
        """Test loading config without API key."""
        with patch.dict(os.environ, {}, clear=True), \
             patch("src.utils.config.load_dotenv"):
            config = AppConfig.from_env()
            assert config.weather_api_key == ""

    def test_validate_success(self):
        """Test successful validation."""
        config = AppConfig(
            weather_api_key="valid-key",
            api_timeout=10,
            max_retries=3
        )
        assert config.validate() is True

    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        config = AppConfig(
            weather_api_key="",
            api_timeout=10
        )
        assert config.validate() is False

    def test_validate_invalid_timeout(self):
        """Test validation with invalid timeout."""
        config = AppConfig(
            weather_api_key="valid-key",
            api_timeout=0
        )
        assert config.validate() is False

        config.api_timeout = -5
        assert config.validate() is False

    def test_validate_invalid_retries(self):
        """Test validation with invalid retry count."""
        config = AppConfig(
            weather_api_key="valid-key",
            api_timeout=10,
            max_retries=-1
        )
        assert config.validate() is False

    def test_to_dict(self):
        """Test config to dictionary conversion."""
        config = AppConfig(
            weather_api_key="secret-key",
            api_timeout=15,
            aws_region="eu-west-1",
            aws_s3_bucket="my-bucket",
            log_level="WARNING",
            max_retries=2
        )
        result = config.to_dict()

        assert result["weather_api_key"] == "***"  # Masked
        assert result["api_timeout"] == 15
        assert result["aws_region"] == "eu-west-1"
        assert result["aws_s3_bucket"] == "my-bucket"
        assert result["log_level"] == "WARNING"
        assert result["max_retries"] == 2

    def test_to_dict_no_api_key(self):
        """Test to_dict when API key is not set."""
        config = AppConfig(
            weather_api_key="",
            api_timeout=10
        )
        result = config.to_dict()

        assert result["weather_api_key"] == "NOT_SET"

    def test_config_defaults(self):
        """Test default values in config."""
        config = AppConfig(weather_api_key="test-key")

        assert config.api_timeout == 10
        assert config.aws_region == "ap-southeast-1"
        assert config.aws_s3_bucket is None
        assert config.lambda_timeout == 600
        assert config.lambda_memory == 1024
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.max_retries == 3
        assert config.batch_size == 50

    def test_config_custom_values(self):
        """Test setting custom config values."""
        config = AppConfig(
            weather_api_key="key",
            api_timeout=30,
            aws_region="ap-northeast-1",
            aws_s3_bucket="custom-bucket",
            lambda_timeout=900,
            lambda_memory=512,
            log_level="DEBUG",
            log_file="/var/log/app.log",
            max_retries=5,
            batch_size=200
        )

        assert config.api_timeout == 30
        assert config.aws_region == "ap-northeast-1"
        assert config.aws_s3_bucket == "custom-bucket"
        assert config.lambda_timeout == 900
        assert config.lambda_memory == 512
        assert config.log_level == "DEBUG"
        assert config.log_file == "/var/log/app.log"
        assert config.max_retries == 5
        assert config.batch_size == 200

    def test_from_env_type_conversion(self):
        """Test proper type conversion from environment variables."""
        with patch.dict(os.environ, {
            "WEATHER_API_KEY": "test-key",
            "API_TIMEOUT": "25",
            "LAMBDA_TIMEOUT": "300",
            "LAMBDA_MEMORY": "512",
            "MAX_RETRIES": "2",
            "BATCH_SIZE": "75"
        }):
            config = AppConfig.from_env()

            assert isinstance(config.api_timeout, int)
            assert config.api_timeout == 25
            assert isinstance(config.lambda_timeout, int)
            assert config.lambda_timeout == 300
            assert isinstance(config.lambda_memory, int)
            assert config.lambda_memory == 512
            assert isinstance(config.max_retries, int)
            assert config.max_retries == 2
            assert isinstance(config.batch_size, int)
            assert config.batch_size == 75
