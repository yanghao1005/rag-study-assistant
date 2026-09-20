"""Smoke tests that ports are abstract interfaces."""

from __future__ import annotations

import pytest

from app.ports.auth import AuthPort
from app.ports.llm import EmbeddingPort, LLMPort
from app.ports.parsing import ChunkerPort, DocumentParserPort
from app.ports.repositories import (
    ChatRepositoryPort,
    DocumentRepositoryPort,
    JobRepositoryPort,
    ProfileRepositoryPort,
    StudyRepositoryPort,
    SubjectRepositoryPort,
)
from app.ports.retrieval import VectorSearchPort
from app.ports.storage import StoragePort


@pytest.mark.parametrize(
    "port_cls",
    [
        AuthPort,
        StoragePort,
        DocumentParserPort,
        ChunkerPort,
        EmbeddingPort,
        LLMPort,
        VectorSearchPort,
        ProfileRepositoryPort,
        SubjectRepositoryPort,
        DocumentRepositoryPort,
        StudyRepositoryPort,
        ChatRepositoryPort,
        JobRepositoryPort,
    ],
)
def test_ports_cannot_be_instantiated(port_cls: type) -> None:
    with pytest.raises(TypeError):
        port_cls()  # type: ignore[call-arg]
