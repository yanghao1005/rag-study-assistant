import json
from typing import Any, List, Tuple

from pydantic import ValidationError

from app.core.config import get_settings
from app.core.debug_artifacts import persist_debug_artifact
from app.core.dependencies import get_vector_repository
from app.core.exceptions import AppError
from app.domain.generation import (
    ContextScore,
    FlashcardItem,
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    GeneratedHistoryItem,
    GeneratedHistoryResponse,
    PromptProfile,
    QuizQuestion,
    RetrievalDiagnostics,
    ScopeType,
    SourceCitation,
)


class GenerationService:
    def _flashcard_profile_instructions(self, profile: PromptProfile) -> str:
        if profile == PromptProfile.EXAM:
            return "Focus on exam-relevant facts, definitions, and distinctions."
        if profile == PromptProfile.CONCEPTUAL:
            return "Focus on concepts, relationships, and why/how understanding."
        return "Keep cards concise and practical for fast revision."

    def _quiz_profile_instructions(self, profile: PromptProfile) -> str:
        if profile == PromptProfile.EXAM:
            return "Prioritize exam-style discriminative questions with plausible distractors."
        if profile == PromptProfile.CONCEPTUAL:
            return "Prioritize conceptual understanding and reasoning over memorization."
        return "Keep questions clear, short, and directly grounded in context."

    @staticmethod
    def _truncate_text(value: str, max_chars: int) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[: max_chars - 1].rstrip() + "…"
    def _attach_debug_trace(
        self,
        diagnostics: RetrievalDiagnostics,
        payload: dict[str, Any],
        enable_debug: bool,
        request_id: str | None,
    ) -> RetrievalDiagnostics:
        if not (enable_debug or self.settings.debug):
            return diagnostics

        trace_id = request_id or diagnostics.debug_trace_id
        final_trace_id, artifact_path = persist_debug_artifact("generation", payload, trace_id=trace_id)
        diagnostics.debug_trace_id = final_trace_id
        diagnostics.debug_artifact_path = artifact_path
        return diagnostics

    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository = get_vector_repository()

    def _retrieve_scope_context(self, scope: ScopeType, scope_id: str, query: str) -> Tuple[List[dict[str, Any]], RetrievalDiagnostics]:
        rows = self.repository.retrieve(query=query, top_k=self.settings.top_k, scope=scope.value, scope_id=scope_id)
        if not rows:
            raise AppError(
                error="insufficient_context",
                message="Insufficient context for topic",
                details={"scope": scope.value, "scope_id": scope_id},
                status_code=400,
            )
        query_tokens = {token.lower() for token in query.split() if token.strip()}
        context_scores: List[ContextScore] = []
        if not query_tokens:
            for row in rows:
                metadata = row.get("metadata", {})
                threshold = self._score_threshold(row)
                context_scores.append(
                    ContextScore(
                        document_type=metadata.get("document_type"),
                        page=metadata.get("page"),
                        chapter_name=metadata.get("chapter_name"),
                        score=1.0,
                        threshold=threshold,
                        accepted=True,
                    )
                )
            diagnostics = RetrievalDiagnostics(
                scope=scope,
                scope_id=scope_id,
                query=query,
                total_candidates=len(rows),
                accepted_candidates=len(rows),
                best_score=1.0,
                context_scores=context_scores,
            )
            return rows, diagnostics

        filtered_rows: List[dict[str, Any]] = []
        best_score = 0.0
        for row in rows:
            score = self._row_relevance_score(row, query_tokens)
            best_score = max(best_score, score)
            threshold = self._score_threshold(row)
            accepted = score >= threshold
            metadata = row.get("metadata", {})
            context_scores.append(
                ContextScore(
                    document_type=metadata.get("document_type"),
                    page=metadata.get("page"),
                    chapter_name=metadata.get("chapter_name"),
                    score=round(score, 4),
                    threshold=threshold,
                    accepted=accepted,
                )
            )
            if accepted:
                filtered_rows.append(row)

        if not filtered_rows:
            raise AppError(
                error="insufficient_context",
                message="Insufficient context for topic",
                details={
                    "scope": scope.value,
                    "scope_id": scope_id,
                    "best_score": round(best_score, 4),
                    "context_scores": [score.model_dump() for score in context_scores],
                },
                status_code=400,
            )
        diagnostics = RetrievalDiagnostics(
            scope=scope,
            scope_id=scope_id,
            query=query,
            total_candidates=len(rows),
            accepted_candidates=len(filtered_rows),
            best_score=round(best_score, 4),
            context_scores=context_scores,
        )
        return filtered_rows, diagnostics

    def _score_threshold(self, row: dict[str, Any]) -> float:
        metadata = row.get("metadata", {})
        document_type = metadata.get("document_type", "pdf")
        if document_type == "summary":
            return self.settings.similarity_threshold_summary
        return self.settings.similarity_threshold_pdf

    def _row_relevance_score(self, row: dict[str, Any], query_tokens: set[str]) -> float:
        existing = row.get("_score")
        if isinstance(existing, (int, float)):
            return float(existing)

        content = row.get("content", "").lower()
        if not content:
            return 0.0
        matches = sum(1 for token in query_tokens if token in content)
        return matches / max(1, len(query_tokens))

    def _parse_json(self, raw_text: str) -> Any:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        return json.loads(cleaned)

    def _call_llm(self, prompt: str, schema_name: str, schema: dict[str, Any]) -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")

        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response_schema = schema
        if schema.get("type") == "array":
            response_schema = {
                "type": "object",
                "additionalProperties": False,
                "properties": {"items": schema},
                "required": ["items"],
            }
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": response_schema,
                    "strict": True,
                },
            },
        )
        return response.choices[0].message.content or ""

    def _normalize_parsed_output(self, parsed: Any, schema: dict[str, Any]) -> Any:
        if schema.get("type") == "array":
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                return parsed["items"]
        return parsed

    def _generate_with_retry(self, prompt: str, schema_name: str, schema: dict[str, Any]) -> Any:
        attempts = [
            prompt,
            f"{prompt}\n\nIMPORTANT: return strict JSON only and follow schema exactly.",
        ]
        last_error = ""
        for attempt_prompt in attempts:
            try:
                raw = self._call_llm(attempt_prompt, schema_name=schema_name, schema=schema)
                parsed = self._parse_json(raw)
                return self._normalize_parsed_output(parsed, schema)
            except Exception as exc:
                last_error = str(exc)
                continue
        raise AppError(
            error="invalid_generation_output",
            message="LLM returned invalid JSON after one retry",
            details={"error": last_error},
            status_code=502,
        )

    def _sources_from_rows(self, rows: List[dict[str, Any]]) -> List[SourceCitation]:
        sources: List[SourceCitation] = []
        for row in rows:
            metadata = row.get("metadata", {})
            sources.append(
                SourceCitation(
                    document_type=metadata.get("document_type"),
                    page=metadata.get("page"),
                    chapter_name=metadata.get("chapter_name"),
                    preview=row.get("content", "")[:180],
                )
            )
        return sources

    def _resolve_summary_for_scope(self, scope: ScopeType, scope_id: str, rows: List[dict[str, Any]]) -> str | None:
        if scope in {ScopeType.DOCUMENT, ScopeType.SUMMARY}:
            return self.repository.get_document_summary(document_id=scope_id)

        candidate_document_ids = {row.get("document_id") for row in rows if row.get("document_id")}
        if len(candidate_document_ids) == 1:
            return self.repository.get_document_summary(document_id=next(iter(candidate_document_ids)))
        return None

    def _compose_context(self, rows: List[dict[str, Any]], summary_text: str | None) -> str:
        chunk_context = "\n\n".join(row.get("content", "") for row in rows)
        if summary_text:
            return f"Document Summary:\n{summary_text}\n\nRetrieved Chunks:\n{chunk_context}".strip()
        return chunk_context

    def _resolve_user_id(self, explicit_user_id: str | None, rows: List[dict[str, Any]]) -> str | None:
        if explicit_user_id:
            return explicit_user_id
        user_ids = {row.get("user_id") for row in rows if row.get("user_id")}
        if len(user_ids) == 1:
            return next(iter(user_ids))
        return None

    def _persist_generated_result(
        self,
        *,
        save: bool,
        user_id: str | None,
        scope: ScopeType,
        scope_id: str,
        generated_type: str,
        content_json: dict[str, Any],
    ) -> None:
        if not save or not user_id:
            return
        self.repository.persist_generated_content(
            user_id=user_id,
            scope=scope.value,
            scope_id=scope_id,
            generated_type=generated_type,
            content_json=content_json,
        )

    def generate_flashcards(
        self, payload: GenerateFlashcardsRequest, request_id: str | None = None
    ) -> GenerateFlashcardsResponse:
        query = (payload.query or "").strip()
        rows, diagnostics = self._retrieve_scope_context(payload.scope, payload.scope_id, query)
        summary_text = self._resolve_summary_for_scope(payload.scope, payload.scope_id, rows)
        context = self._compose_context(rows, summary_text)

        focus_clause = (
            f"Focus on this topic: {query}. "
            if query
            else "Select the most important concepts from the provided context. "
        )

        prompt = (
            f"Context:\n{context}\n\n"
            f"Generate exactly {payload.count} flashcards from this context. "
            f"{focus_clause}"
            f"{self._flashcard_profile_instructions(payload.prompt_profile)} "
            f"Use front <= {payload.front_max_chars} chars and back <= {payload.back_max_chars} chars. "
            "Return a JSON array of objects with keys: front, back."
        )

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "front": {"type": "string"},
                    "back": {"type": "string"},
                },
                "required": ["front", "back"],
            },
        }

        if self.settings.openai_api_key:
            parsed = self._generate_with_retry(prompt, schema_name="flashcards", schema=schema)
        else:
            parsed = []
            if summary_text:
                parsed.append({"front": "Document Summary", "back": summary_text[:180]})
            for index, row in enumerate(rows[: payload.count]):
                if len(parsed) >= payload.count:
                    break
                parsed.append(
                    {
                        "front": f"Concept {index + 1}",
                        "back": row.get("content", "")[:180],
                    }
                )

        try:
            flashcards = [
                FlashcardItem.model_validate(
                    {
                        "front": self._truncate_text(str(item.get("front", "")), payload.front_max_chars),
                        "back": self._truncate_text(str(item.get("back", "")), payload.back_max_chars),
                    }
                )
                for item in parsed
            ]
        except (ValidationError, TypeError, ValueError) as exc:
            raise AppError("invalid_generation_output", "Invalid flashcard JSON output", {"error": str(exc)}) from exc

        diagnostics = self._attach_debug_trace(
            diagnostics,
            payload={
                "request_id": request_id,
                "type": "flashcards",
                "scope": payload.scope.value,
                "scope_id": payload.scope_id,
                "query": query or "[auto]",
                "diagnostics": diagnostics.model_dump(),
            },
            enable_debug=payload.debug,
            request_id=request_id,
        )

        resolved_user_id = self._resolve_user_id(payload.user_id, rows)
        self._persist_generated_result(
            save=payload.save,
            user_id=resolved_user_id,
            scope=payload.scope,
            scope_id=payload.scope_id,
            generated_type="flashcard",
            content_json={
                "flashcards": [item.model_dump() for item in flashcards[: payload.count]],
                "sources": [source.model_dump() for source in self._sources_from_rows(rows)],
            },
        )

        return GenerateFlashcardsResponse(
            flashcards=flashcards[: payload.count],
            sources=self._sources_from_rows(rows),
            diagnostics=diagnostics,
        )

    def generate_quiz(self, payload: GenerateQuizRequest, request_id: str | None = None) -> GenerateQuizResponse:
        query = (payload.query or "").strip()
        rows, diagnostics = self._retrieve_scope_context(payload.scope, payload.scope_id, query)
        summary_text = self._resolve_summary_for_scope(payload.scope, payload.scope_id, rows)
        context = self._compose_context(rows, summary_text)

        focus_clause = (
            f"Focus on this topic: {query}. "
            if query
            else "Select the most important concepts from the provided context. "
        )

        prompt = (
            f"Context:\n{context}\n\n"
            f"Generate exactly {payload.count} quiz questions with difficulty {payload.difficulty}. "
            f"{focus_clause}"
            f"{self._quiz_profile_instructions(payload.prompt_profile)} "
            f"Use question <= {payload.question_max_chars} chars and explanation <= {payload.explanation_max_chars} chars. "
            "Return JSON array with keys: question, options(4), correct_answer(0-3), explanation."
        )

        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 4,
                        "maxItems": 4,
                    },
                    "correct_answer": {"type": "integer", "minimum": 0, "maximum": 3},
                    "explanation": {"type": "string"},
                },
                "required": ["question", "options", "correct_answer", "explanation"],
            },
        }

        if self.settings.openai_api_key:
            parsed = self._generate_with_retry(prompt, schema_name="quiz", schema=schema)
        else:
            parsed = []
            if summary_text and payload.count > 0:
                parsed.append(
                    {
                        "question": "According to the document summary, what is a key point?",
                        "options": [
                            summary_text[:60] or "Summary point",
                            "Distractor B",
                            "Distractor C",
                            "Distractor D",
                        ],
                        "correct_answer": 0,
                        "explanation": "The first option is grounded in the persisted document summary.",
                    }
                )
            for index, row in enumerate(rows[: payload.count]):
                if len(parsed) >= payload.count:
                    break
                parsed.append(
                    {
                        "question": f"Question {index + 1}: What does this text describe?",
                        "options": [
                            row.get("content", "")[:60] or "Option A",
                            "Distractor B",
                            "Distractor C",
                            "Distractor D",
                        ],
                        "correct_answer": 0,
                        "explanation": "The first option is directly grounded in retrieved context.",
                    }
                )

        questions: List[QuizQuestion] = []
        sources = self._sources_from_rows(rows)
        try:
            for index, item in enumerate(parsed):
                source = sources[index] if index < len(sources) else None
                question = QuizQuestion.model_validate(
                    {
                        **item,
                        "question": self._truncate_text(str(item.get("question", "")), payload.question_max_chars),
                        "explanation": self._truncate_text(
                            str(item.get("explanation", "")), payload.explanation_max_chars
                        ),
                        "source": source.model_dump() if source else None,
                    }
                )
                questions.append(question)
        except (ValidationError, TypeError, ValueError) as exc:
            raise AppError("invalid_generation_output", "Invalid quiz JSON output", {"error": str(exc)}) from exc

        diagnostics = self._attach_debug_trace(
            diagnostics,
            payload={
                "request_id": request_id,
                "type": "quiz",
                "scope": payload.scope.value,
                "scope_id": payload.scope_id,
                "query": query,
                "diagnostics": diagnostics.model_dump(),
            },
            enable_debug=payload.debug,
            request_id=request_id,
        )

        resolved_user_id = self._resolve_user_id(payload.user_id, rows)
        self._persist_generated_result(
            save=payload.save,
            user_id=resolved_user_id,
            scope=payload.scope,
            scope_id=payload.scope_id,
            generated_type="quiz",
            content_json={"questions": [question.model_dump() for question in questions[: payload.count]]},
        )

        return GenerateQuizResponse(questions=questions[: payload.count], diagnostics=diagnostics)

    def generate_summary(self, payload: GenerateSummaryRequest) -> GenerateSummaryResponse:
        summary = self.repository.get_document_summary(document_id=payload.scope_id, user_id=payload.user_id)
        if not summary:
            raise AppError(
                error="summary_not_found",
                message="No persisted document summary found",
                details={"scope": "summary", "scope_id": payload.scope_id},
                status_code=404,
            )
        return GenerateSummaryResponse(summary=summary, scope_id=payload.scope_id)

    def get_generated_history(
        self,
        *,
        user_id: str,
        scope: ScopeType,
        scope_id: str,
        limit: int = 20,
    ) -> GeneratedHistoryResponse:
        rows = self.repository.get_generated_history(
            user_id=user_id,
            scope=scope.value,
            scope_id=scope_id,
            limit=max(1, min(limit, 100)),
        )
        items = [GeneratedHistoryItem.model_validate(row) for row in rows]
        return GeneratedHistoryResponse(items=items)
