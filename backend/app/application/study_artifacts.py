"""Helpers for study artifact titles, origin and library summaries."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.study import Flashcard, QuizQuestion, StudyArtifact

_ORIGINS = frozenset({"generated", "manual", "imported"})


def study_artifact_title(query: str | None, *, kind: str) -> str:
    cleaned = " ".join((query or "").split())
    if cleaned:
        return cleaned[:80]
    label = "Quiz" if kind == "quiz" else "Flashcards"
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
    return f"{label} · {stamp}"


def artifact_origin(metadata: dict[str, Any] | None) -> str:
    origin = (metadata or {}).get("origin")
    if origin in _ORIGINS:
        return str(origin)
    return "generated"


def artifact_item_count(artifact: StudyArtifact) -> int:
    content = artifact.content_json or {}
    if artifact.artifact_type.value == "flashcard_deck":
        cards = content.get("cards")
        return len(cards) if isinstance(cards, list) else 0
    if artifact.artifact_type.value == "quiz":
        questions = content.get("questions")
        return len(questions) if isinstance(questions, list) else 0
    return 0


def flashcards_content(cards: list[Flashcard]) -> dict[str, Any]:
    return {
        "cards": [
            {"front": card.front, "back": card.back, "hint": card.hint} for card in cards
        ]
    }


def questions_content(questions: list[QuizQuestion]) -> dict[str, Any]:
    return {
        "questions": [
            {
                "question": item.question,
                "options": item.options,
                "correct_option_index": item.correct_option_index,
                "explanation": item.explanation,
            }
            for item in questions
        ]
    }
