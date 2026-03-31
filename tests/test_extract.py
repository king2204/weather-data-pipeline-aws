"""Unit tests for extract module."""
import pandas as pd
import pytest
import requests
import requests_mock

from src.extract import extract_weather_data


def test_extract_weather_data_success(sample_weather_api_response):
    """Test successful weather data extraction."""
    with requests_mock.Mocker() as m:
        m.get("http://api.openweathermap.org/data/2.5/weather", json=sample_weather_api_response)

        result = extract_weather_data(
            city="Bangkok",
            api_key="test-key",
            api_timeout=10
        )

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["city"] == "Bangkok"
        assert result.iloc[0]["temperature"] == 28.5
        assert result.iloc[0]["humidity"] == 75


def test_extract_weather_data_api_error():
    """Test extraction with API error."""
    with requests_mock.Mocker() as m:
        m.get(
            "http://api.openweathermap.org/data/2.5/weather",
            status_code=401,
            text="Invalid API key"
        )

        result = extract_weather_data(
            city="Bangkok",
            api_key="invalid-key",
            api_timeout=10
        )

        assert result is None


def test_extract_weather_data_missing_api_key():
    """Test extraction without API key."""
    result = extract_weather_data(city="Bangkok", api_key="", api_timeout=10)
    assert result is None


def test_extract_weather_data_timeout():
    """Test extraction with timeout."""
    with requests_mock.Mocker() as m:
        m.get(
            "http://api.openweathermap.org/data/2.5/weather",
            exc=requests.exceptions.Timeout
        )

        with pytest.raises(requests.exceptions.Timeout):
            extract_weather_data(
                city="Bangkok",
                api_key="test-key",
                api_timeout=10
            )


def test_extract_weather_data_invalid_response(invalid_api_response):
    """Test extraction with invalid API response (missing fields)."""
    with requests_mock.Mocker() as m:
        m.get(
            "http://api.openweathermap.org/data/2.5/weather",
            json=invalid_api_response
        )

        result = extract_weather_data(
            city="Bangkok",
            api_key="test-key",
            api_timeout=10
        )

        # Should return None since response is missing required fields
        assert result is None


def test_extract_weather_data_retry_on_failure():
    """Test retry mechanism on temporary failure."""
    responses = [
        {"status_code": 500, "text": "Server error"},
        {"status_code": 500, "text": "Server error"},
        {
            "status_code": 200,
            "json": {
                "name": "Bangkok",
                "main": {"temp": 28.5, "humidity": 75},
                "weather": [{"description": "Sunny"}]
            }
        }
    ]

    with requests_mock.Mocker() as m:
        for resp in responses:
            m.get(
                "http://api.openweathermap.org/data/2.5/weather",
                status_code=resp["status_code"],
                json=resp.get("json") if resp["status_code"] == 200 else None,
                text=resp.get("text")
            )

        # Should eventually succeed after retries
        result = extract_weather_data(
            city="Bangkok",
            api_key="test-key",
            api_timeout=10
        )

        assert result is not None
