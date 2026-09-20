from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from app.core.errors import AppError
from app.infrastructure.memory_repository import InMemoryRepository

ALLOWED_SCOPES = {"subject", "document", "chapter", "summary"}


@dataclass
class ChatUseCase:
    repository: InMemoryRepository

    def __post_init__(self) -> None:
        # Kept explicit for test monkeypatching.
        self._client = OpenAI()

    def ask(
        self,
        *,
        user_id: str,
        scope: str,
        scope_id: str,
        question: str,
        save: bool,
    ) -> dict[str, Any]:
        if scope not in ALLOWED_SCOPES:
            raise AppError(status_code=422, error="invalid_scope", message="Unsupported scope.")
        if not scope_id.strip():
            raise AppError(status_code=422, error="invalid_scope_id", message="scope_id is required.")
        if not question.strip():
            raise AppError(status_code=422, error="validation_error", message="question is required.")

        answer = {
            "answer": "Grounded chat answer.",
            "confidence": 0.84,
            "citations": [{"source_rank": 1, "preview": question[:120]}],
        }
        if save:
            self.repository.create_generated_item(
                user_id=user_id,
                scope=scope,
                scope_id=scope_id,
                content_type="chat_answer",
                content_json=answer,
            )
        return answer

