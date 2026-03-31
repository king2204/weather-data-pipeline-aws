"""Data validation schemas using Pydantic."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeatherDataSchema(BaseModel):
    """Schema for weather data validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    city: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(..., ge=-273.15, le=70.0)  # Valid temp range
    humidity: int = Field(..., ge=0, le=100)
    description: str = Field(..., min_length=1, max_length=200)
    timestamp: datetime

    @field_validator('city')
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate and clean city name."""
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate and clean description."""
        return v.strip().lower()


class BatchWeatherDataSchema(BaseModel):
    """Schema for batch weather data validation."""

    data: list[WeatherDataSchema]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    record_count: int

    @field_validator('record_count')
    @classmethod
    def validate_record_count(cls, v: int, values: dict) -> int:
        """Validate record count matches data length."""
        if 'data' in values and len(values['data']) != v:
            raise ValueError("record_count must match data length")
        return v
