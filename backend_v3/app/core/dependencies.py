from functools import lru_cache

from app.core.database import get_supabase_client
from app.infrastructure.repository import InMemoryVectorRepository, SupabaseVectorRepository, VectorRepository


@lru_cache(maxsize=1)
def get_vector_repository() -> VectorRepository:
    supabase_client = get_supabase_client()
    if supabase_client is not None:
        return SupabaseVectorRepository(supabase_client)
    return InMemoryVectorRepository()


def reset_in_memory_repository() -> None:
    repo = get_vector_repository()
    if isinstance(repo, InMemoryVectorRepository):
        repo.clear()
