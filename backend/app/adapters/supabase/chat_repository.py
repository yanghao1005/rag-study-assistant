"""Supabase chat repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from supabase import Client

from app.domain.entities.chat import ChatMessage, ChatThread
from app.domain.entities.enums import ChatRole
from app.ports.repositories import ChatRepositoryPort


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


class SupabaseChatRepository(ChatRepositoryPort):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def create_thread(self, thread: ChatThread) -> ChatThread:
        payload = {
            "id": thread.id or str(uuid4()),
            "user_id": thread.user_id,
            "subject_id": thread.subject_id,
            "title": thread.title,
        }
        response = self._client.table("chat_threads").insert(payload).execute()
        row = response.data[0]
        return ChatThread(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            subject_id=str(row["subject_id"]),
            title=str(row["title"]),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
        )

    async def get_thread(self, *, user_id: str, thread_id: str) -> ChatThread | None:
        response = (
            self._client.table("chat_threads")
            .select("*")
            .eq("id", thread_id)
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        row = response.data[0]
        return ChatThread(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            subject_id=str(row["subject_id"]),
            title=str(row["title"]),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
        )

    async def list_threads(self, *, user_id: str, subject_id: str) -> list[ChatThread]:
        response = (
            self._client.table("chat_threads")
            .select("*")
            .eq("user_id", user_id)
            .eq("subject_id", subject_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return [
            ChatThread(
                id=str(row["id"]),
                user_id=str(row["user_id"]),
                subject_id=str(row["subject_id"]),
                title=str(row["title"]),
                created_at=_parse_dt(row.get("created_at")),
                updated_at=_parse_dt(row.get("updated_at")),
            )
            for row in response.data or []
        ]

    async def add_message(self, message: ChatMessage) -> ChatMessage:
        payload = {
            "id": message.id or str(uuid4()),
            "user_id": message.user_id,
            "thread_id": message.thread_id,
            "role": message.role.value,
            "content": message.content,
            "citations": message.citations,
            "model": message.model,
            "token_usage": message.token_usage,
        }
        response = self._client.table("chat_messages").insert(payload).execute()
        row = response.data[0]
        return ChatMessage(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            thread_id=str(row["thread_id"]),
            role=ChatRole(row["role"]),
            content=str(row["content"]),
            citations=list(row.get("citations") or []),
            model=row.get("model"),
            token_usage=row.get("token_usage"),
            created_at=_parse_dt(row.get("created_at")),
        )

    async def list_messages(
        self, *, user_id: str, thread_id: str, limit: int = 100
    ) -> list[ChatMessage]:
        response = (
            self._client.table("chat_messages")
            .select("*")
            .eq("user_id", user_id)
            .eq("thread_id", thread_id)
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return [
            ChatMessage(
                id=str(row["id"]),
                user_id=str(row["user_id"]),
                thread_id=str(row["thread_id"]),
                role=ChatRole(row["role"]),
                content=str(row["content"]),
                citations=list(row.get("citations") or []),
                model=row.get("model"),
                token_usage=row.get("token_usage"),
                created_at=_parse_dt(row.get("created_at")),
            )
            for row in response.data or []
        ]
