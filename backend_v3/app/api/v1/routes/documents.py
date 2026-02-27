from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import APIRouter, File, Form, Request, UploadFile

from app.application.pipeline_runner import PipelineRunner
from app.core.config import get_settings
from app.core.database import get_supabase_client
from app.core.exceptions import AppError
from app.domain.pipeline import PipelineRunRequest, PipelineStage

router = APIRouter()
runner = PipelineRunner()


@router.post("/upload")
def upload_pdf_document(
    request: Request,
    file: UploadFile = File(...),
    subject_id: str = Form(...),
    user_id: str = Form(...),
) -> dict:
    filename = Path(file.filename or "document.pdf").name
    if not filename.lower().endswith(".pdf"):
        raise AppError("invalid_file_type", "Only PDF files are supported", status_code=400)

    settings = get_settings()
    document_id = str(uuid4())

    upload_root = Path(settings.uploads_dir)
    user_dir = upload_root / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_path = user_dir / f"{document_id}_{filename}"

    with stored_path.open("wb") as target:
        copyfileobj(file.file, target)

    file_size = stored_path.stat().st_size
    supabase_client = get_supabase_client()
    if supabase_client is None:
        raise AppError("storage_unavailable", "Supabase client is not configured", status_code=500)

    supabase_client.table("documents").insert(
        {
            "id": document_id,
            "user_id": user_id,
            "subject_id": subject_id,
            "document_type": "pdf",
            "filename": filename,
            "file_size": file_size,
            "status": "processing",
        }
    ).execute()

    request_id = getattr(request.state, "request_id", None)
    pipeline_payload = PipelineRunRequest(
        document_id=document_id,
        user_id=user_id,
        subject_id=subject_id,
        document_type="pdf",
        file_path=str(stored_path),
        from_stage=PipelineStage.VALIDATE_INPUT,
        to_stage=PipelineStage.BUILD_DOCUMENT_INDEX,
        debug=True,
    )

    try:
        result = runner.run(pipeline_payload, request_id=request_id)
        total_pages = 0
        for stage_result in result.stage_results:
            if stage_result.stage.value == "parse_document":
                total_pages = int(stage_result.details.get("total_pages", 0))
                break

        supabase_client.table("documents").update(
            {"status": "ready", "total_pages": total_pages, "error_message": None}
        ).eq("id", document_id).eq("user_id", user_id).execute()

        return {
            "document_id": document_id,
            "status": "ready",
            "filename": filename,
            "file_size": file_size,
            "total_pages": total_pages,
        }
    except Exception as exc:
        supabase_client.table("documents").update(
            {"status": "error", "error_message": str(exc)}
        ).eq("id", document_id).eq("user_id", user_id).execute()
        raise
