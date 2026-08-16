"""MCP prompt templates exposed by the server."""

from __future__ import annotations

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts on the server."""
    from mcp_apps_lab.prompts import briefing, duo

    briefing.register(mcp)
    duo.register(mcp)


__all__ = ["register_prompts"]
