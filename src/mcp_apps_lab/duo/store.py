"""SQLite persistence for English Duo.

One small database (default ``~/.mcp-apps-lab/duo.db``, override with
``DUO_DB_PATH``) holds:

- ``profile`` — key/value user state (XP, streak, hearts, dates)
- ``words``   — the word bank (seed content + words the LLM adds)
- ``cards``   — one FSRS card per word (JSON state + due timestamp)
- ``reviews`` — the review history (for future FSRS optimization)

All methods open a short-lived connection, so the store is safe to call
from threads (FastMCP runs tools in a thread pool).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from mcp_apps_lab.data.english import WORD_BANK
from mcp_apps_lab.duo import game
from mcp_apps_lab.duo.scheduler import due_iso

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS words (
    word       TEXT PRIMARY KEY,
    pos        TEXT NOT NULL DEFAULT '',
    definition TEXT NOT NULL,
    example    TEXT NOT NULL DEFAULT '',
    level      TEXT NOT NULL DEFAULT 'b1',
    source     TEXT NOT NULL DEFAULT 'seed'
);
CREATE TABLE IF NOT EXISTS cards (
    word        TEXT PRIMARY KEY,
    card_json   TEXT NOT NULL,
    due         TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'Learning',
    reps        INTEGER NOT NULL DEFAULT 0,
    lapses      INTEGER NOT NULL DEFAULT 0,
    last_review TEXT,
    created     TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    word         TEXT NOT NULL,
    rating       INTEGER NOT NULL,
    reviewed_at  TEXT NOT NULL,
    interval_days REAL NOT NULL DEFAULT 0
);
"""


def default_db_path() -> Path:
    """Database location: ``DUO_DB_PATH`` env var or ``~/.mcp-apps-lab/duo.db``."""
    override = os.environ.get("DUO_DB_PATH")
    if override:
        return Path(override)
    return Path.home() / ".mcp-apps-lab" / "duo.db"


def today_iso() -> str:
    """UTC date as ISO string (the day boundary for streaks/hearts)."""
    return datetime.now(UTC).date().isoformat()


