"""
Embedding generation service with batch processing
Uses AI provider factory for flexible model switching
"""
import asyncio
from typing import List, Dict, Optional

from app.core.logging import logger
from app.services.ai.factory import get_embedding_instance


async def generate_embeddings_batch(
    chunks: List[Dict],
    batch_size: int = 100,
    delay_between_batches: float = 1.0,
) -> List[Dict]:
    """
    Generate embeddings for chunks in batches to avoid rate limits
    
    Args:
        chunks: List of chunks from text_chunker
               [{"content": "...", "metadata": {...}}]
        batch_size: Number of chunks to embed per batch
        delay_between_batches: Seconds to wait between batches
        
    Returns:
        List of chunks with embeddings added:
        [{
            "content": "...",
            "metadata": {...},
            "embedding": [0.123, -0.456, ...]  # Dimension based on model
        }]
    """
    if not chunks:
        logger.warning("No chunks provided for embedding generation")
        return []
    
    # Get embedding service from factory
    embedding_service = get_embedding_instance()
    embedding_dim = embedding_service.get_dimension()
    
    logger.info(
        f"Generating embeddings for {len(chunks)} chunks "
        f"(batch_size={batch_size}, dim={embedding_dim})"
    )
    
    enriched_chunks = []
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    for batch_idx in range(0, len(chunks), batch_size):
        batch = chunks[batch_idx:batch_idx + batch_size]
        batch_num = (batch_idx // batch_size) + 1
        
        logger.debug(
            f"Processing batch {batch_num}/{total_batches} "
            f"({len(batch)} chunks)"
        )
        
        try:
            # Extract text content
            texts = [chunk["content"] for chunk in batch]
            
            # Generate embeddings
            embeddings = await embedding_service.aembed_texts(texts)
            
            # Verify dimension matches
            if embeddings and len(embeddings[0]) != embedding_dim:
                logger.warning(
                    f"Expected dimension {embedding_dim}, "
                    f"got {len(embeddings[0])}"
                )
            
            # Add embeddings to chunks
            for chunk, embedding in zip(batch, embeddings):
                enriched_chunk = {
                    "content": chunk["content"],
                    "metadata": chunk["metadata"],
                    "embedding": embedding,
                }
                enriched_chunks.append(enriched_chunk)
            
            logger.debug(
                f"Batch {batch_num}/{total_batches} completed successfully"
            )
            
            # Delay between batches to respect rate limits
            if batch_idx + batch_size < len(chunks):
                await asyncio.sleep(delay_between_batches)
        
        except Exception as e:
            logger.error(
                f"Error generating embeddings for batch {batch_num}: {e}",
                exc_info=True
            )
            # Continue with remaining batches
            continue
    
    logger.info(
        f"Successfully generated {len(enriched_chunks)}/{len(chunks)} embeddings"
    )
    
    return enriched_chunks


async def generate_single_embedding(query: str) -> List[float]:
    """
    Generate embedding for a single query text
    Used for search queries in RAG pipeline
    
    Args:
        query: Text to embed (usually user question)
        
    Returns:
        Embedding vector as list of floats
    """
    if not query or not query.strip():
        logger.warning("Empty query provided for embedding")
        return []
    
    embedding_service = get_embedding_instance()
    
    try:
        # Embed single text
        embeddings = await embedding_service.aembed_texts([query])
        
        if embeddings:
            logger.debug(
                f"Generated query embedding (dim={len(embeddings[0])})"
            )
            return embeddings[0]
        else:
            logger.error("No embedding returned for query")
            return []
    
    except Exception as e:
        logger.error(f"Error generating query embedding: {e}", exc_info=True)
        return []


def validate_embeddings(chunks_with_embeddings: List[Dict]) -> List[str]:
    """
    Validate embeddings and return warnings
    
    Args:
        chunks_with_embeddings: List of chunks with embeddings
        
    Returns:
        List of warning messages
    """
    warnings = []
    
    if not chunks_with_embeddings:
        warnings.append("No chunks with embeddings to validate")
        return warnings
    
    # Check for missing embeddings
    missing = [
        idx for idx, chunk in enumerate(chunks_with_embeddings)
        if "embedding" not in chunk or not chunk["embedding"]
    ]
    
    if missing:
        warnings.append(
            f"{len(missing)} chunks missing embeddings: {missing[:10]}"
        )
    
    # Check embedding dimensions
    dimensions = set()
    for chunk in chunks_with_embeddings:
        if "embedding" in chunk and chunk["embedding"]:
            dimensions.add(len(chunk["embedding"]))
    
    if len(dimensions) > 1:
        warnings.append(
            f"Inconsistent embedding dimensions: {dimensions}"
        )
    
    # Check for all-zero embeddings (likely errors)
    zero_embeddings = []
    for idx, chunk in enumerate(chunks_with_embeddings):
        if "embedding" in chunk and chunk["embedding"]:
            if all(v == 0.0 for v in chunk["embedding"]):
                zero_embeddings.append(idx)
    
    if zero_embeddings:
        warnings.append(
            f"{len(zero_embeddings)} chunks have all-zero embeddings: "
            f"{zero_embeddings[:10]}"
        )
    
    return warnings


async def regenerate_failed_embeddings(
    chunks: List[Dict],
    chunks_with_embeddings: List[Dict],
) -> List[Dict]:
    """
    Retry embedding generation for chunks that failed
    
    Args:
        chunks: Original chunks without embeddings
        chunks_with_embeddings: Chunks after first embedding attempt
        
    Returns:
        Updated chunks with failed embeddings regenerated
    """
    # Find chunks that failed
    failed_indices = []
    for idx, chunk in enumerate(chunks_with_embeddings):
        if "embedding" not in chunk or not chunk["embedding"]:
            failed_indices.append(idx)
    
    if not failed_indices:
        logger.info("No failed embeddings to regenerate")
        return chunks_with_embeddings
    
    logger.warning(
        f"Attempting to regenerate {len(failed_indices)} failed embeddings"
    )
    
    # Extract failed chunks from original
    failed_chunks = [chunks[idx] for idx in failed_indices]
    
    # Regenerate embeddings (smaller batch size, no delay)
    regenerated = await generate_embeddings_batch(
        chunks=failed_chunks,
        batch_size=10,
        delay_between_batches=0.5,
    )
    
    # Update the original list
    result = chunks_with_embeddings.copy()
    for idx, regenerated_chunk in zip(failed_indices, regenerated):
        result[idx] = regenerated_chunk
    
    # Count successes
    still_failed = sum(
        1 for chunk in result
        if "embedding" not in chunk or not chunk["embedding"]
    )
    
    logger.info(
        f"Regeneration complete: {len(failed_indices) - still_failed} recovered, "
        f"{still_failed} still failed"
    )
    
    return result


def get_embedding_stats(chunks_with_embeddings: List[Dict]) -> Dict:
    """
    Calculate statistics about embeddings
    
    Args:
        chunks_with_embeddings: List of chunks with embeddings
        
    Returns:
        Dict with stats: total, successful, failed, dimension, avg_norm
    """
    if not chunks_with_embeddings:
        return {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "dimension": 0,
            "avg_norm": 0.0,
        }
    
    successful = [
        chunk for chunk in chunks_with_embeddings
        if "embedding" in chunk and chunk["embedding"]
    ]
    
    # Calculate average L2 norm
    norms = []
    for chunk in successful:
        embedding = chunk["embedding"]
        norm = sum(v * v for v in embedding) ** 0.5
        norms.append(norm)
    
    avg_norm = sum(norms) / len(norms) if norms else 0.0
    
    dimension = len(successful[0]["embedding"]) if successful else 0
    
    return {
        "total": len(chunks_with_embeddings),
        "successful": len(successful),
        "failed": len(chunks_with_embeddings) - len(successful),
        "dimension": dimension,
        "avg_norm": round(avg_norm, 4),
    }


# Testing
if __name__ == "__main__":
    import sys
    
    # Example usage
    sample_chunks = [
        {
            "content": "This is the first chunk of text about machine learning.",
            "metadata": {"page_num": 1, "chunk_index": 0},
        },
        {
            "content": "This is the second chunk discussing neural networks.",
            "metadata": {"page_num": 1, "chunk_index": 1},
        },
        {
            "content": "The third chunk covers deep learning architectures.",
            "metadata": {"page_num": 2, "chunk_index": 0},
        },
    ]
    
    async def test():
        print("\n=== Generating Embeddings ===")
        enriched = await generate_embeddings_batch(
            chunks=sample_chunks,
            batch_size=2,
            delay_between_batches=0.5,
        )
        
        print(f"\nGenerated {len(enriched)} embeddings")
        for chunk in enriched:
            if "embedding" in chunk:
                print(f"  Chunk: '{chunk['content'][:50]}...'")
                print(f"  Embedding dim: {len(chunk['embedding'])}")
                print(f"  First 5 values: {chunk['embedding'][:5]}")
        
        # Get stats
        stats = get_embedding_stats(enriched)
        print("\n=== Stats ===")
        print(f"Total: {stats['total']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Avg L2 norm: {stats['avg_norm']}")
        
        # Test query embedding
        print("\n=== Query Embedding ===")
        query_emb = await generate_single_embedding("What is machine learning?")
        if query_emb:
            print(f"Query embedding dim: {len(query_emb)}")
            print(f"First 5 values: {query_emb[:5]}")
    
    # Run async test
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(test())
