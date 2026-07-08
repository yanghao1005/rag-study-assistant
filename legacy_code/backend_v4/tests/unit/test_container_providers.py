from app import container


def test_container_uses_memory_repo_by_default(monkeypatch) -> None:
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")
    container.get_settings.cache_clear()
    container.get_vector_repository.cache_clear()
    repo = container.get_vector_repository()
    assert repo.__class__.__name__ == "InMemoryVectorRepository"

    container.get_settings.cache_clear()
    container.get_vector_repository.cache_clear()


def test_container_supabase_without_keys_falls_back_to_memory(monkeypatch) -> None:
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "supabase")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)

    container.get_settings.cache_clear()
    container.get_vector_repository.cache_clear()


def test_container_openai_llm_without_key_falls_back_to_stub(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")

    container.get_settings.cache_clear()
    container.get_llm_provider.cache_clear()
    provider = container.get_llm_provider()
    assert provider.__class__.__name__ == "LLMProvider"

    container.get_settings.cache_clear()
    container.get_llm_provider.cache_clear()


def test_container_openai_embeddings_without_key_falls_back_to_stub(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("VECTOR_REPOSITORY_PROVIDER", "memory")

    container.get_settings.cache_clear()
    container.get_embeddings_provider.cache_clear()
    provider = container.get_embeddings_provider()
    assert provider.__class__.__name__ == "EmbeddingsProvider"

    container.get_settings.cache_clear()
    container.get_embeddings_provider.cache_clear()
    container.get_vector_repository.cache_clear()
    repo = container.get_vector_repository()
    assert repo.__class__.__name__ == "InMemoryVectorRepository"

    container.get_settings.cache_clear()
    container.get_vector_repository.cache_clear()

    container.get_settings.cache_clear()
    container.get_vector_repository.cache_clear()
