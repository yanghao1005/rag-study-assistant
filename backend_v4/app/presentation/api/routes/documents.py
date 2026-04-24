from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from app.container import get_pipeline_runner
from app.core.config import get_settings
from app.core.exceptions import AppError

router = APIRouter(prefix="/documents", tags=["documents"])


class CreateSummaryRequest(BaseModel):
    subject_id: str
    user_id: str
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


def _build_supabase_client():
    settings = get_settings()
    key = settings.supabase_service_key or settings.supabase_key
    if not settings.supabase_url or not key:
        return None

    from supabase import create_client

    return create_client(settings.supabase_url, key)


def _insert_document_row(*, supabase, user_id: str, subject_id: str, document_type: str, filename: str, file_size: int, content_text: str | None = None) -> str | None:
    if supabase is None:
        return None

    payload: dict[str, object] = {
        "user_id": user_id,
        "subject_id": subject_id,
        "document_type": document_type,
        "filename": filename,
        "status": "processing",
        "total_pages": 0,
        "file_size": file_size,
    }
    if content_text is not None:
        payload["content_text"] = content_text

    created = supabase.table("documents").insert(payload).execute()
    return (created.data or [{}])[0].get("id")


def _run_pipeline_and_mark_status(*, supabase, document_id: str, file_path: str, user_id: str, settings) -> None:
    try:
        get_pipeline_runner().run(
            {
                "document_id": document_id,
                "file_path": file_path,
                "user_id": user_id,
                "debug": settings.enable_debug_endpoints,
            }
        )
    except Exception as exc:
        if supabase is not None:
            supabase.table("documents").update({"status": "error", "error_message": str(exc)}).eq("id", document_id).execute()
        raise AppError(error="pipeline_failed", message=str(exc), status_code=500) from exc

    if supabase is not None:
        supabase.table("documents").update({"status": "ready"}).eq("id", document_id).execute()


def _pick_uploaded_file(filename: str) -> Path | None:
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        return None

    matches = [path for path in uploads_dir.glob(f"*-{filename}") if path.is_file()]
    if not matches:
        return None
    return max(matches, key=lambda p: p.stat().st_mtime)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    user_id: str = Form(...),
) -> dict[str, object]:
    settings = get_settings()

    filename = file.filename or "document.pdf"
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise AppError(
            error="invalid_file_type",
            message="Only .pdf, .txt, and .md files are supported",
            status_code=422,
        )

    content = await file.read()
    if not content:
        raise AppError(error="empty_file", message="Uploaded file is empty", status_code=422)

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4()}-{Path(filename).name}"
    stored_path = uploads_dir / stored_name
    stored_path.write_bytes(content)

    supabase = _build_supabase_client()
    document_id = _insert_document_row(
        supabase=supabase,
        user_id=user_id,
        subject_id=subject_id,
        document_type="pdf",
        filename=filename,
        file_size=len(content),
    )

    if not document_id:
        document_id = str(uuid4())

    _run_pipeline_and_mark_status(
        supabase=supabase,
        document_id=document_id,
        file_path=str(stored_path),
        user_id=user_id,
        settings=settings,
    )

    return {
        "document_id": document_id,
        "filename": filename,
        "file_path": str(stored_path),
        "status": "ready",
    }


@router.post("/summary")
async def create_summary_document(request: CreateSummaryRequest) -> dict[str, object]:
    settings = get_settings()
    content = request.content.strip()
    if not content:
        raise AppError(error="empty_content", message="Summary content cannot be empty", status_code=422)

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4()}-{request.title[:60].strip().replace(' ', '_') or 'summary'}.txt"
    stored_path = uploads_dir / stored_name
    stored_path.write_text(content, encoding="utf-8")

    supabase = _build_supabase_client()
    document_id = _insert_document_row(
        supabase=supabase,
        user_id=request.user_id,
        subject_id=request.subject_id,
        document_type="summary",
        filename=request.title,
        file_size=len(content.encode("utf-8")),
        content_text=content,
    )
    if not document_id:
        document_id = str(uuid4())

    _run_pipeline_and_mark_status(
        supabase=supabase,
        document_id=document_id,
        file_path=str(stored_path),
        user_id=request.user_id,
        settings=settings,
    )

    return {
        "document_id": document_id,
        "filename": request.title,
        "file_path": str(stored_path),
        "status": "ready",
    }


@router.get("/{document_id}/download")
def download_document(document_id: str, user_id: str) -> Response:
    supabase = _build_supabase_client()
    if supabase is None:
        raise AppError(
            error="backend_not_configured",
            message="Document download requires Supabase configuration",
            status_code=503,
        )

    response = (
        supabase.table("documents")
        .select("id,user_id,filename,document_type,content_text")
        .eq("id", document_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    document = (response.data or [None])[0]
    if not document:
        raise AppError(error="document_not_found", message="Document not found", status_code=404)

    filename = str(document.get("filename") or "document")
    content_text = document.get("content_text")

    file_path = _pick_uploaded_file(filename)
    if file_path:
        media_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        return FileResponse(path=str(file_path), media_type=media_type, filename=filename)

    if content_text:
        text_name = filename if filename.lower().endswith(".txt") else f"{filename}.txt"
        return Response(
            content=str(content_text),
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{text_name}"'},
        )

    raise AppError(error="file_not_available", message="Stored file is not available", status_code=404)