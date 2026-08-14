"""MCP prompt templates — ``morning-briefing``."""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all MCP prompts on the server."""

    @mcp.prompt("morning-briefing")
    def morning_briefing(topic: str = "Global Markets") -> str:
        """Walk the user through today's news for a topic.

        - topic: e.g. "Global Markets", "AI & Tech", "Energy"
        """
        return f"""You are the user's morning news briefing assistant. Topic: {topic}.

1. Read the live feeds as resources — news://bloomberg/feed, news://cnbc/feed,
   news://guardian/feed, news://bbc/feed — and summarize the top stories.
2. Highlight the market movers and any shifts across sources.
3. Launch the news_curator UI with topic "{topic}" so the user can browse
   the live feeds and send a compiled briefing back to the chat.

Keep the summary tight: 3-5 bullets, then hand off to the UI."""
