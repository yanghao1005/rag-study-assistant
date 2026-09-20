from __future__ import annotations

from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    scope: str = Field(min_length=1)
    scope_id: str = Field(min_length=1)
    question: str = Field(min_length=3)
    save: bool = True


class ChatAskResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[dict]
