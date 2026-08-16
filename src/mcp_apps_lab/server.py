"""The one mcp-apps-lab server.

A single ``FastMCP`` instance exposes:

- **Prefab UI apps** (via ``providers``): ``take_quiz``, ``weather_app``,
  ``news_curator``, and ``duo_english`` — the only tools advertised to the
  LLM. Which apps are enabled is controlled by ``config.json`` (see
  ``mcp_apps_lab.config``); disabled apps are not registered at all.
- **Backend tools** owned by each app (``tools/``) — called by the UIs over
  the tool proxy under hashed names; never listed to the LLM.
- **MCP resources** (``resources/``) — ``news://{source}/feed``,
  ``news://{source}/briefing``, ``weather://{city}/current``,
  ``duo://profile``, ``duo://due``, ``duo://words/{level}``,
  ``duo://guide/{level}``, ``duo://levels``.
- **MCP prompts** (``prompts/``) — ``morning-briefing``, ``daily-english``.

Run with:

    uv run python -m mcp_apps_lab            # streamable HTTP on :8090
    uv run fastmcp dev apps src/mcp_apps_lab/server.py --mcp-port 8090
"""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_apps_lab.apps import duo_app, news_app, quiz_app, weather_app
from mcp_apps_lab.config import enabled_tools
from mcp_apps_lab.prompts import register_prompts
from mcp_apps_lab.resources import register_resources

# UI tool name -> its FastMCPApp provider.
_APPS = {
    "take_quiz": quiz_app,
    "weather_app": weather_app,
    "news_curator": news_app,
    "duo_english": duo_app,
}


def build_server() -> FastMCP:
    """Construct the server with only the apps enabled in config.json."""
    enabled = enabled_tools()
    providers = [app for name, app in _APPS.items() if name in enabled]
    return FastMCP("mcp-apps-lab", providers=providers)


mcp = build_server()

register_resources(mcp)
register_prompts(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8090)
