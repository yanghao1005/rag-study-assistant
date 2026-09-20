from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from src.domain.entities import Subject, Document, Chunk

class SubjectRepository(ABC):
    @abstractmethod
    async def save(self, subject: Subject) -> Subject:
        pass

    @abstractmethod
    async def get_by_id(self, subject_id: UUID) -> Optional[Subject]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Subject]:
        pass

    @abstractmethod
    async def delete(self, subject_id: UUID) -> bool:
        pass

class DocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: Document) -> Document:
        pass

    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        pass

    @abstractmethod
    async def get_by_subject(self, subject_id: UUID) -> List[Document]:
        pass

    @abstractmethod
    async def delete(self, document_id: UUID) -> bool:
        pass

    @abstractmethod
    async def update_status(self, document_id: UUID, status: str, error_message: str = None) -> bool:
        pass

class VectorStore(ABC):
    @abstractmethod
    async def add_chunks(self, chunks: List[Chunk]) -> int:
        pass

    @abstractmethod
    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        subject_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_by_document(self, document_id: UUID) -> int:
        pass

    @abstractmethod
    async def get_chunks_by_ids(self, chunk_ids: List[UUID]) -> List[Chunk]:
        pass

    @abstractmethod
    async def get_chunks_by_index(self, document_id: UUID, chunk_indices: List[int]) -> List[Chunk]:
        pass

class LLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    async def generate_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

class EmbeddingService(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class FileParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse file and return metadata and list of pages with text
        Returns: (metadata, pages_data)
        """
        pass

class TextChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        pass
    
    @abstractmethod
    def chunk_with_metadata(self, pages_data: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
        pass
