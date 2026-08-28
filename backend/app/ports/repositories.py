"""Persistence ports for domain aggregates."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.document import Document, DocumentChunk
from app.domain.entities.job import Job, PipelineStageRun
from app.domain.entities.profile import Profile
from app.domain.entities.review import FlashcardReview
from app.domain.entities.study import DueFlashcard, Flashcard, QuizQuestion, StudyArtifact
from app.domain.entities.subject import Subject


class ProfileRepositoryPort(ABC):
    @abstractmethod
    async def get(self, user_id: str) -> Profile | None: ...

    @abstractmethod
    async def upsert(self, profile: Profile) -> Profile: ...


class SubjectRepositoryPort(ABC):
    @abstractmethod
    async def create(self, subject: Subject) -> Subject: ...

    @abstractmethod
    async def get(self, *, user_id: str, subject_id: str) -> Subject | None: ...

    @abstractmethod
    async def list_for_user(self, user_id: str) -> list[Subject]: ...

    @abstractmethod
    async def update(self, subject: Subject) -> Subject: ...

    @abstractmethod
    async def delete(self, *, user_id: str, subject_id: str) -> bool: ...


class DocumentRepositoryPort(ABC):
    @abstractmethod
    async def create(self, document: Document) -> Document: ...

    @abstractmethod
    async def get(self, *, user_id: str, document_id: str) -> Document | None: ...

    @abstractmethod
    async def list_for_subject(self, *, user_id: str, subject_id: str) -> list[Document]: ...

    @abstractmethod
    async def update(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, *, user_id: str, document_id: str) -> bool: ...

    @abstractmethod
    async def replace_chunks(
        self,
        *,
        user_id: str,
        document_id: str,
        subject_id: str,
        chunks: list[DocumentChunk],
    ) -> int: ...

    @abstractmethod
    async def list_chunks(
        self,
        *,
        user_id: str,
        document_id: str | None = None,
        subject_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentChunk]: ...

    @abstractmethod
    async def get_chunk(
        self,
        *,
        user_id: str,
        document_id: str,
        chunk_id: str,
    ) -> DocumentChunk | None: ...


class StudyRepositoryPort(ABC):
    @abstractmethod
    async def create_artifact(self, artifact: StudyArtifact) -> StudyArtifact: ...

    @abstractmethod
    async def get_artifact(self, *, user_id: str, artifact_id: str) -> StudyArtifact | None: ...

    @abstractmethod
    async def list_artifacts(
        self,
        *,
        user_id: str,
        subject_id: str,
        artifact_type: str | None = None,
    ) -> list[StudyArtifact]: ...

    @abstractmethod
    async def delete_artifact(self, *, user_id: str, artifact_id: str) -> bool: ...

    @abstractmethod
    async def update_artifact(self, artifact: StudyArtifact) -> StudyArtifact: ...

    @abstractmethod
    async def save_flashcards(self, cards: list[Flashcard]) -> int: ...

    @abstractmethod
    async def list_flashcards(self, *, user_id: str, artifact_id: str) -> list[Flashcard]: ...

    @abstractmethod
    async def get_flashcard(self, *, user_id: str, flashcard_id: str) -> Flashcard | None: ...

    @abstractmethod
    async def update_flashcard(self, card: Flashcard) -> Flashcard: ...

    @abstractmethod
    async def delete_flashcard(self, *, user_id: str, flashcard_id: str) -> bool: ...

    @abstractmethod
    async def save_quiz_questions(self, questions: list[QuizQuestion]) -> int: ...

    @abstractmethod
    async def list_quiz_questions(
        self, *, user_id: str, artifact_id: str
    ) -> list[QuizQuestion]: ...

    @abstractmethod
    async def get_quiz_question(
        self, *, user_id: str, question_id: str
    ) -> QuizQuestion | None: ...

    @abstractmethod
    async def update_quiz_question(self, question: QuizQuestion) -> QuizQuestion: ...

    @abstractmethod
    async def delete_quiz_question(self, *, user_id: str, question_id: str) -> bool: ...

    @abstractmethod
    async def list_due_flashcards(
        self, *, user_id: str, subject_id: str, limit: int = 20
    ) -> list[DueFlashcard]: ...

    @abstractmethod
    async def get_review(self, *, user_id: str, flashcard_id: str) -> FlashcardReview | None: ...

    @abstractmethod
    async def upsert_review(self, review: FlashcardReview) -> FlashcardReview: ...


class ChatRepositoryPort(ABC):
    @abstractmethod
    async def create_thread(self, thread: ChatThread) -> ChatThread: ...

    @abstractmethod
    async def get_thread(self, *, user_id: str, thread_id: str) -> ChatThread | None: ...

    @abstractmethod
    async def list_threads(self, *, user_id: str, subject_id: str) -> list[ChatThread]: ...

    @abstractmethod
    async def add_message(self, message: ChatMessage) -> ChatMessage: ...

    @abstractmethod
    async def list_messages(
        self, *, user_id: str, thread_id: str, limit: int = 100
    ) -> list[ChatMessage]: ...


class JobRepositoryPort(ABC):
    @abstractmethod
    async def create(self, job: Job) -> Job: ...

    @abstractmethod
    async def get(self, *, user_id: str, job_id: str) -> Job | None: ...

    @abstractmethod
    async def update(self, job: Job) -> Job: ...

    @abstractmethod
    async def claim_next(self, *, job_types: list[str] | None = None) -> Job | None: ...

    @abstractmethod
    async def add_stage_run(self, stage_run: PipelineStageRun) -> PipelineStageRun: ...

    @abstractmethod
    async def list_stage_runs(self, job_id: str) -> list[PipelineStageRun]: ...
