"""Gemini chat / JSON generation adapter."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from google import genai
from google.genai import types

from app.ports.llm import (
    ChatCompletionMessage,
    GenerationResult,
    LLMPort,
    StructuredGenerationResult,
)


class GeminiLLMAdapter(LLMPort):
    def __init__(self, *, api_key: str, model: str = "gemini-2.5-flash") -> None:
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY is required for LLM provider=gemini")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def _split_system(
        self, messages: list[ChatCompletionMessage]
    ) -> tuple[str | None, list[ChatCompletionMessage]]:
        system_parts = [m.content for m in messages if m.role == "system"]
        rest = [m for m in messages if m.role != "system"]
        system = "\n\n".join(system_parts) if system_parts else None
        return system, rest

    def _to_contents(self, messages: list[ChatCompletionMessage]) -> list[types.Content]:
        contents: list[types.Content] = []
        for message in messages:
            role = "model" if message.role == "assistant" else "user"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=message.content)])
            )
        return contents

    async def complete(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        system, rest = self._split_system(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system,
        )
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=self._to_contents(rest),
            config=config,
        )
        usage: dict[str, int] = {}
        meta = getattr(response, "usage_metadata", None)
        if meta is not None:
            usage = {
                "prompt_tokens": int(getattr(meta, "prompt_token_count", 0) or 0),
                "completion_tokens": int(getattr(meta, "candidates_token_count", 0) or 0),
                "total_tokens": int(getattr(meta, "total_token_count", 0) or 0),
            }
        return GenerationResult(
            content=response.text or "",
            model=self._model,
            raw={"text": response.text},
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
        system, rest = self._split_system(messages)
        instruction = (
            f"{system or ''}\n\nRespond with a valid JSON object for schema `{schema_name}`."
        ).strip()
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=instruction,
            response_mime_type="application/json",
        )
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=self._to_contents(rest),
            config=config,
        )
        data = json.loads(response.text or "{}")
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object for schema {schema_name}")
        return StructuredGenerationResult(
            data=data,
            model=self._model,
            raw={"text": response.text},
            usage={},
        )

    async def stream(
        self,
        *,
        messages: list[ChatCompletionMessage],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        system, rest = self._split_system(messages)
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system,
        )
        stream = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=self._to_contents(rest),
            config=config,
        )
        async for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text
