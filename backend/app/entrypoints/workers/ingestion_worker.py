"""Async ingestion worker loop."""

from __future__ import annotations

import asyncio
import logging

from app.application.ingestion_pipeline import IngestionPipeline
from app.core.config import Settings
from app.domain.entities.enums import JobType
from app.ports.repositories import JobRepositoryPort

logger = logging.getLogger(__name__)


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

    async def run_forever(self) -> None:
        logger.info("Ingestion worker started")
        while not self._stopped.is_set():
            claimed = await self._jobs.claim_next(
                job_types=[JobType.INGEST_DOCUMENT.value, JobType.REINDEX_DOCUMENT.value]
            )
            if claimed is None:
                try:
                    await asyncio.wait_for(
                        self._stopped.wait(),
                        timeout=self._settings.worker_poll_interval_seconds,
                    )
                except TimeoutError:
                    continue
                break

            try:
                await self._pipeline.process_job(claimed)
                logger.info("Ingestion job completed id=%s", claimed.id)
            except Exception:  # noqa: BLE001
                logger.exception("Ingestion job failed id=%s", claimed.id)
        logger.info("Ingestion worker stopped")
