"""English Duo resources — ``duo://profile`` and ``duo://due``.

Read live from the SQLite store, so the assistant can check the learner's
streak/XP/due reviews before launching a lesson.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from mcp_apps_lab.duo import engine


def register(mcp: FastMCP) -> None:
    """Register the duo resources on the server."""

    @mcp.resource("duo://profile")
    def duo_profile() -> str:
        """English Duo learner profile: streak, XP, level, hearts, stats."""
        return json.dumps(engine.get_profile(), indent=2)

    @mcp.resource("duo://due")
    def duo_due() -> str:
        """Words due for review now, with definitions and levels."""
        from mcp_apps_lab.duo.store import Store

        return json.dumps(Store().due_words_detail(25), indent=2)
