"""Weather backend tools — called by the weather dashboard buttons."""

from __future__ import annotations

from mcp_apps_lab.data.weather import get_weather_data


def get_weather(city: str) -> dict:
    """Get current weather for a city (called by the dashboard buttons)."""
    data = get_weather_data(city)
    return {"city": city.lower(), **data}
