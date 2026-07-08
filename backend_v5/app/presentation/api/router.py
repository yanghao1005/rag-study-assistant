from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse, Response

from app import container
from app.application.use_cases.chat_use_case import ChatUseCase
from app.application.use_cases.documents_use_case import DocumentsUseCase
from app.application.use_cases.generation_use_case import GenerationUseCase
from app.application.use_cases.jobs_use_case import JobsUseCase
from app.application.use_cases.pipeline_use_case import PipelineUseCase
from app.core.auth import CurrentUser, get_current_user
from app.core.errors import AppError
from app.presentation.api.request_models import (
    ChatAskRequest,
    DocumentRenameRequest,
    GenerateFlashcardsRequest,
    GeneratedGroupUpdateRequest,
    GenerateQuizRequest,
    GenerateSummaryRequest,
    PipelineRunRequest,
    ScopeLiteral,
    SummaryDocumentCreateRequest,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/documents/upload")
async def upload_document(
    subject_id: str,
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
    documents_use_case: DocumentsUseCase = Depends(container.get_documents_use_case),
) -> dict[str, object]:
    content = (await file.read()).decode("utf-8", errors="ignore")
    payload = documents_use_case.create_summary_document(
        user_id=user.user_id,
        subject_id=subject_id,
        title=file.filename or "upload.txt",
        content=content,
    )
    return payload


@router.post("/documents/summary")
def create_summary_document(
    request: SummaryDocumentCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    documents_use_case: DocumentsUseCase = Depends(container.get_documents_use_case),
) -> dict[str, object]:
    return documents_use_case.create_summary_document(
        user_id=user.user_id,
        subject_id=request.subject_id,
        title=request.title,
        content=request.content,
    )


@router.get("/documents")
def list_documents(
    subject_id: str | None = Query(default=None),
    user: CurrentUser = Depends(get_current_user),
    documents_use_case: DocumentsUseCase = Depends(container.get_documents_use_case),
) -> dict[str, object]:
    return documents_use_case.list_documents(user_id=user.user_id, subject_id=subject_id)


@router.patch("/documents/{document_id}")
def rename_document(
    document_id: str,
    request: DocumentRenameRequest,
    user: CurrentUser = Depends(get_current_user),
    documents_use_case: DocumentsUseCase = Depends(container.get_documents_use_case),
) -> dict[str, object]:
    return documents_use_case.rename_document(
        user_id=user.user_id,
        document_id=document_id,
        filename=request.filename,
    )


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    user: CurrentUser = Depends(get_current_user),
    documents_use_case: DocumentsUseCase = Depends(container.get_documents_use_case),
) -> dict[str, object]:
    return documents_use_case.delete_document(user_id=user.user_id, document_id=document_id)


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    user: CurrentUser = Depends(get_current_user),
    repository=Depends(container.get_repository),
) -> Response:
    document = repository.get_document(document_id=document_id)
    if not document or document["user_id"] != user.user_id:
        raise AppError(status_code=404, error="document_not_found", message="Document not found.")
    content = str(document.get("content_text") or "")
    return Response(
        content=content.encode("utf-8"),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={document['filename']}"},
    )


@router.post("/pipeline/run")
def run_pipeline(
    request: PipelineRunRequest,
    user: CurrentUser = Depends(get_current_user),
    pipeline_use_case: PipelineUseCase = Depends(container.get_pipeline_use_case),
) -> dict[str, object]:
    stage_from = request.from_stage or request.stage
    stage_to = request.to_stage
    return pipeline_use_case.run_pipeline_range(
        user_id=user.user_id,
        document_id=request.document_id,
        file_path=request.file_path,
        stage_from=stage_from,
        stage_to=stage_to,
        debug=request.debug,
    )


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    user: CurrentUser = Depends(get_current_user),
    jobs_use_case: JobsUseCase = Depends(container.get_jobs_use_case),
) -> dict[str, object]:
    return jobs_use_case.get_job(user_id=user.user_id, job_id=job_id)


@router.post("/generate/flashcards")
def generate_flashcards(
    request: GenerateFlashcardsRequest,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.generate_flashcards(
        user_id=user.user_id,
        scope=request.scope,
        scope_id=request.scope_id,
        source_document_ids=request.source_document_ids,
        query=request.query,
        count=request.count,
        save=request.save,
    )


@router.post("/generate/quiz")
def generate_quiz(
    request: GenerateQuizRequest,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.generate_quiz(
        user_id=user.user_id,
        scope=request.scope,
        scope_id=request.scope_id,
        source_document_ids=request.source_document_ids,
        query=request.query,
        count=request.count,
        difficulty=request.difficulty,
        save=request.save,
    )


@router.post("/generate/summary")
def generate_summary(
    request: GenerateSummaryRequest,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.generate_summary(user_id=user.user_id, scope_id=request.scope_id)


@router.get("/generate/history")
def get_generation_history(
    scope: Annotated[ScopeLiteral, Query(...)],
    scope_id: Annotated[str, Query(...)],
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.get_history(
        user_id=user.user_id,
        scope=scope,
        scope_id=scope_id,
        limit=limit,
    )


@router.get("/generate/groups/{group_id}")
def get_generated_group(
    group_id: str,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.get_generated_group(user_id=user.user_id, group_id=group_id)


@router.patch("/generate/groups/{group_id}")
def update_generated_group(
    group_id: str,
    request: GeneratedGroupUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.update_generated_group(
        user_id=user.user_id,
        group_id=group_id,
        content_json=request.content_json,
    )


@router.delete("/generate/groups/{group_id}")
def delete_generated_group(
    group_id: str,
    user: CurrentUser = Depends(get_current_user),
    generation_use_case: GenerationUseCase = Depends(container.get_generation_use_case),
) -> dict[str, object]:
    return generation_use_case.delete_generated_group(user_id=user.user_id, group_id=group_id)


@router.post("/chat/ask")
def ask_chat(
    request: ChatAskRequest,
    user: CurrentUser = Depends(get_current_user),
    chat_use_case: ChatUseCase = Depends(container.get_chat_use_case),
) -> dict[str, object]:
    return chat_use_case.ask(
        user_id=user.user_id,
        scope=request.scope,
        scope_id=request.scope_id,
        question=request.question,
        save=request.save,
    )


@router.get("/_debug/ping")
def debug_ping() -> JSONResponse:
    return JSONResponse({"ok": True})

