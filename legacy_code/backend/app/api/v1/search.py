"""
Search API endpoints
Handles vector similarity search
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.schemas import SearchRequest, SearchResponse, SearchResult
from app.services.embedding_service import generate_single_embedding
from app.services.vector_store import similarity_search
from app.core.logging import logger

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for similar content using vector similarity
    
    - **query**: The search query text
    - **subject_id**: Optional filter by subject
    - **document_id**: Optional filter by specific document
    - **top_k**: Number of results to return (1-20, default 5)
    - **similarity_threshold**: Minimum similarity score (0-1, default 0.7)
    """
    try:
        logger.info(f"Search query: '{request.query}' (top_k={request.top_k}, threshold={request.similarity_threshold})")
        
        # 1. Generate query embedding
        query_embedding = await generate_single_embedding(request.query)
        
        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate query embedding"
            )
        
        # 2. Perform similarity search
        results = await similarity_search(
            query_embedding=query_embedding,
            subject_id=str(request.subject_id) if request.subject_id else None,
            document_id=str(request.document_id) if request.document_id else None,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold
        )
        
        # 3. Format results
        search_results = [
            SearchResult(
                id=UUID(result["id"]),
                content=result["content"],
                similarity=result["similarity"],
                page_num=result.get("page_num"),
                chapter_name=result.get("chapter_name"),
                document_id=UUID(result["document_id"]),
                metadata=result.get("metadata", {})
            )
            for result in results
        ]
        
        logger.info(f"Found {len(search_results)} results for query: '{request.query}'")
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
