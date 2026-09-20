"""Supabase subjects repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.domain.entities.subject import Subject
from app.ports.repositories import SubjectRepositoryPort
from supabase import Client


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _from_row(row: dict[str, Any]) -> Subject:
    return Subject(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=str(row["name"]),
        description=row.get("description"),
        color=row.get("color"),
        sort_order=int(row.get("sort_order") or 0),
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


class SupabaseSubjectRepository(SubjectRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create(self, subject: Subject) -> Subject:
        payload = {
            "id": subject.id or str(uuid4()),
            "user_id": subject.user_id,
            "name": subject.name,
            "description": subject.description,
            "color": subject.color,
            "sort_order": subject.sort_order,
        }
        response = self._client.table("subjects").insert(payload).execute()
        return _from_row(response.data[0])

    async def get(self, *, user_id: str, subject_id: str) -> Subject | None:
        response = (
            self._client.table("subjects")
            .select("*")
            .eq("id", subject_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _from_row(response.data[0])

    async def list_for_user(self, user_id: str) -> list[Subject]:
        response = (
            self._client.table("subjects")
            .select("*")
            .eq("user_id", user_id)
            .order("sort_order")
            .order("created_at")
            .execute()
        )
        return [_from_row(row) for row in response.data or []]

    async def update(self, subject: Subject) -> Subject:
        payload = {
            "name": subject.name,
            "description": subject.description,
            "color": subject.color,
            "sort_order": subject.sort_order,
        }
        response = (
            self._client.table("subjects")
            .update(payload)
            .eq("id", subject.id)
            .eq("user_id", subject.user_id)
            .execute()
        )
        return _from_row(response.data[0])

    async def delete(self, *, user_id: str, subject_id: str) -> bool:
        response = (
            self._client.table("subjects")
            .delete()
            .eq("id", subject_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(response.data)
