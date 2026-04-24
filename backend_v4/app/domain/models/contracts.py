from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ScopeLiteral = Literal["subject", "document", "chapter", "summary"]
PromptProfileLiteral = Literal["concise", "exam", "conceptual"]
DifficultyLiteral = Literal["easy", "medium", "hard"]
DocumentTypeLiteral = Literal["pdf", "summary"]


class SourceItem(BaseModel):
    document_type: DocumentTypeLiteral | None = None
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


class GenerateFlashcardsRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    count: int = Field(ge=1, le=20)
    query: str | None = None
    user_id: str | None = None
    save: bool = True
    prompt_profile: PromptProfileLiteral | None = None
    front_max_chars: int | None = Field(default=None, ge=1)
    back_max_chars: int | None = Field(default=None, ge=1)
    debug: bool = False


class GenerateQuizRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    count: int = Field(ge=1, le=20)
    query: str | None = None
    user_id: str | None = None
    save: bool = True
    prompt_profile: PromptProfileLiteral | None = None
    question_max_chars: int | None = Field(default=None, ge=1)
    explanation_max_chars: int | None = Field(default=None, ge=1)
    difficulty: DifficultyLiteral | None = None
    debug: bool = False


class GenerateSummaryRequest(BaseModel):
    scope_id: str
    user_id: str | None = None


class FlashcardItem(BaseModel):
    front: str
    back: str


class GenerateFlashcardsResponse(BaseModel):
    flashcards: list[FlashcardItem]
    sources: list[SourceItem] = Field(default_factory=list)
    diagnostics: RetrievalDiagnostics


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct_answer: int = Field(ge=0)
    explanation: str
    source: SourceItem | None = None


class GenerateQuizResponse(BaseModel):
    questions: list[QuizQuestion]
    diagnostics: RetrievalDiagnostics


class GenerateSummaryResponse(BaseModel):
    summary: str
    scope: Literal["summary"] = "summary"
    scope_id: str


class GeneratedHistoryItem(BaseModel):
    id: str
    user_id: str
    scope: ScopeLiteral
    type: str
    created_at: datetime | None = None
    subject_id: str | None = None
    document_id: str | None = None
    chapter_id: str | None = None
    content_json: dict[str, Any]


class GenerateHistoryResponse(BaseModel):
    items: list[GeneratedHistoryItem]


class PipelineRunRequest(BaseModel):
    document_id: str
    file_path: str
    user_id: str | None = None
    stage: str | None = None
    from_stage: str | None = Field(default=None, alias="from")
    to_stage: str | None = Field(default=None, alias="to")
    debug: bool = False


class PipelineStageResult(BaseModel):
    stage: str
    status: Literal["ok", "skipped", "error"]
    duration_ms: int = Field(default=0, ge=0)
    details: dict[str, Any] = Field(default_factory=dict)


class PipelineRunResponse(BaseModel):
    request_id: str | None = None
    document_id: str
    executed_stages: list[str]
    stage_results: list[PipelineStageResult]
    output: dict[str, Any] = Field(default_factory=dict)
