from fastapi import APIRouter, Request

from app.application.pipeline_runner import PipelineRunner
from app.domain.pipeline import PipelineRunRequest, PipelineRunResponse

router = APIRouter()
runner = PipelineRunner()


@router.post("/run", response_model=PipelineRunResponse)
def run_pipeline(payload: PipelineRunRequest, request: Request) -> PipelineRunResponse:
    request_id = getattr(request.state, "request_id", None)
    return runner.run(payload, request_id=request_id)
