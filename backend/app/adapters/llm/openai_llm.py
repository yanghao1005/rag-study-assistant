"""OpenAI chat / JSON generation adapter."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from app.ports.llm import (
    ChatCompletionMessage,
    GenerationResult,
    LLMPort,
    StructuredGenerationResult,
)


class OpenAILLMAdapter(LLMPort):
    def __init__(self, *, api_key: str, model: str = "gpt-4.1-mini") -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM provider=openai")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    def _to_openai_messages(self, messages: list[ChatCompletionMessage]) -> list[dict[str, str]]:
        return [{"role": message.role, "content": message.content} for message in messages]

    async def complete(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": self._to_openai_messages(messages),
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0].message
        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0,
            }
        return GenerationResult(
            content=choice.content or "",
            model=response.model,
            raw=response.model_dump(),
            usage=usage,
        )

    async def complete_json(
        self,
        *,
        messages: list[ChatCompletionMessage],
        schema_name: str,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> StructuredGenerationResult:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": self._to_openai_messages(messages),
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object for schema {schema_name}")

        usage = {}
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0,
            }
        return StructuredGenerationResult(
            data=data,
            model=response.model,
            raw=response.model_dump(),
            usage=usage,
        )

    async def stream(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": self._to_openai_messages(messages),
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        stream = await self._client.chat.completions.create(**kwargs)
        async for event in stream:
            delta = event.choices[0].delta.content if event.choices else None
            if delta:
                yield delta
