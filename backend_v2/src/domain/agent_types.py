from typing import TypedDict, List
from src.domain.entities import Document, Chunk

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    
    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents 
    """
    question: str
    generation: str
    documents: List[Chunk]
    subject_id: str
    generation_type: str # 'answer', 'quiz', 'flashcards'
    hallucination_status: str # 'grounded', 'hallucinated'
    answer_status: str # 'useful', 'not_useful'
    loop_count: int
    transform_count: int
    feedback: str # Feedback for regeneration
