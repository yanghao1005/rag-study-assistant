"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


# Subject Schemas
class SubjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    subject_id: UUID


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    subject_id: Optional[UUID] = None


class DocumentResponse(DocumentBase):
    id: UUID
    file_path: Optional[str] = None
    file_size_mb: Optional[float] = None
    page_count: Optional[int] = None
    status: str = "pending"
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Chunk Schemas
class ChunkBase(BaseModel):
    content: str
    page_num: Optional[int] = None
    chapter_name: Optional[str] = None


class ChunkResponse(ChunkBase):
    id: UUID
    document_id: UUID
    subject_id: UUID
    chunk_index: int
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True


# Upload Schemas
class UploadResponse(BaseModel):
    document_id: UUID
    status: str
    message: str
    chunks_created: int
    processing_time_seconds: float


# Search Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    subject_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    id: UUID
    content: str
    similarity: float
    page_num: Optional[int] = None
    chapter_name: Optional[str] = None
    document_id: UUID
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int


# Processing Status Schema
class ProcessingStatus(BaseModel):
    document_id: UUID
    status: str  # pending, processing, completed, failed
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None
    chunks_processed: Optional[int] = None
    total_chunks: Optional[int] = None


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
