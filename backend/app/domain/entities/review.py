"""Spaced-repetition review entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class FlashcardReview:
    id: str
    user_id: str
    flashcard_id: str
    ease: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    next_review_at: datetime | None = None
    last_reviewed_at: datetime | None = None
    last_quality: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
