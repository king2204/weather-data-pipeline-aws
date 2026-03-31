resource "aws_s3_bucket" "weather_data" {
  bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "Weather ETL Data Lake"
  }
}

resource "aws_s3_bucket_versioning" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    filter {
      prefix = "processed/"
    }

    transition {
      days          = var.data_retention_days
      storage_class = "GLACIER"
    }

    expiration {
      days = 730  # Keep for 2 years before deletion
    }
  }
}

resource "aws_s3_bucket_logging" "weather_data" {
  bucket = aws_s3_bucket.weather_data.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-logs/"
}

# Logs bucket
resource "aws_s3_bucket" "logs" {
  bucket = "${var.project_name}-logs-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "Weather ETL Logs"
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    expiration {
      days = 30  # Delete logs after 30 days
    }
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = 14

  tags = {
    Name = "Weather ETL Lambda Logs"
  }
}
