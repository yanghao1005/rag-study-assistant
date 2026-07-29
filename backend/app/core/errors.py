"""HTTP/application errors mapped to API responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    status_code: int
    error: str
    message: str

    def __str__(self) -> str:
        return self.message
