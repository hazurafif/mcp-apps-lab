"""MCP resources exposed by the server — ``news://``, ``weather://``, ``duo://``."""

from __future__ import annotations

from fastmcp import FastMCP


def register_resources(mcp: FastMCP) -> None:
    """Register all MCP resources on the server."""
    from mcp_apps_lab.resources import duo, news, weather

    duo.register(mcp)
    news.register(mcp)
    weather.register(mcp)


__all__ = ["register_resources"]
