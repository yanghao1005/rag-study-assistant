from typing import Dict, Any, Optional
from uuid import UUID
import logging
from src.domain.ports import VectorStore, LLMService, EmbeddingService

logger = logging.getLogger("rag_backend_v2")

class SimpleRAGUseCase:
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        llm_service: LLMService
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_service = llm_service

    async def execute(
        self, 
        query: str, 
        subject_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        
        logger.info(f"Processing Simple RAG query: {query}")
        
        # 1. Embed Query
        query_embedding = await self.embedding_service.embed_text(query)
        
        # 2. Retrieve Context
        results = await self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            subject_id=subject_id,
            document_id=document_id
        )
        
        if not results:
            return {
                "answer": "I couldn't find any relevant information.",
                "context": []
            }

        # 3. Construct Prompt
        context_text = "\n\n".join([
            f"[Source: Page {r.get('page_num', '?')}]\n{r['content']}" 
            for r in results
        ])
        
        prompt = f"""
        You are a helpful study assistant. Answer the question below based ONLY on the provided context.
        If the answer is not in the context, say "I don't have enough information to answer that."
        
        Context:
        {context_text}
        
        Question: {query}
        
        Answer:
        """
        
        # 4. Generate Answer
        answer = await self.llm_service.generate(prompt)
        
        return {
            "answer": answer,
            "context": results
        }
