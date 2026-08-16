"""The four FastMCPApp UIs, each owning its backend tools.

Each app module creates a ``FastMCPApp``, registers its backend tools from
``mcp_apps_lab.tools`` (which hashes them to this app), and defines the
LLM-facing ``@app.ui()`` entry point. ``server.py`` exposes all four apps
on the single MCP server via ``providers=[...]``.
"""

from mcp_apps_lab.apps.duo import app as duo_app
from mcp_apps_lab.apps.news import app as news_app
from mcp_apps_lab.apps.quiz import app as quiz_app
from mcp_apps_lab.apps.weather import app as weather_app

__all__ = ["duo_app", "news_app", "quiz_app", "weather_app"]
