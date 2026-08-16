"""Duolingo-style game mechanics for English Duo.

Pure functions — no I/O — so they are easy to unit test:
- XP with a combo bonus (capped)
- hearts (mistake penalty, daily refill)
- daily streak (increments once per day, on lesson completion)
- level ladder (1-10) with league names
"""

from __future__ import annotations

MAX_HEARTS = 5
BASE_XP = 10
COMBO_BONUS = 2  # extra XP per combo step
COMBO_BONUS_CAP = 10  # max bonus from a streak of correct answers

# Cumulative XP needed to REACH each level (index 0 = level 1).
LEVEL_THRESHOLDS = (0, 50, 120, 220, 360, 550, 800, 1120, 1520, 2000)

# League names by level tier (1-2 Bronze ... 9-10 Diamond).
_LEAGUES = {1: "Bronze", 2: "Silver", 3: "Gold", 4: "Platinum", 5: "Diamond"}


def xp_for(correct: bool, combo: int) -> int:
    """XP gained for an answer: 10 base + combo bonus when correct.

    combo is the number of *consecutive* correct answers INCLUDING this one;
    the bonus starts on the second (combo 1 = plain base XP).
    """
    if not correct:
        return 0
    bonus = min(max(0, combo - 1) * COMBO_BONUS, COMBO_BONUS_CAP)
    return BASE_XP + bonus


def level_for(xp: int) -> tuple[int, int, int]:
    """Map total XP to (level, xp_into_level, xp_needed_for_next_level)."""
    level = 1
    for threshold in LEVEL_THRESHOLDS[1:]:
        if xp < threshold:
            break
        level += 1
    level = min(level, len(LEVEL_THRESHOLDS))
    into = xp - LEVEL_THRESHOLDS[level - 1]
    if level >= len(LEVEL_THRESHOLDS):
        return level, into, 0
    next_xp = LEVEL_THRESHOLDS[level] - LEVEL_THRESHOLDS[level - 1]
    return level, into, next_xp


def league_for(level: int) -> str:
    """League name for a level: Bronze/Silver/Gold/Platinum/Diamond."""
    tier = min((level - 1) // 2 + 1, 5)
    return _LEAGUES[tier]


def hearts_after_answer(hearts: int, correct: bool) -> int:
    """Hearts remaining after an answer (lose one on a mistake)."""
    if correct:
        return hearts
    return max(0, hearts - 1)
