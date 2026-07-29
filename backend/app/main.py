"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
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
    container: "AppContainer | None" = None,
) -> FastAPI:
    cfg = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = container or build_container(cfg)
        yield

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
