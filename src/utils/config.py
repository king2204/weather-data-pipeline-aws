"""Configuration management."""
import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger("weather_etl")


@dataclass
class AppConfig:
    """Application configuration."""

    # API Configuration
    weather_api_key: str
    api_timeout: int = 10

    # AWS Configuration
    aws_region: str = "ap-southeast-1"
    aws_s3_bucket: Optional[str] = None

    # Lambda Configuration
    lambda_timeout: int = 600
    lambda_memory: int = 1024

    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Application Configuration
    max_retries: int = 3
    batch_size: int = 50

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            weather_api_key=os.getenv("WEATHER_API_KEY", ""),
            api_timeout=int(os.getenv("API_TIMEOUT", "10")),
            aws_region=os.getenv("AWS_REGION", "ap-southeast-1"),
            aws_s3_bucket=os.getenv("AWS_S3_BUCKET"),
            lambda_timeout=int(os.getenv("LAMBDA_TIMEOUT", "600")),
            lambda_memory=int(os.getenv("LAMBDA_MEMORY", "1024")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE"),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            batch_size=int(os.getenv("BATCH_SIZE", "50")),
        )

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.weather_api_key:
            logger.error("WEATHER_API_KEY is required")
            return False

        if self.api_timeout <= 0:
            logger.error("API_TIMEOUT must be greater than 0")
            return False

        if self.max_retries < 0:
            logger.error("MAX_RETRIES must be non-negative")
            return False

        return True

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "weather_api_key": "***" if self.weather_api_key else "NOT_SET",
            "api_timeout": self.api_timeout,
            "aws_region": self.aws_region,
            "aws_s3_bucket": self.aws_s3_bucket,
            "log_level": self.log_level,
            "max_retries": self.max_retries,
        }
