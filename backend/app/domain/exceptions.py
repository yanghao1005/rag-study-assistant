"""Domain-level exceptions (framework-agnostic)."""

from __future__ import annotations


class DomainError(Exception):
    """Base domain error."""


class NotFoundError(DomainError):
    def __init__(self, entity: str, entity_id: str) -> None:
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} not found: {entity_id}")


class AuthorizationError(DomainError):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(message)


class ValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class IngestionError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
