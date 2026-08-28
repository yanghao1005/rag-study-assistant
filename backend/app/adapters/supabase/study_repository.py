"""Supabase study artifacts repository."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.enums import (
    ArtifactStatus,
    ArtifactType,
    Difficulty,
    QuestionType,
    SourceScope,
)
from app.domain.entities.review import FlashcardReview
from app.domain.entities.study import DueFlashcard, Flashcard, QuizQuestion, StudyArtifact
from app.ports.repositories import StudyRepositoryPort
from supabase import Client


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _artifact_from_row(row: dict[str, Any]) -> StudyArtifact:
    return StudyArtifact(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        subject_id=str(row["subject_id"]),
        artifact_type=ArtifactType(row["artifact_type"]),
        title=str(row["title"]),
        document_id=str(row["document_id"]) if row.get("document_id") else None,
        status=ArtifactStatus(row.get("status") or "ready"),
        source_scope=SourceScope(row.get("source_scope") or "subject"),
        source_ref=row.get("source_ref"),
        content_json=row.get("content_json") or {},
        metadata=row.get("metadata") or {},
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


def _flashcard_from_row(row: dict[str, Any]) -> Flashcard:
    return Flashcard(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        artifact_id=str(row["artifact_id"]),
        front=str(row["front"]),
        back=str(row["back"]),
        hint=row.get("hint"),
        difficulty=Difficulty(row["difficulty"]) if row.get("difficulty") else None,
        tags=list(row.get("tags") or []),
        source_chunk_ids=[str(x) for x in (row.get("source_chunk_ids") or [])],
        position=int(row.get("position") or 0),
        created_at=_parse_dt(row.get("created_at")),
    )


def _question_from_row(row: dict[str, Any]) -> QuizQuestion:
    return QuizQuestion(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        artifact_id=str(row["artifact_id"]),
        question=str(row["question"]),
        options=list(row.get("options") or []),
        correct_option_index=row.get("correct_option_index"),
        correct_answer=row.get("correct_answer"),
        explanation=row.get("explanation"),
        question_type=QuestionType(row.get("question_type") or "multiple_choice"),
        difficulty=Difficulty(row["difficulty"]) if row.get("difficulty") else None,
        source_chunk_ids=[str(x) for x in (row.get("source_chunk_ids") or [])],
        position=int(row.get("position") or 0),
        created_at=_parse_dt(row.get("created_at")),
    )


def _review_from_row(row: dict[str, Any]) -> FlashcardReview:
    return FlashcardReview(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        flashcard_id=str(row["flashcard_id"]),
        ease=float(row.get("ease") or 2.5),
        interval_days=int(row.get("interval_days") or 0),
        repetitions=int(row.get("repetitions") or 0),
        next_review_at=_parse_dt(row.get("next_review_at")),
        last_reviewed_at=_parse_dt(row.get("last_reviewed_at")),
        last_quality=row.get("last_quality"),
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


class SupabaseStudyRepository(StudyRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create_artifact(self, artifact: StudyArtifact) -> StudyArtifact:
        payload = {
            "id": artifact.id or str(uuid4()),
            "user_id": artifact.user_id,
            "subject_id": artifact.subject_id,
            "document_id": artifact.document_id,
            "artifact_type": artifact.artifact_type.value,
            "title": artifact.title,
            "status": artifact.status.value,
            "source_scope": artifact.source_scope.value,
            "source_ref": artifact.source_ref,
            "content_json": artifact.content_json,
            "metadata": artifact.metadata,
        }
        response = self._client.table("study_artifacts").insert(payload).execute()
        return _artifact_from_row(response.data[0])

    async def get_artifact(self, *, user_id: str, artifact_id: str) -> StudyArtifact | None:
        response = (
            self._client.table("study_artifacts")
            .select("*")
            .eq("id", artifact_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _artifact_from_row(response.data[0])

    async def list_artifacts(
        self,
        *,
        user_id: str,
        subject_id: str,
        artifact_type: str | None = None,
    ) -> list[StudyArtifact]:
        query = (
            self._client.table("study_artifacts")
            .select("*")
            .eq("user_id", user_id)
            .eq("subject_id", subject_id)
            .order("updated_at", desc=True)
            .order("created_at", desc=True)
        )
        if artifact_type:
            query = query.eq("artifact_type", artifact_type)
        response = query.execute()
        return [_artifact_from_row(row) for row in response.data or []]

    async def delete_artifact(self, *, user_id: str, artifact_id: str) -> bool:
        response = (
            self._client.table("study_artifacts")
            .delete()
            .eq("id", artifact_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    async def update_artifact(self, artifact: StudyArtifact) -> StudyArtifact:
        payload = {
            "title": artifact.title,
            "status": artifact.status.value,
            "source_scope": artifact.source_scope.value,
            "source_ref": artifact.source_ref,
            "content_json": artifact.content_json,
            "metadata": artifact.metadata,
            "document_id": artifact.document_id,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        response = (
            self._client.table("study_artifacts")
            .update(payload)
            .eq("id", artifact.id)
            .eq("user_id", artifact.user_id)
            .execute()
        )
        if not response.data:
            return artifact
        return _artifact_from_row(response.data[0])

    async def save_flashcards(self, cards: list[Flashcard]) -> int:
        if not cards:
            return 0
        rows = [
            {
                "id": card.id or str(uuid4()),
                "user_id": card.user_id,
                "artifact_id": card.artifact_id,
                "front": card.front,
                "back": card.back,
                "hint": card.hint,
                "difficulty": card.difficulty.value if card.difficulty else None,
                "tags": card.tags,
                "source_chunk_ids": card.source_chunk_ids,
                "position": card.position,
            }
            for card in cards
        ]
        response = self._client.table("flashcards").insert(rows).execute()
        return len(response.data or [])

    async def list_flashcards(self, *, user_id: str, artifact_id: str) -> list[Flashcard]:
        response = (
            self._client.table("flashcards")
            .select("*")
            .eq("user_id", user_id)
            .eq("artifact_id", artifact_id)
            .order("position")
            .execute()
        )
        return [_flashcard_from_row(row) for row in response.data or []]

    async def get_flashcard(self, *, user_id: str, flashcard_id: str) -> Flashcard | None:
        response = (
            self._client.table("flashcards")
            .select("*")
            .eq("id", flashcard_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _flashcard_from_row(response.data[0])

    async def update_flashcard(self, card: Flashcard) -> Flashcard:
        payload = {
            "front": card.front,
            "back": card.back,
            "hint": card.hint,
            "difficulty": card.difficulty.value if card.difficulty else None,
            "tags": card.tags,
            "source_chunk_ids": card.source_chunk_ids,
            "position": card.position,
        }
        response = (
            self._client.table("flashcards")
            .update(payload)
            .eq("id", card.id)
            .eq("user_id", card.user_id)
            .execute()
        )
        if not response.data:
            return card
        return _flashcard_from_row(response.data[0])

    async def delete_flashcard(self, *, user_id: str, flashcard_id: str) -> bool:
        response = (
            self._client.table("flashcards")
            .delete()
            .eq("id", flashcard_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    async def save_quiz_questions(self, questions: list[QuizQuestion]) -> int:
        if not questions:
            return 0
        rows = [
            {
                "id": q.id or str(uuid4()),
                "user_id": q.user_id,
                "artifact_id": q.artifact_id,
                "question": q.question,
                "options": q.options,
                "correct_option_index": q.correct_option_index,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "question_type": q.question_type.value,
                "difficulty": q.difficulty.value if q.difficulty else None,
                "source_chunk_ids": q.source_chunk_ids,
                "position": q.position,
            }
            for q in questions
        ]
        response = self._client.table("quiz_questions").insert(rows).execute()
        return len(response.data or [])

    async def list_quiz_questions(self, *, user_id: str, artifact_id: str) -> list[QuizQuestion]:
        response = (
            self._client.table("quiz_questions")
            .select("*")
            .eq("user_id", user_id)
            .eq("artifact_id", artifact_id)
            .order("position")
            .execute()
        )
        return [_question_from_row(row) for row in response.data or []]

    async def get_quiz_question(self, *, user_id: str, question_id: str) -> QuizQuestion | None:
        response = (
            self._client.table("quiz_questions")
            .select("*")
            .eq("id", question_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _question_from_row(response.data[0])

    async def update_quiz_question(self, question: QuizQuestion) -> QuizQuestion:
        payload = {
            "question": question.question,
            "options": question.options,
            "correct_option_index": question.correct_option_index,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "question_type": question.question_type.value,
            "difficulty": question.difficulty.value if question.difficulty else None,
            "source_chunk_ids": question.source_chunk_ids,
            "position": question.position,
        }
        response = (
            self._client.table("quiz_questions")
            .update(payload)
            .eq("id", question.id)
            .eq("user_id", question.user_id)
            .execute()
        )
        if not response.data:
            return question
        return _question_from_row(response.data[0])

    async def delete_quiz_question(self, *, user_id: str, question_id: str) -> bool:
        response = (
            self._client.table("quiz_questions")
            .delete()
            .eq("id", question_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)

    async def list_due_flashcards(
        self, *, user_id: str, subject_id: str, limit: int = 20
    ) -> list[DueFlashcard]:
        artifacts = await self.list_artifacts(
            user_id=user_id, subject_id=subject_id, artifact_type="flashcard_deck"
        )
        due: list[DueFlashcard] = []
        now = datetime.now(UTC)
        for artifact in artifacts:
            cards = await self.list_flashcards(user_id=user_id, artifact_id=artifact.id)
            for card in cards:
                review = await self.get_review(user_id=user_id, flashcard_id=card.id)
                if review is not None and review.next_review_at and review.next_review_at > now:
                    continue
                due.append(
                    DueFlashcard(
                        card=card,
                        subject_id=subject_id,
                        artifact_title=artifact.title,
                        review=review,
                    )
                )
                if len(due) >= limit:
                    return due
        return due

    async def get_review(self, *, user_id: str, flashcard_id: str) -> FlashcardReview | None:
        response = (
            self._client.table("flashcard_reviews")
            .select("*")
            .eq("user_id", user_id)
            .eq("flashcard_id", flashcard_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _review_from_row(response.data[0])

    async def upsert_review(self, review: FlashcardReview) -> FlashcardReview:
        payload = {
            "id": review.id or str(uuid4()),
            "user_id": review.user_id,
            "flashcard_id": review.flashcard_id,
            "ease": review.ease,
            "interval_days": review.interval_days,
            "repetitions": review.repetitions,
            "next_review_at": review.next_review_at.isoformat() if review.next_review_at else None,
            "last_reviewed_at": (
                review.last_reviewed_at.isoformat() if review.last_reviewed_at else None
            ),
            "last_quality": review.last_quality,
        }
        response = (
            self._client.table("flashcard_reviews")
            .upsert(payload, on_conflict="user_id,flashcard_id")
            .execute()
        )
        return _review_from_row(response.data[0])
