"""Domain layer — pure business entities and rules."""

from app.domain.exceptions import (
    AuthorizationError,
    DomainError,
    IngestionError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "AuthorizationError",
    "DomainError",
    "IngestionError",
    "NotFoundError",
    "ValidationError",
]
