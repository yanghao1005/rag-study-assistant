"""Planner / spaced-repetition use case."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.core.errors import AppError
from app.domain.entities.review import FlashcardReview
from app.domain.srs import SrsState, apply_sm2
from app.ports.repositories import StudyRepositoryPort, SubjectRepositoryPort


class PlannerUseCase:
    def __init__(self, *, subjects: SubjectRepositoryPort, study: StudyRepositoryPort) -> None:
        self._subjects = subjects
        self._study = study

    async def due(
        self, *, user_id: str, subject_id: str, limit: int = 20
    ) -> list[dict[str, object]]:
        subject = await self._subjects.get(user_id=user_id, subject_id=subject_id)
        if subject is None:
            raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")
        items = await self._study.list_due_flashcards(
            user_id=user_id, subject_id=subject_id, limit=limit
        )
        return [
            {
                "flashcard_id": item.card.id,
                "front": item.card.front,
                "back": item.card.back,
                "hint": item.card.hint,
                "artifact_title": item.artifact_title,
                "next_review_at": (
                    item.review.next_review_at.isoformat()
                    if item.review and item.review.next_review_at
                    else None
                ),
                "repetitions": item.review.repetitions if item.review else 0,
            }
            for item in items
        ]

    async def review(
        self, *, user_id: str, flashcard_id: str, quality: int
    ) -> dict[str, object]:
        existing = await self._study.get_review(user_id=user_id, flashcard_id=flashcard_id)
        previous = (
            SrsState(
                ease=existing.ease,
                interval_days=existing.interval_days,
                repetitions=existing.repetitions,
                next_review_at=existing.next_review_at,
                last_quality=existing.last_quality,
            )
            if existing
            else None
        )
        now = datetime.now(UTC)
        nxt = apply_sm2(previous, quality=quality, now=now)
        saved = await self._study.upsert_review(
            FlashcardReview(
                id=existing.id if existing else str(uuid4()),
                user_id=user_id,
                flashcard_id=flashcard_id,
                ease=nxt.ease,
                interval_days=nxt.interval_days,
                repetitions=nxt.repetitions,
                next_review_at=nxt.next_review_at,
                last_reviewed_at=now,
                last_quality=nxt.last_quality,
            )
        )
        return {
            "flashcard_id": saved.flashcard_id,
            "ease": saved.ease,
            "interval_days": saved.interval_days,
            "repetitions": saved.repetitions,
            "next_review_at": saved.next_review_at.isoformat() if saved.next_review_at else None,
        }
