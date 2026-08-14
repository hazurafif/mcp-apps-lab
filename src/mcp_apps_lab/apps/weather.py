"""Weather app — a city dashboard with free-text location input.

The LLM calls ``weather_app(city)`` to launch a weather dashboard. The user
can type any location into the input — names are looked up directly, no
geocoding — or tap a preset city button. Each lookup calls the ``get_weather``
backend tool (from ``mcp_apps_lab.tools``) through the host's tools/call
proxy (the tool name is hashed server-side and resolved by FastMCP's
``get_tool_by_hash`` — the proxy never needs to know the mapping). Unknown
names fall back to Jakarta, and the toast says so.
"""

from __future__ import annotations

from fastmcp import FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Button,
    Card,
    Column,
    Heading,
    Input,
    Muted,
    Row,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx

from mcp_apps_lab.data.weather import CITIES, get_weather_data
from mcp_apps_lab.tools.weather import get_weather

app = FastMCPApp("Weather")
app.add_tool(get_weather)


@app.ui()
def weather_app(city: str = "jakarta") -> PrefabApp:
    """Launch a weather dashboard.

    - city: lowercase city name to show first. Defaults to ``jakarta`` when
      not given. The user can type any location into the input — looked up
      directly (no geocoding); unknown names fall back to Jakarta.
    """
    city_rx = Rx("city")
    weather = Rx("weather")

    def lookup_actions() -> list:
        """Actions after a successful lookup: sync state + inform via toast."""
        return [
            SetState("city", RESULT.city),
            SetState("weather", RESULT),
            ShowToast(
                f"Menampilkan {RESULT.city}"
                f"{RESULT.is_fallback.then(' — lokasi tidak ditemukan, memakai Jakarta', '')}"
            ),
        ]

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
            Text("Lokasi:", css_class="text-sm font-medium text-muted-foreground")
            with Row(gap=2):
                location = Input(
                    placeholder="mis. jakarta, tokyo, paris...",
                    value=city.lower(),
                    name="location",
                )
                Button(
                    "Lihat",
                    variant="default",
                    on_click=CallTool(
                        get_weather,
                        arguments={"city": str(location.rx)},
                        on_success=lookup_actions(),
                        on_error=ShowToast(ERROR, variant="error"),
                    ),
                )

            Text("Cepat:", css_class="text-sm font-medium text-muted-foreground")
            with Row(gap=2, wrap=True):
                for city in CITIES:
                    Button(
                        city.title(),
                        variant="outline",
                        css_class="flex-1",
                        on_click=CallTool(
                            get_weather,
                            arguments={"city": city},
                            on_success=[*lookup_actions(), SetState("location", city)],
                            on_error=ShowToast(ERROR, variant="error"),
                        ),
                    )

    return PrefabApp(
        view=view,
        state={
            "city": city.lower(),
            "location": city.lower(),
            "weather": get_weather_data(city),
        },
    )
