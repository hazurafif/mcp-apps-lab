"""English Duo engine — lesson building and grading.

Five exercise types, like a real language app:

- ``mc``    — "What does X mean?" — pick the right definition
- ``fill``  — sentence with a blank — pick the word that fits
- ``type``  — sentence with a blank + definition hint — TYPE the word
- ``order`` — build the sentence by tapping scrambled word tiles
- ``flip``  — flashcard: flip the card, then self-rate Again/Hard/Good/Easy
             (maps straight onto the FSRS ratings, so reviews get a real
             difficulty signal instead of just right/wrong)

``build_lesson`` picks due FSRS cards + new words and cycles the types;
``grade_answer`` grades any type, updates the FSRS card, and applies the
game mechanics (XP/combo/hearts/streak/level).
"""

from __future__ import annotations

import random
import re
from pathlib import Path

from fsrs import Card

from mcp_apps_lab.data.english import LEVELS, words_by_level
from mcp_apps_lab.duo import game
from mcp_apps_lab.duo.scheduler import review_card
from mcp_apps_lab.duo.store import Store

BLANK = "____"
DISTRACTORS = 3
OPTIONS = DISTRACTORS + 1

# Exercise types cycle through a lesson (index % len).
EXERCISE_TYPES = ("mc", "fill", "type", "order", "flip")

# Flip-card self-ratings: FSRS rating -> XP base (0 for Again).
FLIP_XP = {1: 0, 2: 8, 3: 10, 4: 12}


def _normalize(text: object) -> str:
    """Lowercase + strip leading/trailing punctuation for answer matching."""
    return re.sub(r"^[\W_]+|[\W_]+$", "", str(text).strip().lower())


def _norm_words(words: list[str]) -> list[str]:
    return [_normalize(w) for w in words]


def _blank_example(entry: dict) -> str:
    return entry["example"].replace(entry["word"], BLANK, 1)


def _example_words(entry: dict) -> list[str]:
    """The example sentence split into words (punctuation stripped)."""
    words = re.findall(r"[\w'-]+", entry["example"])
    return [w for w in words if w.lower() != entry["word"].lower()]


def _distractor_pool(level: str) -> list[dict]:
    """Word-bank entries at a level, plus a spill-over from all levels."""
    pool = words_by_level(level)
    if len(pool) < OPTIONS * 2:
        pool = pool + [w for w in words_by_level("a2") if w not in pool]
    return pool


def _build_mc(entry: dict) -> dict:
    """What does X mean? — pick the right definition."""
    rng = random.Random(entry["word"])
    distractors = [
        w["definition"]
        for w in _distractor_pool(entry["level"])
        if w["word"] != entry["word"] and w["definition"] != entry["definition"]
    ]
    options = list(dict.fromkeys([entry["definition"], *distractors]))[:OPTIONS]
    rng.shuffle(options)
    return {
        "type": "mc",
        "prompt": f"What does “{entry['word']}” mean?",
        "options": options,
        "correct": options.index(entry["definition"]),
    }


def _build_fill(entry: dict) -> dict:
    """Sentence with a blank — pick the word that fits."""
    rng = random.Random(f"{entry['word']}#fill")
    same_pos = [
        w["word"]
        for w in _distractor_pool(entry["level"])
        if w["word"] != entry["word"] and w["pos"] == entry["pos"]
    ]
    others = [
        w["word"]
        for w in _distractor_pool(entry["level"])
        if w["word"] != entry["word"] and w["pos"] != entry["pos"]
    ]
    candidates = list(dict.fromkeys([*same_pos, *others]))[:DISTRACTORS]
    options = list(dict.fromkeys([entry["word"], *candidates]))
    rng.shuffle(options)
    return {
        "type": "fill",
        "prompt": _blank_example(entry),
        "options": options,
        "correct": options.index(entry["word"]),
    }


def _build_type(entry: dict) -> dict:
    """Type the missing word — no choices at all."""
    return {
        "type": "type",
        "prompt": _blank_example(entry),
        "hint": f"Definition: {entry['definition']}",
        "correct": entry["word"],
    }


def _build_order(entry: dict) -> dict:
    """Build the sentence by tapping scrambled word tiles."""
    rng = random.Random(f"{entry['word']}#order")
    words = _example_words(entry)
    tiles = words[:]
    rng.shuffle(tiles)
    return {
        "type": "order",
        "prompt": f"Build the sentence: {entry['definition']}",
        "tiles": tiles,
        "target": words,
    }


def _build_flip(entry: dict) -> dict:
    """Flashcard: flip, then self-rate Again/Hard/Good/Easy."""
    return {
        "type": "flip",
        "prompt": entry["word"],
        "definition": entry["definition"],
        "example": entry["example"],
    }


_BUILDERS = {
    "mc": _build_mc,
    "fill": _build_fill,
    "type": _build_type,
    "order": _build_order,
    "flip": _build_flip,
}


