import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

# Setup path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Load Env
load_dotenv(project_root / ".env")

from src.config import get_settings
from supabase import create_client, Client

async def test_conn():
    settings = get_settings()
    
    print(f"--- DEBUG INFO ---")
    print(f"SUPABASE_URL from Env: '{os.getenv('SUPABASE_URL')}'")
    print(f"SUPABASE_URL from Settings: '{settings.SUPABASE_URL}'")
    print(f"SUPABASE_KEY loaded: {'Yes' if settings.SUPABASE_KEY else 'No'}")
    
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    
    if not url or "your-project" in url:
        print("ERROR: URL looks invalid or placeholder.")
        return

    try:
        print(f"Attempting to connect to {url}...")
        supabase: Client = create_client(url, key)
        # Try a simple health check or table list (if possible, or just a dummy query)
        # We'll just try to select from a non-existent table to see if we reach the server
        # or just check if the client initialization failed (it's usually lazy though)
        
        # Real network check
        print("Making network request...")
        # Assuming 'documents' table exists, or just check 'subjects'
        response = supabase.table("subjects").select("*").limit(1).execute()
        print("Connection SUCCESS!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Connection FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
