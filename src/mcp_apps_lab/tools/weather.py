"""Weather backend tools — live forecast from the Open-Meteo API.

``get_weather`` geocodes any city name (no more fixed-city table) and returns
current conditions plus a 5-day forecast, with the city's local time. Falls
back to built-in sample data when the API is unreachable (``live=False``).
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp_apps_lab.data.weather import DAY_NAMES, WEATHER_CODES, get_weather_data

_UA = "Mozilla/5.0 (mcp-apps-lab; personal demo)"
_FETCH_TIMEOUT = 8.0
_FORECAST_DAYS = 5

_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _fetch_json(url: str) -> dict:
    """GET a JSON API endpoint (raises on any failure)."""
    request = urllib.request.Request(
        url, headers={"User-Agent": _UA, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=_FETCH_TIMEOUT) as response:
        return json.loads(response.read())


def _geocode(city: str) -> dict | None:
    """Resolve a city name to coordinates + metadata; None if not found."""
    params = urllib.parse.urlencode(
        {"name": city, "count": 5, "language": "en", "format": "json"}
    )
    data = _fetch_json(f"{_GEO_URL}?{params}")
    results = data.get("results") or []
    if not results:
        return None
    best = results[0]
    return {
        "lat": best["latitude"],
        "lon": best["longitude"],
        "label": best.get("name") or city.title(),
        "region": best.get("admin1") or "",
        "country": best.get("country") or "",
        "timezone": best.get("timezone") or "UTC",
    }


def _forecast(lat: float, lon: float, timezone: str) -> dict:
    """Fetch current conditions + daily forecast for a location."""
    params = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "weather_code,wind_speed_10m"
            ),
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": timezone,
            "forecast_days": _FORECAST_DAYS,
            "wind_speed_unit": "kmh",
        }
    )
    data = _fetch_json(f"{_FORECAST_URL}?{params}")

    current = data["current"]
    condition, emoji = WEATHER_CODES.get(current["weather_code"], ("Cerah", "☀️"))

    daily = data["daily"]
    forecast = []
    for i, day in enumerate(daily["time"]):
        day_condition, day_emoji = WEATHER_CODES.get(
            daily["weather_code"][i], ("Cerah", "☀️")
        )
        day_name = "Hari Ini" if i == 0 else DAY_NAMES[datetime.fromisoformat(day).weekday()]
        forecast.append(
            {
                "day": day_name,
                "date": day,
                "temp_min": round(daily["temperature_2m_min"][i]),
                "temp_max": round(daily["temperature_2m_max"][i]),
                "condition": day_condition,
                "emoji": day_emoji,
            }
        )

    now = datetime.now(ZoneInfo(timezone))
    return {
        "temperature_c": round(current["temperature_2m"]),
        "feels_like_c": round(current["apparent_temperature"]),
        "humidity": current["relative_humidity_2m"],
        "wind_kmh": round(current["wind_speed_10m"]),
        "condition": condition,
        "emoji": emoji,
        "timezone": timezone,
        "updated_local": now.strftime("%H:%M"),
        "tz_name": now.tzname() or "",
        "forecast": forecast,
    }


def _offline_fallback(city: str) -> dict:
    """Sample data when the API is unreachable (unknown city → Jakarta)."""
    base = get_weather_data(city)
    now = datetime.now(ZoneInfo(base["timezone"]))
    return {
        **base,
        "city": city.lower(),
        "is_fallback": True,
        "live": False,
        "updated_local": now.strftime("%H:%M"),
        "tz_name": now.tzname() or "",
    }


def get_weather(city: str) -> dict:
    """Get current weather + 5-day forecast for any city (live API).

    Args:
        city: Any city name (e.g. "bekasi", "singapore", "london"). Geocoded
            against the Open-Meteo API; unknown names fall back to Jakarta.

    Returns a dict with:
    - city: the requested name (lowercase)
    - label: the resolved city name (e.g. "Bekasi")
    - region / country: administrative info from geocoding
    - is_fallback: whether the requested name wasn't found (→ Jakarta)
    - live: whether data came from the live API (False = sample data)
    - temperature_c / feels_like_c / humidity / wind_kmh / condition / emoji
    - timezone / updated_local / tz_name: the city's local time
    - forecast: list of daily forecasts (day, date, temp_min, temp_max,
      condition, emoji)
    """
    name = city.strip().lower()
    try:
        geo = _geocode(name)
        is_fallback = geo is None
        if geo is None:
            # Unknown city → fall back to Jakarta (resolved live if possible).
            geo = _geocode("jakarta") or {
                "lat": -6.2088,
                "lon": 106.8456,
                "label": "Jakarta",
                "region": "DKI Jakarta",
                "country": "Indonesia",
                "timezone": "Asia/Jakarta",
            }
        current = _forecast(geo["lat"], geo["lon"], geo["timezone"])
        return {
            "city": name,
            "label": geo["label"],
            "region": geo["region"],
            "country": geo["country"],
            "is_fallback": is_fallback,
            "live": True,
            **current,
        }
    except Exception:
        return _offline_fallback(name)
