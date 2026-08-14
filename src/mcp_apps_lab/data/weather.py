"""Weather data — WMO code map and offline fallback data.

Live data comes from the Open-Meteo API (``mcp_apps_lab.tools.weather``);
``FALLBACK_WEATHER`` is only used when the API can't be reached.
"""

from __future__ import annotations

# Quick-pick preset cities shown as buttons in the dashboard.
CITIES = ["jakarta", "bekasi", "tokyo", "paris", "berlin"]

# WMO weather code → (Indonesian label, emoji)
WEATHER_CODES: dict[int, tuple[str, str]] = {
    0: ("Cerah", "☀️"),
    1: ("Cerah Berawan", "🌤️"),
    2: ("Berawan Sebagian", "⛅"),
    3: ("Mendung", "☁️"),
    45: ("Berkabut", "🌫️"),
    48: ("Kabut Membeku", "🌫️"),
    51: ("Gerimis Ringan", "🌦️"),
    53: ("Gerimis", "🌦️"),
    55: ("Gerimis Lebat", "🌧️"),
    56: ("Gerimis Membeku", "🌧️"),
    57: ("Gerimis Membeku Lebat", "🌧️"),
    61: ("Hujan Ringan", "🌧️"),
    63: ("Hujan", "🌧️"),
    65: ("Hujan Lebat", "🌧️"),
    66: ("Hujan Membeku", "🌧️"),
    67: ("Hujan Membeku Lebat", "🌧️"),
    71: ("Salju Ringan", "🌨️"),
    73: ("Salju", "🌨️"),
    75: ("Salju Lebat", "❄️"),
    77: ("Butiran Salju", "🌨️"),
    80: ("Hujan Ringan", "🌦️"),
    81: ("Hujan", "🌧️"),
    82: ("Hujan Lebat", "⛈️"),
    85: ("Salju Ringan", "🌨️"),
    86: ("Salju Lebat", "❄️"),
    95: ("Badai Petir", "⛈️"),
    96: ("Badai Petir & Hujan Es", "⛈️"),
    99: ("Badai Petir & Hujan Es", "⛈️"),
}

# Indonesian day names for the forecast rows.
DAY_NAMES = [
    "Senin",
    "Selasa",
    "Rabu",
    "Kamis",
    "Jumat",
    "Sabtu",
    "Minggu",
]


def _fallback_forecast() -> list[dict]:
    """A short sample 5-day forecast for offline fallback (marked SAMPEL)."""
    return [
        {"day": "Hari Ini", "temp_min": 24, "temp_max": 32, "condition": "Cerah Berawan", "emoji": "🌤️"},
        {"day": "Besok", "temp_min": 24, "temp_max": 31, "condition": "Hujan Ringan", "emoji": "🌧️"},
        {"day": "Lusa", "temp_min": 24, "temp_max": 31, "condition": "Berawan Sebagian", "emoji": "⛅"},
        {"day": "3 Hari Lagi", "temp_min": 24, "temp_max": 32, "condition": "Cerah", "emoji": "☀️"},
        {"day": "4 Hari Lagi", "temp_min": 25, "temp_max": 32, "condition": "Hujan", "emoji": "🌧️"},
    ]


# Offline fallback data — shown when the API is unreachable.
FALLBACK_WEATHER: dict[str, dict] = {
    "jakarta": {
        "label": "Jakarta",
        "region": "DKI Jakarta",
        "country": "Indonesia",
        "temperature_c": 29,
        "feels_like_c": 33,
        "humidity": 72,
        "wind_kmh": 10,
        "condition": "Berawan Sebagian",
        "emoji": "⛅",
        "timezone": "Asia/Jakarta",
        "forecast": _fallback_forecast(),
    },
    "bekasi": {
        "label": "Bekasi",
        "region": "Jawa Barat",
        "country": "Indonesia",
        "temperature_c": 29,
        "feels_like_c": 33,
        "humidity": 74,
        "wind_kmh": 8,
        "condition": "Berawan Sebagian",
        "emoji": "⛅",
        "timezone": "Asia/Jakarta",
        "forecast": _fallback_forecast(),
    },
    "tokyo": {
        "label": "Tokyo",
        "region": "Tokyo",
        "country": "Jepang",
        "temperature_c": 21,
        "feels_like_c": 21,
        "humidity": 65,
        "wind_kmh": 14,
        "condition": "Cerah",
        "emoji": "☀️",
        "timezone": "Asia/Tokyo",
        "forecast": _fallback_forecast(),
    },
    "paris": {
        "label": "Paris",
        "region": "Île-de-France",
        "country": "Prancis",
        "temperature_c": 18,
        "feels_like_c": 17,
        "humidity": 62,
        "wind_kmh": 12,
        "condition": "Berawan Sebagian",
        "emoji": "⛅",
        "timezone": "Europe/Paris",
        "forecast": _fallback_forecast(),
    },
    "berlin": {
        "label": "Berlin",
        "region": "Berlin",
        "country": "Jerman",
        "temperature_c": 14,
        "feels_like_c": 13,
        "humidity": 58,
        "wind_kmh": 16,
        "condition": "Mendung",
        "emoji": "☁️",
        "timezone": "Europe/Berlin",
        "forecast": _fallback_forecast(),
    },
}


def get_weather_data(city: str) -> dict:
    """Offline fallback lookup; unknown cities fall back to jakarta."""
    return FALLBACK_WEATHER.get(city.lower(), FALLBACK_WEATHER["jakarta"])
