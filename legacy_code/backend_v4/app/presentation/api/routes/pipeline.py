from typing import Any

from fastapi import APIRouter, Request

from app.container import get_pipeline_runner
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.domain.models.contracts import PipelineRunRequest

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(request: PipelineRunRequest, http_request: Request) -> dict[str, Any]:
    settings = get_settings()
    if not settings.enable_debug_endpoints:
        raise AppError(
            error="debug_endpoint_disabled",
            message="Pipeline debug endpoint is disabled",
            status_code=403,
        )

    try:
        result = get_pipeline_runner().run(request.model_dump(by_alias=True))
    except ValueError as exc:
        raise AppError(error="invalid_pipeline_request", message=str(exc), status_code=422) from exc

    result["request_id"] = getattr(http_request.state, "request_id", None)
    return result
