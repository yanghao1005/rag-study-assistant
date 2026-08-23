"""Spaced-repetition planner routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.application.planner_use_case import PlannerUseCase
from app.entrypoints.api.deps import ContainerDep, CurrentUserDep
from app.entrypoints.api.schemas import ReviewRequest

router = APIRouter(prefix="/planner", tags=["planner"])


def _use_case(container: ContainerDep) -> PlannerUseCase:
    return PlannerUseCase(subjects=container.subjects, study=container.study)


@router.get("/due")
async def list_due(
    user: CurrentUserDep,
    container: ContainerDep,
    subject_id: str = Query(...),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict[str, object]:
    items = await _use_case(container).due(user_id=user.id, subject_id=subject_id, limit=limit)
    return {"items": items}


@router.post("/review")
async def review_card(
    body: ReviewRequest,
    user: CurrentUserDep,
    container: ContainerDep,
) -> dict[str, object]:
    return await _use_case(container).review(
        user_id=user.id,
        flashcard_id=body.flashcard_id,
        quality=body.quality,
    )
