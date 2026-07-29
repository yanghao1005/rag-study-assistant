"""Chat RAG routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.application.chat_use_case import ChatUseCase
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import ChatAskRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask")
async def ask_chat(
    body: ChatAskRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    use_case = ChatUseCase(
        subjects=container.subjects,
        chat=container.chat,
        retrieval=container.retrieval,
        embeddings=container.embeddings,
        llm=container.llm,
    )
    return await use_case.ask(
        user_id=user.id,
        subject_id=body.subject_id,
        question=body.question,
        thread_id=body.thread_id,
        document_id=body.document_id,
        save=body.save,
    )
