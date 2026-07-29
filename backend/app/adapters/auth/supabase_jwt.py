"""Supabase JWT authentication adapter."""

from __future__ import annotations

from typing import Any

import jwt

from app.core.config import Settings
from app.core.errors import AppError
from app.ports.auth import AuthenticatedUser, AuthPort


class SupabaseJwtAuthAdapter(AuthPort):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def verify_token(self, token: str) -> AuthenticatedUser:
        if not self._settings.supabase_jwt_secret:
            raise AppError(
                status_code=500,
                error="auth_misconfigured",
                message="SUPABASE_JWT_SECRET is not configured.",
            )
        try:
            claims: dict[str, Any] = jwt.decode(
                token,
                self._settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except jwt.PyJWTError as exc:
            raise AppError(
                status_code=401,
                error="unauthorized",
                message="Invalid or expired token.",
            ) from exc

        user_id = str(claims.get("sub") or "").strip()
        if not user_id:
            raise AppError(
                status_code=401,
                error="unauthorized",
                message="Token subject is missing.",
            )
        return AuthenticatedUser(
            id=user_id,
            email=str(claims["email"]) if claims.get("email") else None,
            role=str(claims.get("role") or "authenticated"),
        )
