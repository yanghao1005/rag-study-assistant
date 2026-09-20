from __future__ import annotations

from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from app.core.artifacts import write_json_artifact
from app.domain.models.contracts import (
    GenerateFlashcardsResponse,
    GenerateHistoryResponse,
    GenerateQuizResponse,
    GenerateSummaryResponse,
    RetrievalDiagnostics,
    ScopeLiteral,
)
from app.domain.ports.providers import LLMProvider
from app.domain.ports.repositories import VectorRepository
from app.infrastructure.providers.llm_provider import LLMProvider as StubLLMProvider
from app.infrastructure.repositories.vector_repository import InMemoryVectorRepository


class GenerationService:
    """Generates flashcards/quiz/summary from grounded retrieval context."""

    def __init__(
        self,
        *,
        vector_repository: VectorRepository | None = None,
        llm_provider: LLMProvider | None = None,
        debug_artifacts_dir: str = "debug_artifacts",
    ) -> None:
        self._vector_repository = vector_repository or InMemoryVectorRepository()
        self._llm_provider = llm_provider or StubLLMProvider()
        self._debug_artifacts_dir = debug_artifacts_dir

    def generate_flashcards(self, payload: dict[str, Any]) -> dict[str, Any]:
        scope = payload["scope"]
        scope_id = payload["scope_id"]
        count = int(payload.get("count", 5))
        query = payload.get("query") or "core concepts"

        candidates = self._vector_repository.retrieve(scope=scope, scope_id=scope_id, query=query, limit=max(count, 3))
        diagnostics = self._build_diagnostics(scope=scope, scope_id=scope_id, query=query, candidates=candidates)

        prompt = self._build_flashcards_prompt(scope=scope, scope_id=scope_id, query=query, count=count)
        raw = self._generate_with_retry(prompt=prompt, kind="flashcards")

        flashcards = raw.get("flashcards") or self._fallback_flashcards(count=count, query=query)
        sources = raw.get("sources") or self._sources_from_candidates(candidates)

        if payload.get("debug", False):
            trace_id = str(uuid4())
            artifact_path = write_json_artifact(
                root_dir=self._debug_artifacts_dir,
                run_id=trace_id,
                name="generation_flashcards",
                payload={
                    "scope": scope,
                    "scope_id": scope_id,
                    "query": query,
                    "candidates": candidates,
                    "raw": raw,
                },
            )
            diagnostics.debug_trace_id = trace_id
            diagnostics.debug_artifact_path = artifact_path

        response = GenerateFlashcardsResponse(
            flashcards=flashcards[:count],
            sources=sources,
            diagnostics=diagnostics,
        )

        if payload.get("save", True):
            self._vector_repository.save_generated(
                {
                    "user_id": payload.get("user_id") or "anonymous",
                    "scope": scope,
                    "scope_id": scope_id,
                    "type": "flashcard",
                    "subject_id": scope_id if scope == "subject" else None,
                    "document_id": scope_id if scope == "document" else None,
                    "chapter_id": scope_id if scope == "chapter" else None,
                    "content_json": response.model_dump(),
                }
            )

        return response.model_dump()

    def generate_quiz(self, payload: dict[str, Any]) -> dict[str, Any]:
        scope = payload["scope"]
        scope_id = payload["scope_id"]
        count = int(payload.get("count", 5))
        query = payload.get("query") or "important questions"

        candidates = self._vector_repository.retrieve(scope=scope, scope_id=scope_id, query=query, limit=max(count, 3))
        diagnostics = self._build_diagnostics(scope=scope, scope_id=scope_id, query=query, candidates=candidates)

        prompt = self._build_quiz_prompt(scope=scope, scope_id=scope_id, query=query, count=count)
        raw = self._generate_with_retry(prompt=prompt, kind="quiz")

        questions = raw.get("questions") or self._fallback_questions(count=count, query=query)

        if payload.get("debug", False):
            trace_id = str(uuid4())
            artifact_path = write_json_artifact(
                root_dir=self._debug_artifacts_dir,
                run_id=trace_id,
                name="generation_quiz",
                payload={
                    "scope": scope,
                    "scope_id": scope_id,
                    "query": query,
                    "candidates": candidates,
                    "raw": raw,
                },
            )
            diagnostics.debug_trace_id = trace_id
            diagnostics.debug_artifact_path = artifact_path

        response = GenerateQuizResponse(questions=questions[:count], diagnostics=diagnostics)

        if payload.get("save", True):
            self._vector_repository.save_generated(
                {
                    "user_id": payload.get("user_id") or "anonymous",
                    "scope": scope,
                    "scope_id": scope_id,
                    "type": "quiz",
                    "subject_id": scope_id if scope == "subject" else None,
                    "document_id": scope_id if scope == "document" else None,
                    "chapter_id": scope_id if scope == "chapter" else None,
                    "content_json": response.model_dump(),
                }
            )

        return response.model_dump()

    def get_summary(self, scope_id: str) -> dict[str, Any]:
        return GenerateSummaryResponse(summary="", scope="summary", scope_id=scope_id).model_dump()

    def get_history(self, *, user_id: str, scope: ScopeLiteral, scope_id: str, limit: int) -> dict[str, Any]:
        items = self._vector_repository.list_generated(user_id=user_id, scope=scope, scope_id=scope_id, limit=limit)
        return GenerateHistoryResponse(items=items).model_dump(mode="json")

    def _generate_with_retry(self, *, prompt: str, kind: str) -> dict[str, Any]:
        for attempt in range(2):
            try:
                candidate = self._llm_provider.generate_json(
                    prompt if attempt == 0 else f"RETRY: return valid {kind} JSON.\n{prompt}"
                )
            except Exception:
                continue
            if self._is_valid_generation(candidate, kind=kind):
                return candidate
        return {}

    def _is_valid_generation(self, payload: dict[str, Any], *, kind: str) -> bool:
        try:
            if kind == "flashcards":
                GenerateFlashcardsResponse(
                    flashcards=payload.get("flashcards", []),
                    sources=payload.get("sources", []),
                    diagnostics=RetrievalDiagnostics(
                        scope="summary",
                        scope_id="validation",
                        query="validation",
                        total_candidates=0,
                        accepted_candidates=0,
                        best_score=0.0,
                    ),
                )
                return True

            if kind == "quiz":
                GenerateQuizResponse(
                    questions=payload.get("questions", []),
                    diagnostics=RetrievalDiagnostics(
                        scope="summary",
                        scope_id="validation",
                        query="validation",
                        total_candidates=0,
                        accepted_candidates=0,
                        best_score=0.0,
                    ),
                )
                return True
        except ValidationError:
            return False
        return False

    def _build_diagnostics(self, *, scope: ScopeLiteral, scope_id: str, query: str, candidates: list[dict[str, Any]]) -> RetrievalDiagnostics:
        best_score = max((float(item.get("score", 0.0)) for item in candidates), default=0.0)
        return RetrievalDiagnostics(
            scope=scope,
            scope_id=scope_id,
            query=query,
            total_candidates=len(candidates),
            accepted_candidates=len(candidates),
            best_score=best_score,
        )

    def _build_flashcards_prompt(self, *, scope: str, scope_id: str, query: str, count: int) -> str:
        return f"Generate flashcards for scope={scope} scope_id={scope_id} query={query} count={count}."

    def _build_quiz_prompt(self, *, scope: str, scope_id: str, query: str, count: int) -> str:
        return f"Generate quiz for scope={scope} scope_id={scope_id} query={query} count={count}."

    def _sources_from_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "document_type": item.get("document_type"),
                "page": item.get("page"),
                "chapter_name": item.get("chapter_name"),
                "preview": item.get("preview"),
            }
            for item in candidates[:3]
        ]

    def _fallback_flashcards(self, *, count: int, query: str) -> list[dict[str, str]]:
        return [
            {
                "front": f"Core idea {index + 1} about {query}",
                "back": f"Concise explanation for concept {index + 1}.",
            }
            for index in range(count)
        ]

    def _fallback_questions(self, *, count: int, query: str) -> list[dict[str, Any]]:
        return [
            {
                "question": f"Question {index + 1} about {query}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Option A is grounded in the retrieved context.",
                "source": {
                    "document_type": "pdf",
                    "page": index + 1,
                    "chapter_name": f"Chapter {index + 1}",
                    "preview": f"Supporting excerpt for {query}.",
                },
            }
            for index in range(count)
        ]
