"""
Vector store service for Supabase pgvector
Handles storing and retrieving document chunks with embeddings
"""
from typing import List, Dict, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.logging import logger


async def store_chunks(
    chunks_with_embeddings: List[Dict],
    document_id: str,
    subject_id: Optional[str] = None,
) -> int:
    """
    Store chunks with embeddings in Supabase database
    
    Args:
        chunks_with_embeddings: List of chunks with embeddings
                               [{"content": "...", "metadata": {...}, "embedding": [...]}]
        document_id: Document UUID
        subject_id: Subject UUID (optional, can be in metadata)
        
    Returns:
        Number of chunks successfully stored
    """
    if not chunks_with_embeddings:
        logger.warning("No chunks provided for storage")
        return 0
    
    db = get_db()
    stored_count = 0
    
    logger.info(
        f"Storing {len(chunks_with_embeddings)} chunks for document {document_id}"
    )
    
    # Prepare batch insert data
    records = []
    for chunk in chunks_with_embeddings:
        # Skip chunks without embeddings
        if "embedding" not in chunk or not chunk["embedding"]:
            logger.warning("Skipping chunk without embedding")
            continue
        
        metadata = chunk.get("metadata", {})
        
        # Extract metadata fields
        subject_id_final = subject_id or metadata.get("subject_id")
        page_num = metadata.get("page_num")
        chapter_name = metadata.get("chapter_name")
        chunk_index = metadata.get("chunk_index", 0)
        is_summary = metadata.get("is_summary", False)
        
        record = {
            "document_id": document_id,
            "subject_id": subject_id_final,
            "content": chunk["content"],
            "embedding": chunk["embedding"],  # pgvector handles list->vector conversion
            "page_num": page_num,
            "chapter_name": chapter_name,
            "chunk_index": chunk_index,
            "metadata": metadata,  # Store full metadata as JSONB
        }
        
        records.append(record)
    
    if not records:
        logger.error("No valid records to store")
        return 0
    
    try:
        # Batch insert into document_chunks table
        result = db.table("document_chunks").insert(records).execute()
        
        stored_count = len(result.data) if result.data else 0
        
        logger.info(
            f"Successfully stored {stored_count}/{len(records)} chunks "
            f"for document {document_id}"
        )
    
    except Exception as e:
        logger.error(
            f"Error storing chunks in database: {e}",
            exc_info=True
        )
        raise
    
    return stored_count


async def similarity_search(
    query_embedding: List[float],
    subject_id: Optional[str] = None,
    document_id: Optional[str] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
) -> List[Dict]:
    """
    Search for similar chunks using pgvector cosine similarity
    
    Args:
        query_embedding: Embedding vector for search query
        subject_id: Filter by subject (optional)
        document_id: Filter by document (optional)
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score (0-1)
        
    Returns:
        List of matching chunks with similarity scores:
        [{
            "id": "uuid",
            "content": "...",
            "similarity": 0.89,
            "metadata": {...},
            "page_num": 5,
            "chapter_name": "Chapter 2"
        }]
    """
    if not query_embedding:
        logger.warning("Empty query embedding provided")
        return []
    
    db = get_db()
    
    logger.debug(
        f"Searching for top {top_k} chunks (threshold={similarity_threshold})"
    )
    
    try:
        # Call the match_documents SQL function from master_prompt.md
        # This function uses pgvector's cosine similarity (<=>)
        result = db.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": similarity_threshold,
                "match_count": top_k,
                "filter_subject_id": subject_id,
                "filter_document_id": document_id,
            }
        ).execute()
        
        chunks = result.data if result.data else []
        
        logger.info(f"Found {len(chunks)} matching chunks")
        
        return chunks
    
    except Exception as e:
        logger.error(f"Error during similarity search: {e}", exc_info=True)
        raise


async def delete_document_chunks(document_id: str) -> int:
    """
    Delete all chunks for a specific document
    Used when re-uploading or deleting a document
    
    Args:
        document_id: Document UUID
        
    Returns:
        Number of chunks deleted
    """
    db = get_db()
    
    logger.info(f"Deleting chunks for document {document_id}")
    
    try:
        # Delete from document_chunks table
        result = db.table("document_chunks") \
            .delete() \
            .eq("document_id", document_id) \
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        
        return deleted_count
    
    except Exception as e:
        logger.error(
            f"Error deleting chunks for document {document_id}: {e}",
            exc_info=True
        )
        raise


