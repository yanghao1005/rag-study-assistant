from supabase import create_client, Client
from src.config import get_settings

class SupabaseClient:
    _instance: Client = None

    @classmethod
    def get_instance(cls) -> Client:
        if cls._instance is None:
            settings = get_settings()
            cls._instance = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
