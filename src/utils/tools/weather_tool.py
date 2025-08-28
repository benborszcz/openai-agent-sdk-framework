# tools_open_meteo.py

from agents import function_tool
from typing import Optional, Union, Iterable, Dict, Any
from src.services.open_meteo import (
    get_current_weather,
    get_daily_forecast,
    get_hourly_forecast,
    get_air_quality,
    get_marine_forecast,
    geocode_search,
    get_historical_weather,
    get_historical_forecast,
    get_weather_bundle,
)

# ---- Forecast tools --------------------------------------------------------

@function_tool
async def tool_get_current_weather(
    latitude: float,
    longitude: float,
    timezone: str = "auto"
) -> Dict[str, Any]:
    """
    Fetch the current weather for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        timezone: The timezone for the results (default: "auto").
    """
    return await get_current_weather(latitude, longitude, timezone=timezone)


@function_tool
async def tool_get_daily_forecast(
    latitude: float,
    longitude: float,
    days: int = 3,
    timezone: str = "auto",
    daily: Optional[Union[str, Iterable[str]]] = None,
) -> Dict[str, Any]:
    """
    Fetch the daily weather forecast for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        days: Number of days to forecast (default: 3).
        timezone: The timezone for the results (default: "auto").
        daily: Optional list of daily metrics to request.
    """
    return await get_daily_forecast(latitude, longitude, days=days, timezone=timezone, daily=daily)


@function_tool
async def tool_get_hourly_forecast(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
    limit_hours: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fetch the hourly weather forecast for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        timezone: The timezone for the results (default: "auto").
        hourly: Optional list of hourly metrics to request.
        limit_hours: Optionally limit the number of hours returned.
    """
    return await get_hourly_forecast(latitude, longitude, timezone=timezone, hourly=hourly, limit_hours=limit_hours)


# ---- Air Quality -----------------------------------------------------------

@function_tool
async def tool_get_air_quality(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
    current: Optional[Union[str, Iterable[str]]] = None,
) -> Dict[str, Any]:
    """
    Fetch the air quality for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        timezone: The timezone for the results (default: "auto").
        hourly: Optional list of hourly air quality metrics.
        current: Optional list of current air quality metrics.
    """
    return await get_air_quality(latitude, longitude, timezone=timezone, hourly=hourly, current=current)


# ---- Marine ----------------------------------------------------------------

@function_tool
async def tool_get_marine_forecast(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
) -> Dict[str, Any]:
    """
    Fetch the marine forecast for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        timezone: The timezone for the results (default: "auto").
        hourly: Optional list of hourly marine metrics to request.
    """
    return await get_marine_forecast(latitude, longitude, timezone=timezone, hourly=hourly)


# ---- Geocoding -------------------------------------------------------------

@function_tool
async def tool_geocode_search(
    name: str,
    count: int = 10,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search for a location by name or postal code using the Open-Meteo Geocoding API.

    This tool queries Open-Meteo’s free geocoding endpoint and returns matching 
    locations with latitude/longitude and metadata. It supports filtering by country, 
    language localization, and multiple result formats.

    Args:
        name: 
            The location name or postal code to search for. 
            - Minimum length: 2 characters (exact match only) 
            - 3 or more characters: enables fuzzy matching.
        count: 
            Maximum number of results to return. 
            - Default: 10 
            - Maximum: 100
        language: 
            Optional ISO language code (lowercase) to localize place names.
            Example: "fr" for French, "es" for Spanish. If no translation exists, 
            falls back to English or the native name.

    Returns:
        A dictionary containing:
        - `results`: A list of matching locations. Each entry may include:
            - `id`: Unique identifier
            - `name`: Location name
            - `latitude` / `longitude`
            - `country`, `country_code`
            - `admin1` … `admin4`: Administrative divisions
            - `timezone`
        - `generationtime_ms`: Server processing time
    """
    #print(f"Geocoding search for '{name}' (count={count}, language={language})")
    ret = await geocode_search(name, count=count, language=language)
    #print(ret)
    return ret

# ---- Historical ------------------------------------------------------------

@function_tool
async def tool_get_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
) -> Dict[str, Any]:
    """
    Fetch historical weather (reanalysis data) for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        start_date: The start date (YYYY-MM-DD).
        end_date: The end date (YYYY-MM-DD).
        timezone: The timezone for the results (default: "auto").
        hourly: Optional list of hourly metrics to request.
    """
    return await get_historical_weather(latitude, longitude, start_date=start_date, end_date=end_date, timezone=timezone, hourly=hourly)


@function_tool
async def tool_get_historical_forecast(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
) -> Dict[str, Any]:
    """
    Fetch archived forecast model data for a given location and time range.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        start_date: The start date (YYYY-MM-DD).
        end_date: The end date (YYYY-MM-DD).
        timezone: The timezone for the results (default: "auto").
        hourly: Optional list of hourly metrics to request.
    """
    return await get_historical_forecast(latitude, longitude, start_date=start_date, end_date=end_date, timezone=timezone, hourly=hourly)


# ---- Convenience bundle ----------------------------------------------------

@function_tool
async def tool_get_weather_bundle(
    latitude: float,
    longitude: float,
    days: int = 3,
    timezone: str = "auto",
) -> Dict[str, Any]:
    """
    Fetch both the current weather and multi-day forecast for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        days: Number of days to forecast (default: 3).
        timezone: The timezone for the results (default: "auto").
    """
    return await get_weather_bundle(latitude, longitude, timezone=timezone, days=days)
