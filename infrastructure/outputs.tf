output "s3_bucket_name" {
  description = "Name of the S3 bucket for weather data"
  value       = aws_s3_bucket.weather_data.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.weather_data.arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.weather_etl.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.weather_etl.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_role.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch Log Group for Lambda"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "cloudwatch_rule_name" {
  description = "Name of the CloudWatch Events rule"
  value       = aws_cloudwatch_event_rule.weather_etl_schedule.name
}

output "cloudwatch_rule_arn" {
  description = "ARN of the CloudWatch Events rule"
  value       = aws_cloudwatch_event_rule.weather_etl_schedule.arn
}

output "next_lambda_execution" {
  description = "Help text for finding next Lambda execution time"
  value       = "View in CloudWatch Events console or use: aws events list-rule-names-by-target --target-arn $(terraform output -raw lambda_function_arn)"
}

output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "deployment_instructions" {
  description = "Instructions for deploying Lambda"
  value = <<-EOT
    1. Build the Docker image: docker build -t weather-etl-pipeline .
    2. Create a ZIP file of the Python code:
       cd src && zip -r ../lambda_function.zip . && cd ..
    3. Update lambda_function.zip path in lambda.tf
    4. Run terraform plan & terraform apply
    5. Monitor Lambda execution in CloudWatch Logs
  EOT
}
