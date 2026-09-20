from typing import Dict, Any, Optional
from uuid import UUID
import logging
from src.infrastructure.ai.graph_builder import build_graph

logger = logging.getLogger("rag_backend_v2")

class AgenticRAGUseCase:
    def __init__(self, vector_store, embedding_service, llm_service):
        self.app = build_graph()

    async def execute(
        self, 
        query: str, 
        subject_id: Optional[UUID] = None,
        document_id: Optional[UUID] = None,
        top_k: int = 5,
        generation_type: str = "answer"
    ) -> Dict[str, Any]:
        
        logger.info(f"Processing Agentic RAG query: {query} (type={generation_type})")
        
        requests_subject_id = str(subject_id) if subject_id else None
        
        inputs = {
            "question": query, 
            "generation_type": generation_type,
            "subject_id": requests_subject_id
        }
        result = await self.app.ainvoke(inputs)
        
        answer = result.get("generation", "No answer generated.")
        documents = result.get("documents", [])
        
        formatted_docs = []
        for d in documents:
            if isinstance(d, dict):
                formatted_docs.append({
                    "id": d.get("id"),
                    "content": d.get("content"),
                    "page_num": d.get("page_num"),
                    "chapter_name": d.get("chapter_name"),
                    "similarity": d.get("similarity"),
                    "metadata": d.get("metadata", {})
                })
            else:
                formatted_docs.append({
                     "id": d.id,
                     "content": d.content,
                     "page_num": d.page_num,
                     "metadata": d.metadata
                })

        return {
            "answer": answer,
            "context": formatted_docs
        }
