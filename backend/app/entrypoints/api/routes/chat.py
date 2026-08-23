"""Chat RAG routes (sync ask + SSE stream + history)."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.application.chat_use_case import ChatUseCase, sse_event
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import ChatAskRequest

router = APIRouter(prefix="/chat", tags=["chat"])


def _use_case(container: ContainerDep) -> ChatUseCase:
    return ChatUseCase(
        subjects=container.subjects,
        chat=container.chat,
        documents=container.documents,
        retrieval=container.retrieval,
        embeddings=container.embeddings,
        llm=container.llm,
        enable_hierarchical_rag=container.settings.enable_hierarchical_rag,
        enable_agentic_rag=container.settings.enable_agentic_rag,
    )


@router.post("/ask")
async def ask_chat(
    body: ChatAskRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _use_case(container).ask(
        user_id=user.id,
        subject_id=body.subject_id,
        question=body.question,
        thread_id=body.thread_id,
        document_id=body.document_id,
        document_ids=body.document_ids,
        save=body.save,
        mode=body.mode,
    )


@router.post("/ask/stream")
async def ask_chat_stream(
    body: ChatAskRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> StreamingResponse:
    use_case = _use_case(container)

    async def event_source() -> AsyncIterator[str]:
        try:
            async for event in use_case.ask_stream(
                user_id=user.id,
                subject_id=body.subject_id,
                question=body.question,
                thread_id=body.thread_id,
                document_id=body.document_id,
                document_ids=body.document_ids,
                save=body.save,
                mode=body.mode,
            ):
                yield sse_event(event)
        except Exception as exc:  # noqa: BLE001
            yield sse_event({"type": "error", "message": str(exc)})

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/threads")
async def list_threads(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str = Query(...),
) -> dict[str, object]:
    items = await _use_case(container).list_threads(user_id=user.id, subject_id=subject_id)
    return {"items": items}


@router.get("/threads/{thread_id}/messages")
async def list_thread_messages(
    thread_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    items = await _use_case(container).list_messages(user_id=user.id, thread_id=thread_id)
    return {"items": items}
