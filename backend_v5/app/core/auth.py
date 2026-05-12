from __future__ import annotations

import base64
import json

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.errors import AppError

bearer = HTTPBearer(auto_error=False)


class AuthUser(BaseModel):
    user_id: str
    role: str | None = None


def _decode_jwt_payload(token: str) -> dict:
    settings = get_settings()

    if settings.supabase_jwt_secret:
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            if not isinstance(payload, dict):
                raise AppError(error="invalid_token", message="Invalid token payload", status_code=401)
            return payload
        except jwt.PyJWTError as exc:
            raise AppError(error="unauthorized", message="Invalid bearer token", status_code=401) from exc

    parts = token.split(".")
    if len(parts) < 2:
        raise AppError(error="invalid_token", message="Malformed bearer token", status_code=401)

    payload_b64 = parts[1]
    padding = "=" * (-len(payload_b64) % 4)
    payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
    payload = json.loads(payload_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise AppError(error="invalid_token", message="Invalid token payload", status_code=401)
    return payload


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> AuthUser:
    if credentials is None or not credentials.credentials:
        raise AppError(error="unauthorized", message="Missing bearer token", status_code=401)

    claims = _decode_jwt_payload(credentials.credentials)
    user_id = claims.get("sub")
    if not isinstance(user_id, str) or not user_id.strip():
        raise AppError(error="unauthorized", message="Token subject is missing", status_code=401)

    role = claims.get("role")
    return AuthUser(user_id=user_id, role=role if isinstance(role, str) else None)
