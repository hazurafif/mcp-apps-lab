"""News resources — ``news://{source}/feed`` and ``news://{source}/briefing``.

Both fetch the live RSS feed on read (sample fallback offline).
"""

from __future__ import annotations

import asyncio
import json

from fastmcp import FastMCP

from mcp_apps_lab.tools.news import get_feed


def register(mcp: FastMCP) -> None:
    """Register the news resources on the server."""

    @mcp.resource("news://{source}/feed")
    async def news_feed(source: str) -> str:
        """Latest stories for a source feed as JSON (live RSS, sample fallback).

        - source: bloomberg, cnbc, guardian, or bbc
        """
        data = await asyncio.to_thread(get_feed, source, "Financial News", 10)
        return json.dumps(data["stories"], indent=2)

    @mcp.resource("news://{source}/briefing")
    async def news_briefing(source: str) -> str:
        """Markdown briefing of a source's latest stories (live RSS)."""
        data = await asyncio.to_thread(get_feed, source, "Daily Briefing", 6)
        return data["briefing"]
