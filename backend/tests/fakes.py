"""In-memory fakes for API contract tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

from app.application.ingestion_pipeline import IngestionPipeline
from app.container import AppContainer
from app.core.config import Settings
from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.document import Document, DocumentChunk
from app.domain.entities.job import Job, PipelineStageRun
from app.domain.entities.profile import Profile
from app.domain.entities.review import FlashcardReview
from app.domain.entities.study import DueFlashcard, Flashcard, QuizQuestion, StudyArtifact
from app.domain.entities.subject import Subject
from app.ports.auth import AuthenticatedUser, AuthPort
from app.ports.llm import (
    ChatCompletionMessage,
    EmbeddingPort,
    GenerationResult,
    LLMPort,
    StructuredGenerationResult,
)
from app.ports.parsing import ChunkerPort, DocumentParserPort, ParsedDocument, TextChunk
from app.ports.repositories import (
    ChatRepositoryPort,
    DocumentRepositoryPort,
    JobRepositoryPort,
    ProfileRepositoryPort,
    StudyRepositoryPort,
    SubjectRepositoryPort,
)
from app.ports.retrieval import (
    HybridRetrievalResult,
    RetrievalFilters,
    RetrievedChunk,
    VectorSearchPort,
)
from app.ports.storage import StoragePort, StoredObject


class FakeAuth(AuthPort):
    def __init__(self, user_id: str = "user-1") -> None:
        self.user_id = user_id

    async def verify_token(self, token: str) -> AuthenticatedUser:
        if token != "test-token":
            from app.core.errors import AppError

            raise AppError(status_code=401, error="unauthorized", message="bad token")
        return AuthenticatedUser(id=self.user_id, email="test@example.com", role="authenticated")


class FakeStorage(StoragePort):
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def upload(
        self, *, path: str, data: bytes, content_type: str, upsert: bool = False
    ) -> StoredObject:
        self.objects[path] = data
        return StoredObject(
            path=path,
            bucket="documents",
            size_bytes=len(data),
            content_type=content_type,
        )

    async def download(self, *, path: str) -> bytes:
        return self.objects[path]

    async def delete(self, *, path: str) -> None:
        self.objects.pop(path, None)

    async def create_signed_url(self, *, path: str, expires_in: int = 3600) -> str:
        return f"https://example.test/{path}?exp={expires_in}"


class FakeSubjects(SubjectRepositoryPort):
    def __init__(self) -> None:
        self.items: dict[str, Subject] = {}

    async def create(self, subject: Subject) -> Subject:
        self.items[subject.id] = subject
        return subject

    async def get(self, *, user_id: str, subject_id: str) -> Subject | None:
        subject = self.items.get(subject_id)
        if subject and subject.user_id == user_id:
            return subject
        return None

    async def list_for_user(self, user_id: str) -> list[Subject]:
        return [s for s in self.items.values() if s.user_id == user_id]

    async def update(self, subject: Subject) -> Subject:
        self.items[subject.id] = subject
        return subject

    async def delete(self, *, user_id: str, subject_id: str) -> bool:
        subject = self.items.get(subject_id)
        if subject and subject.user_id == user_id:
            del self.items[subject_id]
            return True
        return False


class FakeDocuments(DocumentRepositoryPort):
    def __init__(self) -> None:
        self.items: dict[str, Document] = {}
        self.chunks: dict[str, list[DocumentChunk]] = {}

    async def create(self, document: Document) -> Document:
        self.items[document.id] = document
        return document

    async def get(self, *, user_id: str, document_id: str) -> Document | None:
        doc = self.items.get(document_id)
        if doc and doc.user_id == user_id:
            return doc
        return None

    async def list_for_subject(self, *, user_id: str, subject_id: str) -> list[Document]:
        return [
            d
            for d in self.items.values()
            if d.user_id == user_id and d.subject_id == subject_id
        ]

    async def update(self, document: Document) -> Document:
        self.items[document.id] = document
        return document

    async def delete(self, *, user_id: str, document_id: str) -> bool:
        doc = self.items.get(document_id)
        if doc and doc.user_id == user_id:
            del self.items[document_id]
            self.chunks.pop(document_id, None)
            return True
        return False

    async def replace_chunks(
        self,
        *,
        user_id: str,
        document_id: str,
        subject_id: str,
        chunks: list[DocumentChunk],
    ) -> int:
        self.chunks[document_id] = chunks
        return len(chunks)

    async def list_chunks(
        self,
        *,
        user_id: str,
        document_id: str | None = None,
        subject_id: str | None = None,
        limit: int = 100,
    ) -> list[DocumentChunk]:
        values: list[DocumentChunk] = []
        for _doc_id, chunks in self.chunks.items():
            for chunk in chunks:
                if chunk.user_id != user_id:
                    continue
                if document_id and chunk.document_id != document_id:
                    continue
                if subject_id and chunk.subject_id != subject_id:
                    continue
                values.append(chunk)
        return values[:limit]

    async def get_chunk(
        self,
        *,
        user_id: str,
        document_id: str,
        chunk_id: str,
    ) -> DocumentChunk | None:
        for chunk in self.chunks.get(document_id, []):
            if chunk.user_id == user_id and chunk.id == chunk_id:
                return chunk
        return None


class FakeJobs(JobRepositoryPort):
    def __init__(self) -> None:
        self.items: dict[str, Job] = {}
        self.stages: dict[str, list[PipelineStageRun]] = {}

    async def create(self, job: Job) -> Job:
        self.items[job.id] = job
        return job

    async def get(self, *, user_id: str, job_id: str) -> Job | None:
        job = self.items.get(job_id)
        if job and job.user_id == user_id:
            return job
        return None

    async def update(self, job: Job) -> Job:
        self.items[job.id] = job
        return job

    async def claim_next(self, *, job_types: list[str] | None = None) -> Job | None:
        for job in self.items.values():
            if job.status.value != "queued":
                continue
            if job_types and job.job_type.value not in job_types:
                continue
            job.mark_running(now=datetime.now(UTC))
            return job
        return None

    async def add_stage_run(self, stage_run: PipelineStageRun) -> PipelineStageRun:
        self.stages.setdefault(stage_run.job_id, []).append(stage_run)
        return stage_run

    async def list_stage_runs(self, job_id: str) -> list[PipelineStageRun]:
        return list(self.stages.get(job_id, []))


class FakeStudy(StudyRepositoryPort):
    def __init__(self) -> None:
        self.artifacts: dict[str, StudyArtifact] = {}
        self.cards: dict[str, list[Flashcard]] = {}
        self.questions: dict[str, list[QuizQuestion]] = {}
        self.reviews: dict[str, FlashcardReview] = {}
        self._clock = datetime.now(UTC)

    def _tick(self) -> datetime:
        self._clock = self._clock + timedelta(seconds=1)
        return self._clock

    async def create_artifact(self, artifact: StudyArtifact) -> StudyArtifact:
        now = self._tick()
        if artifact.created_at is None:
            artifact.created_at = now
        if artifact.updated_at is None:
            artifact.updated_at = now
        self.artifacts[artifact.id] = artifact
        return artifact

    async def get_artifact(self, *, user_id: str, artifact_id: str) -> StudyArtifact | None:
        artifact = self.artifacts.get(artifact_id)
        if artifact and artifact.user_id == user_id:
            return artifact
        return None

    async def list_artifacts(
        self, *, user_id: str, subject_id: str, artifact_type: str | None = None
    ) -> list[StudyArtifact]:
        items = [
            a
            for a in self.artifacts.values()
            if a.user_id == user_id and a.subject_id == subject_id
        ]
        if artifact_type:
            items = [a for a in items if a.artifact_type.value == artifact_type]
        return sorted(
            items,
            key=lambda item: item.updated_at or item.created_at or datetime.min.replace(tzinfo=UTC),
            reverse=True,
        )

    async def delete_artifact(self, *, user_id: str, artifact_id: str) -> bool:
        artifact = self.artifacts.get(artifact_id)
        if artifact and artifact.user_id == user_id:
            del self.artifacts[artifact_id]
            self.cards.pop(artifact_id, None)
            self.questions.pop(artifact_id, None)
            return True
        return False

    async def update_artifact(self, artifact: StudyArtifact) -> StudyArtifact:
        artifact.updated_at = self._tick()
        self.artifacts[artifact.id] = artifact
        return artifact

    async def save_flashcards(self, cards: list[Flashcard]) -> int:
        for card in cards:
            self.cards.setdefault(card.artifact_id, []).append(card)
        return len(cards)

    async def list_flashcards(self, *, user_id: str, artifact_id: str) -> list[Flashcard]:
        return [c for c in self.cards.get(artifact_id, []) if c.user_id == user_id]

    async def get_flashcard(self, *, user_id: str, flashcard_id: str) -> Flashcard | None:
        for cards in self.cards.values():
            for card in cards:
                if card.id == flashcard_id and card.user_id == user_id:
                    return card
        return None

    async def update_flashcard(self, card: Flashcard) -> Flashcard:
        items = self.cards.get(card.artifact_id, [])
        for index, existing in enumerate(items):
            if existing.id == card.id:
                items[index] = card
                break
        return card

    async def delete_flashcard(self, *, user_id: str, flashcard_id: str) -> bool:
        for artifact_id, cards in list(self.cards.items()):
            kept = [c for c in cards if not (c.id == flashcard_id and c.user_id == user_id)]
            if len(kept) != len(cards):
                self.cards[artifact_id] = kept
                return True
        return False

    async def save_quiz_questions(self, questions: list[QuizQuestion]) -> int:
        for q in questions:
            self.questions.setdefault(q.artifact_id, []).append(q)
        return len(questions)

    async def list_quiz_questions(self, *, user_id: str, artifact_id: str) -> list[QuizQuestion]:
        return [q for q in self.questions.get(artifact_id, []) if q.user_id == user_id]

    async def get_quiz_question(self, *, user_id: str, question_id: str) -> QuizQuestion | None:
        for questions in self.questions.values():
            for item in questions:
                if item.id == question_id and item.user_id == user_id:
                    return item
        return None

    async def update_quiz_question(self, question: QuizQuestion) -> QuizQuestion:
        items = self.questions.get(question.artifact_id, [])
        for index, existing in enumerate(items):
            if existing.id == question.id:
                items[index] = question
                break
        return question

    async def delete_quiz_question(self, *, user_id: str, question_id: str) -> bool:
        for artifact_id, questions in list(self.questions.items()):
            kept = [q for q in questions if not (q.id == question_id and q.user_id == user_id)]
            if len(kept) != len(questions):
                self.questions[artifact_id] = kept
                return True
        return False

    async def list_due_flashcards(
        self, *, user_id: str, subject_id: str, limit: int = 20
    ) -> list[DueFlashcard]:
        due: list[DueFlashcard] = []
        now = datetime.now(UTC)
        for artifact in self.artifacts.values():
            if artifact.user_id != user_id or artifact.subject_id != subject_id:
                continue
            if artifact.artifact_type.value != "flashcard_deck":
                continue
            for card in self.cards.get(artifact.id, []):
                review = self.reviews.get(f"{user_id}:{card.id}")
                if review is not None and review.next_review_at and review.next_review_at > now:
                    continue
                due.append(
                    DueFlashcard(
                        card=card,
                        subject_id=subject_id,
                        artifact_title=artifact.title,
                        review=review,
                    )
                )
                if len(due) >= limit:
                    return due
        return due

    async def get_review(self, *, user_id: str, flashcard_id: str) -> FlashcardReview | None:
        return self.reviews.get(f"{user_id}:{flashcard_id}")

    async def upsert_review(self, review: FlashcardReview) -> FlashcardReview:
        self.reviews[f"{review.user_id}:{review.flashcard_id}"] = review
        return review


class FakeChat(ChatRepositoryPort):
    def __init__(self) -> None:
        self.threads: dict[str, ChatThread] = {}
        self.messages: dict[str, list[ChatMessage]] = {}

    async def create_thread(self, thread: ChatThread) -> ChatThread:
        self.threads[thread.id] = thread
        return thread

    async def get_thread(self, *, user_id: str, thread_id: str) -> ChatThread | None:
        thread = self.threads.get(thread_id)
        if thread and thread.user_id == user_id:
            return thread
        return None

    async def list_threads(self, *, user_id: str, subject_id: str) -> list[ChatThread]:
        return [
            t
            for t in self.threads.values()
            if t.user_id == user_id and t.subject_id == subject_id
        ]

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        self.messages.setdefault(message.thread_id, []).append(message)
        return message

    async def list_messages(
        self, *, user_id: str, thread_id: str, limit: int = 100
    ) -> list[ChatMessage]:
        return [m for m in self.messages.get(thread_id, []) if m.user_id == user_id][:limit]


class FakeEmbeddings(EmbeddingPort):
    @property
    def dimensions(self) -> int:
        return 1536

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.01] * 1536 for _ in texts]


class FakeLLM(LLMPort):
    async def complete(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        return GenerationResult(content="Respuesta de prueba [1]", model="fake-llm", usage={})

    async def complete_json(
        self,
        *,
        messages: list[ChatCompletionMessage],
        schema_name: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> StructuredGenerationResult:
        if schema_name == "flashcards":
            data: dict[str, Any] = {
                "cards": [{"front": "Q1", "back": "A1", "hint": None}]
            }
        elif schema_name == "rerank":
            data = {"order": [1]}
        elif schema_name == "agentic_plan":
            data = {"need_more": False, "rewritten_query": None, "reason": "sufficient"}
        else:
            data = {
                "questions": [
                    {
                        "question": "What?",
                        "options": ["A", "B", "C", "D"],
                        "correct_option_index": 0,
                        "explanation": "Because",
                    }
                ]
            }
        return StructuredGenerationResult(data=data, model="fake-llm", usage={})

    async def stream(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        for part in ("Respuesta ", "en ", "streaming"):
            yield part


class FakeRetrieval(VectorSearchPort):
    async def dense_search(
        self, *, query_embedding: list[float], filters: RetrievalFilters, match_count: int = 10
    ) -> list[RetrievedChunk]:
        return []

    async def lexical_search(
        self, *, query_text: str, filters: RetrievalFilters, match_count: int = 10
    ) -> list[RetrievedChunk]:
        return []

    async def hybrid_search(
        self,
        *,
        query_text: str,
        query_embedding: list[float],
        filters: RetrievalFilters,
        match_count: int | None = None,
    ) -> HybridRetrievalResult:
        scoped = filters.resolved_document_ids()
        if scoped and "doc-1" not in scoped:
            return HybridRetrievalResult(chunks=[], dense_ids=[], lexical_ids=[])
        chunk = RetrievedChunk(
            id="chunk-1",
            document_id="doc-1",
            subject_id=filters.subject_id or "sub-1",
            chunk_index=0,
            content="El teorema de Pitágoras relaciona lados de un triángulo rectángulo.",
            score=1.0,
        )
        return HybridRetrievalResult(chunks=[chunk], dense_ids=[chunk.id], lexical_ids=[chunk.id])


class FakeParser(DocumentParserPort):
    async def parse(self, data: bytes, *, filename: str) -> ParsedDocument:
        from app.ports.parsing import ParsedPage

        return ParsedDocument(pages=[ParsedPage(page_number=1, text="hello")], total_pages=1)


class FakeChunker(ChunkerPort):
    def chunk(self, document: ParsedDocument) -> list[TextChunk]:
        return [TextChunk(index=0, content=document.full_text or "hello")]


class FakeProfiles(ProfileRepositoryPort):
    def __init__(self) -> None:
        self.items: dict[str, Profile] = {}

    async def get(self, user_id: str) -> Profile | None:
        return self.items.get(user_id)

    async def upsert(self, profile: Profile) -> Profile:
        self.items[profile.id] = profile
        return profile


def build_fake_container() -> AppContainer:
    settings = Settings(  # type: ignore[call-arg]
        APP_NAME="Test API",
        API_PREFIX="/api",
        OPENAI_API_KEY="sk-test",
        SUPABASE_URL="https://example.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY="service",
        SUPABASE_JWT_SECRET="secret",
    )
    documents = FakeDocuments()
    jobs = FakeJobs()
    storage = FakeStorage()
    parser = FakeParser()
    chunker = FakeChunker()
    embeddings = FakeEmbeddings()
    pipeline = IngestionPipeline(
        documents=documents,
        jobs=jobs,
        storage=storage,
        parser=parser,
        chunker=chunker,
        embeddings=embeddings,
        llm=FakeLLM(),
        enable_hierarchical_rag=True,
    )
    return AppContainer(
        settings=settings,
        auth=FakeAuth(),
        llm=FakeLLM(),
        embeddings=embeddings,
        parser=parser,
        chunker=chunker,
        storage=storage,
        profiles=FakeProfiles(),
        subjects=FakeSubjects(),
        documents=documents,
        jobs=jobs,
        study=FakeStudy(),
        chat=FakeChat(),
        retrieval=FakeRetrieval(),
        ingestion_pipeline=pipeline,
    )