async def delete_subject_chunks(subject_id: str) -> int:
    """
    Delete all chunks for a specific subject
    Used when deleting a subject
    
    Args:
        subject_id: Subject UUID
        
    Returns:
        Number of chunks deleted
    """
    db = get_db()
    
    logger.info(f"Deleting chunks for subject {subject_id}")
    
    try:
        result = db.table("document_chunks") \
            .delete() \
            .eq("subject_id", subject_id) \
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        logger.info(f"Deleted {deleted_count} chunks for subject {subject_id}")
        
        return deleted_count
    
    except Exception as e:
        logger.error(
            f"Error deleting chunks for subject {subject_id}: {e}",
            exc_info=True
        )
        raise


async def get_chunk_count(
    document_id: Optional[str] = None,
    subject_id: Optional[str] = None,
) -> int:
    """
    Count chunks for a document or subject
    
    Args:
        document_id: Document UUID (optional)
        subject_id: Subject UUID (optional)
        
    Returns:
        Number of chunks
    """
    db = get_db()
    
    try:
        query = db.table("document_chunks").select("id", count="exact")
        
        if document_id:
            query = query.eq("document_id", document_id)
        if subject_id:
            query = query.eq("subject_id", subject_id)
        
        result = query.execute()
        
        count = result.count if hasattr(result, "count") else 0
        
        return count
    
    except Exception as e:
        logger.error(f"Error counting chunks: {e}", exc_info=True)
        return 0


async def get_chunks_by_document(
    document_id: str,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    """
    Retrieve chunks for a specific document (without embeddings)
    
    Args:
        document_id: Document UUID
        limit: Maximum chunks to return
        offset: Pagination offset
        
    Returns:
        List of chunks (without embedding vectors for efficiency)
    """
    db = get_db()
    
    logger.debug(
        f"Retrieving chunks for document {document_id} "
        f"(limit={limit}, offset={offset})"
    )
    
    try:
        result = db.table("document_chunks") \
            .select("id, content, page_num, chapter_name, chunk_index, metadata") \
            .eq("document_id", document_id) \
            .order("chunk_index") \
            .range(offset, offset + limit - 1) \
            .execute()
        
        chunks = result.data if result.data else []
        
        logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
        
        return chunks
    
    except Exception as e:
        logger.error(
            f"Error retrieving chunks for document {document_id}: {e}",
            exc_info=True
        )
        raise


async def update_chunk_metadata(
    chunk_id: str,
    metadata_updates: Dict,
) -> bool:
    """
    Update metadata for a specific chunk
    
    Args:
        chunk_id: Chunk UUID
        metadata_updates: Dict of metadata fields to update
        
    Returns:
        True if successful
    """
    db = get_db()
    
    logger.debug(f"Updating metadata for chunk {chunk_id}")
    
    try:
        # Get current metadata
        result = db.table("document_chunks") \
            .select("metadata") \
            .eq("id", chunk_id) \
            .single() \
            .execute()
        
        if not result.data:
            logger.warning(f"Chunk {chunk_id} not found")
            return False
        
        # Merge with updates
        current_metadata = result.data.get("metadata", {})
        updated_metadata = {**current_metadata, **metadata_updates}
        
        # Update
        db.table("document_chunks") \
            .update({"metadata": updated_metadata}) \
            .eq("id", chunk_id) \
            .execute()
        
        logger.info(f"Updated metadata for chunk {chunk_id}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating chunk metadata: {e}", exc_info=True)
        return False


# Alias for convenience
async def get_document_chunks_count(document_id: str) -> int:
    """Convenience alias for get_chunk_count with document_id"""
    return await get_chunk_count(document_id=document_id)


# Testing
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def test():
        # Test data
        sample_chunks = [
            {
                "content": "Machine learning is a subset of artificial intelligence.",
                "metadata": {
                    "page_num": 1,
                    "chapter_name": "Introduction",
                    "chunk_index": 0,
                },
                "embedding": [0.1] * 1536,  # Dummy embedding
            },
            {
                "content": "Neural networks are inspired by biological neurons.",
                "metadata": {
                    "page_num": 2,
                    "chapter_name": "Introduction",
                    "chunk_index": 1,
                },
                "embedding": [0.2] * 1536,
            },
        ]
        
        # Note: This requires a real Supabase connection
        print("\n=== Vector Store Test ===")
        print("Note: Requires valid Supabase connection in .env")
        print(f"Sample chunks prepared: {len(sample_chunks)}")
        
        # In real usage:
        # stored = await store_chunks(sample_chunks, "doc-123", "subj-456")
        # print(f"Stored {stored} chunks")
        
        # Search example:
        # query_emb = [0.15] * 1536
        # results = await similarity_search(query_emb, top_k=2)
        # for result in results:
        #     print(f"  Similarity: {result['similarity']}")
        #     print(f"  Content: {result['content'][:60]}...")
    
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test())


# Convenience alias for backward compatibility
async def get_document_chunks_count(document_id: str) -> int:
    """Alias for get_chunk_count with document_id parameter"""
    return await get_chunk_count(document_id=document_id)
