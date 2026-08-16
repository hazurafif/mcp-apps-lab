"""English Duo resources.

- ``duo://profile``          — streak, XP, level, hearts, stats
- ``duo://due``              — words due for review now
- ``duo://words/{level}``    — every word in the bank at a CEFR level
  (seed + user/AI-added), so the AI can match style and avoid duplicates
  before generating fresh vocabulary
- ``duo://guide/{level}``    — the generation guide (the "prompt") for
  creating level-appropriate vocabulary: learner profile, word scope,
  definition/example rules, and the exact output format
- ``duo://levels``           — overview of the CEFR levels + word counts

All read live from the SQLite store / word bank.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from mcp_apps_lab.data.english import GENERATION_GUIDES, LEVELS
from mcp_apps_lab.duo import engine
from mcp_apps_lab.duo.store import Store


def register(mcp: FastMCP) -> None:
    """Register the duo resources on the server."""

    @mcp.resource("duo://profile")
    def duo_profile() -> str:
        """English Duo learner profile: streak, XP, level, hearts, stats."""
        return json.dumps(engine.get_profile(), indent=2)

    @mcp.resource("duo://due")
    def duo_due() -> str:
        """Words due for review now, with definitions and levels."""
        return json.dumps(Store().due_words_detail(25), indent=2)

    @mcp.resource("duo://words/{level}")
    def duo_words(level: str) -> str:
        """All words in the bank at a CEFR level (for AI generation reference)."""
        level = level.lower()
        if level not in LEVELS:
            return json.dumps(
                {"error": f"unknown level {level!r}", "levels": list(LEVELS)}, indent=2
            )
        words = Store().words_at_level(level)
        return json.dumps({"level": level, "count": len(words), "words": words}, indent=2)

    @mcp.resource("duo://guide/{level}")
    def duo_guide(level: str) -> str:
        """Generation guide for a CEFR level — how to write words/definitions/examples."""
        level = level.lower()
        if level not in LEVELS:
            return f"Unknown level {level!r}. Available: {', '.join(LEVELS)}."
        return GENERATION_GUIDES[level]

    @mcp.resource("duo://levels")
    def duo_levels() -> str:
        """Overview of the CEFR levels and how many words each holds."""
        overview = [
            {
                "level": lvl,
                "words": len(Store().words_at_level(lvl)),
                "guide": f"duo://guide/{lvl}",
            }
            for lvl in LEVELS
        ]
        return json.dumps({"levels": overview}, indent=2)
