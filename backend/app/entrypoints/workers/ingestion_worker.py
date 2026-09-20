"""Async ingestion worker loop."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from app.application.ingestion_pipeline import IngestionPipeline
from app.core.config import Settings
from app.domain.entities.enums import JobType
from app.ports.repositories import JobRepositoryPort

logger = logging.getLogger(__name__)


def _attach_uvicorn_logging() -> None:
    """Show worker logs in `docker compose logs backend` (uvicorn default config)."""
    uvicorn_error = logging.getLogger("uvicorn.error")
    if not uvicorn_error.handlers:
        return
    logger.setLevel(logging.INFO)
    logger.handlers = list(uvicorn_error.handlers)
    logger.propagate = False


class IngestionWorker:
    def __init__(
        self,
        *,
        jobs: JobRepositoryPort,
        pipeline: IngestionPipeline,
        settings: Settings,
    ) -> None:
        self._jobs = jobs
        self._pipeline = pipeline
        self._settings = settings
        self._stopped = asyncio.Event()

    def stop(self) -> None:
        self._stopped.set()

    async def _idle(self) -> bool:
        """Wait for the poll interval. Returns False if the worker was stopped."""
        try:
            await asyncio.wait_for(
                self._stopped.wait(),
                timeout=self._settings.worker_poll_interval_seconds,
            )
        except TimeoutError:
            return True
        return False

    async def run_forever(self) -> None:
        _attach_uvicorn_logging()
        logger.info("Ingestion worker started")
        while not self._stopped.is_set():
            try:
                claimed = await self._jobs.claim_next(
                    job_types=[JobType.INGEST_DOCUMENT.value, JobType.REINDEX_DOCUMENT.value]
                )
            except Exception:  # noqa: BLE001 - keep polling after a transient DB/API error
                logger.exception("Failed to claim next ingestion job")
                if not await self._idle():
                    break
                continue

            if claimed is None:
                if not await self._idle():
                    break
                continue

            if not claimed.document_id:
                claimed.mark_failed(
                    now=datetime.now(UTC),
                    message="ingest job missing document_id",
                )
                try:
                    await self._jobs.update(claimed)
                except Exception:  # noqa: BLE001
                    logger.exception("Failed to mark orphan job as failed id=%s", claimed.id)
                logger.warning("Skipped ingest job without document_id id=%s", claimed.id)
                continue

            try:
                await self._pipeline.process_job(claimed)
                logger.info("Ingestion job completed id=%s", claimed.id)
            except Exception:  # noqa: BLE001
                logger.exception("Ingestion job failed id=%s", claimed.id)
        logger.info("Ingestion worker stopped")
