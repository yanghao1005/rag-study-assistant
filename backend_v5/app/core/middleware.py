from __future__ import annotations

import base64
import json
import time
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from opentelemetry import metrics, trace
except Exception:  # pragma: no cover - optional dependency fallback
    metrics = None
    trace = None


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Adds a request correlation id to request state and response headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class _SlidingWindowLimiter:
    def __init__(self, *, requests_per_minute: int) -> None:
        self._window_seconds = 60.0
        self._limit = max(1, requests_per_minute)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and (now - bucket[0]) > self._window_seconds:
                bucket.popleft()

            if len(bucket) >= self._limit:
                retry_after = max(1, int(self._window_seconds - (now - bucket[0])))
                return False, retry_after

            bucket.append(now)
            return True, 0


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        enabled: bool,
        max_request_size_bytes: int,
        max_upload_size_bytes: int,
        blocked_user_agents: list[str],
        upload_path_prefix: str,
    ) -> None:
        super().__init__(app)
        self._enabled = enabled
        self._max_request_size_bytes = max(1, max_request_size_bytes)
        self._max_upload_size_bytes = max(1, max_upload_size_bytes)
        self._blocked_user_agents = [value.lower().strip() for value in blocked_user_agents if value.strip()]
        self._upload_path_prefix = upload_path_prefix

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._enabled:
            return await call_next(request)

        user_agent = request.headers.get("user-agent", "").lower()
        if any(pattern in user_agent for pattern in self._blocked_user_agents):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "forbidden_client",
                    "message": "Blocked user-agent pattern detected",
                    "details": {},
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        size_header = request.headers.get("content-length")
        if size_header and size_header.isdigit():
            body_size = int(size_header)
            max_size = self._max_upload_size_bytes if request.url.path.startswith(self._upload_path_prefix) else self._max_request_size_bytes
            if body_size > max_size:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "payload_too_large",
                        "message": f"Request body exceeds max size of {max_size} bytes",
                        "details": {"limit_bytes": max_size},
                        "request_id": getattr(request.state, "request_id", None),
                    },
                )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        enabled: bool,
        requests_per_minute: int,
        exempt_path_prefixes: list[str],
    ) -> None:
        super().__init__(app)
        self._enabled = enabled
        self._limiter = _SlidingWindowLimiter(requests_per_minute=requests_per_minute)
        self._exempt_path_prefixes = [item.strip() for item in exempt_path_prefixes if item.strip()]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self._enabled or any(request.url.path.startswith(prefix) for prefix in self._exempt_path_prefixes):
            return await call_next(request)

        key = self._rate_limit_key(request)
        allowed, retry_after = self._limiter.allow(key)
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limited",
                    "message": "Too many requests. Please retry later.",
                    "details": {"retry_after_seconds": retry_after},
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
            response.headers["Retry-After"] = str(retry_after)
            return response

        return await call_next(request)

    def _rate_limit_key(self, request: Request) -> str:
        auth_sub = self._extract_subject(request)
        if auth_sub:
            return f"sub:{auth_sub}"

        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
            if ip:
                return f"ip:{ip}"

        host = request.client.host if request.client else "unknown"
        return f"ip:{host}"

    def _extract_subject(self, request: Request) -> str | None:
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.replace("Bearer ", "", 1).strip()
        parts = token.split(".")
        if len(parts) < 2:
            return None

        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        try:
            payload_raw = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_raw.decode("utf-8"))
        except Exception:
            return None

        sub = payload.get("sub") if isinstance(payload, dict) else None
        return str(sub) if isinstance(sub, str) and sub.strip() else None


class TelemetryMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, service_name: str = "backend_v5") -> None:
        super().__init__(app)
        self._tracer = trace.get_tracer(service_name) if trace else None
        meter = metrics.get_meter(service_name) if metrics else None
        self._request_counter = meter.create_counter("http.server.request.count") if meter else None
        self._duration_histogram = meter.create_histogram("http.server.request.duration", unit="ms") if meter else None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        started = time.perf_counter()
        route = request.url.path
        method = request.method
        attrs = {"http.method": method, "http.route": route}

        if self._tracer is None:
            response = await call_next(request)
        else:
            with self._tracer.start_as_current_span("http.request") as span:
                span.set_attribute("http.method", method)
                span.set_attribute("http.route", route)
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)

        duration_ms = (time.perf_counter() - started) * 1000.0
        attrs["http.status_code"] = getattr(response, "status_code", 500)
        if self._request_counter is not None:
            self._request_counter.add(1, attributes=attrs)
        if self._duration_histogram is not None:
            self._duration_histogram.record(duration_ms, attributes=attrs)

        return response
