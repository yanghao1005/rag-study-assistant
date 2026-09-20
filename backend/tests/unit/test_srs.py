"""SM-2 lite unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.domain.exceptions import ValidationError
from app.domain.srs import apply_sm2


def test_first_good_review_sets_one_day() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    state = apply_sm2(None, quality=4, now=now)
    assert state.interval_days == 1
    assert state.repetitions == 1
    assert state.next_review_at is not None


def test_second_good_review_sets_six_days() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    first = apply_sm2(None, quality=4, now=now)
    second = apply_sm2(first, quality=4, now=now)
    assert second.repetitions == 2
    assert second.interval_days == 6


def test_again_resets_repetitions() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    first = apply_sm2(None, quality=4, now=now)
    again = apply_sm2(first, quality=1, now=now)
    assert again.repetitions == 0
    assert again.interval_days == 1


def test_invalid_quality() -> None:
    with pytest.raises(ValidationError):
        apply_sm2(None, quality=9)
