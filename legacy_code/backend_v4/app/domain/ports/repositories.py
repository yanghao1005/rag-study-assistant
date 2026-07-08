from typing import Protocol


class VectorRepository(Protocol):
    def save_chunks(self, *, document_id: str, chunks: list[dict], scope: str, scope_id: str, user_id: str) -> int:
        ...

    def retrieve(self, *, scope: str, scope_id: str, query: str | None, limit: int) -> list[dict]:
        ...

    def save_generated(self, payload: dict) -> None:
        ...

    def list_generated(self, *, user_id: str, scope: str, scope_id: str, limit: int) -> list[dict]:
        ...
