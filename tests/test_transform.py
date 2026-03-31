"""Unit tests for transform module."""
import pandas as pd
import pytest

from src.transform import transform_weather_data


def test_transform_weather_data_success(sample_weather_data):
    """Test successful weather data transformation."""
    result = transform_weather_data(sample_weather_data)

    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert "city" in result.columns
    assert "temperature" in result.columns
    assert "humidity" in result.columns


def test_transform_weather_data_empty_dataframe(empty_dataframe):
    """Test transformation with empty DataFrame."""
    result = transform_weather_data(empty_dataframe)
    assert result is None


def test_transform_weather_data_none():
    """Test transformation with None."""
    result = transform_weather_data(None)
    assert result is None


def test_transform_weather_data_with_nulls():
    """Test transformation with null values."""
    df = pd.DataFrame({
        "city": ["Bangkok", None],
        "temperature": [28.5, 22.3],
        "humidity": [75, None],
        "description": ["Sunny", "Cloudy"],
        "timestamp": [pd.Timestamp.now(), pd.Timestamp.now()]
    })

    result = transform_weather_data(df)

    # Should remove rows with nulls
    assert result is not None
    assert len(result) == 1
    assert result.iloc[0]["city"] == "Bangkok"


def test_transform_weather_data_temperature_rounding(sample_weather_data):
    """Test that temperature is rounded to 2 decimal places."""
    df = sample_weather_data.copy()
    df["temperature"] = [28.5555, 22.3333]

    result = transform_weather_data(df)

    assert result is not None
    assert result.iloc[0]["temperature"] == 28.56
    assert result.iloc[1]["temperature"] == 22.33


def test_transform_weather_data_humidity_conversion(sample_weather_data):
    """Test that humidity is converted to integer."""
    df = sample_weather_data.copy()
    df["humidity"] = [75.5, 65.9]

    result = transform_weather_data(df)

    assert result is not None
    assert result.iloc[0]["humidity"] == 75
    assert result.iloc[1]["humidity"] == 65


def test_transform_weather_data_city_strip(sample_weather_data):
    """Test that city names are stripped of whitespace."""
    df = sample_weather_data.copy()
    df["city"] = ["  Bangkok  ", " Chiang Mai "]

    result = transform_weather_data(df)

    assert result is not None
    assert result.iloc[0]["city"] == "Bangkok"
    assert result.iloc[1]["city"] == "Chiang Mai"


def test_transform_weather_data_invalid_temperature(invalid_weather_data):
    """Test that rows with invalid temperature are removed."""
    result = transform_weather_data(invalid_weather_data)

    # Both rows have invalid temperatures, should return None
    assert result is None


def test_transform_weather_data_description_lowercase(sample_weather_data):
    """Test that description is converted to lowercase."""
    df = sample_weather_data.copy()
    df["description"] = ["PARTLY CLOUDY", "Clear Sky"]

    result = transform_weather_data(df)

    assert result is not None
    assert result.iloc[0]["description"] == "partly cloudy"
    assert result.iloc[1]["description"] == "clear sky"


def test_transform_weather_data_preserves_original(sample_weather_data):
    """Test that original DataFrame is not modified."""
    original_copy = sample_weather_data.copy()

    transform_weather_data(sample_weather_data)

    pd.testing.assert_frame_equal(sample_weather_data, original_copy)
