"""Weather app — live forecast for any city, with a 5-day outlook.

The LLM calls ``weather_app(city)`` to launch the dashboard. The user can
type any location into the input — names are geocoded against the
Open-Meteo API (no more fixed-city table, so "bekasi" works) — or tap a
preset city button. Each lookup calls the ``get_weather`` backend tool
(from ``mcp_apps_lab.tools``) through the host's tools/call proxy (hashed
tool names — the proxy never sees the mapping). Unknown names fall back to
Jakarta; offline, sample data is shown and the LIVE/SAMPEL badge says so.
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
    If,
    Input,
    Muted,
    Row,
    Text,
)
from prefab_ui.rx import ERROR, RESULT, Rx

from mcp_apps_lab.data.weather import CITIES
from mcp_apps_lab.tools.weather import get_weather

app = FastMCPApp("Weather")
app.add_tool(get_weather)

FORECAST_DAYS = 5


@app.ui()
def weather_app(city: str = "jakarta") -> PrefabApp:
    """Launch a weather dashboard with a live 5-day forecast.

    - city: any city name (e.g. "bekasi", "singapore", "london") — geocoded
      against the Open-Meteo API. Defaults to ``jakarta`` when not given;
      unknown names fall back to Jakarta (the toast says so).
    """
    weather = Rx("weather")
    forecast = Rx("forecast")
    live = Rx("live")

    def lookup_actions() -> list:
        """Actions after a successful lookup: sync state + inform via toast."""
        return [
            SetState("city", RESULT.city),
            SetState("weather", RESULT),
            SetState("forecast", RESULT.forecast),
            SetState("live", RESULT.live),
            ShowToast(
                f"Menampilkan {RESULT.label}"
                f"{RESULT.is_fallback.then(' — lokasi tidak ditemukan, memakai Jakarta', '')}"
            ),
        ]

    def forecast_row(i: int) -> None:
        """Render forecast day slot ``i`` (hidden until data arrives)."""
        slot = forecast[i]
        with If(slot), Row(gap=3, align="center", css_class="w-full py-1"):
            Text(slot.day, css_class="w-24 text-sm font-medium")
            Text(f"{slot.emoji} {slot.condition}", css_class="flex-1 text-sm")
            Muted(f"{slot.temp_min}° / {slot.temp_max}°C")

    # The first city's forecast is fetched at launch (short timeout; sample
    # fallback if the network is unreachable).
    initial = get_weather(city)

    with Column(gap=6, css_class="p-6 max-w-md") as view:
        with Column(gap=1):
            Heading("Cuaca Sekarang")
            Muted("Prakiraan langsung dari Open-Meteo.")

        with Row(gap=2, align="center", wrap=True):
            Badge(f"{weather.label}", variant="secondary")
            Badge(f"{weather.temperature_c}°C", variant="outline")
            Badge(f"🕐 {weather.updated_local} {weather.tz_name}", variant="ghost")

        with Card(), Column(gap=2, css_class="p-4"):
            Text(
                f"{weather.emoji} {weather.condition}",
                css_class="text-lg font-semibold",
            )
            Muted(
                f"Terasa {weather.feels_like_c}°C · Kelembapan {weather.humidity}% · "
                f"Angin {weather.wind_kmh} km/h"
            )
            with If(weather.region):
                Muted(f"{weather.region} · {weather.country}")
            with If(~weather.region):
                Muted(f"{weather.country}")

        with Card(), Column(gap=2, css_class="p-4"):
            with Row(gap=2, align="center", css_class="w-full"):
                Text(
                    "Prakiraan 5 Hari",
                    css_class="text-sm font-semibold",
                )
                Badge(live.then("● LIVE", "○ SAMPEL"), variant="secondary")
            for i in range(FORECAST_DAYS):
                forecast_row(i)

        with Column(gap=2):
            Text("Lokasi:", css_class="text-sm font-medium text-muted-foreground")
            with Row(gap=2):
                location = Input(
                    placeholder="mis. bekasi, tokyo, paris...",
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
            "city": initial["city"],
            "location": initial["city"],
            "weather": initial,
            "forecast": initial["forecast"],
            "live": initial["live"],
        },
    )
