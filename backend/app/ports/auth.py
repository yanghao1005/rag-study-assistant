"""Authentication port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    id: str
    email: str | None = None
    role: str | None = None


class AuthPort(ABC):
    """Verifies JWTs / sessions issued by the identity provider."""

    @abstractmethod
    async def verify_token(self, token: str) -> AuthenticatedUser:
        """Validate a bearer token and return the authenticated principal."""
        ...
