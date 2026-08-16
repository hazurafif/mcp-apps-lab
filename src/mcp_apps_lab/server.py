"""The one mcp-apps-lab server.

A single ``FastMCP`` instance exposes:

- **Four Prefab UI apps** (via ``providers``): ``take_quiz``, ``weather_app``,
  ``news_curator``, and ``duo_english`` — the only tools advertised to the LLM.
- **Backend tools** owned by each app (``tools/``) — called by the UIs over
  the tool proxy under hashed names; never listed to the LLM.
- **MCP resources** (``resources/``) — ``news://{source}/feed``,
  ``news://{source}/briefing``, ``weather://{city}/current``,
  ``duo://profile``, ``duo://due``.
- **MCP prompts** (``prompts/``) — ``morning-briefing``, ``daily-english``.

Run with:

    uv run python -m mcp_apps_lab            # streamable HTTP on :8090
    uv run fastmcp dev apps src/mcp_apps_lab/server.py --mcp-port 8090
"""

from __future__ import annotations

from fastmcp import FastMCP

from mcp_apps_lab.apps import duo_app, news_app, quiz_app, weather_app
from mcp_apps_lab.prompts import register_prompts
from mcp_apps_lab.resources import register_resources

mcp = FastMCP("mcp-apps-lab", providers=[quiz_app, weather_app, news_app, duo_app])

register_resources(mcp)
register_prompts(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8090)
