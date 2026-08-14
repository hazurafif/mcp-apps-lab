"""Run the mcp-apps-lab server: ``uv run python -m mcp_apps_lab``."""

from __future__ import annotations

import os

from mcp_apps_lab.server import mcp

DEFAULT_PORT = int(os.environ.get("MCP_APPS_LAB_PORT", "8090"))


def main() -> None:
    """Run the streamable-HTTP MCP server (port 8090 by default)."""
    mcp.run(transport="http", host="127.0.0.1", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
