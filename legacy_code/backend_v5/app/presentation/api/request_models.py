from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ScopeLiteral = Literal["subject", "document", "chapter", "summary"]


class SummaryDocumentCreateRequest(BaseModel):
    subject_id: str
    title: str
    content: str


class DocumentRenameRequest(BaseModel):
    filename: str


class PipelineRunRequest(BaseModel):
    document_id: str
    file_path: str
    subject_id: str | None = None
    stage: str | None = None
    from_stage: str | None = Field(default=None, alias="from")
    to_stage: str | None = Field(default=None, alias="to")
    debug: bool = False


class GenerateFlashcardsRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    source_document_ids: list[str] = Field(default_factory=list)
    query: str
    count: int = 5
    save: bool = False


class GenerateQuizRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    source_document_ids: list[str] = Field(default_factory=list)
    query: str
    count: int = 5
    difficulty: str | None = None
    save: bool = False


class GenerateSummaryRequest(BaseModel):
    scope_id: str


class ChatAskRequest(BaseModel):
    scope: ScopeLiteral
    scope_id: str
    question: str
    save: bool = False


class GeneratedGroupUpdateRequest(BaseModel):
    content_json: dict[str, Any]

