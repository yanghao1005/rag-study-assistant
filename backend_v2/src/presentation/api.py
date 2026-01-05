from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from uuid import UUID
from typing import Optional
import shutil
from pathlib import Path

from src.container import Container
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.application.use_cases.rag_query import RAGQueryUseCase
from src.presentation.schemas import DocumentResponse, SearchRequest, RAGResponse

router = APIRouter()

def get_container():
    return Container.get_instance()

@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    subject_id: UUID = Form(...),
    title: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    container: Container = Depends(get_container)
):
    # Save file temporarily
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{subject_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    use_case = IngestDocumentUseCase(
        container.document_repository,
        container.vector_store,
        container.embedding_service,
        container.file_parser,
        container.text_chunker
    )
    
    # Run ingestion immediately (or background)
    # For now, we'll run it async but wait for the doc creation part, 
    # ideally we should kick off a task.
    # The Use Case handles doc creation then processing.
    
    # We'll run proper background task
    # But we need to create the doc first to return it.
    # Refactoring use case to split creation and processing?
    # Or just run the whole thing in background?
    # User expects a document ID.
    
    # Let's simple it:
    # 1. Create a "pending" document manually here or via a small service call?
    # The Use Case does it all. Let's call it awaitable for now to see errors, 
    # OR run in background.
    
    # Better: Run entirely in background, but we need the ID.
    # I'll update UseCase to be split or just await it for MVP if it's not too slow.
    # Parsing PDF can be slow.
    
    # Let's just await it for now as per "simple implementation" requests often imply
    # straightforward logic. The user didn't ask for background tasks explicitly 
    # but "scalable" implies it.
    
    # Changing to Background Task:
    # We need to create the doc entity first to return 202 Accepted.
    
    # Hack: I'll stick to awaiting for the MVP to ensure it works before optimizing.
    # It allows immediate feedback on errors.
    
    doc = await use_case.execute(
        str(file_path), 
        subject_id, 
        title or file.filename
    )
    
    return doc

@router.post("/rag/query", response_model=RAGResponse)
async def query_rag(
    request: SearchRequest,
    container: Container = Depends(get_container)
):
    use_case = RAGQueryUseCase(
        container.vector_store,
        container.embedding_service,
        container.llm_service
    )
    
    result = await use_case.execute(
        query=request.query,
        subject_id=request.subject_id,
        document_id=request.document_id,
        top_k=request.top_k
    )
    
    return result
