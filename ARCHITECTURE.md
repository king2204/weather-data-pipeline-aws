# Weather ETL Pipeline - Architecture Documentation

## Overview

The Weather ETL Pipeline is a production-grade data engineering solution that collects, processes, and stores weather data from multiple cities. It leverages AWS serverless technologies for scalability and cost-effectiveness.

## System Architecture

### High-Level Flow

```
┌─────────────────────┐
│  CloudWatch Events  │ (Daily @ 9 AM UTC)
│  (Scheduler)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AWS Lambda        │ (Python 3.11)
│   (Orchestrator)    │
└──────────┬──────────┘
           │
           ├──────────────────────┤
           │                      │
           ▼                      ▼
    ┌─────────────┐        ┌──────────────┐
    │  Extract    │        │  Transform   │
    │  (API Call) │        │  (Validate)  │
    └──────┬──────┘        └──────┬───────┘
           │                      │
           ▼                      ▼
    ┌─────────────────────────────────────┐
    │         Load (Parquet)              │
    │        (S3 Data Lake)               │
    └─────────────┬───────────────────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │    S3 Bucket        │
        │  (Partitioned Data) │
        │  year/month/day/    │
        └────────────┬────────┘
                     │
                     ▼
        ┌──────────────────────┐
        │  AWS Athena          │
        │  (SQL Analytics)     │
        └──────────────────────┘
```

## Components

### 1. Data Extraction (`src/extract.py`)

**Purpose**: Fetch weather data from OpenWeatherMap API

**Features**:
- Retry logic with exponential backoff (3 attempts)
- Configurable timeout handling
- Graceful error handling
- Type hints and logging

**Key Functions**:
```python
extract_weather_data(city: str, api_key: str) -> Optional[pd.DataFrame]
```

**Error Handling**:
- API timeouts (10s default)
- Invalid API responses
- Network errors
- Missing credentials

### 2. Data Transformation (`src/transform.py`)

**Purpose**: Clean, validate, and prepare data for storage

**Features**:
- Null value handling (drop rows with missing data)
- Data type conversion
- Range validation using Pydantic schemas
- String normalization

**Validation Rules**:
- Temperature: -273.15°C to 70°C (realistic range)
- Humidity: 0-100%
- City name: 1-100 characters
- Description: 1-200 characters

**Data Quality Checks**:
1. **Schema Validation**: Pydantic models ensure type safety
2. **Business Logic**: Temperature and humidity ranges
3. **Data Completeness**: No null values allowed
4. **Consistency**: Standardized string formatting

### 3. Data Loading (`src/load.py`)

**Purpose**: Store processed data in S3 for analytics

**Supported Formats**:
- Parquet (default, columnar, compressed)
- CSV (for compatibility)
- JSON (for APIs)

**S3 Partitioning**:
```
s3://bucket/
├── raw/                          (unprocessed data)
├── processed/
│   ├── year=2026/
│   │   ├── month=03/
│   │   │   ├── day=31/
│   │   │   │   └── weather_YYYYMMDD_HHMMSS.parquet
│   │   │   └── day=30/
│   │   └── month=02/
```

**Lifecycle Management**:
- Move to Glacier after 90 days (cost optimization)
- Delete after 2 years (retention policy)

### 4. AWS Integration

#### Lambda Function (`src/lambda_handler.py`)

Entry point for AWS Lambda execution:

```python
def lambda_handler(event: Dict, context: Any) -> Dict
```

**Responsibilities**:
- Load configuration
- Orchestrate E/T/L steps
- Handle errors gracefully
- Return JSON response

**Event Format**:
```json
{
  "cities": ["Bangkok", "Chiang Mai", ...]
}
```

**Response Format**:
```json
{
  "statusCode": 200,
  "body": {
    "message": "ETL pipeline completed successfully",
    "records_processed": 14,
    "cities_processed": 14,
    "failed_cities": []
  }
}
```

#### S3 Data Lake

**Bucket Structure**:
- Public access blocked (security)
- Versioning enabled (recovery)
- Encryption enabled (data protection)
- Lifecycle policies (cost optimization)

**Partitioning Strategy**:
- Year/month/day: Efficient Athena queries
- Fast pruning for date ranges
- Supports incremental loads

#### CloudWatch Integration

**Logs**:
- Lambda logs to `/aws/lambda/weather-etl-pipeline`
- Retention: 14 days (configurable)
- Structured logging for easy parsing

**Metrics**:
- Duration: Lambda execution time
- Invocations: Number of runs
- Errors: Failure count
- ConcurrentExecutions: Parallel runs

**Alarms**:
- Duration > 80% timeout (600s)
- Errors >= 1
- SNS notifications on alarm

#### Event Scheduling

**CloudWatch Events Rule**:
- Daily at 9 AM UTC
- Configurable schedule expression
- Automatic retry on failure

## Technology Stack

### Core
- **Language**: Python 3.11
- **Runtime**: AWS Lambda
- **Data Processing**: Pandas, Pydantic
- **API**: OpenWeatherMap REST API

### Cloud Services
- **Compute**: AWS Lambda
- **Storage**: AWS S3
- **Analytics**: AWS Athena
- **Logging**: AWS CloudWatch
- **Scheduling**: AWS CloudWatch Events
- **Secrets**: AWS Secrets Manager (planned)

