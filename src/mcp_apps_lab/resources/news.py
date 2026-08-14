"""News resources — ``news://{source}/feed`` and ``news://{source}/briefing``."""

from __future__ import annotations

import json

from fastmcp import FastMCP

from mcp_apps_lab.data.news import stories_by_source
from mcp_apps_lab.tools.news import compile_briefing


def register(mcp: FastMCP) -> None:
    """Register the news resources on the server."""

    @mcp.resource("news://{source}/feed")
    def news_feed(source: str) -> str:
        """Curated feed for a source as JSON.

        - source: bloomberg, reuters, guardian, or bbc
        """
        return json.dumps(stories_by_source(source), indent=2)

    @mcp.resource("news://{source}/briefing")
    def news_briefing(source: str) -> str:
        """Markdown briefing of a source's feed (same text as ``compile_briefing``)."""
        return compile_briefing(source)["briefing"]
