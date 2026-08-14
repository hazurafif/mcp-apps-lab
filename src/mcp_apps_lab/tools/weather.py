"""Weather backend tools — called by the weather dashboard."""

from __future__ import annotations

from mcp_apps_lab.data.weather import get_weather_data, resolve_city


def get_weather(city: str) -> dict:
    """Get current weather for a city (called by the dashboard).

    City names are looked up directly — no geocoding. Unknown names fall
    back to Jakarta; ``is_fallback`` flags that so the UI can say so.

    Returns a dict with:
    - city: the resolved city name (lowercase)
    - is_fallback: whether the requested name wasn't found
    - condition / temperature_c / humidity / emoji: the weather itself
    """
    normalized = city.strip().lower()
    effective = resolve_city(normalized)
    return {
        "city": effective,
        "is_fallback": effective != normalized,
        **get_weather_data(effective),
    }