### Development & Testing
- **Testing**: pytest, pytest-cov
- **Code Quality**: flake8, mypy, black
- **Containerization**: Docker, docker-compose
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions

### Monitoring & Observability
- **Logging**: Python logging module
- **Metrics**: CloudWatch metrics
- **Alerting**: CloudWatch alarms
- **Tracing**: X-Ray (planned)

## Data Flow

### 1. Extraction Phase
```
CloudWatch Events
       ↓
Lambda triggered
       ↓
Load cities list from event
       ↓
For each city:
  - Fetch from OpenWeatherMap API
  - Parse JSON response
  - Convert to DataFrame
       ↓
Collect all DataFrames
```

### 2. Transformation Phase
```
Raw DataFrame (1 city per row)
       ↓
Check for nulls, drop if found
       ↓
Normalize strings (strip, lowercase)
       ↓
Convert types (temperature: float, humidity: int)
       ↓
Validate ranges (Pydantic)
       ↓
Combine results (one DataFrame pers city)
       ↓
Aggregated Clean DataFrame
```

### 3. Loading Phase
```
Clean DataFrame
       ↓
Add partition columns (year, month, day)
       ↓
Convert to Parquet format
       ↓
Upload to S3 with partitioned path
       ↓
Data Lake S3 Bucket
```

## Error Handling & Resilience

### Retry Strategy
- **Extract**: 3 attempts with exponential backoff (1s → 2s → 4s)
- **Transform**: No retries (fails on validation error)
- **Load**: 1 attempt with detailed error logging

### Failure Scenarios

| Scenario | Handling |
|----------|----------|
| API timeout | Retry with backoff, eventually fail |
| Invalid API response | Skip city, log error, continue |
| S3 upload failure | Log error, return failure status |
| Invalid data | Drop row, log validation error |
| Lambda timeout | CloudWatch alarm triggered |
| Lambda OOM | Auto-scale memory in Terraform |

## Performance Considerations

### Optimization
1. **Parquet Format**:
   - Columnar storage → faster queries
   - Compression → 70% size reduction
   - Large file throughput

2. **S3 Partitioning**:
   - Query pruning (scan only relevant partitions)
   - Parallel reads in Lambda
   - Efficient Athena scans

3. **Batch Processing**:
   - Process multiple cities in single Lambda
   - Combine DataFrames efficiently
   - Single S3 upload per run

### Scalability
- **Horizontal**: Process more cities by increasing Lambda memory
- **Vertical**: Increase Lambda timeout for larger batches
- **Temporal**: Schedule multiple runs per day

## Security

### Authentication & Authorization
- **API Key**: OpenWeatherMap API in environment variables
- **AWS**: IAM roles with least-privilege
- **S3**: Block public access, encryption enabled

### Data Protection
- **In Transit**: HTTPS for API, encrypted S3 connections
- **At Rest**: AES-256 S3 encryption
- **Access**: IAM policies restrict bucket access

### Best Practices
- No secrets in code (using `.env` and Secrets Manager)
- Audit CloudWatch logs for suspicious activity
- Regular key rotation
- Principle of least privilege in IAM

## Deployment

### Infrastructure as Code (Terraform)
- Reproducible deployments
- Version controlled infrastructure
- Easy rollback
- Environment parity

### Deployment Steps
1. Create S3 bucket for Terraform state
2. Initialize Terraform
3. Plan infrastructure changes
4. Apply Terraform
5. Update Lambda code
6. Monitor CloudWatch logs

## Monitoring & Operations

### Metrics to Track
- **API Response Time**: Average latency
- **Data Quality**: % rows that passed validation
- **Pipeline Duration**: E2E execution time
- **Error Rate**: % failed cities
- **S3 Storage**: Total bytes stored

### Real-World Queries
```sql
-- Get latest weather for each city
SELECT city, temperature, humidity,
       ROW_NUMBER() OVER (PARTITION BY city ORDER BY timestamp DESC) as rn
FROM weather
WHERE rn = 1;

-- Average temperature by day
SELECT DATE(timestamp) as date, AVG(temperature) as avg_temp
FROM weather
WHERE city = 'Bangkok'
GROUP BY DATE(timestamp);

-- Cities with highest humidity
SELECT city, MAX(humidity) as max_humidity
FROM weather
GROUP BY city
ORDER BY max_humidity DESC;
```

## Future Enhancements

### Short Term
- [ ] AWS Secrets Manager integration
- [ ] X-Ray tracing for debugging
- [ ] Incremental/delta loads
- [ ] Historical data aggregations

### Medium Term
- [ ] Multi-region deployment
- [ ] Real-time streaming (Kinesis)
- [ ] Advanced alerting (SNS)
- [ ] Cost anomaly detection

### Long Term
- [ ] Machine learning predictions
- [ ] Data catalog (AWS Glue)
- [ ] dbt for data transformations
- [ ] Advanced analytics dashboards

## References

- [AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Amazon S3](https://docs.aws.amazon.com/s3/)
- [AWS Athena](https://docs.aws.amazon.com/athena/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)

---

**Last Updated**: 2026-03-31
**Version**: 1.0.0
