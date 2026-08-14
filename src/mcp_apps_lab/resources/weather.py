"""Weather resources — ``weather://{city}/current``."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from mcp_apps_lab.data.weather import get_weather_data


def register(mcp: FastMCP) -> None:
    """Register the weather resources on the server."""

    @mcp.resource("weather://{city}/current")
    def current_weather(city: str) -> str:
        """Current weather for a city as JSON.

        - city: lowercase city name (jakarta, tokyo, paris, berlin)
        """
        data = get_weather_data(city)
        return json.dumps({"city": city.lower(), **data}, indent=2)
