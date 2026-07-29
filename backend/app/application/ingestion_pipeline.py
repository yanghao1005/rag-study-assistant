"""Ingestion use-case: PDF -> parse -> chunk -> embed -> store."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.entities.document import DocumentChunk
from app.domain.entities.enums import JobType, PipelineStage, StageRunStatus
from app.domain.entities.job import Job, PipelineStageRun
from app.domain.exceptions import IngestionError, NotFoundError
from app.ports.llm import EmbeddingPort
from app.ports.parsing import ChunkerPort, DocumentParserPort
from app.ports.repositories import DocumentRepositoryPort, JobRepositoryPort
from app.ports.storage import StoragePort


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
    ) -> None:
        self._documents = documents
        self._jobs = jobs
        self._storage = storage
        self._parser = parser
        self._chunker = chunker
        self._embeddings = embeddings

    async def process_job(self, job: Job) -> Job:
        if job.job_type not in {JobType.INGEST_DOCUMENT, JobType.REINDEX_DOCUMENT}:
            raise IngestionError(f"Unsupported job type: {job.job_type}")
        if not job.document_id:
            raise IngestionError("ingest job missing document_id")

        document = await self._documents.get(user_id=job.user_id, document_id=job.document_id)
        if document is None:
            raise NotFoundError("Document", job.document_id)
        if not document.storage_path:
            raise IngestionError("document has no storage_path")

        now = datetime.now(timezone.utc)
        job.mark_running(now=now)
        job.progress = 5
        await self._jobs.update(job)
        document.mark_processing()
        await self._documents.update(document)

        try:
            # download
            t0 = time.perf_counter()
            pdf_bytes = await self._storage.download(path=document.storage_path)
            await self._record_stage(
                job.id, PipelineStage.DOWNLOAD, StageRunStatus.OK, t0, {"bytes": len(pdf_bytes)}
            )
            job.progress = 20
            await self._jobs.update(job)

            # parse
            t0 = time.perf_counter()
            parsed = await self._parser.parse(pdf_bytes, filename=document.filename)
            await self._record_stage(
                job.id,
                PipelineStage.PARSE,
                StageRunStatus.OK,
                t0,
                {"pages": parsed.total_pages},
            )
            job.progress = 40
            await self._jobs.update(job)

            # chunk
            t0 = time.perf_counter()
            text_chunks = self._chunker.chunk(parsed)
            await self._record_stage(
                job.id,
                PipelineStage.CHUNK,
                StageRunStatus.OK,
                t0,
                {"chunks": len(text_chunks)},
            )
            job.progress = 55
            await self._jobs.update(job)

            # embed
            t0 = time.perf_counter()
            vectors = await self._embeddings.embed([chunk.content for chunk in text_chunks])
            await self._record_stage(
                job.id,
                PipelineStage.EMBED,
                StageRunStatus.OK,
                t0,
                {"vectors": len(vectors), "dims": self._embeddings.dimensions},
            )
            job.progress = 80
            await self._jobs.update(job)

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
                    embedding=vectors[index] if index < len(vectors) else None,
                )
                for index, chunk in enumerate(text_chunks)
            ]

            # store
            t0 = time.perf_counter()
            stored = await self._documents.replace_chunks(
                user_id=job.user_id,
                document_id=document.id,
                subject_id=document.subject_id,
                chunks=domain_chunks,
            )
            await self._record_stage(
                job.id, PipelineStage.STORE, StageRunStatus.OK, t0, {"stored": stored}
            )

            document.mark_ready(total_pages=parsed.total_pages)
            await self._documents.update(document)

            now = datetime.now(timezone.utc)
            job.mark_completed(
                now=now,
                result={
                    "document_id": document.id,
                    "chunks": stored,
                    "pages": parsed.total_pages,
                },
            )
            return await self._jobs.update(job)
        except Exception as exc:  # noqa: BLE001 - convert to job failure
            document.mark_error(str(exc))
            await self._documents.update(document)
            now = datetime.now(timezone.utc)
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

    async def _record_stage(
        self,
        job_id: str,
        stage: PipelineStage,
        status: StageRunStatus,
        started_perf: float,
        details: dict,
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
