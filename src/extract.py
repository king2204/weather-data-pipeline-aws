"""Weather data extraction module."""
import logging
from typing import Optional

import pandas as pd
import requests

from src.utils.logger import get_logger
from src.utils.retry import retry_with_backoff

logger = get_logger("weather_etl")


@retry_with_backoff(max_attempts=3, initial_delay=1.0)
def extract_weather_data(
    city: str = "Bangkok",
    api_key: str = "",
    api_timeout: int = 10,
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"
) -> Optional[pd.DataFrame]:
    """
    Extract weather data from OpenWeatherMap API.

    Args:
        city: City name
        api_key: API key for OpenWeatherMap
        api_timeout: Request timeout in seconds
        base_url: Base URL for API

    Returns:
        DataFrame with weather data or None if failed
    """
    if not api_key:
        logger.error("API key is required for weather extraction")
        return None

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        logger.info(f"Extracting weather data for: {city}")
        response = requests.get(base_url, params=params, timeout=api_timeout)

        if response.status_code != 200:
            logger.error(
                f"API request failed with status {response.status_code}: {response.text}"
            )
            return None

        data = response.json()
        logger.info(f"Successfully extracted data for {city}")

        # Validate required fields
        if not data.get('main') or not data.get('weather'):
            logger.error("API response missing required fields (main or weather)")
            return None

        # Build DataFrame
        weather_dict = {
            "city": [data.get('name', 'Unknown')],
            "temperature": [data['main'].get('temp')],
            "humidity": [data['main'].get('humidity')],
            "description": [data['weather'][0].get('description', 'N/A')],
            "timestamp": [pd.Timestamp.now()]
        }

        df = pd.DataFrame(weather_dict)
        logger.debug(f"Extracted data shape: {df.shape}")

        return df

    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {city} (>{api_timeout}s)")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while extracting {city}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during extraction for {city}: {str(e)}")
        raise
