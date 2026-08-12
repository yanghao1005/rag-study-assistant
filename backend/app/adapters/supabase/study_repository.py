"""Supabase study artifacts repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.enums import (
    ArtifactStatus,
    ArtifactType,
    Difficulty,
    QuestionType,
    SourceScope,
)
from app.domain.entities.study import Flashcard, QuizQuestion, StudyArtifact
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
        cards: list[Flashcard] = []
        for row in response.data or []:
            cards.append(
                Flashcard(
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
            )
        return cards

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
        items: list[QuizQuestion] = []
        for row in response.data or []:
            items.append(
                QuizQuestion(
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
            )
        return items
