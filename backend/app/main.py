"""FastAPI application entry point."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.container import build_container
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.telemetry import setup_telemetry
from app.domain.exceptions import DomainError, NotFoundError, ValidationError
from app.entrypoints.api.router import api_router

if TYPE_CHECKING:
    from app.container import AppContainer


def create_app(
    settings: Settings | None = None,
    container: AppContainer | None = None,
) -> FastAPI:
    cfg = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        import asyncio

        resolved = container or build_container(cfg)
        app.state.container = resolved
        worker_task: asyncio.Task[None] | None = None
        worker = None
        if cfg.enable_async_ingestion:
            worker = resolved.create_ingestion_worker()
            worker_task = asyncio.create_task(worker.run_forever(), name="ingestion-worker")

            def _log_worker_crash(task: asyncio.Task[None]) -> None:
                if task.cancelled():
                    return
                exc = task.exception()
                if exc is not None:
                    logging.getLogger("uvicorn.error").error(
                        "Ingestion worker crashed: %s",
                        exc,
                        exc_info=exc,
                    )

            worker_task.add_done_callback(_log_worker_crash)
        try:
            yield
        finally:
            if worker is not None:
                worker.stop()
            if worker_task is not None:
                worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await worker_task

    app = FastAPI(
        title=cfg.app_name,
        docs_url=f"{cfg.api_prefix}/docs",
        openapi_url=f"{cfg.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error, "message": exc.message},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "message": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def validation_domain_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "validation_error", "message": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": "domain_error", "message": str(exc)},
        )

    app.include_router(api_router, prefix=cfg.api_prefix)
    setup_telemetry(app, service_name=cfg.app_name)
    return app


app = create_app()
