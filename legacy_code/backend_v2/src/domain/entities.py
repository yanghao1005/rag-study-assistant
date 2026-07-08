from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Subject:
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(name: str, description: Optional[str] = None) -> 'Subject':
        return Subject(
            id=uuid4(),
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

@dataclass
class Document:
    id: UUID
    subject_id: UUID
    title: str
    file_path: Optional[str] = None
    file_size_mb: Optional[float] = None
    page_count: Optional[int] = None
    summary: Optional[str] = None
    index: Optional[Dict[str, Any]] = None
    status: str = "pending" # pending, processing, completed, failed
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(subject_id: UUID, title: str, file_path: str = None) -> 'Document':
        return Document(
            id=uuid4(),
            subject_id=subject_id,
            title=title,
            file_path=file_path,
            summary=None,
            index=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

@dataclass
class Chunk:
    id: UUID
    document_id: UUID
    content: str
    chunk_index: int
    page_num: Optional[int] = None
    chapter_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(
        document_id: UUID, 
        content: str, 
        chunk_index: int,
        page_num: Optional[int] = None,
        chapter_name: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Chunk':
        return Chunk(
            id=uuid4(),
            document_id=document_id,
            content=content,
            chunk_index=chunk_index,
            page_num=page_num,
            chapter_name=chapter_name,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
