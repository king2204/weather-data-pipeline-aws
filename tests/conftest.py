"""Pytest configuration and fixtures."""
import json
from datetime import datetime
from typing import Generator

import boto3
import pandas as pd
import pytest
from moto import mock_aws


@pytest.fixture
def sample_weather_data() -> pd.DataFrame:
    """Create sample weather data for testing."""
    return pd.DataFrame({
        "city": ["Bangkok", "Chiang Mai"],
        "temperature": [28.5, 22.3],
        "humidity": [75, 65],
        "description": ["Partly cloudy", "Clear sky"],
        "timestamp": [pd.Timestamp.now(), pd.Timestamp.now()]
    })


@pytest.fixture
def sample_weather_api_response() -> dict:
    """Create sample OpenWeatherMap API response."""
    return {
        "coord": {"lon": 100.4944, "lat": 13.7563},
        "weather": [
            {
                "id": 803,
                "main": "Clouds",
                "description": "broken clouds",
                "icon": "04d"
            }
        ],
        "main": {
            "temp": 28.5,
            "feels_like": 32.5,
            "temp_min": 28.0,
            "temp_max": 29.0,
            "pressure": 1010,
            "humidity": 75
        },
        "visibility": 10000,
        "wind": {
            "speed": 5.1,
            "deg": 230
        },
        "clouds": {
            "all": 75
        },
        "dt": 1234567890,
        "sys": {
            "country": "TH",
            "sunrise": 1234534500,
            "sunset": 1234579500
        },
        "timezone": 25200,
        "id": 1609350,
        "name": "Bangkok",
        "cod": 200
    }


@pytest.fixture
def invalid_api_response() -> dict:
    """Create invalid API response (missing fields)."""
    return {
        "name": "Bangkok",
        "main": {
            "temp": 28.5
            # Missing humidity
        },
        "weather": []  # Empty weather list
    }


@pytest.fixture
@mock_aws
def s3_setup() -> Generator[boto3.client, None, None]:
    """Setup mock S3 bucket for testing."""
    # Create mock S3 client
    s3 = boto3.client('s3', region_name='ap-southeast-1')

    # Create test bucket
    bucket_name = 'test-weather-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )

    yield s3

    # Cleanup is automatic with moto


@pytest.fixture
def mock_lambda_context():
    """Create mock Lambda context."""
    class MockContext:
        """Mock Lambda context."""
        aws_request_id = "test-request-id-12345"
        function_name = "weather-etl-pipeline"
        memory_limit_in_mb = 1024
        invoked_function_arn = "arn:aws:lambda:ap-southeast-1:123456789:function:weather-etl-pipeline"

        def get_remaining_time_in_millis(self) -> int:
            return 600000

    return MockContext()


@pytest.fixture
def valid_config_dict() -> dict:
    """Create valid configuration dictionary."""
    return {
        "weather_api_key": "test-api-key",
        "api_timeout": 10,
        "aws_region": "ap-southeast-1",
        "aws_s3_bucket": "test-bucket",
        "log_level": "INFO",
        "max_retries": 3
    }


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Create empty DataFrame."""
    return pd.DataFrame()


@pytest.fixture
def invalid_weather_data() -> pd.DataFrame:
    """Create invalid weather data (out of range values)."""
    return pd.DataFrame({
        "city": ["Bangkok", "Chiang Mai"],
        "temperature": [-400, 300],  # Invalid ranges
        "humidity": [150, -10],  # Invalid ranges
        "description": ["Sunny", "Cloudy"],
        "timestamp": [pd.Timestamp.now(), pd.Timestamp.now()]
    })
