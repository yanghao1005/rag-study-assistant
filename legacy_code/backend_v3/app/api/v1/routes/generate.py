from fastapi import APIRouter, Query, Request, Response

from app.application.generation_service import GenerationService
from app.domain.generation import (
    GenerateFlashcardsRequest,
    GenerateFlashcardsResponse,
    GenerateQuizRequest,
    GenerateQuizResponse,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    GeneratedHistoryResponse,
    ScopeType,
)

router = APIRouter()
service = GenerationService()


@router.post("/flashcards", response_model=GenerateFlashcardsResponse)
def generate_flashcards(
    payload: GenerateFlashcardsRequest, request: Request, response: Response
) -> GenerateFlashcardsResponse:
    request_id = getattr(request.state, "request_id", None)
    result = service.generate_flashcards(payload, request_id=request_id)
    if result.diagnostics and result.diagnostics.debug_trace_id:
        response.headers["X-Debug-Trace"] = result.diagnostics.debug_trace_id
    return result


@router.post("/quiz", response_model=GenerateQuizResponse)
def generate_quiz(payload: GenerateQuizRequest, request: Request, response: Response) -> GenerateQuizResponse:
    request_id = getattr(request.state, "request_id", None)
    result = service.generate_quiz(payload, request_id=request_id)
    if result.diagnostics and result.diagnostics.debug_trace_id:
        response.headers["X-Debug-Trace"] = result.diagnostics.debug_trace_id
    return result


@router.post("/summary", response_model=GenerateSummaryResponse)
def generate_summary(payload: GenerateSummaryRequest) -> GenerateSummaryResponse:
    return service.generate_summary(payload)


@router.get("/history", response_model=GeneratedHistoryResponse)
def get_generation_history(
    user_id: str = Query(...),
    scope: ScopeType = Query(...),
    scope_id: str = Query(...),
    limit: int = Query(default=20, ge=1, le=100),
) -> GeneratedHistoryResponse:
    return service.get_generated_history(user_id=user_id, scope=scope, scope_id=scope_id, limit=limit)
