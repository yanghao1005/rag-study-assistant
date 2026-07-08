from fastapi import APIRouter, Depends
from src.container import Container
from src.application.use_cases.agentic_rag import AgenticRAGUseCase
from src.presentation.schemas import SearchRequest, RAGResponse

router = APIRouter()

def get_container():
    return Container.get_instance()

@router.post("/rag/query", response_model=RAGResponse)
async def query_agentic_rag(
    request: SearchRequest,
    container: Container = Depends(get_container)
):
    # For Agentic RAG, we might inject different services or just let the graph build itself
    # as per current AgenticRAGUseCase impl
    use_case = AgenticRAGUseCase(
        container.vector_store,
        container.embedding_service,
        container.llm_service
    )
    
    result = await use_case.execute(
        query=request.query,
        subject_id=request.subject_id,
        document_id=request.document_id,
        top_k=request.top_k,
        generation_type=request.type
    )
    
    return result
