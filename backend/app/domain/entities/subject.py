"""Subject (course / study topic) entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain.exceptions import ValidationError


@dataclass(slots=True)
class Subject:
    id: str
    user_id: str
    name: str
    description: str | None = None
    color: str | None = None
    sort_order: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Subject name cannot be blank")

    def rename(self, name: str) -> None:
        if not name or not name.strip():
            raise ValidationError("Subject name cannot be blank")
        self.name = name.strip()
