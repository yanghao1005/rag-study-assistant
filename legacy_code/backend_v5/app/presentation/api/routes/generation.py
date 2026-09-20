from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Query

from app.container import get_generation_use_case
from app.core.auth import AuthUser
from app.core.errors import AppError
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.generation import (
    DeleteGeneratedGroupResponse,
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    GeneratedGroupResponse,
    GeneratedHistoryResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    ScopeLiteral,
    UpdateGeneratedGroupRequest,
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
    if scope in {"document", "summary", "subject"}:
        try:
            UUID(scope_id)
        except ValueError as exc:
            raise AppError(error="invalid_scope_id", message=f"scope_id must be a valid UUID for scope '{scope}'", status_code=422) from exc
    return get_generation_use_case().get_history(user_id=user.user_id, scope=scope, scope_id=scope_id, limit=limit)


@router.get("/groups/{group_id}", response_model=GeneratedGroupResponse)
def get_generated_group(
    group_id: str,
    user: AuthUser = Depends(get_current_user),
) -> GeneratedGroupResponse:
    return get_generation_use_case().get_generated_group(user_id=user.user_id, generated_id=group_id)


@router.patch("/groups/{group_id}", response_model=GeneratedGroupResponse)
def update_generated_group(
    group_id: str,
    request: UpdateGeneratedGroupRequest,
    user: AuthUser = Depends(get_current_user),
) -> GeneratedGroupResponse:
    return get_generation_use_case().update_generated_group(user_id=user.user_id, generated_id=group_id, request=request)


@router.delete("/groups/{group_id}", response_model=DeleteGeneratedGroupResponse)
def delete_generated_group(
    group_id: str,
    user: AuthUser = Depends(get_current_user),
) -> DeleteGeneratedGroupResponse:
    return get_generation_use_case().delete_generated_group(user_id=user.user_id, generated_id=group_id)
