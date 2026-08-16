"""mcp-apps-lab — one MCP server hosting four interactive Prefab apps.

Server layout:

- ``server.py``      — the single ``FastMCP`` server wiring everything together
- ``apps/``          — the ``FastMCPApp`` UIs (LLM-facing entry points)
- ``tools/``         — backend tool functions the UIs call via the tool proxy
- ``resources/``     — MCP resources over the shared data (``news://``, ``weather://``, ``duo://``)
- ``prompts/``       — MCP prompt templates (``morning-briefing``, ``daily-english``)
- ``data/``          — shared static data behind tools, apps, and resources
- ``duo/``           — the English Duo engine (word bank, FSRS scheduler, game mechanics)
- ``config.py``      — tool enable/disable config (``config.json``)
"""

from mcp_apps_lab.server import mcp

__version__ = "0.2.0"

__all__ = ["__version__", "mcp"]
