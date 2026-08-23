"""Ingestion use-case: PDF -> parse -> chunk -> embed -> store -> synopsis."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.document import Document, DocumentChunk
from app.domain.entities.enums import JobType, PipelineStage, StageRunStatus
from app.domain.entities.job import Job, PipelineStageRun
from app.domain.exceptions import IngestionError, NotFoundError
from app.ports.llm import ChatCompletionMessage, EmbeddingPort, LLMPort
from app.ports.parsing import ChunkerPort, DocumentParserPort, ParsedDocument, TextChunk
from app.ports.repositories import DocumentRepositoryPort, JobRepositoryPort
from app.ports.storage import StoragePort

STAGE_ORDER: tuple[PipelineStage, ...] = (
    PipelineStage.DOWNLOAD,
    PipelineStage.PARSE,
    PipelineStage.CHUNK,
    PipelineStage.EMBED,
    PipelineStage.STORE,
    PipelineStage.SYNOPSIS,
)


@dataclass(slots=True)
class PipelineContext:
    pdf_bytes: bytes | None = None
    parsed: ParsedDocument | None = None
    text_chunks: list[TextChunk] = field(default_factory=list)
    vectors: list[list[float]] = field(default_factory=list)
    stored: int = 0
    synopsis: str | None = None


class IngestionPipeline:
    def __init__(
        self,
        *,
        documents: DocumentRepositoryPort,
        jobs: JobRepositoryPort,
        storage: StoragePort,
        parser: DocumentParserPort,
        chunker: ChunkerPort,
        embeddings: EmbeddingPort,
        llm: LLMPort | None = None,
        enable_hierarchical_rag: bool = True,
    ) -> None:
        self._documents = documents
        self._jobs = jobs
        self._storage = storage
        self._parser = parser
        self._chunker = chunker
        self._embeddings = embeddings
        self._llm = llm
        self._enable_hierarchical_rag = enable_hierarchical_rag

    async def process_job(self, job: Job) -> Job:
        return await self.run_range(
            job,
            from_stage=PipelineStage.DOWNLOAD,
            to_stage=PipelineStage.SYNOPSIS,
        )

    async def run_range(
        self,
        job: Job,
        *,
        from_stage: PipelineStage,
        to_stage: PipelineStage,
    ) -> Job:
        if job.job_type not in {JobType.INGEST_DOCUMENT, JobType.REINDEX_DOCUMENT}:
            raise IngestionError(f"Unsupported job type: {job.job_type}")
        if not job.document_id:
            raise IngestionError("ingest job missing document_id")
        if from_stage not in STAGE_ORDER or to_stage not in STAGE_ORDER:
            raise IngestionError("unsupported pipeline stage")
        start = STAGE_ORDER.index(from_stage)
        end = STAGE_ORDER.index(to_stage)
        if start > end:
            raise IngestionError("from_stage must precede to_stage")

        document = await self._documents.get(user_id=job.user_id, document_id=job.document_id)
        if document is None:
            raise NotFoundError("Document", job.document_id)
        if not document.storage_path:
            raise IngestionError("document has no storage_path")

        now = datetime.now(UTC)
        job.mark_running(now=now)
        job.progress = 5
        await self._jobs.update(job)
        document.mark_processing()
        await self._documents.update(document)

        context = PipelineContext()
        try:
            for index, stage in enumerate(STAGE_ORDER):
                if index > end:
                    break
                if stage == PipelineStage.DOWNLOAD:
                    await self._stage_download(job, document, context)
                elif stage == PipelineStage.PARSE:
                    await self._stage_parse(job, document, context)
                elif stage == PipelineStage.CHUNK:
                    await self._stage_chunk(job, context)
                elif stage == PipelineStage.EMBED:
                    await self._stage_embed(job, context)
                elif stage == PipelineStage.STORE:
                    await self._stage_store(job, document, context)
                elif stage == PipelineStage.SYNOPSIS:
                    await self._stage_synopsis(job, document, context)

            if to_stage in {PipelineStage.STORE, PipelineStage.SYNOPSIS}:
                document.mark_ready(total_pages=context.parsed.total_pages if context.parsed else 0)
                document.synopsis = context.synopsis or document.synopsis
                await self._documents.update(document)
                now = datetime.now(UTC)
                job.mark_completed(
                    now=now,
                    result={
                        "document_id": document.id,
                        "chunks": context.stored,
                        "pages": context.parsed.total_pages if context.parsed else 0,
                        "synopsis": context.synopsis,
                        "from_stage": from_stage.value,
                        "to_stage": to_stage.value,
                    },
                )
            else:
                job.progress = 100
                await self._jobs.update(job)
                now = datetime.now(UTC)
                job.mark_completed(
                    now=now,
                    result={
                        "document_id": document.id,
                        "from_stage": from_stage.value,
                        "to_stage": to_stage.value,
                        "chunks": len(context.text_chunks),
                    },
                )
            return await self._jobs.update(job)
        except Exception as exc:  # noqa: BLE001 - convert to job failure
            document.mark_error(str(exc))
            await self._documents.update(document)
            now = datetime.now(UTC)
            job.mark_failed(now=now, message=str(exc))
            await self._jobs.update(job)
            await self._record_stage(
                job.id,
                PipelineStage.STORE,
                StageRunStatus.ERROR,
                time.perf_counter(),
                {"error": str(exc)},
                duration_override_ms=0,
            )
            raise

    async def _stage_download(
        self, job: Job, document: Document, context: PipelineContext
    ) -> None:
        if not document.storage_path:
            raise IngestionError("document has no storage_path")
        t0 = time.perf_counter()
        context.pdf_bytes = await self._storage.download(path=document.storage_path)
        await self._record_stage(
            job.id,
            PipelineStage.DOWNLOAD,
            StageRunStatus.OK,
            t0,
            {"bytes": len(context.pdf_bytes)},
        )
        job.progress = 20
        await self._jobs.update(job)

    async def _stage_parse(
        self, job: Job, document: Document, context: PipelineContext
    ) -> None:
        if context.pdf_bytes is None:
            raise IngestionError("parse requires downloaded bytes")
        t0 = time.perf_counter()
        context.parsed = await self._parser.parse(context.pdf_bytes, filename=document.filename)
        await self._record_stage(
            job.id,
            PipelineStage.PARSE,
            StageRunStatus.OK,
            t0,
            {"pages": context.parsed.total_pages},
        )
        job.progress = 40
        await self._jobs.update(job)

    async def _stage_chunk(self, job: Job, context: PipelineContext) -> None:
        if context.parsed is None:
            raise IngestionError("chunk requires parsed document")
        t0 = time.perf_counter()
        context.text_chunks = self._chunker.chunk(context.parsed)
        await self._record_stage(
            job.id,
            PipelineStage.CHUNK,
            StageRunStatus.OK,
            t0,
            {"chunks": len(context.text_chunks)},
        )
        job.progress = 55
        await self._jobs.update(job)

    async def _stage_embed(self, job: Job, context: PipelineContext) -> None:
        if not context.text_chunks:
            raise IngestionError("embed requires chunks")
        t0 = time.perf_counter()
        context.vectors = await self._embeddings.embed(
            [chunk.content for chunk in context.text_chunks]
        )
        await self._record_stage(
            job.id,
            PipelineStage.EMBED,
            StageRunStatus.OK,
            t0,
            {"vectors": len(context.vectors), "dims": self._embeddings.dimensions},
        )
        job.progress = 80
        await self._jobs.update(job)

    async def _stage_store(
        self, job: Job, document: Document, context: PipelineContext
    ) -> None:
        if not context.text_chunks:
            raise IngestionError("store requires chunks")
        domain_chunks = [
            DocumentChunk(
                id=str(uuid4()),
                user_id=job.user_id,
                subject_id=document.subject_id,
                document_id=document.id,
                chunk_index=chunk.index,
                content=chunk.content,
                chapter_name=chunk.chapter_name,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                token_count=chunk.token_count,
                metadata=dict(chunk.metadata),
                embedding=context.vectors[index] if index < len(context.vectors) else None,
            )
            for index, chunk in enumerate(context.text_chunks)
        ]
        t0 = time.perf_counter()
        context.stored = await self._documents.replace_chunks(
            user_id=job.user_id,
            document_id=document.id,
            subject_id=document.subject_id,
            chunks=domain_chunks,
        )
        await self._record_stage(
            job.id, PipelineStage.STORE, StageRunStatus.OK, t0, {"stored": context.stored}
        )

    async def _stage_synopsis(
        self, job: Job, document: Document, context: PipelineContext
    ) -> None:
        t0 = time.perf_counter()
        if not self._enable_hierarchical_rag:
            await self._record_stage(
                job.id,
                PipelineStage.SYNOPSIS,
                StageRunStatus.SKIPPED,
                t0,
                {"reason": "hierarchical_rag_disabled"},
                duration_override_ms=0,
            )
            return
        excerpt = ""
        if context.parsed is not None:
            excerpt = context.parsed.full_text[:4000]
        elif context.text_chunks:
            excerpt = "\n".join(chunk.content for chunk in context.text_chunks[:8])[:4000]
        synopsis = excerpt[:600] if excerpt else None
        if self._llm is not None and excerpt:
            completion = await self._llm.complete(
                messages=[
                    ChatCompletionMessage(
                        role="system",
                        content=(
                            "Escribe una sinopsis académica de 4 a 6 frases del material. "
                            "Sin adornos ni metadatos."
                        ),
                    ),
                    ChatCompletionMessage(
                        role="user",
                        content=f"Documento: {document.filename}\n\n{excerpt}",
                    ),
                ],
                max_tokens=350,
            )
            synopsis = completion.content.strip() or synopsis
        context.synopsis = synopsis
        document.synopsis = synopsis
        await self._documents.update(document)
        await self._record_stage(
            job.id,
            PipelineStage.SYNOPSIS,
            StageRunStatus.OK,
            t0,
            {"chars": len(synopsis or "")},
        )
        job.progress = 95
        await self._jobs.update(job)

    async def _record_stage(
        self,
        job_id: str,
        stage: PipelineStage,
        status: StageRunStatus,
        started_perf: float,
        details: dict[str, object],
        *,
        duration_override_ms: int | None = None,
    ) -> None:
        duration_ms = (
            duration_override_ms
            if duration_override_ms is not None
            else int((time.perf_counter() - started_perf) * 1000)
        )
        await self._jobs.add_stage_run(
            PipelineStageRun(
                id=str(uuid4()),
                job_id=job_id,
                stage=stage,
                status=status,
                duration_ms=max(duration_ms, 0),
                details=details,
            )
        )
