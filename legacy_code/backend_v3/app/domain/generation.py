from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ScopeType(str, Enum):
    SUBJECT = "subject"
    DOCUMENT = "document"
    CHAPTER = "chapter"
    SUMMARY = "summary"


class PromptProfile(str, Enum):
    CONCISE = "concise"
    EXAM = "exam"
    CONCEPTUAL = "conceptual"


class SourceCitation(BaseModel):
    document_type: Optional[str] = None
    page: Optional[int] = None
    chapter_name: Optional[str] = None
    preview: Optional[str] = None


class ContextScore(BaseModel):
    document_type: Optional[str] = None
    page: Optional[int] = None
    chapter_name: Optional[str] = None
    score: float
    threshold: float
    accepted: bool


class RetrievalDiagnostics(BaseModel):
    scope: ScopeType
    scope_id: str
    query: str
    total_candidates: int
    accepted_candidates: int
    best_score: float
    debug_trace_id: Optional[str] = None
    debug_artifact_path: Optional[str] = None
    context_scores: List[ContextScore] = Field(default_factory=list)


class GenerateFlashcardsRequest(BaseModel):
    scope: ScopeType
    scope_id: str
    count: int = Field(default=5, ge=1, le=20)
    query: Optional[str] = Field(default=None, max_length=300)
    user_id: Optional[str] = None
    save: bool = True
    prompt_profile: PromptProfile = PromptProfile.CONCISE
    front_max_chars: int = Field(default=90, ge=20, le=240)
    back_max_chars: int = Field(default=220, ge=40, le=800)
    debug: bool = False


class FlashcardItem(BaseModel):
    front: str
    back: str


class GenerateFlashcardsResponse(BaseModel):
    flashcards: List[FlashcardItem]
    sources: List[SourceCitation] = Field(default_factory=list)
    diagnostics: Optional[RetrievalDiagnostics] = None


class GenerateQuizRequest(BaseModel):
    scope: ScopeType
    scope_id: str
    count: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium")
    query: Optional[str] = Field(default=None, max_length=300)
    user_id: Optional[str] = None
    save: bool = True
    prompt_profile: PromptProfile = PromptProfile.CONCISE
    question_max_chars: int = Field(default=180, ge=40, le=400)
    explanation_max_chars: int = Field(default=260, ge=60, le=1000)
    debug: bool = False


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: int = Field(ge=0, le=3)
    explanation: str
    source: Optional[SourceCitation] = None


class GenerateQuizResponse(BaseModel):
    questions: List[QuizQuestion]
    diagnostics: Optional[RetrievalDiagnostics] = None


class GenerateSummaryRequest(BaseModel):
    scope_id: str
    user_id: Optional[str] = None


class GenerateSummaryResponse(BaseModel):
    summary: str
    scope: ScopeType = ScopeType.SUMMARY
    scope_id: str


class GeneratedHistoryItem(BaseModel):
    id: str
    user_id: str
    scope: ScopeType
    type: str
    created_at: Optional[str] = None
    subject_id: Optional[str] = None
    document_id: Optional[str] = None
    chapter_id: Optional[str] = None
    content_json: dict


class GeneratedHistoryResponse(BaseModel):
    items: List[GeneratedHistoryItem]
