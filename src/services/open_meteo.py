# async_open_meteo.py
# Requires: httpx  (pip install httpx)

from __future__ import annotations
import asyncio
from typing import Any, Dict, Iterable, List, Optional, Union
import httpx

# ---- Hosts & base paths -----------------------------------------------------
API_BASE = "https://api.open-meteo.com"
FORECAST_PATH = "/v1/forecast"

AIR_QUALITY_BASE = "https://air-quality-api.open-meteo.com"
AIR_QUALITY_PATH = "/v1/air-quality"

MARINE_BASE = "https://marine-api.open-meteo.com"
MARINE_PATH = "/v1/marine"

GEOCODING_BASE = "https://geocoding-api.open-meteo.com"
GEOCODING_PATH = "/v1/search"

ARCHIVE_BASE = "https://archive-api.open-meteo.com"
ARCHIVE_PATH = "/v1/archive"

HIST_FORECAST_BASE = "https://historical-forecast-api.open-meteo.com"
# Same /v1/forecast path & params as normal forecast
HIST_FORECAST_PATH = "/v1/forecast"

DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
DEFAULT_HEADERS = {"Accept": "application/json", "User-Agent": "async-open-meteo/1.0"}


# ---- Utils -----------------------------------------------------------------
def _as_list(value: Optional[Union[str, Iterable[str]]]) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        return [value]
    return list(value)


def build_client(
    *,
    timeout: httpx.Timeout = DEFAULT_TIMEOUT,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=timeout, headers={**DEFAULT_HEADERS, **(headers or {})}
    )


async def _get_json(
    client: httpx.AsyncClient,
    url: str,
    params: Dict[str, Any],
    *,
    retries: int = 2,
    backoff: float = 0.6,
) -> Dict[str, Any]:
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            last_exc = exc
            if attempt < retries:
                await asyncio.sleep(backoff * (2**attempt))
            else:
                raise
    assert last_exc
    raise last_exc


# ---- Forecast (current/hourly/daily) ---------------------------------------
async def get_current_weather(
    lat: float,
    lon: float,
    *,
    timezone: str = "auto",
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        data = await _get_json(
            client,
            f"{API_BASE}{FORECAST_PATH}",
            {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "timezone": timezone,
            },
        )
        return data.get("current_weather", {}) or {}
    finally:
        if close:
            await client.aclose()


async def get_hourly_forecast(
    lat: float,
    lon: float,
    *,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
    limit_hours: Optional[int] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    fields = _as_list(hourly) or [
        "temperature_2m",
        "precipitation",
        "windspeed_10m",
        "weathercode",
    ]
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        data = await _get_json(
            client,
            f"{API_BASE}{FORECAST_PATH}",
            {"latitude": lat, "longitude": lon, "hourly": fields, "timezone": timezone},
        )
        hourly_block = data.get("hourly", {}) or {}
        if limit_hours and "time" in hourly_block:
            n = min(limit_hours, len(hourly_block["time"]))
            for k, v in list(hourly_block.items()):
                if isinstance(v, list):
                    hourly_block[k] = v[:n]
        return hourly_block
    finally:
        if close:
            await client.aclose()


async def get_daily_forecast(
    lat: float,
    lon: float,
    *,
    days: int = 3,
    timezone: str = "auto",
    daily: Optional[Union[str, Iterable[str]]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    metrics = _as_list(daily) or [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
    ]
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        data = await _get_json(
            client,
            f"{API_BASE}{FORECAST_PATH}",
            {
                "latitude": lat,
                "longitude": lon,
                "daily": metrics,
                "forecast_days": max(1, int(days)),
                "timezone": timezone,
            },
        )
        return data.get("daily", {}) or {}
    finally:
        if close:
            await client.aclose()


# ---- Air Quality -----------------------------------------------------------
async def get_air_quality(
    lat: float,
    lon: float,
    *,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
    current: Optional[Union[str, Iterable[str]]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    h = _as_list(hourly)
    c = _as_list(current)
    params = {"latitude": lat, "longitude": lon, "timezone": timezone}
    if h:
        params["hourly"] = h
    if c:
        params["current"] = c
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        return await _get_json(client, f"{AIR_QUALITY_BASE}{AIR_QUALITY_PATH}", params)
    finally:
        if close:
            await client.aclose()


# ---- Marine ----------------------------------------------------------------
async def get_marine_forecast(
    lat: float,
    lon: float,
    *,
    timezone: str = "auto",
    hourly: Optional[Union[str, Iterable[str]]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    fields = _as_list(hourly) or [
        "wave_height",
        "wave_direction",
        "wave_period",
        "wind_wave_height",
    ]
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        return await _get_json(
            client,
            f"{MARINE_BASE}{MARINE_PATH}",
            {"latitude": lat, "longitude": lon, "hourly": fields, "timezone": timezone},
        )
    finally:
        if close:
            await client.aclose()


# ---- Geocoding -------------------------------------------------------------
async def geocode_search(
    name: str,
    *,
    count: int = 10,
    language: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    params = {"name": name, "count": max(1, min(100, int(count)))}
    if language:
        params["language"] = language
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        ret = await _get_json(client, f"{GEOCODING_BASE}{GEOCODING_PATH}", params)
        # print(ret)
        return ret
    finally:
        if close:
            await client.aclose()


# ---- Historical (Reanalysis) -----------------------------------------------
async def get_historical_weather(
    lat: float,
    lon: float,
    *,
    start_date: str,
    end_date: str,
    hourly: Optional[Union[str, Iterable[str]]] = None,
    timezone: str = "auto",
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    fields = _as_list(hourly) or ["temperature_2m", "precipitation", "windspeed_10m"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": fields,
        "timezone": timezone,
    }
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        return await _get_json(client, f"{ARCHIVE_BASE}{ARCHIVE_PATH}", params)
    finally:
        if close:
            await client.aclose()


# ---- Historical Forecast (recent years) ------------------------------------
async def get_historical_forecast(
    lat: float,
    lon: float,
    *,
    start_date: str,
    end_date: str,
    hourly: Optional[Union[str, Iterable[str]]] = None,
    timezone: str = "auto",
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    fields = _as_list(hourly) or [
        "temperature_2m",
        "precipitation",
        "windspeed_10m",
        "weathercode",
    ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": fields,
        "timezone": timezone,
    }
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        return await _get_json(
            client, f"{HIST_FORECAST_BASE}{HIST_FORECAST_PATH}", params
        )
    finally:
        if close:
            await client.aclose()


# ---- Convenience bundle -----------------------------------------------------
async def get_weather_bundle(
    lat: float,
    lon: float,
    *,
    timezone: str = "auto",
    days: int = 3,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    close = False
    if client is None:
        client, close = build_client(), True
    try:
        t1 = asyncio.create_task(
            get_current_weather(lat, lon, timezone=timezone, client=client)
        )
        t2 = asyncio.create_task(
            get_daily_forecast(lat, lon, days=days, timezone=timezone, client=client)
        )
        current, daily = await asyncio.gather(t1, t2)
        return {"current": current, "daily": daily}
    finally:
        if close:
            await client.aclose()
