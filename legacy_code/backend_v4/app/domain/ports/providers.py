from typing import Protocol


class LLMProvider(Protocol):
    def generate_json(self, prompt: str) -> dict:
        ...


class EmbeddingsProvider(Protocol):
    def embed(self, text: str) -> list[float]:
        ...