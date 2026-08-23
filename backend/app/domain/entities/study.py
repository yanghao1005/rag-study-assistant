"""Study artifact entities: decks, flashcards, quizzes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.entities.enums import (
    ArtifactStatus,
    ArtifactType,
    Difficulty,
    QuestionType,
    SourceScope,
)
from app.domain.entities.review import FlashcardReview
from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class StudyArtifact:
    id: str
    user_id: str
    subject_id: str
    artifact_type: ArtifactType
    title: str
    document_id: str | None = None
    status: ArtifactStatus = ArtifactStatus.READY
    source_scope: SourceScope = SourceScope.SUBJECT
    source_ref: str | None = None
    content_json: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def mark_ready(self) -> None:
        self.status = ArtifactStatus.READY

    def mark_error(self) -> None:
        self.status = ArtifactStatus.ERROR


@dataclass(slots=True)
class Flashcard:
    id: str
    user_id: str
    artifact_id: str
    front: str
    back: str
    hint: str | None = None
    difficulty: Difficulty | None = None
    tags: list[str] = field(default_factory=list)
    source_chunk_ids: list[str] = field(default_factory=list)
    position: int = 0
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.front.strip() or not self.back.strip():
            raise ValidationError("Flashcard front and back are required")


@dataclass(slots=True)
class QuizQuestion:
    id: str
    user_id: str
    artifact_id: str
    question: str
    options: list[Any] = field(default_factory=list)
    correct_option_index: int | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    difficulty: Difficulty | None = None
    source_chunk_ids: list[str] = field(default_factory=list)
    position: int = 0
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.question.strip():
            raise ValidationError("Quiz question text is required")
        if self.correct_option_index is None and not self.correct_answer:
            raise ValidationError("Quiz question must have a correct answer")


@dataclass(slots=True)
class DueFlashcard:
    card: Flashcard
    subject_id: str
    artifact_title: str
    review: FlashcardReview | None = None
