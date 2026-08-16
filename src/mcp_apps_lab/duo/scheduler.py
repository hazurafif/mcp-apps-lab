"""FSRS-6 spaced-repetition wrapper for English Duo.

Thin layer over the `fsrs` package (the algorithm modern Anki uses):
each word is one card; answering grades it Again (wrong) or Good (right)
and the scheduler returns the next due time. Card state is stored as the
package's JSON representation, so it survives restarts and can be upgraded.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fsrs import Card, Rating, Scheduler

# Map an exercise result to an FSRS rating.
RATING_CORRECT = Rating.Good  # remembered (after a hesitation)
RATING_WRONG = Rating.Again  # forgot

# App-level bounds the scheduler respects.
MAX_INTERVAL_DAYS = 365
DESIRED_RETENTION = 0.9


def review_card(
    card_json: str | None,
    correct: bool,
    rating: int | None = None,
) -> tuple[str, str, float]:
    """Review a card (existing JSON state or a fresh card).

    ``correct`` maps to Good/Again; pass ``rating`` (1-4 FSRS rating) to
    override, e.g. for flip-card self-ratings (Again/Hard/Good/Easy).

    Returns ``(card_json, due_iso, interval_days)`` where ``due_iso`` is the
    UTC ISO timestamp of the next review.
    """
    scheduler = Scheduler(
        desired_retention=DESIRED_RETENTION,
        maximum_interval=MAX_INTERVAL_DAYS,
    )
    card = Card.from_json(card_json) if card_json else Card()
    if rating is not None:
        card, log = scheduler.review_card(card, Rating(rating))
    else:
        rating = RATING_CORRECT if correct else RATING_WRONG
        card, log = scheduler.review_card(card, rating)
    interval = (card.due - log.review_datetime).total_seconds() / 86400.0
    return card.to_json(), card.due.isoformat(), round(interval, 2)


def new_card_json() -> str:
    """JSON state for a freshly introduced word (due immediately)."""
    return Card().to_json()


def due_iso() -> str:
    """UTC now as the ISO string used for due comparisons."""
    return datetime.now(UTC).isoformat()
