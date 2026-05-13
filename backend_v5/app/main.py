from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.middleware import AbuseProtectionMiddleware, RateLimitMiddleware, RequestIdMiddleware, TelemetryMiddleware
from app.core.telemetry import configure_telemetry
from app.presentation.api.router import api_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    allowed_origins = [origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()]
    allow_all_origins = "*" in allowed_origins
    if allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"] if allow_all_origins else allowed_origins,
            allow_credentials=not allow_all_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"],
        )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        AbuseProtectionMiddleware,
        enabled=settings.enable_abuse_protection,
        max_request_size_bytes=settings.max_request_size_bytes,
        max_upload_size_bytes=settings.max_upload_size_bytes,
        blocked_user_agents=settings.blocked_user_agents.split(","),
        upload_path_prefix=f"{settings.api_prefix}/documents/upload",
    )
    app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.enable_rate_limit,
        requests_per_minute=settings.rate_limit_requests_per_minute,
        exempt_path_prefixes=settings.rate_limit_exempt_paths.split(","),
    )
    app.add_middleware(TelemetryMiddleware, service_name=settings.otel_service_name)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)
    configure_telemetry(app=app, settings=settings)
    return app


app = create_app()
