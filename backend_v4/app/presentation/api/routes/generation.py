from typing import Any

from fastapi import APIRouter, Query

from app.container import get_generation_service
from app.domain.models.contracts import (
    GenerateFlashcardsRequest,
    GenerateQuizRequest,
    GenerateSummaryRequest,
    ScopeLiteral,
)

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/flashcards")
def generate_flashcards(request: GenerateFlashcardsRequest) -> dict[str, Any]:
    return get_generation_service().generate_flashcards(request.model_dump())


@router.post("/quiz")
def generate_quiz(request: GenerateQuizRequest) -> dict[str, Any]:
    return get_generation_service().generate_quiz(request.model_dump())


@router.post("/summary")
def generate_summary(request: GenerateSummaryRequest) -> dict[str, Any]:
    return get_generation_service().get_summary(scope_id=request.scope_id)


@router.get("/history")
def generate_history(
    user_id: str = Query(...),
    scope: ScopeLiteral = Query(...),
    scope_id: str = Query(...),
    limit: int = Query(8, ge=1, le=100),
) -> dict[str, Any]:
    return get_generation_service().get_history(user_id=user_id, scope=scope, scope_id=scope_id, limit=limit)
