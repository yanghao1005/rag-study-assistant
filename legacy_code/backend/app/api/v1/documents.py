"""
Document API endpoints
Handles document upload, processing, and management
"""
import time
from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, BackgroundTasks
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings
from app.schemas import (
    DocumentResponse,
    UploadResponse,
    ProcessingStatus,
    ErrorResponse
)
from app.services.pdf_parser import parse_pdf
from app.services.chapter_detector import detect_and_merge_chapters
from app.services.text_chunker import chunk_pages_text
from app.services.embedding_service import generate_embeddings_batch
from app.services.vector_store import store_chunks
from app.core.logging import logger

router = APIRouter(prefix="/documents", tags=["documents"])

# Directory for uploaded PDFs
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def process_pdf_document(
    document_id: str,
    subject_id: str,
    file_path: str
):
    """Background task to process PDF and generate embeddings"""
    db = get_db()
    
    try:
        # Update status to processing
        db.table("documents").update({
            "status": "processing"
        }).eq("id", document_id).execute()
        
        # 1. Parse PDF
        logger.info(f"Parsing PDF: {file_path}")
        metadata, pages = parse_pdf(file_path)
        
        # Update document with metadata
        db.table("documents").update({
            "page_count": metadata["total_pages"],
            "file_size_mb": Path(file_path).stat().st_size / (1024 * 1024)
        }).eq("id", document_id).execute()
        
        # 2. Detect chapters
        logger.info(f"Detecting chapters...")
        chapters = detect_and_merge_chapters(pages)
        
        # 3. Chunk text
        logger.info(f"Chunking text...")
        chunks = chunk_pages_text(
            pages_text=pages,
            chapters=chapters,
            subject_id=subject_id,
            document_id=document_id
        )
        
        # 4. Generate embeddings
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        enriched_chunks = await generate_embeddings_batch(chunks, batch_size=10)
        
        # 5. Store in vector database
        logger.info(f"Storing chunks in vector database...")
        stored_count = await store_chunks(enriched_chunks, document_id=document_id)
        
        # Update status to completed
        db.table("documents").update({
            "status": "completed"
        }).eq("id", document_id).execute()
        
        logger.info(f"Document {document_id} processed successfully: {stored_count} chunks")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}", exc_info=True)
        
        # Update status to failed
        db.table("documents").update({
            "status": "failed",
            "error_message": str(e)
        }).eq("id", document_id).execute()


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject_id: UUID = Form(...),
    title: str = Form(None)
):
    """
    Upload a PDF document and process it
    Processing happens in the background
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Check if subject exists
        db = get_db()
        subject = db.table("subjects").select("id").eq("id", str(subject_id)).execute()
        if not subject.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subject {subject_id} not found"
            )
        
        # Generate document ID
        document_id = str(uuid4())
        
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{document_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        
        # Create document record
        doc_data = {
            "id": document_id,
            "subject_id": str(subject_id),
            "title": title or file.filename,
            "file_path": str(file_path),
            "status": "pending"
        }
        
        result = db.table("documents").insert(doc_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create document record"
            )
        
        # Process in background
        background_tasks.add_task(
            process_pdf_document,
            document_id=document_id,
            subject_id=str(subject_id),
            file_path=str(file_path)
        )
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            document_id=UUID(document_id),
            status="processing",
            message="Document uploaded successfully. Processing in background.",
            chunks_created=0,  # Will be updated after processing
            processing_time_seconds=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID):
    """Get document by ID"""
    try:
        db = get_db()
        result = db.table("documents").select("*").eq("id", str(document_id)).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return result.data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}/status", response_model=ProcessingStatus)
async def get_document_status(document_id: UUID):
    """Get processing status of a document"""
    try:
        db = get_db()
        
        # Get document
        doc = db.table("documents").select("*").eq("id", str(document_id)).single().execute()
        
        if not doc.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Get chunk count
        from app.services.vector_store import get_document_chunks_count
        chunks_count = await get_document_chunks_count(str(document_id))
        
        return ProcessingStatus(
            document_id=document_id,
            status=doc.data["status"],
            message=doc.data.get("error_message"),
            chunks_processed=chunks_count if chunks_count > 0 else None,
            total_chunks=chunks_count if doc.data["status"] == "completed" else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document status {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: UUID):
    """Delete a document and all its chunks"""
    try:
        db = get_db()
        
        # Get document
        doc = db.table("documents").select("*").eq("id", str(document_id)).single().execute()
        
        if not doc.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Delete file if exists
        if doc.data.get("file_path"):
            file_path = Path(doc.data["file_path"])
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
        
        # Delete from database (cascade will delete chunks)
        db.table("documents").delete().eq("id", str(document_id)).execute()
        
        logger.info(f"Deleted document: {document_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
