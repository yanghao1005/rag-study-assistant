"""Supabase Storage adapter."""

from __future__ import annotations

from app.ports.storage import StoragePort, StoredObject
from supabase import Client


class SupabaseStorageAdapter(StoragePort):
    def __init__(self, client: Client, *, bucket: str = "documents") -> None:
        self._client = client
        self._bucket = bucket

    async def upload(
        self,
        *,
        path: str,
        data: bytes,
        content_type: str,
        upsert: bool = False,
    ) -> StoredObject:
        options = {"content-type": content_type, "upsert": str(upsert).lower()}
        self._client.storage.from_(self._bucket).upload(path, data, file_options=options)
        return StoredObject(
            path=path,
            bucket=self._bucket,
            size_bytes=len(data),
            content_type=content_type,
        )

    async def download(self, *, path: str) -> bytes:
        data = self._client.storage.from_(self._bucket).download(path)
        return bytes(data)

    async def delete(self, *, path: str) -> None:
        self._client.storage.from_(self._bucket).remove([path])

    async def create_signed_url(self, *, path: str, expires_in: int = 3600) -> str:
        result = self._client.storage.from_(self._bucket).create_signed_url(path, expires_in)
        signed = result.get("signedURL") or result.get("signedUrl")
        if not signed:
            raise RuntimeError(f"Failed to create signed URL for {path}")
        return str(signed)
