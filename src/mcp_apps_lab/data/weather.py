"""Weather data — the built-in city forecast table."""

from __future__ import annotations

CITIES = ["jakarta", "tokyo", "paris", "berlin"]

WEATHER: dict[str, dict] = {
    "jakarta": {"condition": "Cerah", "temperature_c": 24, "humidity": 40, "emoji": "☀️"},
    "tokyo": {"condition": "Berawan", "temperature_c": 18, "humidity": 65, "emoji": "☁️"},
    "paris": {"condition": "Hujan ringan", "temperature_c": 12, "humidity": 80, "emoji": "🌧️"},
    "berlin": {"condition": "Berkabut", "temperature_c": 8, "humidity": 85, "emoji": "🌫️"},
}


def get_weather_data(city: str) -> dict:
    """Look up a city's weather; unknown cities fall back to jakarta."""
    return WEATHER.get(city.lower(), WEATHER["jakarta"])


def resolve_city(city: str) -> str:
    """Normalize a city name; unknown names resolve to "jakarta".

    Used by the backend tool so callers know whether a fallback happened.
    """
    normalized = city.strip().lower()
    return normalized if normalized in WEATHER else "jakarta"
