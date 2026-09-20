from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import jwt
from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.errors import AppError


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: str


def _bearer_token_from_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise AppError(status_code=401, error="unauthorized", message="Missing authorization header.")

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise AppError(status_code=401, error="unauthorized", message="Invalid authorization header.")
    return authorization[len(prefix) :].strip()


def decode_token_optional(token: str, settings: Settings) -> dict[str, Any] | None:
    if not token or not settings.supabase_jwt_secret:
        return None
    try:
        claims = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return claims if isinstance(claims, dict) else None
    except jwt.PyJWTError:
        return None


def decode_token_required(token: str, settings: Settings) -> dict[str, Any]:
    claims = decode_token_optional(token=token, settings=settings)
    if not claims:
        raise AppError(status_code=401, error="unauthorized", message="Invalid or expired token.")
    return claims


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    token = _bearer_token_from_header(authorization=authorization)
    claims = decode_token_required(token=token, settings=settings)
    user_id = str(claims.get("sub") or "").strip()
    role = str(claims.get("role") or "authenticated").strip()
    if not user_id:
        raise AppError(status_code=401, error="unauthorized", message="Token subject is missing.")
    return CurrentUser(user_id=user_id, role=role)

