"""Unit tests for pure domain entities."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.document import Document, DocumentChunk
from app.domain.entities.enums import (
    ChatRole,
    DocumentStatus,
    JobStatus,
    JobType,
    QuestionType,
)
from app.domain.entities.job import Job
from app.domain.entities.study import Flashcard, QuizQuestion
from app.domain.entities.subject import Subject
from app.domain.exceptions import ValidationError


def test_subject_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        Subject(id="s1", user_id="u1", name="   ")


def test_subject_rename() -> None:
    subject = Subject(id="s1", user_id="u1", name="Math")
    subject.rename("Algebra")
    assert subject.name == "Algebra"


def test_document_lifecycle() -> None:
    doc = Document(id="d1", user_id="u1", subject_id="s1", filename="notes.pdf")
    assert doc.status == DocumentStatus.QUEUED
    doc.mark_processing()
    assert doc.status == DocumentStatus.PROCESSING
    doc.mark_ready(total_pages=12)
    assert doc.status == DocumentStatus.READY
    assert doc.total_pages == 12


def test_chunk_requires_content() -> None:
    with pytest.raises(ValidationError):
        DocumentChunk(
            id="c1",
            user_id="u1",
            subject_id="s1",
            document_id="d1",
            chunk_index=0,
            content="  ",
        )


def test_flashcard_and_quiz_validation() -> None:
    card = Flashcard(
        id="f1",
        user_id="u1",
        artifact_id="a1",
        front="Q?",
        back="A",
    )
    assert card.front == "Q?"

    with pytest.raises(ValidationError):
        QuizQuestion(
            id="q1",
            user_id="u1",
            artifact_id="a1",
            question="What?",
            question_type=QuestionType.SHORT_ANSWER,
        )


def test_job_progress_and_completion() -> None:
    now = datetime.now(timezone.utc)
    job = Job(id="j1", user_id="u1", job_type=JobType.INGEST_DOCUMENT)
    job.mark_running(now=now)
    assert job.status == JobStatus.RUNNING
    job.mark_completed(now=now, result={"chunks": 3})
    assert job.status == JobStatus.COMPLETED
    assert job.progress == 100.0


def test_chat_message_rejects_empty() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(
            id="m1",
            user_id="u1",
            thread_id="t1",
            role=ChatRole.USER,
            content="",
        )


def test_chat_thread_rename() -> None:
    thread = ChatThread(id="t1", user_id="u1", subject_id="s1")
    thread.rename("Exam prep")
    assert thread.title == "Exam prep"
