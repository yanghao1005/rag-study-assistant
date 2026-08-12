"""RAG chat use case."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from app.core.errors import AppError
from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.enums import ChatRole
from app.ports.llm import ChatCompletionMessage, EmbeddingPort, LLMPort
from app.ports.repositories import ChatRepositoryPort, SubjectRepositoryPort
from app.ports.retrieval import RetrievalFilters, VectorSearchPort


class ChatUseCase:
    def __init__(
        self,
        *,
        subjects: SubjectRepositoryPort,
        chat: ChatRepositoryPort,
        retrieval: VectorSearchPort,
        embeddings: EmbeddingPort,
        llm: LLMPort,
    ) -> None:
        self._subjects = subjects
        self._chat = chat
        self._retrieval = retrieval
        self._embeddings = embeddings
        self._llm = llm

    async def _prepare(
        self,
        *,
        user_id: str,
        subject_id: str,
        question: str,
        thread_id: str | None,
        document_id: str | None,
        save: bool,
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

        query_embedding = (await self._embeddings.embed([question]))[0]
        result = await self._retrieval.hybrid_search(
            query_text=question,
            query_embedding=query_embedding,
            filters=RetrievalFilters(
                user_id=user_id,
                subject_id=subject_id,
                document_id=document_id,
            ),
        )
        context_blocks: list[str] = []
        citations: list[dict[str, object]] = []
        for index, chunk in enumerate(result.chunks, start=1):
            context_blocks.append(f"[{index}] {chunk.content}")
            citations.append(
                {
                    "index": index,
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "page_start": chunk.page_start,
                    "score": chunk.score,
                }
            )
        context = "\n\n".join(context_blocks) if context_blocks else "No retrieved context."
        messages = [
            ChatCompletionMessage(
                role="system",
                content=(
                    "You are a study assistant. Answer using only the provided context. "
                    "If the context is insufficient, say so. Cite sources as [n]."
                ),
            ),
            ChatCompletionMessage(
                role="user",
                content=f"Context:\n{context}\n\nQuestion: {question}",
            ),
        ]
        return thread, citations, messages

    async def ask(
        self,
        *,
        user_id: str,
        subject_id: str,
        question: str,
        thread_id: str | None = None,
        document_id: str | None = None,
        save: bool = True,
    ) -> dict[str, object]:
        thread, citations, messages = await self._prepare(
            user_id=user_id,
            subject_id=subject_id,
            question=question,
            thread_id=thread_id,
            document_id=document_id,
            save=save,
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
        save: bool = True,
    ) -> AsyncIterator[dict[str, Any]]:
        thread, citations, messages = await self._prepare(
            user_id=user_id,
            subject_id=subject_id,
            question=question,
            thread_id=thread_id,
            document_id=document_id,
            save=save,
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

    async def list_messages(
        self, *, user_id: str, thread_id: str
    ) -> list[dict[str, object]]:
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
