"""mcp-apps-lab — one MCP server hosting three interactive Prefab apps.

Server layout:

- ``server.py``      — the single ``FastMCP`` server wiring everything together
- ``apps/``          — the ``FastMCPApp`` UIs (LLM-facing entry points)
- ``tools/``         — backend tool functions the UIs call via the tool proxy
- ``resources/``     — MCP resources over the shared data (``news://``, ``weather://``)
- ``prompts/``       — MCP prompt templates (``morning-briefing``)
- ``data/``          — shared static data behind tools, apps, and resources
"""

from mcp_apps_lab.server import mcp

__version__ = "0.2.0"

__all__ = ["__version__", "mcp"]
