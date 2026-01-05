from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from uuid import UUID
from typing import Optional
import shutil
from pathlib import Path

from src.container import Container
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.application.use_cases.simple_rag import SimpleRAGUseCase
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
    
    doc = await use_case.execute(
        str(file_path), 
        subject_id, 
        title or file.filename
    )
    
    return doc

@router.post("/rag/query", response_model=RAGResponse)
async def query_simple_rag(
    request: SearchRequest,
    container: Container = Depends(get_container)
):
    use_case = SimpleRAGUseCase(
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
