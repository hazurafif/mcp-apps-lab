"""Quiz data — the built-in fallback question set."""

from __future__ import annotations

from typing import TypedDict


class Question(TypedDict):
    question: str
    options: list[str]
    correct: int


DEFAULT_QUESTIONS: list[Question] = [
    {
        "question": "What is the capital of Australia?",
        "options": ["Sydney", "Melbourne", "Canberra", "Perth"],
        "correct": 2,
    },
    {
        "question": "Which planet has the most moons?",
        "options": ["Jupiter", "Saturn", "Uranus", "Neptune"],
        "correct": 1,
    },
    {
        "question": "What year did the Berlin Wall fall?",
        "options": ["1987", "1989", "1991", "1993"],
        "correct": 1,
    },
    {
        "question": "Which element has the chemical symbol 'Au'?",
        "options": ["Silver", "Aluminum", "Gold", "Argon"],
        "correct": 2,
    },
    {
        "question": "What is the deepest ocean?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "correct": 3,
    },
]
