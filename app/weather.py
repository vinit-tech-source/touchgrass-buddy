"""
weather.py: Geocoding, reverse geocoding, and weather fetching with robust retries.
"""

from __future__ import annotations

import httpx
from dataclasses import dataclass
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
REVERSE_GEOCODING_URL = "https://nominatim.openstreetmap.org/reverse"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

@dataclass
class WeatherInfo:
    temperature_c: float
    rain_chance: int
    wind_kmh: float
    description: str
    is_day: bool
    sunrise_str: str
    sunset_str: str


def _describe_weather(temp_c: float, rain_pct: int, wind_kmh: float) -> str:
    parts: list[str] = []
    if temp_c <= 0: parts.append("freezing cold")
    elif temp_c <= 10: parts.append("quite chilly")
    elif temp_c <= 20: parts.append("mild and pleasant")
    elif temp_c <= 30: parts.append("warm")
    elif temp_c <= 38: parts.append("hot")
    else: parts.append("extremely hot")

    if rain_pct >= 70: parts.append("likely rainy")
    elif rain_pct >= 40: parts.append("chance of rain")

    if wind_kmh >= 50: parts.append("very windy")
    elif wind_kmh >= 30: parts.append("breezy")

    return ", ".join(parts) if parts else "mild and pleasant"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=1, max=5),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def forward_geocode(query: str, count: int = 8) -> list[dict[str, Any]]:
    """Search for locations by name."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            GEOCODING_URL,
            params={"name": query, "count": count, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "name": r.get("name"),
                "admin1": r.get("admin1"),
                "country": r.get("country"),
                "latitude": r.get("latitude"),
                "longitude": r.get("longitude"),
            }
            for r in results
        ]

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=1, max=5),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def reverse_geocode(lat: float, lon: float) -> dict[str, str]:
    """Get location name from coordinates using Nominatim."""
    headers = {"User-Agent": "TouchGrassBuddy/3.0 (github.com/touchgrass-buddy)"}
    async with httpx.AsyncClient(timeout=10, headers=headers) as client:
        resp = await client.get(
            REVERSE_GEOCODING_URL,
            params={"lat": lat, "lon": lon, "format": "jsonv2"},
        )
        resp.raise_for_status()
        data = resp.json()
        
        address = data.get("address", {})
        # Pick the most specific name
        place_name = (
            address.get("village") or address.get("town") or 
            address.get("city") or address.get("suburb") or 
            address.get("county") or "Unknown Location"
        )
        state = address.get("state", "")
        country = address.get("country", "")
        
        display = place_name
        if state: display += f", {state}"
        if country: display += f", {country}"
        
        return {"name": place_name, "display_name": display}


def parse_weather_data(current: dict, daily: dict) -> WeatherInfo:
    temp_c = float(current.get("temperature_2m", 20))
    rain_pct = int(current.get("precipitation_probability", current.get("rain", 0)))
    if rain_pct == 0 and float(current.get("precipitation", 0)) > 0:
        rain_pct = 80
    wind_kmh = float(current.get("wind_speed_10m", 0))
    is_day = bool(current.get("is_day", 1))

    sunrise_str = ""
    sunset_str = ""
    if daily and "sunrise" in daily and daily["sunrise"]:
        sunrise_str = daily["sunrise"][0][-5:]
    if daily and "sunset" in daily and daily["sunset"]:
        sunset_str = daily["sunset"][0][-5:]

    return WeatherInfo(
        temperature_c=temp_c,
        rain_chance=rain_pct,
        wind_kmh=wind_kmh,
        description=_describe_weather(temp_c, rain_pct, wind_kmh),
        is_day=is_day,
        sunrise_str=sunrise_str,
        sunset_str=sunset_str,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=1, max=5),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def get_weather(lat: float, lon: float) -> WeatherInfo:
    """Fetch forecast given coordinates."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,rain,wind_speed_10m,is_day",
                "daily": "sunrise,sunset",
                "timezone": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    return parse_weather_data(data.get("current", {}), data.get("daily", {}))
