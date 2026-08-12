"""Composition root — wires ports to adapters from settings."""

from __future__ import annotations

from dataclasses import dataclass

from app.adapters.auth.supabase_jwt import SupabaseJwtAuthAdapter
from app.adapters.llm.factory import create_embedding_port, create_llm_port
from app.adapters.parsing.pdf_parser import PyPdfParserAdapter
from app.adapters.parsing.semantic_chunker import SemanticChunkerAdapter
from app.adapters.supabase.chat_repository import SupabaseChatRepository
from app.adapters.supabase.client import create_supabase_admin_client
from app.adapters.supabase.documents_repository import SupabaseDocumentRepository
from app.adapters.supabase.jobs_repository import SupabaseJobRepository
from app.adapters.supabase.retrieval import SupabaseHybridRetrievalAdapter
from app.adapters.supabase.storage import SupabaseStorageAdapter
from app.adapters.supabase.study_repository import SupabaseStudyRepository
from app.adapters.supabase.subjects_repository import SupabaseSubjectRepository
from app.application.ingestion_pipeline import IngestionPipeline
from app.core.config import Settings, get_settings
from app.entrypoints.workers.ingestion_worker import IngestionWorker
from app.ports.auth import AuthPort
from app.ports.llm import EmbeddingPort, LLMPort
from app.ports.parsing import ChunkerPort, DocumentParserPort
from app.ports.repositories import (
    ChatRepositoryPort,
    DocumentRepositoryPort,
    JobRepositoryPort,
    StudyRepositoryPort,
    SubjectRepositoryPort,
)
from app.ports.retrieval import VectorSearchPort
from app.ports.storage import StoragePort


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    auth: AuthPort
    llm: LLMPort
    embeddings: EmbeddingPort
    parser: DocumentParserPort
    chunker: ChunkerPort
    storage: StoragePort
    subjects: SubjectRepositoryPort
    documents: DocumentRepositoryPort
    jobs: JobRepositoryPort
    study: StudyRepositoryPort
    chat: ChatRepositoryPort
    retrieval: VectorSearchPort
    ingestion_pipeline: IngestionPipeline

    def create_ingestion_worker(self) -> IngestionWorker:
        return IngestionWorker(
            jobs=self.jobs,
            pipeline=self.ingestion_pipeline,
            settings=self.settings,
        )


def build_container(settings: Settings | None = None) -> AppContainer:
    cfg = settings or get_settings()
    supabase = create_supabase_admin_client(cfg)

    llm = create_llm_port(cfg)
    embeddings = create_embedding_port(cfg)
    parser: DocumentParserPort = PyPdfParserAdapter()
    chunker: ChunkerPort = SemanticChunkerAdapter(
        max_chars=cfg.chunk_max_chars,
        overlap_chars=cfg.chunk_overlap_chars,
    )
    storage: StoragePort = SupabaseStorageAdapter(
        supabase, bucket=cfg.supabase_storage_bucket
    )
    subjects: SubjectRepositoryPort = SupabaseSubjectRepository(supabase)
    documents: DocumentRepositoryPort = SupabaseDocumentRepository(supabase)
    jobs: JobRepositoryPort = SupabaseJobRepository(supabase)
    study: StudyRepositoryPort = SupabaseStudyRepository(supabase)
    chat: ChatRepositoryPort = SupabaseChatRepository(supabase)
    retrieval: VectorSearchPort = SupabaseHybridRetrievalAdapter(
        supabase,
        dense_top_k=cfg.retrieval_dense_top_k,
        lexical_top_k=cfg.retrieval_lexical_top_k,
        final_top_k=cfg.retrieval_final_top_k,
        rerank_provider=cfg.rerank_provider,
        llm=llm if cfg.rerank_provider == "llm" else None,
    )
    pipeline = IngestionPipeline(
        documents=documents,
        jobs=jobs,
        storage=storage,
        parser=parser,
        chunker=chunker,
        embeddings=embeddings,
    )
    return AppContainer(
        settings=cfg,
        auth=SupabaseJwtAuthAdapter(cfg),
        llm=llm,
        embeddings=embeddings,
        parser=parser,
        chunker=chunker,
        storage=storage,
        subjects=subjects,
        documents=documents,
        jobs=jobs,
        study=study,
        chat=chat,
        retrieval=retrieval,
        ingestion_pipeline=pipeline,
    )
