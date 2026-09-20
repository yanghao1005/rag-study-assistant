from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from src.domain.entities import Document, Subject, Chunk
from src.domain.ports import DocumentRepository, SubjectRepository, VectorStore
from src.infrastructure.supabase.client import SupabaseClient
from src.core.logging import logger

class SupabaseSubjectRepository(SubjectRepository):
    def __init__(self):
        self.client = SupabaseClient.get_instance()
        self.table = "subjects"

    async def save(self, subject: Subject) -> Subject:
        data = {
            "id": str(subject.id),
            "name": subject.name,
            "description": subject.description,
            "created_at": subject.created_at.isoformat(),
            "updated_at": subject.updated_at.isoformat()
        }
        # Upsert
        self.client.table(self.table).upsert(data).execute()
        return subject

    async def get_by_id(self, subject_id: UUID) -> Optional[Subject]:
        response = self.client.table(self.table).select("*").eq("id", str(subject_id)).execute()
        if not response.data:
            return None
        data = response.data[0]
        return Subject(
            id=UUID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

    async def get_all(self) -> List[Subject]:
        response = self.client.table(self.table).select("*").execute()
        subjects = []
        for data in response.data:
            subjects.append(Subject(
                id=UUID(data["id"]),
                name=data["name"],
                description=data.get("description"),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            ))
        return subjects

    async def delete(self, subject_id: UUID) -> bool:
        self.client.table(self.table).delete().eq("id", str(subject_id)).execute()
        return True

class SupabaseDocumentRepository(DocumentRepository):
    def __init__(self):
        self.client = SupabaseClient.get_instance()
        self.table = "documents"

    async def save(self, document: Document) -> Document:
        data = {
            "id": str(document.id),
            "subject_id": str(document.subject_id),
            "title": document.title,
            "file_path": document.file_path,
            "file_size_mb": document.file_size_mb,
            "page_count": document.page_count,
            "summary": document.summary,
            "index": document.index,
            "status": document.status,
            "error_message": document.error_message,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
        self.client.table(self.table).upsert(data).execute()
        return document

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        response = self.client.table(self.table).select("*").eq("id", str(document_id)).execute()
        if not response.data:
            return None
        data = response.data[0]
        return self._map_to_entity(data)

    async def get_by_subject(self, subject_id: UUID) -> List[Document]:
        response = self.client.table(self.table).select("*").eq("subject_id", str(subject_id)).execute()
        return [self._map_to_entity(d) for d in response.data]

    async def delete(self, document_id: UUID) -> bool:
        self.client.table(self.table).delete().eq("id", str(document_id)).execute()
        return True

    async def update_status(self, document_id: UUID, status: str, error_message: str = None) -> bool:
        data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        if error_message:
            data["error_message"] = error_message
        self.client.table(self.table).update(data).eq("id", str(document_id)).execute()
        return True

    def _map_to_entity(self, data: Dict) -> Document:
        return Document(
            id=UUID(data["id"]),
            subject_id=UUID(data["subject_id"]),
            title=data["title"],
            file_path=data.get("file_path"),
            file_size_mb=data.get("file_size_mb"),
            page_count=data.get("page_count"),
            summary=data.get("summary"),
            index=data.get("index"),
            status=data.get("status", "pending"),
            error_message=data.get("error_message"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

class SupabaseVectorStore(VectorStore):
    def __init__(self):
        self.client = SupabaseClient.get_instance()
        self.table = "document_chunks"

    async def add_chunks(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0
        records = []
        for chunk in chunks:
            records.append({
                "id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "page_num": chunk.page_num,
                "chapter_name": chunk.chapter_name,
                "metadata": chunk.metadata,
                "embedding": chunk.embedding,
                "created_at": chunk.created_at.isoformat()
            })
        
        # Supabase bulk insert
        response = self.client.table(self.table).insert(records).execute()
        return len(response.data)

    async def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        subject_id: Optional[UUID] = None, 
        document_id: Optional[UUID] = None, 
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        
        # Call the RPC function 'match_documents'
        params = {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": top_k,
            "filter_subject_id": str(subject_id) if subject_id else None,
            "filter_document_id": str(document_id) if document_id else None,
        }
        
        response = self.client.rpc("match_documents", params).execute()
        return response.data

    async def delete_by_document(self, document_id: UUID) -> int:
        response = self.client.table(self.table).delete().eq("document_id", str(document_id)).execute()
        return len(response.data)

    async def get_chunks_by_ids(self, chunk_ids: List[UUID]) -> List[Chunk]:
        if not chunk_ids:
            return []
        
        # Convert UUIDs to strings
        ids_str = [str(uid) for uid in chunk_ids]
        
        # In Supabase, use filter "in"
        response = self.client.table(self.table).select("*").in_("id", ids_str).execute()
        
        chunks = []
        for data in response.data:
            chunks.append(Chunk(
                id=UUID(data["id"]),
                document_id=UUID(data["document_id"]),
                content=data["content"],
                chunk_index=data["chunk_index"],
                page_num=data.get("page_num"),
                chapter_name=data.get("chapter_name"),
                metadata=data.get("metadata", {}),
                embedding=data.get("embedding"), # Note: might need conversion if it's a string, assuming list
                created_at=datetime.fromisoformat(data["created_at"])
            ))
        return chunks

    async def get_chunks_by_index(self, document_id: UUID, chunk_indices: List[int]) -> List[Chunk]:
        if not chunk_indices:
            return []
        
        response = self.client.table(self.table).select("*").eq("document_id", str(document_id)).in_("chunk_index", chunk_indices).execute()
        
        chunks = []
        for data in response.data:
            chunks.append(Chunk(
                id=UUID(data["id"]),
                document_id=UUID(data["document_id"]),
                content=data["content"],
                chunk_index=data["chunk_index"],
                page_num=data.get("page_num"),
                chapter_name=data.get("chapter_name"),
                metadata=data.get("metadata", {}),
                embedding=data.get("embedding"), 
                created_at=datetime.fromisoformat(data["created_at"])
            ))
        return chunks
