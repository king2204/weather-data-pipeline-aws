"""Unit tests for load module."""
import os
from unittest.mock import MagicMock, patch

import boto3
import pandas as pd
import pytest
from moto import mock_aws

from src.load import load_to_local_csv, load_to_local_parquet, load_to_s3


def test_load_to_local_csv(sample_weather_data, tmp_path):
    """Test loading weather data to local CSV."""
    csv_file = tmp_path / "test_weather.csv"

    result = load_to_local_csv(sample_weather_data, str(csv_file))

    assert result is True
    assert csv_file.exists()

    # Verify content
    loaded_df = pd.read_csv(csv_file)
    assert len(loaded_df) == 2
    assert list(loaded_df.columns) == [
        "city", "temperature", "humidity", "description", "timestamp"
    ]


def test_load_to_local_csv_empty_dataframe(empty_dataframe, tmp_path):
    """Test loading empty DataFrame to CSV."""
    csv_file = tmp_path / "test_weather.csv"

    result = load_to_local_csv(empty_dataframe, str(csv_file))

    assert result is False
    assert not csv_file.exists()


def test_load_to_local_csv_none():
    """Test loading None to CSV."""
    result = load_to_local_csv(None, "dummy_path.csv")
    assert result is False


def test_load_to_local_parquet(sample_weather_data, tmp_path):
    """Test loading weather data to local Parquet."""
    parquet_file = tmp_path / "test_weather.parquet"

    result = load_to_local_parquet(sample_weather_data, str(parquet_file))

    assert result is True
    assert parquet_file.exists()

    # Verify content
    loaded_df = pd.read_parquet(parquet_file)
    assert len(loaded_df) == 2


def test_load_to_local_parquet_creates_directory(sample_weather_data, tmp_path):
    """Test that loading creates necessary directories."""
    parquet_file = tmp_path / "subdir" / "test_weather.parquet"

    result = load_to_local_parquet(sample_weather_data, str(parquet_file))

    assert result is True
    assert parquet_file.exists()


@mock_aws
def test_load_to_s3_success(sample_weather_data):
    """Test loading weather data to S3 with Parquet format."""
    # Setup mock S3
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'test-weather-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )

    # Mock AWS credentials
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_S3_BUCKET': bucket_name
    }):
        result = load_to_s3(
            sample_weather_data,
            bucket_name=bucket_name,
            file_format="parquet"
        )

        assert result is True

        # Verify file exists in S3
        response = s3.list_objects_v2(Bucket=bucket_name)
        assert 'Contents' in response
        assert len(response['Contents']) == 1


@mock_aws
def test_load_to_s3_csv_format(sample_weather_data):
    """Test loading to S3 with CSV format."""
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'test-weather-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )

    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_S3_BUCKET': bucket_name
    }):
        result = load_to_s3(
            sample_weather_data,
            bucket_name=bucket_name,
            file_format="csv"
        )

        assert result is True


@mock_aws
def test_load_to_s3_json_format(sample_weather_data):
    """Test loading to S3 with JSON format."""
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'test-weather-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )

    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_S3_BUCKET': bucket_name
    }):
        result = load_to_s3(
            sample_weather_data,
            bucket_name=bucket_name,
            file_format="json"
        )

        assert result is True


def test_load_to_s3_missing_credentials(sample_weather_data):
    """Test S3 loading with missing credentials."""
    with patch.dict(os.environ, {}, clear=True):
        result = load_to_s3(sample_weather_data, bucket_name='test-bucket')
        assert result is False


def test_load_to_s3_empty_dataframe(empty_dataframe):
    """Test S3 loading with empty DataFrame."""
    result = load_to_s3(empty_dataframe, bucket_name='test-bucket')
    assert result is False


def test_load_to_s3_none():
    """Test S3 loading with None."""
    result = load_to_s3(None, bucket_name='test-bucket')
    assert result is False


@mock_aws
def test_load_to_s3_with_date_partitioning(sample_weather_data):
    """Test S3 loading with date-based partitioning."""
    s3 = boto3.client('s3', region_name='ap-southeast-1')
    bucket_name = 'test-weather-bucket'
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'}
    )

    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_REGION': 'ap-southeast-1',
        'AWS_S3_BUCKET': bucket_name
    }):
        result = load_to_s3(
            sample_weather_data,
            bucket_name=bucket_name,
            file_format="parquet",
            partition_by_date=True
        )

        assert result is True

        # Verify partitioned path exists
        response = s3.list_objects_v2(Bucket=bucket_name)
        key = response['Contents'][0]['Key']
        assert 'year=' in key
        assert 'month=' in key
        assert 'day=' in key
