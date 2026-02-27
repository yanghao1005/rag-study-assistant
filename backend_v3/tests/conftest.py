"""Shared pytest fixtures for backend_v3 tests."""

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.dependencies import reset_in_memory_repository


@pytest.fixture(autouse=True)
def _clean_repository() -> None:
	reset_in_memory_repository()
