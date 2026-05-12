from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ScopeLiteral = Literal["subject", "document", "chapter", "summary"]


class GenerateFlashcardsRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str = Field(min_length=1)
    query: str | None = None
    count: int = Field(default=5, ge=1, le=25)
    user_id: str | None = None
    save: bool = True
    prompt_profile: Literal["concise", "exam", "conceptual"] | None = None
    front_max_chars: int | None = None
    back_max_chars: int | None = None
    debug: bool = False


class SourceCitation(BaseModel):
    document_type: Literal["pdf", "summary"] | None = None
    page: int | None = None
    chapter_name: str | None = None
    preview: str | None = None


class RetrievalDiagnostics(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    query: str
    total_candidates: int
    accepted_candidates: int
    best_score: float
    debug_trace_id: str | None = None
    debug_artifact_path: str | None = None


class FlashcardItem(BaseModel):
    front: str
    back: str


class GenerateFlashcardsResponse(BaseModel):
    flashcards: list[FlashcardItem]
    sources: list[SourceCitation] = []
    diagnostics: RetrievalDiagnostics | None = None


class GenerateQuizRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str = Field(min_length=1)
    query: str | None = None
    count: int = Field(default=5, ge=1, le=20)
    user_id: str | None = None
    save: bool = True
    prompt_profile: Literal["concise", "exam", "conceptual"] | None = None
    question_max_chars: int | None = None
    explanation_max_chars: int | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    debug: bool = False


class QuizItem(BaseModel):
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    source: SourceCitation | None = None


class GenerateQuizResponse(BaseModel):
    questions: list[QuizItem]
    diagnostics: RetrievalDiagnostics | None = None


class GenerateSummaryRequest(BaseModel):
    scope_id: str = Field(min_length=1)
    user_id: str | None = None
    mode: Literal["concise", "exam", "conceptual", "chapter"] = "concise"


class GenerateSummaryResponse(BaseModel):
    scope: Literal["summary"] = "summary"
    scope_id: str
    summary: str


class GeneratedHistoryItem(BaseModel):
    id: str
    user_id: str
    scope: ScopeLiteral
    type: str
    created_at: str | None = None
    subject_id: str | None = None
    document_id: str | None = None
    chapter_id: str | None = None
    content_json: dict


class GeneratedHistoryResponse(BaseModel):
    items: list[GeneratedHistoryItem]
