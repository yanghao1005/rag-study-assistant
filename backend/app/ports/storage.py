"""Object storage port (e.g. Supabase Storage)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoredObject:
    path: str
    bucket: str
    size_bytes: int
    content_type: str | None = None


class StoragePort(ABC):
    """Binary object storage for uploaded study documents."""

    @abstractmethod
    async def upload(
        self,
        *,
        path: str,
        data: bytes,
        content_type: str,
        upsert: bool = False,
    ) -> StoredObject:
        ...

    @abstractmethod
    async def download(self, *, path: str) -> bytes:
        ...

    @abstractmethod
    async def delete(self, *, path: str) -> None:
        ...

    @abstractmethod
    async def create_signed_url(self, *, path: str, expires_in: int = 3600) -> str:
        ...
