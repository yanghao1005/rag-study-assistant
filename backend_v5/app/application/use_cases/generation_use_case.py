from __future__ import annotations

import json
from typing import Any

from app.application.services.retrieval_service import RetrievalService
from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.ports.repositories import StudyRepository
from openai import OpenAI
from app.presentation.api.schemas.generation import (
    DeleteGeneratedGroupResponse,
    FlashcardItem,
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    GeneratedGroupResponse,
    GeneratedHistoryItem,
    GeneratedHistoryResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    QuizItem,
    RetrievalDiagnostics,
    SourceCitation,
    UpdateGeneratedGroupRequest,
)


class GenerationUseCase:
    def __init__(self, *, repository: StudyRepository, retrieval_service: RetrievalService) -> None:
        self._repository = repository
        self._retrieval = retrieval_service
        settings = get_settings()
        self._llm_model = settings.openai_llm_model
        if settings.llm_provider == "openai" and settings.openai_api_key:
            self._llm_client: OpenAI | None = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url or None,
            )
        else:
            self._llm_client = None

    def _require_llm_client(self) -> OpenAI:
        if not self._llm_client:
            raise AppError(
                error="llm_not_configured",
                message="OpenAI LLM provider is required for flashcards and quizzes.",
                status_code=503,
            )
        return self._llm_client

    def generate_flashcards(self, *, user_id: str, request: GenerateFlashcardsRequest) -> GenerateFlashcardsResponse:
        self._require_llm_client()
        query = request.query or "core concepts"
        candidates = self._retrieval.retrieve(
            user_id=user_id,
            scope=request.scope,
            scope_id=request.scope_id,
            query=query,
            limit=max(request.count * 2, 8),
            source_document_ids=request.source_document_ids,
        )
        if not candidates:
            raise AppError(
                error="no_context_available",
                message="No indexed context found for this scope. Upload and process documents first.",
                status_code=422,
            )

        diagnostics = self._build_diagnostics(scope=request.scope, scope_id=request.scope_id, query=query, candidates=candidates)
        flashcards = self._generate_flashcards_with_llm(query=query, request=request, candidates=candidates)
        if len(flashcards) < request.count:
            raise AppError(
                error="llm_output_invalid",
                message="LLM returned fewer flashcards than requested.",
                status_code=502,
                details={"expected": request.count, "received": len(flashcards)},
            )

        response = GenerateFlashcardsResponse(
            flashcards=flashcards[: request.count],
            sources=self._sources_from_candidates(candidates),
            diagnostics=diagnostics,
        )

        if request.save:
            payload = response.model_dump(mode="json")
            payload["meta"] = {
                "query": query,
                "source_document_ids": request.source_document_ids,
            }
            saved = self._repository.save_generated(
                user_id=user_id,
                scope=request.scope,
                scope_id=request.scope_id,
                content_type="flashcard",
                content_json=payload,
            )
            response.generated_id = str(saved.get("id") or "") or None

        return response

    def generate_quiz(self, *, user_id: str, request: GenerateQuizRequest) -> GenerateQuizResponse:
        self._require_llm_client()
        query = request.query or "important questions"
        candidates = self._retrieval.retrieve(
            user_id=user_id,
            scope=request.scope,
            scope_id=request.scope_id,
            query=query,
            limit=max(request.count * 2, 8),
            source_document_ids=request.source_document_ids,
        )
        if not candidates:
            raise AppError(
                error="no_context_available",
                message="No indexed context found for this scope. Upload and process documents first.",
                status_code=422,
            )

        diagnostics = self._build_diagnostics(scope=request.scope, scope_id=request.scope_id, query=query, candidates=candidates)
        questions = self._generate_quiz_with_llm(query=query, request=request, candidates=candidates)
        if len(questions) < request.count:
            raise AppError(
                error="llm_output_invalid",
                message="LLM returned fewer quiz questions than requested.",
                status_code=502,
                details={"expected": request.count, "received": len(questions)},
            )

        response = GenerateQuizResponse(questions=questions[: request.count], diagnostics=diagnostics)

        if request.save:
            payload = response.model_dump(mode="json")
            payload["meta"] = {
                "query": query,
                "source_document_ids": request.source_document_ids,
                "difficulty": request.difficulty,
            }
            saved = self._repository.save_generated(
                user_id=user_id,
                scope=request.scope,
                scope_id=request.scope_id,
                content_type="quiz",
                content_json=payload,
            )
            response.generated_id = str(saved.get("id") or "") or None

        return response

    def _generate_flashcards_with_llm(
        self,
        *,
        query: str,
        request: GenerateFlashcardsRequest,
        candidates: list[dict[str, Any]],
    ) -> list[FlashcardItem]:
        if not candidates:
            return []

        llm_client = self._require_llm_client()

        context_lines = []
        for idx, item in enumerate(candidates[:8], start=1):
            context_lines.append(
                f"[{idx}] doc_type={item.get('document_type')} page={item.get('page')} chapter={item.get('chapter_name')}\\n{item.get('preview')}"
            )

        schema_hint = {
            "flashcards": [
                {
                    "front": "string",
                    "back": "string",
                    "source_rank": 1,
                }
            ]
        }

        try:
            completion = llm_client.chat.completions.create(
                model=self._llm_model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate grounded flashcards. "
                            "Use only provided context, return valid JSON, no markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Create {request.count} flashcards for query: {query}.\\n"
                            "Rules:\\n"
                            "- Keep each front concise and clear.\\n"
                            "- Keep each back factual and grounded in context.\\n"
                            "- source_rank should map to the context block used (1..N).\\n"
                            "Return JSON matching this shape exactly:\\n"
                            f"{json.dumps(schema_hint)}\\n\\n"
                            "Context:\\n"
                            + "\\n\\n".join(context_lines)
                        ),
                    },
                ],
            )
            content = completion.choices[0].message.content or "{}"
            parsed = json.loads(content)
        except Exception:
            return []

        raw_flashcards = parsed.get("flashcards") if isinstance(parsed, dict) else None
        if not isinstance(raw_flashcards, list):
            return []

        built: list[FlashcardItem] = []
        for item in raw_flashcards:
            if not isinstance(item, dict):
                continue
            front = str(item.get("front") or "").strip()
            back = str(item.get("back") or "").strip()
            if not front or not back:
                continue
            built.append(
                FlashcardItem(
                    front=self._truncate(front, request.front_max_chars),
                    back=self._truncate(back, request.back_max_chars),
                )
            )
            if len(built) >= request.count:
                break

        return built

    def _generate_quiz_with_llm(
        self,
        *,
        query: str,
        request: GenerateQuizRequest,
        candidates: list[dict[str, Any]],
    ) -> list[QuizItem]:
        if not candidates:
            return []

        llm_client = self._require_llm_client()

        context_lines = []
        for idx, item in enumerate(candidates[:8], start=1):
            context_lines.append(
                f"[{idx}] doc_type={item.get('document_type')} page={item.get('page')} chapter={item.get('chapter_name')}\n{item.get('preview')}"
            )

        schema_hint = {
            "questions": [
                {
                    "question": "string",
                    "options": ["string", "string", "string", "string"],
                    "correct_answer": 0,
                    "explanation": "string",
                    "source_rank": 1,
                }
            ]
        }

        try:
            completion = llm_client.chat.completions.create(
                model=self._llm_model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate grounded multiple-choice quizzes. "
                            "Use only provided context, return valid JSON, no markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Create {request.count} quiz questions for query: {query}.\n"
                            f"Difficulty: {request.difficulty or 'medium'}.\n"
                            "Rules:\n"
                            "- 4 options per question.\n"
                            "- correct_answer must be index 0-3.\n"
                            "- explanation must be concise and grounded in context.\n"
                            "- source_rank should map to the context block used (1..N).\n"
                            "Return JSON matching this shape exactly:\n"
                            f"{json.dumps(schema_hint)}\n\n"
                            "Context:\n"
                            + "\n\n".join(context_lines)
                        ),
                    },
                ],
            )
            content = completion.choices[0].message.content or "{}"
            parsed = json.loads(content)
        except Exception:
            return []

        raw_questions = parsed.get("questions") if isinstance(parsed, dict) else None
        if not isinstance(raw_questions, list):
            return []

        built: list[QuizItem] = []
        for item in raw_questions:
            if not isinstance(item, dict):
                continue
            question = str(item.get("question") or "").strip()
            options = item.get("options")
            correct_answer = item.get("correct_answer")
            explanation = str(item.get("explanation") or "").strip()
            source_rank = item.get("source_rank")

            if not question or not isinstance(options, list) or len(options) != 4:
                continue
            if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
                continue

            source: SourceCitation | None = None
            if isinstance(source_rank, int) and 1 <= source_rank <= len(candidates):
                source = self._source_from_candidate(candidates[source_rank - 1])

            built.append(
                QuizItem(
                    question=self._truncate(question, request.question_max_chars),
                    options=[str(opt) for opt in options],
                    correct_answer=correct_answer,
                    explanation=self._truncate(explanation or "Grounded answer based on retrieved context.", request.explanation_max_chars),
                    source=source,
                )
            )
            if len(built) >= request.count:
                break

        return built[: request.count]

    def generate_summary(self, *, user_id: str, request: GenerateSummaryRequest) -> GenerateSummaryResponse:
        document = self._repository.get_document(user_id=user_id, document_id=request.scope_id)
        summary = ""
        if document:
            summary = str(document.get("content_text") or "")

        if not summary:
            rows = self._repository.list_chunks_for_scope(
                user_id=user_id,
                scope="document",
                scope_id=request.scope_id,
                limit=10,
            )
            joined = "\n".join(str(item.get("content") or "") for item in rows)
            summary = joined[:2200]

        if not summary:
            summary = "No summary available yet for this scope."

        response = GenerateSummaryResponse(scope_id=request.scope_id, summary=summary)

        self._repository.save_generated(
            user_id=user_id,
            scope="summary",
            scope_id=request.scope_id,
            content_type="summary",
            content_json=response.model_dump(mode="json"),
        )

        return response

    def get_history(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> GeneratedHistoryResponse:
        rows = self._repository.list_generated(user_id=user_id, scope=scope, scope_id=scope_id, limit=limit)
        items = [self._row_to_history_item(row, default_scope=scope, default_scope_id=scope_id) for row in rows]

        return GeneratedHistoryResponse(items=items)

    def get_generated_group(self, *, user_id: str, generated_id: str) -> GeneratedGroupResponse:
        row = self._repository.get_generated(user_id=user_id, generated_id=generated_id)
        if not row:
            raise AppError(error="generated_group_not_found", message="Generated group was not found.", status_code=404)
        item_scope = str(row.get("scope") or "subject")
        item_scope_id = str(row.get("scope_id") or "")
        return GeneratedGroupResponse(item=self._row_to_history_item(row, default_scope=item_scope, default_scope_id=item_scope_id))

    def update_generated_group(self, *, user_id: str, generated_id: str, request: UpdateGeneratedGroupRequest) -> GeneratedGroupResponse:
        row = self._repository.update_generated(user_id=user_id, generated_id=generated_id, content_json=request.content_json)
        if not row:
            raise AppError(error="generated_group_not_found", message="Generated group was not found.", status_code=404)
        item_scope = str(row.get("scope") or "subject")
        item_scope_id = str(row.get("scope_id") or "")
        return GeneratedGroupResponse(item=self._row_to_history_item(row, default_scope=item_scope, default_scope_id=item_scope_id))

    def delete_generated_group(self, *, user_id: str, generated_id: str) -> DeleteGeneratedGroupResponse:
        ok = self._repository.delete_generated(user_id=user_id, generated_id=generated_id)
        if not ok:
            raise AppError(error="generated_group_not_found", message="Generated group was not found.", status_code=404)
        return DeleteGeneratedGroupResponse(ok=True, id=generated_id)

    def _row_to_history_item(self, row: dict[str, Any], *, default_scope: str, default_scope_id: str) -> GeneratedHistoryItem:
        item_scope = str(row.get("scope") or default_scope)
        item_scope_id = str(row.get("scope_id") or default_scope_id)
        return GeneratedHistoryItem(
            id=str(row.get("id")),
            user_id=str(row.get("user_id")),
            scope=item_scope,
            type=str(row.get("content_type") or row.get("type") or "unknown"),
            created_at=row.get("created_at"),
            subject_id=item_scope_id if item_scope == "subject" else None,
            document_id=item_scope_id if item_scope in {"document", "summary"} else None,
            chapter_id=item_scope_id if item_scope == "chapter" else None,
            content_json=row.get("content_json") or {},
        )

    def _sources_from_candidates(self, candidates: list[dict[str, Any]]) -> list[SourceCitation]:
        return [
            self._source_from_candidate(item)
            for item in candidates[:3]
        ]

    def _source_from_candidate(self, item: dict[str, Any]) -> SourceCitation:
        return SourceCitation(
            document_type=item.get("document_type"),
            page=item.get("page"),
            chapter_name=item.get("chapter_name"),
            preview=item.get("preview"),
        )

    def _build_diagnostics(
        self,
        *,
        scope: str,
        scope_id: str,
        query: str,
        candidates: list[dict[str, Any]],
    ) -> RetrievalDiagnostics:
        accepted = [item for item in candidates if float(item.get("score", 0.0)) > 0.0]
        best = max((float(item.get("score", 0.0)) for item in candidates), default=0.0)
        return RetrievalDiagnostics(
            scope=scope,
            scope_id=scope_id,
            query=query,
            total_candidates=len(candidates),
            accepted_candidates=len(accepted),
            best_score=best,
        )

    def _truncate(self, text: str, limit: int | None) -> str:
        if not limit or limit <= 0:
            return text
        return text[:limit]
