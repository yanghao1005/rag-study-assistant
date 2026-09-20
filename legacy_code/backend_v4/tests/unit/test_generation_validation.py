from app.application.use_cases.generation_service import GenerationService
from app.infrastructure.repositories.vector_repository import InMemoryVectorRepository


class InvalidThenValidProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate_json(self, prompt: str) -> dict:
        _ = prompt
        self.calls += 1
        if self.calls == 1:
            return {"flashcards": [{"front": "missing_back"}]}
        return {
            "flashcards": [{"front": "Question", "back": "Answer"}],
            "sources": [{"document_type": "pdf", "page": 1, "preview": "Excerpt"}],
        }


def test_generation_service_flashcards_shape() -> None:
    service = GenerationService(vector_repository=InMemoryVectorRepository())
    result = service.generate_flashcards({"scope": "subject", "scope_id": "sub-1", "count": 2})
    assert "flashcards" in result
    assert "diagnostics" in result
    assert result["diagnostics"]["scope"] == "subject"


def test_generation_service_retries_on_invalid_llm_output() -> None:
    provider = InvalidThenValidProvider()
    service = GenerationService(vector_repository=InMemoryVectorRepository(), llm_provider=provider)
    result = service.generate_flashcards({"scope": "subject", "scope_id": "sub-1", "count": 1})
    assert provider.calls == 2
    assert result["flashcards"][0]["front"] == "Question"
