"""
RAG Service
Orchestrates context retrieval and LLM generation
"""
from typing import List, Dict, Optional, Literal
from app.services.vector_store import similarity_search
from app.services.ai.factory import get_llm, get_embedding_service
from app.core.logging import logger

class RAGService:
    def __init__(self):
        self.llm = get_llm()
        self.embedding_service = get_embedding_service()
    
    async def retrieve_context(
        self,
        query: str,
        scope: Literal["subject", "document", "chapter"],
        scope_id: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Retrieve relevant context chunks for a query
        
        Args:
            query: User query or topic
            scope: Scope of search (subject, document, chapter)
            scope_id: UUID of the scope
            top_k: Number of chunks
            threshold: Similarity threshold
            
        Returns:
            List of matching chunks
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Set filters based on scope
        subject_id = scope_id if scope == "subject" else None
        document_id = scope_id if scope == "document" else None
        # Note: Chapter filtering needs DB support or metadata filtering in vector store
        # For now we rely on document/subject level + metadata filtering if implemented
        
        logger.info(f"Retrieving context for query: '{query}' in {scope}={scope_id}")
        
        results = await similarity_search(
            query_embedding=query_embedding,
            subject_id=subject_id,
            document_id=document_id,
            top_k=top_k,
            similarity_threshold=threshold
        )
        
        return results

    async def generate_with_context(
        self,
        query: str,
        context: List[Dict],
        prompt_template: str,
        **kwargs
    ) -> str:
        """
        Generate text using LLM with provided context
        
        Args:
            query: User query/topic
            context: List of context chunks
            prompt_template: String template with {context} and {query} placeholders
            **kwargs: Additional format args for template
            
        Returns:
            Generated string
        """
        # Format context
        context_text = "\n\n".join([
            f"[Source: {c.get('metadata', {}).get('chapter_name', 'Unknown')}, Page {c.get('metadata', {}).get('page_num', '?')}]\n{c['content']}" 
            for c in context
        ])
        
        # Build prompt
        prompt = prompt_template.format(
            context=context_text,
            query=query,
            **kwargs
        )
        
        # Call LLM
        # Use async generate if available, otherwise sync
        if hasattr(self.llm, "agenerate"):
            response = await self.llm.agenerate(prompt)
        else:
            response = self.llm.generate(prompt)
            
        return response
