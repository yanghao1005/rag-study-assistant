from fastapi import APIRouter, Depends
from fastapi import Query

from app.container import get_generation_use_case
from app.core.auth import AuthUser
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.generation import (
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    GeneratedHistoryResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    ScopeLiteral,
)

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/flashcards", response_model=GenerateFlashcardsResponse)
def generate_flashcards(
    request: GenerateFlashcardsRequest,
    user: AuthUser = Depends(get_current_user),
) -> GenerateFlashcardsResponse:
    return get_generation_use_case().generate_flashcards(user_id=user.user_id, request=request)


@router.post("/quiz", response_model=GenerateQuizResponse)
def generate_quiz(
    request: GenerateQuizRequest,
    user: AuthUser = Depends(get_current_user),
) -> GenerateQuizResponse:
    return get_generation_use_case().generate_quiz(user_id=user.user_id, request=request)


@router.post("/summary", response_model=GenerateSummaryResponse)
def generate_summary(
    request: GenerateSummaryRequest,
    user: AuthUser = Depends(get_current_user),
) -> GenerateSummaryResponse:
    return get_generation_use_case().generate_summary(user_id=user.user_id, request=request)


@router.get("/history", response_model=GeneratedHistoryResponse)
def generate_history(
    user_id: str | None = Query(default=None),
    scope: ScopeLiteral = Query(...),
    scope_id: str = Query(...),
    limit: int = Query(8, ge=1, le=100),
    user: AuthUser = Depends(get_current_user),
) -> GeneratedHistoryResponse:
    _ = user_id
    return get_generation_use_case().get_history(user_id=user.user_id, scope=scope, scope_id=scope_id, limit=limit)
