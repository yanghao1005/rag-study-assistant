"""Domain enums — pure Python, no framework imports."""

from __future__ import annotations

from enum import StrEnum


class DocumentType(StrEnum):
    PDF = "pdf"
    TEXT = "text"
    SUMMARY = "summary"


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class ArtifactType(StrEnum):
    FLASHCARD_DECK = "flashcard_deck"
    QUIZ = "quiz"
    SUMMARY = "summary"


class ArtifactStatus(StrEnum):
    GENERATING = "generating"
    READY = "ready"
    ERROR = "error"


class SourceScope(StrEnum):
    SUBJECT = "subject"
    DOCUMENT = "document"
    CHAPTER = "chapter"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class JobType(StrEnum):
    INGEST_DOCUMENT = "ingest_document"
    GENERATE_FLASHCARDS = "generate_flashcards"
    GENERATE_QUIZ = "generate_quiz"
    GENERATE_SUMMARY = "generate_summary"
    REINDEX_DOCUMENT = "reindex_document"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(StrEnum):
    DOWNLOAD = "download"
    PARSE = "parse"
    CHUNK = "chunk"
    EMBED = "embed"
    STORE = "store"
    RETRIEVE = "retrieve"
    GENERATE = "generate"
    VALIDATE = "validate"


class StageRunStatus(StrEnum):
    OK = "ok"
    ERROR = "error"
    SKIPPED = "skipped"
