"""
Database connection and session management
"""
from supabase import create_client, Client
from app.core.config import settings


class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.client: Client = None
    
    def connect(self):
        """Initialize Supabase client"""
        self.client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        return self.client
    
    def get_client(self) -> Client:
        """Get Supabase client instance"""
        if not self.client:
            self.connect()
        return self.client


# Global database instance
db = Database()


def get_db() -> Client:
    """Dependency for FastAPI routes"""
    return db.get_client()
