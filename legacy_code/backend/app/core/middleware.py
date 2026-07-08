import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to logger context if using structured logging
        # (This is a simplified version, ideally we'd use a context var)
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
