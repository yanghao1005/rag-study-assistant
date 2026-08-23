"""Supabase profile repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.entities.profile import Profile
from app.ports.repositories import ProfileRepositoryPort
from supabase import Client


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _profile_from_row(row: dict[str, Any]) -> Profile:
    return Profile(
        id=str(row["id"]),
        display_name=row.get("display_name"),
        avatar_url=row.get("avatar_url"),
        onboarding_completed=bool(row.get("onboarding_completed")),
        preferences=row.get("preferences") or {},
        created_at=_parse_dt(row.get("created_at")),
        updated_at=_parse_dt(row.get("updated_at")),
    )


class SupabaseProfileRepository(ProfileRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def get(self, user_id: str) -> Profile | None:
        response = (
            self._client.table("profiles").select("*").eq("id", user_id).limit(1).execute()
        )
        if not response.data:
            return None
        return _profile_from_row(response.data[0])

    async def upsert(self, profile: Profile) -> Profile:
        payload = {
            "id": profile.id,
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "onboarding_completed": profile.onboarding_completed,
            "preferences": profile.preferences,
        }
        response = self._client.table("profiles").upsert(payload, on_conflict="id").execute()
        return _profile_from_row(response.data[0])
