"""Generation routes (flashcards / quiz)."""

from __future__ import annotations

from fastapi import APIRouter

from app.application.generation_use_case import GenerationUseCase
from app.core.errors import AppError
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import GenerateFlashcardsRequest, GenerateQuizRequest

router = APIRouter(prefix="/generate", tags=["generate"])


def _generation_use_case(container: ContainerDep) -> GenerationUseCase:
    return GenerationUseCase(
        subjects=container.subjects,
        documents=container.documents,
        study=container.study,
        retrieval=container.retrieval,
        embeddings=container.embeddings,
        llm=container.llm,
    )


@router.post("/flashcards")
async def generate_flashcards(
    body: GenerateFlashcardsRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _generation_use_case(container).generate_flashcards(
        user_id=user.id,
        subject_id=body.subject_id,
        count=body.count,
        query=body.query,
        document_id=body.document_id,
        save=body.save,
    )


@router.post("/quiz")
async def generate_quiz(
    body: GenerateQuizRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _generation_use_case(container).generate_quiz(
        user_id=user.id,
        subject_id=body.subject_id,
        count=body.count,
        query=body.query,
        document_id=body.document_id,
        difficulty=body.difficulty,
        save=body.save,
    )


@router.get("/artifacts")
async def list_artifacts(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str,
    artifact_type: str | None = None,
) -> dict[str, object]:
    items = await container.study.list_artifacts(
        user_id=user.id,
        subject_id=subject_id,
        artifact_type=artifact_type,
    )
    return {
        "items": [
            {
                "id": a.id,
                "artifact_type": a.artifact_type.value,
                "title": a.title,
                "status": a.status.value,
                "subject_id": a.subject_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ]
    }


@router.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    artifact = await container.study.get_artifact(user_id=user.id, artifact_id=artifact_id)
    if artifact is None:
        raise AppError(status_code=404, error="artifact_not_found", message="Artifact not found.")

    payload: dict[str, object] = {
        "id": artifact.id,
        "artifact_type": artifact.artifact_type.value,
        "title": artifact.title,
        "status": artifact.status.value,
        "subject_id": artifact.subject_id,
        "content_json": artifact.content_json,
    }
    if artifact.artifact_type.value == "flashcard_deck":
        cards = await container.study.list_flashcards(user_id=user.id, artifact_id=artifact_id)
        payload["cards"] = [
            {"id": c.id, "front": c.front, "back": c.back, "hint": c.hint} for c in cards
        ]
    elif artifact.artifact_type.value == "quiz":
        questions = await container.study.list_quiz_questions(
            user_id=user.id, artifact_id=artifact_id
        )
        payload["questions"] = [
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "correct_option_index": q.correct_option_index,
                "explanation": q.explanation,
            }
            for q in questions
        ]
    return payload
