"""Quiz backend tools — called by the quiz UI to grade answers."""

from __future__ import annotations


def submit_answer(
    question_index: int,
    selected: int,
    correct: int,
    total_questions: int,
    current_score: int,
) -> dict:
    """Grade an answer and return the updated quiz state.

    Returns a dict with:
    - is_correct: whether the selected answer matched the correct index
    - new_score: the updated cumulative score
    - answered_index: the question that was just answered
    - finished: whether this was the last question
    """
    is_correct = selected == correct
    new_score = current_score + (1 if is_correct else 0)
    finished = (question_index + 1) >= total_questions
    return {
        "is_correct": is_correct,
        "new_score": new_score,
        "answered_index": question_index,
        "finished": finished,
    }
