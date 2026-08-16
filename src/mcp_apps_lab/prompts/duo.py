"""MCP prompt templates — ``daily-english``."""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all MCP prompts on the server."""

    @mcp.prompt("daily-english")
    def daily_english(level: str = "auto") -> str:
        """Run the user's daily English Duo practice session.

        - level: CEFR level for new words (a1/a2/b1/b2, or "auto").
        """
        return f"""You are the user's English coach, powered by the English Duo app.

1. Read duo://profile and duo://due to check the streak, XP, hearts, and
   how many words are due for review today.
2. Briefly cheer the user on (Duolingo style — short and playful), then
   launch the duo_english UI with level "{level}" so they can practice.
3. When the lesson result comes back to the conversation, celebrate the
   XP and streak, and suggest what to focus on next (due reviews, or
   asking you to add new words via the add_word tool).

Keep the message to 2-3 sentences before handing off to the UI."""
