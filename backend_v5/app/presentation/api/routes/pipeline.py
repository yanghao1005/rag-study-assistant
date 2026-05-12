from __future__ import annotations

from fastapi import APIRouter, Depends

from app.container import get_pipeline_use_case
from app.core.auth import AuthUser
from app.presentation.api.deps.auth import get_current_user
from app.presentation.api.schemas.pipeline import PipelineRunRequest

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(
    request: PipelineRunRequest,
    user: AuthUser = Depends(get_current_user),
) -> dict:
    payload = request.to_payload()
    if payload.get("from_stage") and not payload.get("from"):
        payload["from"] = payload["from_stage"]
    if payload.get("to_stage") and not payload.get("to"):
        payload["to"] = payload["to_stage"]

    return get_pipeline_use_case().run(user_id=user.user_id, payload=payload)
