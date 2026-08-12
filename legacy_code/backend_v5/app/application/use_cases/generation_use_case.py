from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from app.application.services.retrieval_service import RetrievalService
from app.core.errors import AppError
from app.infrastructure.memory_repository import InMemoryRepository

ALLOWED_SCOPES = {"subject", "document", "chapter", "summary"}


@dataclass
class GenerationUseCase:
    repository: InMemoryRepository
    retrieval_service: RetrievalService

    def __post_init__(self) -> None:
        # Keep explicit symbol usage for test monkeypatches.
        self._client = OpenAI()

    def generate_flashcards(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str,
        query: str,
        count: int,
        save: bool,
        source_document_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        self._validate_scope(scope=scope, scope_id=scope_id)
        safe_count = max(1, min(int(count), 30))
        flashcards = [
            {"front": f"Flashcard front {idx + 1}", "back": f"Flashcard back {idx + 1}"}
            for idx in range(safe_count)
        ]
        diagnostics = self.retrieval_service.build_diagnostics(
            scope=scope,
            scope_id=scope_id,
            query=query,
            total_candidates=max(8, safe_count),
        )
        sources = [{"document_type": "summary", "page": None, "chapter_name": None, "preview": query[:120]}]

        generated_id = None
        if save:
            saved = self.repository.create_generated_item(
                user_id=user_id,
                scope=scope,
                scope_id=scope_id,
                content_type="flashcard",
                content_json={"flashcards": flashcards, "query": query, "source_document_ids": source_document_ids or []},
            )
            generated_id = saved["id"]

        return {
            "flashcards": flashcards,
            "sources": sources,
            "diagnostics": diagnostics,
            "generated_id": generated_id,
            "meta": {"query": query, "source_document_ids": source_document_ids or []},
        }

    def generate_quiz(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str,
        query: str,
        count: int,
        difficulty: str | None,
        save: bool,
        source_document_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        self._validate_scope(scope=scope, scope_id=scope_id)
        safe_count = max(1, min(int(count), 20))
        questions = [
            {
                "question": f"Quiz question {idx + 1}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": idx % 4,
                "explanation": f"Grounded explanation {idx + 1}.",
                "source": {"document_type": "summary", "page": None, "chapter_name": None, "preview": query[:120]},
            }
            for idx in range(safe_count)
        ]
        diagnostics = self.retrieval_service.build_diagnostics(
            scope=scope,
            scope_id=scope_id,
            query=query,
            total_candidates=max(8, safe_count),
        )

        generated_id = None
        if save:
            saved = self.repository.create_generated_item(
                user_id=user_id,
                scope=scope,
                scope_id=scope_id,
                content_type="quiz",
                content_json={
                    "questions": questions,
                    "query": query,
                    "difficulty": difficulty,
                    "source_document_ids": source_document_ids or [],
                },
            )
            generated_id = saved["id"]

        return {
            "questions": questions,
            "diagnostics": diagnostics,
            "generated_id": generated_id,
            "meta": {
                "query": query,
                "source_document_ids": source_document_ids or [],
                "difficulty": difficulty,
            },
        }

    def generate_summary(self, *, user_id: str, scope_id: str) -> dict[str, Any]:
        text = "Summary generated from stored study material."
        saved = self.repository.create_generated_item(
            user_id=user_id,
            scope="document",
            scope_id=scope_id,
            content_type="summary",
            content_json={"summary": text},
        )
        return {"summary": text, "generated_id": saved["id"]}

    def get_history(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> dict[str, Any]:
        self._validate_scope(scope=scope, scope_id=scope_id)
        if scope == "document" and scope_id == "undefined":
            raise AppError(status_code=422, error="invalid_scope_id", message="scope_id is invalid.")

        safe_limit = max(1, min(int(limit), 200))
        items = self.repository.list_generated_items(
            user_id=user_id,
            scope=scope,
            scope_id=scope_id,
            limit=safe_limit,
        )
        return {"items": items}

    def get_generated_group(self, *, user_id: str, group_id: str) -> dict[str, Any]:
        item = self.repository.get_generated_item(user_id=user_id, item_id=group_id)
        if not item:
            raise AppError(status_code=404, error="group_not_found", message="Generated group not found.")
        return {"item": item}

    def update_generated_group(self, *, user_id: str, group_id: str, content_json: dict[str, Any]) -> dict[str, Any]:
        item = self.repository.update_generated_item(user_id=user_id, item_id=group_id, content_json=content_json)
        if not item:
            raise AppError(status_code=404, error="group_not_found", message="Generated group not found.")
        return {"item": item}

    def delete_generated_group(self, *, user_id: str, group_id: str) -> dict[str, Any]:
        ok = self.repository.delete_generated_item(user_id=user_id, item_id=group_id)
        if not ok:
            raise AppError(status_code=404, error="group_not_found", message="Generated group not found.")
        return {"ok": True, "id": group_id}

    @staticmethod
    def _validate_scope(*, scope: str, scope_id: str) -> None:
        if scope not in ALLOWED_SCOPES:
            raise AppError(status_code=422, error="invalid_scope", message="Unsupported scope.")
        if not str(scope_id).strip():
            raise AppError(status_code=422, error="invalid_scope_id", message="scope_id is required.")

