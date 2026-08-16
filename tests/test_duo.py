"""Tests for the English Duo engine: game mechanics, FSRS scheduling,
SQLite persistence, lesson building, and grading."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from mcp_apps_lab.data.english import WORD_BANK
from mcp_apps_lab.duo import engine, game
from mcp_apps_lab.duo.scheduler import review_card
from mcp_apps_lab.duo.store import Store, default_db_path, today_iso

# ---------------------------------------------------------------- game


def test_xp_combo_bonus_caps() -> None:
    assert game.xp_for(False, 5) == 0
    assert game.xp_for(True, 1) == 10  # base, no bonus yet
    assert game.xp_for(True, 2) == 12  # +2 combo bonus
    assert game.xp_for(True, 3) == 14
    assert game.xp_for(True, 10) == 20  # bonus capped at +10


def test_level_ladder_and_leagues() -> None:
    assert game.level_for(0) == (1, 0, 50)
    assert game.level_for(49) == (1, 49, 50)
    assert game.level_for(50) == (2, 0, 70)
    level, into, next_xp = game.level_for(2000)
    assert level == 10 and into == 0 and next_xp == 0  # max level
    assert game.league_for(1) == "Bronze"
    assert game.league_for(3) == "Silver"
    assert game.league_for(5) == "Gold"
    assert game.league_for(10) == "Diamond"


def test_hearts_never_below_zero() -> None:
    assert game.hearts_after_answer(5, True) == 5
    assert game.hearts_after_answer(5, False) == 4
    assert game.hearts_after_answer(1, False) == 0


# ------------------------------------------------------------ scheduler


def test_fsrs_schedules_future_due() -> None:
    _card_json, due, interval = review_card(None, correct=True)
    assert interval > 0
    due_dt = datetime.fromisoformat(due)
    assert due_dt > datetime.now(UTC)


def test_fsrs_wrong_answer_stays_short() -> None:
    _, due_wrong, _ = review_card(None, correct=False)
    _, due_right, _ = review_card(None, correct=True)
    assert datetime.fromisoformat(due_wrong) < datetime.fromisoformat(due_right)


# ---------------------------------------------------------------- store


@pytest.fixture
def store(tmp_path) -> Store:
    return Store(tmp_path / "duo.db")


def test_store_seeds_bank_and_profile(store: Store) -> None:
    profile = store.get_profile()
    assert profile["xp"] == 0
    assert profile["streak"] == 0
    assert profile["hearts"] == 5
    assert store.get_word("apple")["definition"].startswith("a round fruit")
    assert store.get_word("apple")["level"] == "a1"


def test_store_streak_increments_once_per_day(store: Store) -> None:
    day = "2026-01-01"
    assert store.complete_lesson(day) == 1
    assert store.complete_lesson(day) == 1  # same day: no double count
    assert store.complete_lesson("2026-01-02") == 2


def test_store_hearts_refill_on_new_day(store: Store) -> None:
    store.lose_heart()
    store.lose_heart()
    assert store.get_profile()["hearts"] == 3
    # hearts refill applies on the next calendar day
    with store._connect() as conn:
        store._set(conn, "hearts_date", "2099-12-31")
        store._set(conn, "hearts", "1")
    assert store.get_profile()["hearts"] == 5


def test_store_word_add_and_dedup(store: Store) -> None:
    assert store.add_word("Serendipity", "a happy accident") is True
    assert store.add_word("serendipity", "duplicate") is False
    assert store.get_word("serendipity")["definition"] == "a happy accident"


def test_default_db_path_uses_env(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("DUO_DB_PATH", str(tmp_path / "env.db"))
    assert default_db_path() == tmp_path / "env.db"


# ---------------------------------------------------------------- engine


def test_build_lesson_generates_valid_exercises(tmp_path) -> None:
    lesson = engine.build_lesson("auto", 6, tmp_path / "duo.db")
    assert len(lesson["items"]) == 6
    profile = lesson["profile"]
    assert profile["streak"] == 0 and profile["hearts"] == 5
    for _i, item in enumerate(lesson["items"]):
        assert len(item["options"]) == 4
        assert len(set(item["options"])) == 4  # no duplicate options
        assert item["correct"] in range(4)
        assert item["type"] in ("mc", "fill")
        assert any(w["word"] == item["word"] for w in WORD_BANK)  # seeded
        if item["type"] == "fill":
            assert "____" in item["prompt"]
        else:
            assert item["word"] in item["prompt"]


def test_grade_answer_correct_updates_xp_and_schedule(tmp_path) -> None:
    db = tmp_path / "duo.db"
    item = engine.build_lesson("a1", 3, db)["items"][0]
    result = engine.grade_answer(
        item["word"], item["correct"], item["correct"], combo=0, finished=True, db_path=db
    )
    assert result["is_correct"] is True
    assert result["xp_gain"] == 10
    assert result["xp_total"] == 10
    assert result["combo"] == 1
    assert result["hearts"] == 5
    assert result["streak"] == 1
    assert result["finished"] is True
    assert result["game_over"] is False
    # the word's card is now scheduled into the future
    card = Store(db).get_card(item["word"])
    assert card is not None
    assert datetime.fromisoformat(card["due"]) > datetime.now(UTC)


def test_grade_answer_wrong_loses_heart(tmp_path) -> None:
    db = tmp_path / "duo.db"
    item = engine.build_lesson("a1", 3, db)["items"][0]
    wrong = (item["correct"] + 1) % 4
    result = engine.grade_answer(
        item["word"], wrong, item["correct"], combo=2, finished=True, db_path=db
    )
    assert result["is_correct"] is False
    assert result["xp_gain"] == 0
    assert result["combo"] == 0
    assert result["hearts"] == 4
    # a completed lesson counts toward the streak even with mistakes
    assert result["streak"] == 1


def test_game_over_when_hearts_depleted(tmp_path) -> None:
    db = tmp_path / "duo.db"
    store = Store(db)
    with store._connect() as conn:
        store._set(conn, "hearts_date", today_iso())  # today's refill already used
        store._set(conn, "hearts", "1")
    item = engine.build_lesson("a1", 3, db)["items"][0]
    wrong = (item["correct"] + 1) % 4
    result = engine.grade_answer(item["word"], wrong, item["correct"], finished=False, db_path=db)
    assert result["game_over"] is True
    assert result["finished"] is True
    assert result["hearts"] == 0
    # out of hearts -> the lesson does NOT count toward the streak
    assert result["streak"] == 0


def test_lesson_driven_by_due_reviews(tmp_path) -> None:
    db = tmp_path / "duo.db"
    first = engine.build_lesson("a1", 6, db)["items"][0]
    engine.grade_answer(
        first["word"], first["correct"], first["correct"], finished=True, db_path=db
    )
    second = engine.build_lesson("auto", 6, db)
    # the just-reviewed word is no longer due -> not in the new lesson
    assert first["word"] not in [i["word"] for i in second["items"]]


def test_add_word_then_appears_in_lesson(tmp_path) -> None:
    db = tmp_path / "duo.db"
    result = engine.add_word(
        "grok", "to understand something deeply", "I grok this now.", "verb", "b2", db
    )
    assert result["added"] is True
    first = engine.build_lesson("b2", 10, db)["items"]
    assert first
    # work through the seeded b2 words until the new word is introduced
    for _ in range(3):
        for item in first:
            engine.grade_answer(
                item["word"], item["correct"], item["correct"], finished=True, db_path=db
            )
        first = engine.build_lesson("b2", 10, db)["items"]
        if any(i["word"] == "grok" for i in first):
            break
    assert any(i["word"] == "grok" for i in first)


def test_profile_json_round_trip(tmp_path) -> None:
    db = tmp_path / "duo.db"
    profile = engine.get_profile(db)
    assert json.loads(json.dumps(profile)) == profile
