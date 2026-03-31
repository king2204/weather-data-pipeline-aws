"""Weather data transformation module."""
import logging
from typing import Optional

import pandas as pd
from pydantic import ValidationError

from src.utils.logger import get_logger
from src.utils.validators import WeatherDataSchema

logger = get_logger("weather_etl")


def transform_weather_data(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Transform and validate weather data.

    Args:
        df: Raw weather DataFrame

    Returns:
        Transformed DataFrame or None if validation fails
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame provided for transformation")
        return None

    try:
        # Create copy to avoid modifying original
        df_clean = df.copy()

        logger.info(f"Starting transformation on {len(df_clean)} rows")

        # Handle missing values
        if df_clean.isnull().any().any():
            null_counts = df_clean.isnull().sum()
            logger.warning(f"Found null values:\n{null_counts}")
            df_clean = df_clean.dropna()

        if df_clean.empty:
            logger.error("DataFrame is empty after removing null values")
            return None

        # Clean string columns
        if 'city' in df_clean.columns and df_clean['city'].dtype == 'object':
            df_clean['city'] = df_clean['city'].str.strip()

        if 'description' in df_clean.columns and df_clean['description'].dtype == 'object':
            df_clean['description'] = df_clean['description'].str.strip()

        # Convert data types and round values
        df_clean['temperature'] = df_clean['temperature'].astype(float).round(2)
        df_clean['humidity'] = df_clean['humidity'].astype(int)

        # Validate each row using Pydantic schema
        validated_rows = []
        for idx, row in df_clean.iterrows():
            try:
                validated_data = WeatherDataSchema(
                    city=row['city'],
                    temperature=row['temperature'],
                    humidity=row['humidity'],
                    description=row['description'],
                    timestamp=row['timestamp']
                )
                validated_rows.append(validated_data.model_dump())
            except ValidationError as e:
                logger.warning(f"Validation failed for row {idx}: {str(e)}")
                continue

        if not validated_rows:
            logger.error("No rows passed validation")
            return None

        # Create DataFrame from validated data
        df_validated = pd.DataFrame(validated_rows)

        logger.info(f"Successfully transformed {len(df_validated)} rows")

        return df_validated

    except Exception as e:
        logger.error(f"Unexpected error during transformation: {str(e)}")
        raise
