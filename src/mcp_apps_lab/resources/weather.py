"""Weather resources — ``weather://{city}/current`` (live Open-Meteo)."""

from __future__ import annotations

import asyncio
import json

from fastmcp import FastMCP

from mcp_apps_lab.tools.weather import get_weather


def register(mcp: FastMCP) -> None:
    """Register the weather resources on the server."""

    @mcp.resource("weather://{city}/current")
    async def current_weather(city: str) -> str:
        """Current weather + 5-day forecast for a city as JSON (live API).

        - city: any city name (e.g. bekasi, tokyo, paris) — geocoded live
        """
        data = await asyncio.to_thread(get_weather, city)
        return json.dumps(data, indent=2)
