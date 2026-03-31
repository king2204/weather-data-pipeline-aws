# Lambda function (using Docker image from ECR)
resource "aws_lambda_function" "weather_etl" {
  # NOTE: In production, build and push Docker image to ECR first
  # For now, using ZIP package deployment
  # See outputs for instructions

  filename            = "lambda_function.zip"  # Will be created during deployment
  function_name       = var.project_name
  role                = aws_iam_role.lambda_role.arn
  handler             = "src.lambda_handler.lambda_handler"
  runtime             = "python3.11"
  timeout             = var.lambda_timeout
  memory_size         = var.lambda_memory

  environment {
    variables = {
      LOG_LEVEL  = "INFO"
      BATCH_SIZE = 50
    }
  }

  depends_on = [aws_iam_role_policy.lambda_policy]

  tags = {
    Name = "Weather ETL Lambda"
  }
}

# CloudWatch Events Rule for scheduling
resource "aws_cloudwatch_event_rule" "weather_etl_schedule" {
  name                = "${var.project_name}-schedule"
  description         = "Trigger Weather ETL Pipeline daily"
  schedule_expression = var.schedule_expression

  tags = {
    Name = "Weather ETL Schedule"
  }
}

# CloudWatch Events Target (Lambda)
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.weather_etl_schedule.name
  target_id = "WeatherETLLambda"
  arn       = aws_lambda_function.weather_etl.arn

  input = jsonencode({
    cities = var.cities
  })
}

# Lambda Permission for CloudWatch Events
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weather_etl.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weather_etl_schedule.arn
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_duration" {
  alarm_name          = "${var.project_name}-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Average"
  threshold           = var.lambda_timeout * 800  # 80% of timeout
  alarm_description   = "Alert when Lambda duration exceeds 80% timeout"

  dimensions = {
    FunctionName = aws_lambda_function.weather_etl.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alert when Lambda function errors occur"

  dimensions = {
    FunctionName = aws_lambda_function.weather_etl.function_name
  }
}
