"""API request/response schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class SubjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    color: str | None = None


class SubjectUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    color: str | None = None
    sort_order: int | None = None


class ChatAskRequest(BaseModel):
    subject_id: str
    question: str = Field(min_length=1)
    thread_id: str | None = None
    document_id: str | None = None
    document_ids: list[str] = Field(default_factory=list, max_length=50)
    save: bool = True
    mode: Literal["standard", "agentic"] = "standard"


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    preferences: dict[str, Any] | None = None


class ReviewRequest(BaseModel):
    flashcard_id: str
    quality: int = Field(ge=0, le=5)


class PipelineDebugRequest(BaseModel):
    document_id: str
    from_stage: str = "download"
    to_stage: str = "synopsis"


class GenerateFlashcardsRequest(BaseModel):
    subject_id: str
    count: int = Field(default=8, ge=1, le=50)
    query: str | None = None
    document_id: str | None = None
    document_ids: list[str] = Field(default_factory=list, max_length=50)
    save: bool = True


class GenerateQuizRequest(BaseModel):
    subject_id: str
    count: int = Field(default=5, ge=1, le=30)
    query: str | None = None
    document_id: str | None = None
    document_ids: list[str] = Field(default_factory=list, max_length=50)
    difficulty: Literal["easy", "medium", "hard"] | None = "medium"
    save: bool = True


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | None = None
