"""Tests for Lambda handler."""
import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture
def lambda_event():
    """Sample Lambda event."""
    return {
        "cities": ["Bangkok", "Chiang Mai"]
    }


@pytest.fixture
def lambda_event_empty():
    """Lambda event with empty cities."""
    return {
        "cities": []
    }


def test_lambda_handler_success(lambda_event, mock_lambda_context):
    """Test successful Lambda execution."""
    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.transform_weather_data") as mock_transform, \
         patch("src.lambda_handler.load_to_s3") as mock_load, \
         patch("src.lambda_handler.config") as mock_config:

        # Setup config mock
        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {
            "weather_api_key": "***",
            "api_timeout": 10,
            "aws_region": "ap-southeast-1",
            "aws_s3_bucket": "test-bucket",
            "log_level": "INFO",
            "max_retries": 3
        }
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10
        mock_config.aws_s3_bucket = "test-bucket"
        mock_config.log_level = "INFO"

        # Setup extract mock
        df_raw = pd.DataFrame({
            "city": ["Bangkok"],
            "temperature": [28.5],
            "humidity": [75],
            "description": ["Cloudy"],
            "timestamp": [pd.Timestamp.now()]
        })
        mock_extract.return_value = df_raw

        # Setup transform mock
        mock_transform.return_value = df_raw

        # Setup load mock
        mock_load.return_value = True

        # Import inside patch context
        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "message" in body
        assert body["message"] == "ETL pipeline completed successfully"
        assert body["records_processed"] == 2  # Two cities = 2 records after concat


def test_lambda_handler_invalid_config(lambda_event, mock_lambda_context):
    """Test Lambda with invalid configuration."""
    with patch("src.lambda_handler.config") as mock_config:
        mock_config.validate.return_value = False

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body
        assert body["error"] == "Invalid configuration"


def test_lambda_handler_extract_failure(lambda_event, mock_lambda_context):
    """Test Lambda when extract fails."""
    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.config") as mock_config:

        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {"weather_api_key": "***"}
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10

        # Extract returns None
        mock_extract.return_value = None

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body


def test_lambda_handler_no_data_to_load(lambda_event, mock_lambda_context):
    """Test Lambda when no data is processed."""
    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.config") as mock_config:

        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {"weather_api_key": "***"}
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10

        # All extracts fail
        mock_extract.return_value = None

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert body["error"] == "No data processed successfully"


def test_lambda_handler_exception(lambda_event, mock_lambda_context):
    """Test Lambda with unexpected exception."""
    with patch("src.lambda_handler.config") as mock_config:
        mock_config.validate.side_effect = Exception("Test error")

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "error" in body


def test_lambda_handler_transform_failure(lambda_event, mock_lambda_context):
    """Test Lambda when transform fails."""
    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.transform_weather_data") as mock_transform, \
         patch("src.lambda_handler.config") as mock_config:

        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {"weather_api_key": "***"}
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10

        df_raw = pd.DataFrame({
            "city": ["Bangkok"],
            "temperature": [28.5],
            "humidity": [75],
            "description": ["Cloudy"],
            "timestamp": [pd.Timestamp.now()]
        })
        mock_extract.return_value = df_raw
        mock_transform.return_value = None  # Transform fails

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 400


def test_lambda_handler_load_failure(lambda_event, mock_lambda_context):
    """Test Lambda when load to S3 fails."""
    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.transform_weather_data") as mock_transform, \
         patch("src.lambda_handler.load_to_s3") as mock_load, \
         patch("src.lambda_handler.config") as mock_config:

        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {"weather_api_key": "***"}
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10
        mock_config.aws_s3_bucket = "test-bucket"

        df_raw = pd.DataFrame({
            "city": ["Bangkok"],
            "temperature": [28.5],
            "humidity": [75],
            "description": ["Cloudy"],
            "timestamp": [pd.Timestamp.now()]
        })
        mock_extract.return_value = df_raw
        mock_transform.return_value = df_raw
        mock_load.return_value = False  # Load fails

        from src.lambda_handler import lambda_handler

        response = lambda_handler(lambda_event, mock_lambda_context)

        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["error"] == "Failed to load data to S3"


def test_lambda_handler_partial_failure(lambda_event, mock_lambda_context):
    """Test Lambda with partial city processing failure."""
    event = {"cities": ["Bangkok", "Chiang Mai", "Phuket"]}

    with patch("src.lambda_handler.extract_weather_data") as mock_extract, \
         patch("src.lambda_handler.transform_weather_data") as mock_transform, \
         patch("src.lambda_handler.load_to_s3") as mock_load, \
         patch("src.lambda_handler.config") as mock_config:

        mock_config.validate.return_value = True
        mock_config.to_dict.return_value = {"weather_api_key": "***"}
        mock_config.weather_api_key = "test-key"
        mock_config.api_timeout = 10
        mock_config.aws_s3_bucket = "test-bucket"

        df_raw = pd.DataFrame({
            "city": ["Bangkok"],
            "temperature": [28.5],
            "humidity": [75],
            "description": ["Cloudy"],
            "timestamp": [pd.Timestamp.now()]
        })

        # First two succeed, last fails
        mock_extract.side_effect = [df_raw, df_raw, None]
        mock_transform.return_value = df_raw
        mock_load.return_value = True

        from src.lambda_handler import lambda_handler

        response = lambda_handler(event, mock_lambda_context)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["cities_processed"] == 2
        assert len(body["failed_cities"]) == 1
        assert "Phuket" in body["failed_cities"]
