from __future__ import annotations

import json

from app.application.services.retrieval_service import RetrievalService
from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.ports.repositories import StudyRepository
from app.presentation.api.schemas.chat import ChatAskRequest, ChatAskResponse
from app.presentation.api.schemas.generation import SourceCitation
from openai import OpenAI


class ChatUseCase:
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
                message="OpenAI LLM provider is required for chat answers.",
                status_code=503,
            )
        return self._llm_client

    def answer(self, *, user_id: str, request: ChatAskRequest) -> ChatAskResponse:
        llm_client = self._require_llm_client()
        candidates = self._retrieval.retrieve(
            user_id=user_id,
            scope=request.scope,
            scope_id=request.scope_id,
            query=request.question,
            limit=8,
        )
        if not candidates:
            raise AppError(
                error="no_context_available",
                message="No indexed context found for this scope. Upload and process documents first.",
                status_code=422,
            )

        context_lines = []
        for idx, item in enumerate(candidates[:8], start=1):
            context_lines.append(
                f"[{idx}] doc_type={item.get('document_type')} page={item.get('page')} chapter={item.get('chapter_name')}\\n{item.get('preview')}"
            )

        schema_hint = {
            "answer": "string",
            "confidence": 0.0,
            "source_ranks": [1, 2],
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
                            "You are a grounded study assistant. "
                            "Answer using only the provided context, return valid JSON, no markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Question: {request.question}\\n"
                            "Rules:\\n"
                            "- Keep answer concise and factual.\\n"
                            "- confidence must be a float between 0 and 1.\\n"
                            "- source_ranks must reference context block numbers used in the answer.\\n"
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
        except Exception as exc:
            raise AppError(
                error="llm_generation_failed",
                message="Chat generation failed while calling OpenAI.",
                status_code=502,
                details={"type": type(exc).__name__},
            ) from exc

        answer = str(parsed.get("answer") or "").strip() if isinstance(parsed, dict) else ""
        confidence = parsed.get("confidence") if isinstance(parsed, dict) else None
        source_ranks = parsed.get("source_ranks") if isinstance(parsed, dict) else None

        if not answer:
            raise AppError(
                error="llm_output_invalid",
                message="Chat response was empty.",
                status_code=502,
            )

        confidence_value = 0.0
        if isinstance(confidence, (int, float)):
            confidence_value = max(0.0, min(1.0, float(confidence)))

        citations: list[dict] = []
        if isinstance(source_ranks, list):
            for rank in source_ranks:
                if isinstance(rank, int) and 1 <= rank <= len(candidates):
                    source = self._source_from_candidate(candidates[rank - 1])
                    citations.append(source.model_dump(mode="json"))

        if not citations:
            citations = [self._source_from_candidate(item).model_dump(mode="json") for item in candidates[:3]]

        response = ChatAskResponse(
            answer=answer,
            confidence=confidence_value,
            citations=citations,
        )

        if request.save:
            self._repository.save_generated(
                user_id=user_id,
                scope=request.scope,
                scope_id=request.scope_id,
                content_type="chat_answer",
                content_json=response.model_dump(mode="json"),
            )

        return response

    def _source_from_candidate(self, item: dict) -> SourceCitation:
        return SourceCitation(
            document_type=item.get("document_type"),
            page=item.get("page"),
            chapter_name=item.get("chapter_name"),
            preview=item.get("preview"),
        )
