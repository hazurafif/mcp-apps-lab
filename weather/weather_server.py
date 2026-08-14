"""Weather app — a FastMCPApp example with prefab UI.

The LLM calls `weather_app(city)` to launch a weather dashboard. The user
switches cities via buttons; each button calls the `get_weather` backend
tool through the host's tools/call proxy (the tool name is hashed server-side
and resolved by FastMCP's `get_tool_by_hash` — the proxy never needs to know
the mapping).

Wire into ai-backend-lab with:

    MCP_SERVERS_JSON='{"weather":{"url":"http://127.0.0.1:8095/mcp","transport":"streamable_http"}}'
"""

from __future__ import annotations

from fastmcp import FastMCP, FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import Badge, Button, Card, Column, Heading, Muted, Row, Text
from prefab_ui.rx import ERROR, RESULT, Rx

app = FastMCPApp("Weather")

CITIES = ["jakarta", "tokyo", "paris", "berlin"]

WEATHER: dict[str, dict] = {
    "jakarta": {"condition": "Cerah", "temperature_c": 24, "humidity": 40, "emoji": "☀️"},
    "tokyo": {"condition": "Berawan", "temperature_c": 18, "humidity": 65, "emoji": "☁️"},
    "paris": {"condition": "Hujan ringan", "temperature_c": 12, "humidity": 80, "emoji": "🌧️"},
    "berlin": {"condition": "Berkabut", "temperature_c": 8, "humidity": 85, "emoji": "🌫️"},
}


def _weather(city: str) -> dict:
    return WEATHER.get(city.lower(), WEATHER["jakarta"])


@app.tool()
def get_weather(city: str) -> dict:
    """Get current weather for a city (called by the dashboard buttons)."""
    data = _weather(city)
    return {"city": city.lower(), **data}


@app.ui()
def weather_app(city: str = "jakarta") -> PrefabApp:
    """Launch a weather dashboard for a city.

    - city: lowercase city name (jakarta, tokyo, paris, berlin)
    """
    city_rx = Rx("city")
    weather = Rx("weather")

    with Column(gap=6, css_class="p-6 max-w-md") as view:
        Heading("Cuaca Sekarang")

        with Row(gap=3, align="center"):
            Badge(city_rx.upper(), variant="secondary")
            Badge(f"{weather.temperature_c}°C", variant="outline")

        with Card(), Column(gap=2, css_class="p-4"):
            Text(
                f"{weather.emoji} {weather.condition}",
                css_class="text-lg font-semibold",
            )
            Muted(f"Kelembapan: {weather.humidity}%")

        with Column(gap=2):
            Text("Ganti kota:", css_class="text-sm font-medium text-muted-foreground")
            with Row(gap=2, wrap=True):
                for city in CITIES:
                    Button(
                        city.title(),
                        variant="outline",
                        css_class="flex-1",
                        on_click=CallTool(
                            get_weather,
                            arguments={"city": city},
                            on_success=[
                                SetState("city", city),
                                SetState("weather", RESULT),
                            ],
                            on_error=ShowToast(ERROR, variant="error"),
                        ),
                    )

    return PrefabApp(
        view=view,
        state={
            "city": city.lower(),
            "weather": _weather(city),
        },
    )


mcp = FastMCP("Weather Server", providers=[app])

if __name__ == "__main__":
    # Port 8095: keeps clear of the quiz app (:8091) and the plain weather
    # demo server (:8094).
    mcp.run(transport="http", host="127.0.0.1", port=8095)
