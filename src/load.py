"""Weather data loading module."""
import logging
import os
from datetime import datetime
from typing import Literal, Optional

import boto3
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger("weather_etl")


def load_to_s3(
    df: Optional[pd.DataFrame],
    bucket_name: Optional[str] = None,
    file_name: Optional[str] = None,
    file_format: Literal["csv", "parquet", "json"] = "parquet",
    partition_by_date: bool = True
) -> bool:
    """
    Upload weather data to AWS S3.

    Args:
        df: DataFrame to upload
        bucket_name: S3 bucket name (from env if not provided)
        file_name: S3 object key/path
        file_format: File format (csv, parquet, json)
        partition_by_date: Whether to partition by date

    Returns:
        True if successful, False otherwise
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame, skipping S3 upload")
        return False

    # Get credentials from environment
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "ap-southeast-1")
    bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET")

    if not all([aws_access_key, aws_secret_key, bucket_name]):
        logger.error("Missing AWS credentials or S3 bucket configuration")
        return False

    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        # Generate file path
        if partition_by_date:
            now = datetime.now()
            file_name = file_name or f"processed/year={now.year}/month={now.month:02d}/day={now.day:02d}/weather_{now.strftime('%Y%m%d_%H%M%S')}.{file_format}"
        else:
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"processed/weather_{timestamp}.{file_format}"

        # Convert to appropriate format
        if file_format == "parquet":
            buffer = df.to_parquet(index=False)
            content_type = "application/octet-stream"
        elif file_format == "json":
            buffer = df.to_json(orient="records").encode()
            content_type = "application/json"
        else:  # csv
            buffer = df.to_csv(index=False).encode()
            content_type = "text/csv"

        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=buffer,
            ContentType=content_type
        )

        logger.info(f"Successfully uploaded to S3: s3://{bucket_name}/{file_name}")
        return True

    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return False


def load_to_local_csv(
    df: Optional[pd.DataFrame],
    file_path: str = "data/weather_data.csv"
) -> bool:
    """
    Save weather data to local CSV file.

    Args:
        df: DataFrame to save
        file_path: Local file path

    Returns:
        True if successful, False otherwise
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame, skipping local CSV save")
        return False

    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df.to_csv(file_path, index=False)
        logger.info(f"Successfully saved data to: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        return False


def load_to_local_parquet(
    df: Optional[pd.DataFrame],
    file_path: str = "data/weather_data.parquet"
) -> bool:
    """
    Save weather data to local Parquet file.

    Args:
        df: DataFrame to save
        file_path: Local file path

    Returns:
        True if successful, False otherwise
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame, skipping local Parquet save")
        return False

    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df.to_parquet(file_path, index=False)
        logger.info(f"Successfully saved data to: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Error saving to Parquet: {str(e)}")
        return False
