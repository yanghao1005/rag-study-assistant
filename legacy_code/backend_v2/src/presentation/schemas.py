from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class DocumentResponse(BaseModel):
    id: UUID
    subject_id: UUID
    title: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    subject_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    top_k: int = 5
    type: str = "answer" # 'answer', 'quiz', 'flashcards'

class SearchResult(BaseModel):
    id: UUID
    content: str
    page_num: Optional[int] = None
    chapter_name: Optional[str] = None
    similarity: Optional[float] = None
    metadata: Dict[str, Any] = {}

class RAGResponse(BaseModel):
    answer: str
    context: List[SearchResult]
