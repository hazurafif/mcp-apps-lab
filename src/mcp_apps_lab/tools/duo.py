"""English Duo backend tools — called by the duo UI over the tool proxy.

These are registered on the FastMCPApp (hashed names, never listed to the
LLM); the UI calls them to grade exercises, fetch the profile, and let the
LLM add words to the bank. State lives in the SQLite store.
"""

from __future__ import annotations

from mcp_apps_lab.duo import engine


def grade_answer(
    word: str,
    exercise_type: str = "mc",
    selected: object | None = None,
    correct: object | None = None,
    rating: int | None = None,
    combo: int = 0,
    lesson_xp: int = 0,
    lesson_correct: int = 0,
    finished: bool = False,
) -> dict:
    """Grade an English Duo exercise.

    Args:
        word: the word being practiced.
        exercise_type: "mc" / "fill" (option indexes), "type" (typed
            text vs the word), "order" (built sentence vs the target
            words), or "flip" (self-rating, see below).
        selected: the user's answer — option index, typed text, or the
            built sentence.
        correct: the right answer — option index, the word, or the
            target words list.
        rating: for "flip" — 1=Again, 2=Hard, 3=Good, 4=Easy.
        combo: consecutive correct answers so far this lesson.
        lesson_xp: XP earned so far this lesson.
        lesson_correct: correct answers so far this lesson.
        finished: whether this was the last exercise of the lesson.

    Returns the updated state: correctness, XP (+total), combo, hearts,
    level/league, streak, lesson totals, and completion flags.
    """
    return engine.grade_answer(
        word, exercise_type, selected, correct, rating, combo, lesson_xp, lesson_correct, finished
    )


def get_profile() -> dict:
    """The learner profile: streak, XP, level/league, hearts, word stats."""
    return engine.get_profile()


def add_word(
    word: str, definition: str, example: str = "", pos: str = "", level: str = "b1"
) -> dict:
    """Add a new word to the English Duo word bank.

    Args:
        word: the word (lowercased automatically).
        definition: a simple English definition.
        example: an example sentence using the word.
        pos: part of speech (noun, verb, adjective, ...).
        level: CEFR level (a1, a2, b1, b2).

    Returns {"added": bool, "word": ...} — False if it already exists.
    """
    return engine.add_word(word, definition, example, pos, level)
