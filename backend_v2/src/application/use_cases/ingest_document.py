from uuid import UUID
import logging
from src.domain.entities import Document, Chunk
from src.domain.ports import DocumentRepository, VectorStore, EmbeddingService, FileParser, TextChunker

logger = logging.getLogger("rag_backend_v2")

class IngestDocumentUseCase:
    def __init__(
        self,
        document_repository: DocumentRepository,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        file_parser: FileParser,
        text_chunker: TextChunker
    ):
        self.document_repository = document_repository
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.file_parser = file_parser
        self.text_chunker = text_chunker

    async def execute(self, file_path: str, subject_id: UUID, title: str) -> Document:
        # 1. Create Document Entity (Pending)
        doc = Document.create(subject_id=subject_id, title=title, file_path=file_path)
        await self.document_repository.save(doc)
        
        try:
            logger.info(f"Starting ingestion for document {doc.id}")
            
            # 2. Parse PDF
            metadata, pages_data = self.file_parser.parse(file_path)
            
            # Update doc metadata
            doc.page_count = metadata.get("total_pages")
            
            # 3. Chunk Text
            chunks_data = self.text_chunker.chunk_with_metadata(pages_data)
            
            # 4. Generate Embeddings (Batch)
            texts = [c["content"] for c in chunks_data]
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = await self.embedding_service.embed_batch(texts)
            
            # 5. Create Chunk Entities
            chunks_entities = []
            for i, chunk_data in enumerate(chunks_data):
                chunk = Chunk.create(
                    document_id=doc.id,
                    content=chunk_data["content"],
                    chunk_index=chunk_data["metadata"]["chunk_index"],
                    page_num=chunk_data["metadata"]["page_num"],
                    metadata=chunk_data["metadata"]
                )
                chunk.embedding = embeddings[i]
                chunks_entities.append(chunk)
            
            # 6. Store in Vector Store
            logger.info(f"Storing {len(chunks_entities)} chunks")
            await self.vector_store.add_chunks(chunks_entities)
            
            # 7. Update Document Status
            doc.status = "completed"
            await self.document_repository.save(doc)
            logger.info(f"Ingestion completed for document {doc.id}")
            
            return doc
            
        except Exception as e:
            logger.error(f"Ingestion failed for document {doc.id}: {e}")
            doc.status = "failed"
            doc.error_message = str(e)
            await self.document_repository.save(doc)
            raise