class Store:
    """SQLite-backed state for one learner profile."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            self._seed_words(conn)
            self._ensure_profile(conn)

    # ---------------------------------------------------------- plumbing

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _seed_words(self, conn: sqlite3.Connection) -> None:
        conn.executemany(
            "INSERT OR IGNORE INTO words (word, pos, definition, example, level, source)"
            " VALUES (:word, :pos, :definition, :example, :level, 'seed')",
            WORD_BANK,
        )

    def _ensure_profile(self, conn: sqlite3.Connection) -> None:
        defaults = {"xp": "0", "streak": "0", "hearts": str(game.MAX_HEARTS)}
        conn.executemany(
            "INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)",
            [(k, v) for k, v in defaults.items()],
        )

    def _get(self, conn: sqlite3.Connection, key: str, default: str = "0") -> str:
        row = conn.execute("SELECT value FROM profile WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def _set(self, conn: sqlite3.Connection, key: str, value: str) -> None:
        conn.execute(
            "INSERT INTO profile (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    # ---------------------------------------------------------- profile

    def get_profile(self) -> dict:
        """Full learner profile: XP/level/league, streak, hearts, stats."""
        with self._connect() as conn:
            self._refill_hearts(conn)
            xp = int(self._get(conn, "xp"))
            streak = int(self._get(conn, "streak"))
            hearts = int(self._get(conn, "hearts"))
            level, into, next_xp = game.level_for(xp)
            words_learned = conn.execute(
                "SELECT COUNT(*) FROM cards WHERE state = 'Review'"
            ).fetchone()[0]
            due_count = conn.execute(
                "SELECT COUNT(*) FROM cards WHERE due <= ?", (due_iso(),)
            ).fetchone()[0]
        return {
            "xp": xp,
            "level": level,
            "league": game.league_for(level),
            "level_xp": into,
            "next_xp": next_xp,
            "streak": streak,
            "hearts": hearts,
            "max_hearts": game.MAX_HEARTS,
            "words_learned": words_learned,
            "due_count": due_count,
        }

    def add_xp(self, amount: int) -> None:
        """Add XP to the profile (clamped at 0)."""
        if amount <= 0:
            return
        with self._connect() as conn:
            xp = int(self._get(conn, "xp")) + amount
            self._set(conn, "xp", str(xp))

    def _refill_hearts(self, conn: sqlite3.Connection) -> None:
        """Refill hearts to max once per day (Duolingo's daily refill)."""
        last = self._get(conn, "hearts_date", default="")
        if last != today_iso():
            self._set(conn, "hearts", str(game.MAX_HEARTS))
            self._set(conn, "hearts_date", today_iso())

    def lose_heart(self) -> int:
        """Lose one heart; returns hearts remaining (daily refill applies)."""
        with self._connect() as conn:
            self._refill_hearts(conn)
            hearts = max(0, int(self._get(conn, "hearts")) - 1)
            self._set(conn, "hearts", str(hearts))
            return hearts

    def complete_lesson(self, on_day: str | None = None) -> int:
        """Mark a lesson done today; bumps the streak once per day.

        Returns the new streak.
        """
        day = on_day or today_iso()
        with self._connect() as conn:
            last = self._get(conn, "last_completed", default="")
            streak = int(self._get(conn, "streak"))
            if last != day:
                streak += 1
                self._set(conn, "streak", str(streak))
                self._set(conn, "last_completed", day)
            return streak

    # ---------------------------------------------------------- words & cards

    def get_word(self, word: str) -> dict | None:
        """Word bank entry for a word, or None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT word, pos, definition, example, level FROM words WHERE word = ?",
                (word,),
            ).fetchone()
        return dict(row) if row else None

    def add_word(
        self, word: str, definition: str, example: str = "", pos: str = "", level: str = "b1"
    ) -> bool:
        """Add a user-supplied word to the bank; False if it already exists."""
        word = word.strip().lower()
        if not word or not definition.strip():
            raise ValueError("word and definition are required")
        level = level if level in ("a1", "a2", "b1", "b2") else "b1"
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO words (word, pos, definition, example, level, source)"
                " VALUES (?, ?, ?, ?, ?, 'user')",
                (word, pos, definition, example, level),
            )
            return cur.rowcount > 0

    def get_card(self, word: str) -> dict | None:
        """FSRS card state for a word, or None if not introduced yet."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT word, card_json, due, state, reps, lapses, last_review"
                " FROM cards WHERE word = ?",
                (word,),
            ).fetchone()
        return dict(row) if row else None

    def save_review(
        self,
        word: str,
        card_json: str,
        due: str,
        state: str,
        reps: int,
        lapses: int,
        rating: int,
        interval_days: float,
        reviewed_at: str | None = None,
    ) -> None:
        """Persist a card after a review and append to the review log."""
        reviewed_at = reviewed_at or due_iso()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO cards (word, card_json, due, state, reps, lapses, last_review, created)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                " ON CONFLICT(word) DO UPDATE SET"
                " card_json = excluded.card_json, due = excluded.due,"
                " state = excluded.state, reps = excluded.reps,"
                " lapses = excluded.lapses, last_review = excluded.last_review",
                (word, card_json, due, state, reps, lapses, reviewed_at, reviewed_at),
            )
            conn.execute(
                "INSERT INTO reviews (word, rating, reviewed_at, interval_days)"
                " VALUES (?, ?, ?, ?)",
                (word, rating, reviewed_at, interval_days),
            )

    def due_words(self, limit: int, level: str | None = None) -> list[str]:
        """Words due for review now, soonest first.

        With ``level``, only due words at that CEFR level are returned
        (an explicit lesson level must not be polluted by other levels).
        """
        with self._connect() as conn:
            if level:
                rows = conn.execute(
                    "SELECT c.word AS word FROM cards c"
                    " JOIN words w ON w.word = c.word"
                    " WHERE c.due <= ? AND w.level = ?"
                    " ORDER BY c.due ASC LIMIT ?",
                    (due_iso(), level, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT word FROM cards WHERE due <= ? ORDER BY due ASC LIMIT ?",
                    (due_iso(), limit),
                ).fetchall()
        return [r["word"] for r in rows]

    def unseen_words(self, level: str, limit: int) -> list[str]:
        """Word-bank words at a level that have no card yet."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT word FROM words WHERE level = ? AND word NOT IN"
                " (SELECT word FROM cards) ORDER BY word LIMIT ?",
                (level, limit),
            ).fetchall()
        return [r["word"] for r in rows]

    def level_with_most_due(self) -> str:
        """Level whose words have the most due reviews (for auto-pick)."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT w.level AS level, COUNT(*) AS n FROM cards c"
                " JOIN words w ON w.word = c.word"
                " WHERE c.due <= ? GROUP BY w.level ORDER BY n DESC, w.level ASC LIMIT 1",
                (due_iso(),),
            ).fetchone()
        return row["level"] if row else "a1"

    def earliest_unseen_level(self) -> str:
        """First CEFR level (a1 first) that still has unseen words."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT level FROM words WHERE word NOT IN (SELECT word FROM cards)"
                " ORDER BY CASE level WHEN 'a1' THEN 1 WHEN 'a2' THEN 2"
                " WHEN 'b1' THEN 3 ELSE 4 END LIMIT 1"
            ).fetchone()
        return row["level"] if row else "a1"

    def words_at_level(self, level: str) -> list[dict]:
        """All words at a CEFR level (seed bank + user/AI-added), sorted."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT word, pos, definition, example, level, source FROM words"
                " WHERE level = ? ORDER BY word",
                (level,),
            ).fetchall()
        return [dict(r) for r in rows]

    def due_words_detail(self, limit: int = 25) -> list[dict]:
        """Due words with their bank entries (for the duo://due resource)."""
        words = self.due_words(limit)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT c.word AS word, c.due AS due, c.state AS state,"
                " w.definition AS definition, w.level AS level, w.pos AS pos"
                " FROM cards c LEFT JOIN words w ON w.word = c.word"
                " WHERE c.word IN ({})".format(",".join("?" * len(words))),
                words,
            ).fetchall()
        return [dict(r) for r in rows]


def review_state(card: dict) -> str:
    """Human state label for a card row ('Learning'/'Review'/'Relearning')."""
    return card["state"]
