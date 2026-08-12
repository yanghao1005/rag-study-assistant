"""RAG chat use case."""

from __future__ import annotations

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
        context_blocks = []
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

        completion = await self._llm.complete(
            messages=[
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
        )

        if save and thread is not None:
            await self._chat.add_message(
                ChatMessage(
                    id=str(uuid4()),
                    user_id=user_id,
                    thread_id=thread.id,
                    role=ChatRole.USER,
                    content=question,
                )
            )
            await self._chat.add_message(
                ChatMessage(
                    id=str(uuid4()),
                    user_id=user_id,
                    thread_id=thread.id,
                    role=ChatRole.ASSISTANT,
                    content=completion.content,
                    citations=citations,
                    model=completion.model,
                    token_usage=completion.usage,
                )
            )

        return {
            "answer": completion.content,
            "citations": citations,
            "thread_id": thread.id if thread else None,
            "model": completion.model,
            "usage": completion.usage,
        }
