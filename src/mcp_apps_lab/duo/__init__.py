"""English Duo engine — Duolingo-style English learning.

A word bank graded by CEFR level (A1-B2), FSRS-6 spaced-repetition cards,
and Duolingo-style game mechanics (XP + combo, hearts, daily streak, level
ladder) persisted in a local SQLite database.

Public surface (see ``mcp_apps_lab.tools.duo`` for the MCP tools):
- ``build_lesson`` — due reviews + new words as interactive exercises
- ``grade_answer`` — grade, reschedule the card, apply game mechanics
- ``get_profile``  — streak/XP/level/hearts/stats
- ``add_word``     — add a word to the bank from the chat
"""

from mcp_apps_lab.duo.engine import add_word, build_lesson, get_profile, grade_answer

__all__ = ["add_word", "build_lesson", "get_profile", "grade_answer"]
