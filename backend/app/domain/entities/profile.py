"""User profile entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Profile:
    id: str
    display_name: str | None = None
    avatar_url: str | None = None
    onboarding_completed: bool = False
    preferences: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def mark_onboarding_complete(self) -> None:
        self.onboarding_completed = True
