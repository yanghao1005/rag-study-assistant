from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth import decode_token_optional
from app.core.config import Settings


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._settings = settings

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._settings.enable_abuse_protection:
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            if int(content_length) > self._settings.max_request_size_bytes:
                return self._payload_too_large(request)

        return await call_next(request)

    @staticmethod
    def _payload_too_large(request: Request) -> JSONResponse:
        return JSONResponse(
            status_code=413,
            content={
                "error": "payload_too_large",
                "message": "Request payload exceeds configured limits.",
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._settings = settings
        self._window_seconds = 60
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._settings.enable_rate_limit or request.url.path in self._settings.rate_limit_exempt():
            return await call_next(request)

        now = time.time()
        key = self._resolve_key(request=request)
        bucket = self._hits[key]
        window_start = now - self._window_seconds
        bucket[:] = [hit for hit in bucket if hit >= window_start]

        if len(bucket) >= self._settings.rate_limit_requests_per_minute:
            retry_after = int(max(1, self._window_seconds - (now - bucket[0])))
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limited",
                    "message": "Too many requests.",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                },
            )
            response.headers["Retry-After"] = str(retry_after)
            return response

        bucket.append(now)
        return await call_next(request)

    def _resolve_key(self, request: Request) -> str:
        authorization = request.headers.get("authorization", "")
        token = authorization.split(" ", 1)[1].strip() if authorization.startswith("Bearer ") else ""
        claims = decode_token_optional(token=token, settings=self._settings)
        if claims and claims.get("sub"):
            return f"user:{claims['sub']}"
        host = request.client.host if request.client else "unknown"
        return f"ip:{host}"