def _build_item(entry: dict, index: int) -> dict:
    exercise = _BUILDERS[EXERCISE_TYPES[index % len(EXERCISE_TYPES)]](entry)
    base = {
        "word": entry["word"],
        "pos": entry["pos"],
        "level": entry["level"],
        "definition": entry["definition"],
        "example": entry["example"],
    }
    return {**base, **exercise}


def build_lesson(level: str = "auto", items: int = 6, db_path: Path | str | None = None) -> dict:
    """Build a lesson: due reviews first, then new words at the level.

    Returns ``{"items": [...], "profile": {...}}`` for the UI. Exercise
    types cycle mc -> fill -> type -> order -> flip.
    """
    store = Store(db_path)
    items = max(3, min(int(items), 10))
    level = (level or "auto").lower()
    if level not in LEVELS:
        level = store.level_with_most_due() if store.due_words(1) else store.earliest_unseen_level()

    picked = store.due_words(items)
    if len(picked) < items:
        picked += store.unseen_words(level, items - len(picked))

    entries = [store.get_word(w) for w in picked]
    items_out = [_build_item(e, i) for i, e in enumerate(entries) if e]
    return {"items": items_out, "profile": store.get_profile()}


# ---------------------------------------------------------------- grading


def _check_answer(exercise_type: str, selected: object, correct: object) -> bool:
    """Grade a non-flip exercise by type."""
    if exercise_type == "type":
        return _normalize(selected) == _normalize(correct)
    if exercise_type == "order":
        sel = _norm_words(str(selected).split())
        cor = _norm_words(correct if isinstance(correct, list) else str(correct).split())
        return sel == cor
    # mc / fill: index match
    try:
        return int(selected) == int(correct)
    except (TypeError, ValueError):
        return False


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
    db_path: Path | str | None = None,
) -> dict:
    """Grade one exercise and apply FSRS + game mechanics.

    - ``mc``/``fill``: ``selected``/``correct`` are option indexes.
    - ``type``: ``selected`` is the typed text, ``correct`` the word.
    - ``order``: ``selected`` is the built sentence, ``correct`` the words.
    - ``flip``: ``rating`` (1-4 = Again/Hard/Good/Easy) replaces
      ``selected``/``correct``; Again is a mistake (loses a heart),
      Hard/Good/Easy are remembered with 8/10/12 XP base.

    Returns everything the UI needs to update its state (see apps/duo.py).
    """
    store = Store(db_path)
    entry = store.get_word(word)

    if exercise_type == "flip":
        fsrs_rating = int(rating or 3)
        is_correct = fsrs_rating >= 2  # Hard/Good/Easy = remembered
        xp_base = FLIP_XP.get(fsrs_rating, 10)
    else:
        is_correct = _check_answer(exercise_type, selected, correct)
        fsrs_rating = 3 if is_correct else 1
        xp_base = game.BASE_XP

    if is_correct:
        combo = combo + 1
        xp_gain = game.xp_for(True, combo, base=xp_base)
        store.add_xp(xp_gain)
        hearts = int(store.get_profile()["hearts"])
    else:
        combo = 0
        xp_gain = 0
        hearts = store.lose_heart()

    # FSRS: grade the word's card (Again on a mistake, the chosen rating on
    # a flip-card, Good otherwise).
    card = store.get_card(word)
    card_json, due, interval = review_card(
        card["card_json"] if card else None,
        is_correct,
        rating=fsrs_rating if exercise_type == "flip" else None,
    )
    state = Card.from_json(card_json).state.name
    reps = (card["reps"] if card else 0) + 1
    lapses = (card["lapses"] if card else 0) + (0 if is_correct else 1)
    store.save_review(word, card_json, due, state, reps, lapses, fsrs_rating, interval)

    game_over = hearts <= 0
    done = finished or game_over
    lesson_xp = lesson_xp + xp_gain
    lesson_correct = lesson_correct + (1 if is_correct else 0)
    if done and not game_over:
        store.complete_lesson()

    profile = store.get_profile()
    return {
        "is_correct": is_correct,
        "xp_gain": xp_gain,
        "xp_total": profile["xp"],
        "combo": combo,
        "hearts": hearts,
        "level": profile["level"],
        "league": profile["league"],
        "level_xp": profile["level_xp"],
        "next_xp": profile["next_xp"],
        "streak": profile["streak"],
        "lesson_xp": lesson_xp,
        "lesson_correct": lesson_correct,
        "finished": done,
        "game_over": game_over,
        "words_learned": profile["words_learned"],
        "due_count": profile["due_count"],
        "word": word,
        "definition": entry["definition"] if entry else "",
    }


def get_profile(db_path: Path | str | None = None) -> dict:
    """Current learner profile (streak, XP, level, hearts, stats)."""
    return Store(db_path).get_profile()


def add_word(
    word: str,
    definition: str,
    example: str = "",
    pos: str = "",
    level: str = "b1",
    db_path: Path | str | None = None,
) -> dict:
    """Add a learner word to the bank; returns whether it was inserted."""
    added = Store(db_path).add_word(word, definition, example, pos, level)
    return {"added": added, "word": word.strip().lower()}
