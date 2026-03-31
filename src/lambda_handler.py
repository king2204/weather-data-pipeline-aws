"""AWS Lambda handler for Weather ETL Pipeline."""
import json
import logging
from typing import Any, Dict

from src.extract import extract_weather_data
from src.load import load_to_s3
from src.transform import transform_weather_data
from src.utils.config import AppConfig
from src.utils.logger import configure_logging, get_logger

# Configure logging on module load
config = AppConfig.from_env()
configure_logging(level=config.log_level, log_file=config.log_file)
logger = get_logger("weather_etl")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for Weather ETL Pipeline.

    Args:
        event: Lambda event (CloudWatch Events)
        context: Lambda context

    Returns:
        Response dict with status and results
    """
    logger.info("========== Weather ETL Pipeline Started ==========")
    logger.info(f"AWS Request ID: {context.aws_request_id}")

    try:
        # Validate configuration
        if not config.validate():
            logger.error("Configuration validation failed")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid configuration"})
            }

        logger.info(f"Configuration: {config.to_dict()}")

        # Get cities from event or use default
        cities = event.get("cities", ["Bangkok", "Nakhon Pathom", "Samut Sakhon"])

        # Run pipeline
        all_data = []
        failed_cities = []

        for city in cities:
            try:
                logger.info(f"Processing: {city}")

                # Extract
                df_raw = extract_weather_data(
                    city=city,
                    api_key=config.weather_api_key,
                    api_timeout=config.api_timeout
                )

                if df_raw is None:
                    logger.warning(f"Failed to extract data for {city}")
                    failed_cities.append(city)
                    continue

                # Transform
                df_clean = transform_weather_data(df_raw)

                if df_clean is None:
                    logger.warning(f"Failed to transform data for {city}")
                    failed_cities.append(city)
                    continue

                all_data.append(df_clean)
                logger.info(f"Successfully processed: {city}")

            except Exception as e:
                logger.error(f"Error processing {city}: {str(e)}")
                failed_cities.append(city)
                continue

        if not all_data:
            logger.error("No data to load")
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "No data processed successfully",
                    "failed_cities": failed_cities
                })
            }

        # Combine all data
        import pandas as pd
        df_final = pd.concat(all_data, ignore_index=True)

        # Load to S3
        logger.info(f"Loading {len(df_final)} records to S3...")
        success = load_to_s3(
            df=df_final,
            bucket_name=config.aws_s3_bucket,
            file_format="parquet"
        )

        if not success:
            logger.error("Failed to load data to S3")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Failed to load data to S3"})
            }

        logger.info("========== Weather ETL Pipeline Completed Successfully ==========")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "ETL pipeline completed successfully",
                "records_processed": len(df_final),
                "cities_processed": len(cities) - len(failed_cities),
                "failed_cities": failed_cities,
                "aws_request_id": context.aws_request_id
            })
        }

    except Exception as e:
        logger.error(f"Unexpected error in Lambda handler: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Unexpected error: {str(e)}"})
        }
