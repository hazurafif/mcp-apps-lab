"""MCP resources exposed by the server — ``news://`` and ``weather://``."""

from __future__ import annotations

from fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources on the server."""
    from mcp_apps_lab.resources import news, weather

    news.register(mcp)
    weather.register(mcp)


__all__ = ["register_resources"]
