from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class AppError(Exception):
    error: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


def _error_payload(request: Request, error: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": error,
        "message": message,
        "details": details or {},
        "request_id": getattr(request.state, "request_id", None),
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(request, exc.error, exc.message, exc.details),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_error_payload(request, "internal_error", str(exc), {"type": exc.__class__.__name__}),
        )
