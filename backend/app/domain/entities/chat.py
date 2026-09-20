"""Chat thread and message entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.entities.enums import ChatRole
from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class ChatThread:
    id: str
    user_id: str
    subject_id: str
    title: str = "New chat"
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def rename(self, title: str) -> None:
        cleaned = title.strip()
        if not cleaned:
            raise ValidationError("Chat title cannot be blank")
        self.title = cleaned


@dataclass(slots=True)
class ChatMessage:
    id: str
    user_id: str
    thread_id: str
    role: ChatRole
    content: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    model: str | None = None
    token_usage: dict[str, Any] | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValidationError("Chat message content cannot be empty")
