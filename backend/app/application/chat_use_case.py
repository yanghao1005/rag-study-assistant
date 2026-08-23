"""RAG chat use case."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.application.retrieval_policy import (
    build_index_context,
    classify_query,
    documents_for_chapter,
    enrich_citations,
    format_context_blocks,
    is_broad_query,
    maybe_expand_agentic,
    merge_with_opening_chunks,
    search_query_for_intent,
    sort_course_documents,
    system_prompt_for_intent,
)
from app.core.errors import AppError
from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.document import DocumentChunk
from app.domain.entities.enums import ChatRole
from app.ports.llm import ChatCompletionMessage, EmbeddingPort, LLMPort
from app.ports.repositories import ChatRepositoryPort, DocumentRepositoryPort, SubjectRepositoryPort
from app.ports.retrieval import RetrievalFilters, VectorSearchPort


class ChatUseCase:
    def __init__(
        self,
        *,
        subjects: SubjectRepositoryPort,
        chat: ChatRepositoryPort,
        documents: DocumentRepositoryPort,
        retrieval: VectorSearchPort,
        embeddings: EmbeddingPort,
        llm: LLMPort,
        enable_hierarchical_rag: bool = True,
        enable_agentic_rag: bool = False,
    ) -> None:
        self._subjects = subjects
        self._chat = chat
        self._documents = documents
        self._retrieval = retrieval
        self._embeddings = embeddings
        self._llm = llm
        self._enable_hierarchical_rag = enable_hierarchical_rag
        self._enable_agentic_rag = enable_agentic_rag

    async def _prepare(
        self,
        *,
        user_id: str,
        subject_id: str,
        question: str,
        thread_id: str | None,
        document_id: str | None,
        document_ids: list[str] | None,
        save: bool,
        mode: str = "standard",
    ) -> tuple[ChatThread | None, list[dict[str, object]], list[ChatCompletionMessage]]:
        subject = await self._subjects.get(user_id=user_id, subject_id=subject_id)
        if subject is None:
            raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")

        thread: ChatThread | None = None
        if thread_id:
            thread = await self._chat.get_thread(user_id=user_id, thread_id=thread_id)
            if thread is None:
                raise AppError(
                    status_code=404,
                    error="thread_not_found",
                    message="Chat thread not found.",
                )
        elif save:
            thread = await self._chat.create_thread(
                ChatThread(
                    id=str(uuid4()),
                    user_id=user_id,
                    subject_id=subject_id,
                    title=question[:80] or "New chat",
                )
            )

        docs = await self._documents.list_for_subject(user_id=user_id, subject_id=subject_id)
        intent = classify_query(question)
        filters = RetrievalFilters(
            user_id=user_id,
            subject_id=subject_id,
            document_id=document_id,
            document_ids=tuple(document_ids or ()),
        )
        scoped = set(filters.resolved_document_ids())
        if scoped:
            docs = [item for item in docs if item.id in scoped]
        elif (
            intent.kind == "chapter"
            and intent.chapter_number is not None
            and not scoped
        ):
            numbered = documents_for_chapter(docs, intent.chapter_number)
            if numbered:
                docs = numbered
                filters = RetrievalFilters(
                    user_id=user_id,
                    subject_id=subject_id,
                    document_ids=tuple(item.id for item in numbered),
                )
        docs = sort_course_documents(docs)

        search_text = search_query_for_intent(
            question, subject_name=subject.name, intent=intent
        )
        query_embedding = (await self._embeddings.embed([search_text]))[0]
        result = await self._retrieval.hybrid_search(
            query_text=search_text,
            query_embedding=query_embedding,
            filters=filters,
        )
        agentic_used = self._enable_agentic_rag and mode == "agentic"
        if agentic_used and intent.kind == "factual":
            result = await maybe_expand_agentic(
                question=question,
                first=result,
                llm=self._llm,
                embeddings=self._embeddings,
                retrieval=self._retrieval,
                filters=filters,
            )
        if intent.kind in {"summary", "chapter"}:
            openings = await self._opening_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_ids=[item.id for item in docs],
                per_document=2 if intent.kind == "summary" else 4,
            )
            result = merge_with_opening_chunks(
                result,
                openings,
                per_document=2 if intent.kind == "summary" else 6,
                limit=12 if intent.kind == "summary" else 8,
            )

        citations = enrich_citations(result.chunks, docs)
        context = format_context_blocks(result.chunks, docs)
        index_block = ""
        if self._enable_hierarchical_rag:
            retrieved_ids = {chunk.document_id for chunk in result.chunks}
            index_block = build_index_context(
                docs,
                retrieved_ids=retrieved_ids,
                include_all=(
                    intent.kind == "summary"
                    or is_broad_query(question)
                    or not retrieved_ids
                ),
            )
        system = system_prompt_for_intent(intent)
        user_content = (
            f"{index_block}\n\nContext:\n{context}\n\nQuestion: {question}"
            if index_block
            else f"Context:\n{context}\n\nQuestion: {question}"
        )
        messages = [
            ChatCompletionMessage(role="system", content=system),
            ChatCompletionMessage(role="user", content=user_content),
        ]
        return thread, citations, messages

    async def _opening_chunks(
        self,
        *,
        user_id: str,
        subject_id: str,
        document_ids: list[str],
        per_document: int,
    ) -> list[DocumentChunk]:
        if not document_ids:
            return []

        async def load(document_id: str) -> list[DocumentChunk]:
            return await self._documents.list_chunks(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
                limit=per_document,
            )

        parts = await asyncio.gather(*[load(doc_id) for doc_id in document_ids])
        chunks = []
        for part in parts:
            chunks.extend(part)
        return chunks

    async def ask(
        self,
        *,
        user_id: str,
        subject_id: str,
        question: str,
        thread_id: str | None = None,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        save: bool = True,
        mode: str = "standard",
    ) -> dict[str, object]:
        thread, citations, messages = await self._prepare(
            user_id=user_id,
            subject_id=subject_id,
            question=question,
            thread_id=thread_id,
            document_id=document_id,
            document_ids=document_ids,
            save=save,
            mode=mode,
        )
        completion = await self._llm.complete(messages=messages)

        if save and thread is not None:
            await self._persist(
                user_id=user_id,
                thread_id=thread.id,
                question=question,
                answer=completion.content,
                citations=citations,
                model=completion.model,
                usage=completion.usage,
            )

        return {
            "answer": completion.content,
            "citations": citations,
            "thread_id": thread.id if thread else None,
            "model": completion.model,
            "usage": completion.usage,
        }

    async def ask_stream(
        self,
        *,
        user_id: str,
        subject_id: str,
        question: str,
        thread_id: str | None = None,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        save: bool = True,
        mode: str = "standard",
    ) -> AsyncIterator[dict[str, Any]]:
        thread, citations, messages = await self._prepare(
            user_id=user_id,
            subject_id=subject_id,
            question=question,
            thread_id=thread_id,
            document_id=document_id,
            document_ids=document_ids,
            save=save,
            mode=mode,
        )
        yield {
            "type": "meta",
            "thread_id": thread.id if thread else None,
            "citations": citations,
        }

        parts: list[str] = []
        async for token in self._llm.stream(messages=messages):
            parts.append(token)
            yield {"type": "token", "content": token}

        answer = "".join(parts)
        if save and thread is not None:
            await self._persist(
                user_id=user_id,
                thread_id=thread.id,
                question=question,
                answer=answer,
                citations=citations,
                model=None,
                usage={},
            )
        yield {"type": "done", "answer": answer, "thread_id": thread.id if thread else None}

    async def _persist(
        self,
        *,
        user_id: str,
        thread_id: str,
        question: str,
        answer: str,
        citations: list[dict[str, object]],
        model: str | None,
        usage: dict[str, int],
    ) -> None:
        await self._chat.add_message(
            ChatMessage(
                id=str(uuid4()),
                user_id=user_id,
                thread_id=thread_id,
                role=ChatRole.USER,
                content=question,
            )
        )
        await self._chat.add_message(
            ChatMessage(
                id=str(uuid4()),
                user_id=user_id,
                thread_id=thread_id,
                role=ChatRole.ASSISTANT,
                content=answer,
                citations=citations,
                model=model,
                token_usage=usage,
            )
        )

    async def list_threads(self, *, user_id: str, subject_id: str) -> list[dict[str, object]]:
        subject = await self._subjects.get(user_id=user_id, subject_id=subject_id)
        if subject is None:
            raise AppError(status_code=404, error="subject_not_found", message="Subject not found.")
        threads = await self._chat.list_threads(user_id=user_id, subject_id=subject_id)
        return [
            {
                "id": t.id,
                "title": t.title,
                "subject_id": t.subject_id,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in threads
        ]

    async def list_messages(self, *, user_id: str, thread_id: str) -> list[dict[str, object]]:
        thread = await self._chat.get_thread(user_id=user_id, thread_id=thread_id)
        if thread is None:
            raise AppError(
                status_code=404,
                error="thread_not_found",
                message="Chat thread not found.",
            )
        messages = await self._chat.list_messages(user_id=user_id, thread_id=thread_id)
        return [
            {
                "id": m.id,
                "role": m.role.value,
                "content": m.content,
                "citations": m.citations,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]


def sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"
