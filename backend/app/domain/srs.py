"""SM-2 lite spaced repetition (pure domain, no I/O)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class SrsState:
    ease: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    next_review_at: datetime | None = None
    last_quality: int | None = None


def apply_sm2(
    state: SrsState | None,
    *,
    quality: int,
    now: datetime | None = None,
) -> SrsState:
    """Apply SuperMemo-2 with quality 0–5 (Again=1, Hard=3, Good=4, Easy=5)."""
    if quality < 0 or quality > 5:
        raise ValidationError("quality must be between 0 and 5")
    moment = now or datetime.now(UTC)
    ease = state.ease if state else 2.5
    interval = state.interval_days if state else 0
    repetitions = state.repetitions if state else 0

    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = max(1, round(interval * ease))
        repetitions += 1
        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease = max(1.3, ease)

    return SrsState(
        ease=ease,
        interval_days=interval,
        repetitions=repetitions,
        next_review_at=moment + timedelta(days=interval),
        last_quality=quality,
    )
