variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "weather-etl-pipeline"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 600
}

variable "lambda_memory" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 1024
  validation {
    condition     = var.lambda_memory >= 128 && var.lambda_memory <= 10240
    error_message = "Lambda memory must be between 128 and 10240 MB."
  }
}

variable "schedule_expression" {
  description = "CloudWatch Events schedule expression"
  type        = string
  default     = "cron(0 9 * * ? *)"  # Daily at 9 AM UTC
}

variable "cities" {
  description = "List of cities to monitor"
  type        = list(string)
  default = [
    "Bangkok", "Nakhon Pathom", "Samut Sakhon", "Samut Prakan",
    "Ang Thong", "Ayutthaya", "Chachoengsao", "Chai Nat",
    "Chon Buri", "Lopburi", "Nakhon Nayok", "Saraburi",
    "Sing Buri", "Samut Songkhram"
  ]
}

variable "data_retention_days" {
  description = "Number of days to retain data before moving to Glacier"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default = {
    Name        = "Weather ETL Pipeline"
    CostCenter  = "Engineering"
    Owner       = "Data Engineering Team"
  }
}
