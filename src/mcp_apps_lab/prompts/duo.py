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
3. Make the content AI-generated: generate fresh, CEFR-appropriate
   vocabulary YOURSELF (personalized to the user's level and interests)
   and pass it via the `words` argument — each entry: {{"word",
   "definition" (simple English), "example" (sentence using the word),
   "pos", "level"}}. Before generating, read the reference resources:
   duo://guide/{level} (the generation prompt for that level) and
   duo://words/{level} (existing words — match their style, never
   duplicate them). Only fall back to the built-in bank when the user
   just wants their due reviews.
4. If the user asks for flashcards / a review deck specifically, launch
   duo_flashcards instead — a pure flip-card session (Again / Hard /
   Good / Easy), also with AI-generated `words` where fitting.
5. When the session result comes back to the conversation, celebrate the
   XP and streak, and suggest what to focus on next.

Keep the message to 2-3 sentences before handing off to the UI."""
