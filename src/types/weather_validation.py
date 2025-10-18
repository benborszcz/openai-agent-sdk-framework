from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, Iterable, Union


class LatLon(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class DailyForecastParams(LatLon):
    days: int = Field(3, ge=1, le=14)
    timezone: str = Field("auto", min_length=1)
    daily: Optional[Union[str, Iterable[str]]] = None


class HourlyForecastParams(LatLon):
    timezone: str = Field("auto", min_length=1)
    hourly: Optional[Union[str, Iterable[str]]] = None
    limit_hours: Optional[int] = Field(None, gt=0, le=168)


class AirQualityParams(LatLon):
    timezone: str = Field("auto", min_length=1)
    hourly: Optional[Union[str, Iterable[str]]] = None
    current: Optional[Union[str, Iterable[str]]] = None


class MarineParams(LatLon):
    timezone: str = Field("auto", min_length=1)
    hourly: Optional[Union[str, Iterable[str]]] = None


class GeocodeParams(BaseModel):
    name: str = Field(..., min_length=2)
    count: int = Field(10, ge=1, le=100)
    language: Optional[str] = Field(None, min_length=2, max_length=5)


class HistoricalParams(LatLon):
    start_date: str
    end_date: str
    timezone: str = Field("auto", min_length=1)
    hourly: Optional[Union[str, Iterable[str]]] = None

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("Dates must be ISO format YYYY-MM-DD")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_order(cls, v: str, info):
        start_val = info.data.get("start_date")
        if start_val:
            try:
                if date.fromisoformat(v) < date.fromisoformat(start_val):
                    raise ValueError("end_date must be >= start_date")
            except ValueError:
                pass
        return v


class HistoricalForecastParams(HistoricalParams):
    pass


class WeatherBundleParams(LatLon):
    days: int = Field(3, ge=1, le=14)
    timezone: str = Field("auto", min_length=1)
