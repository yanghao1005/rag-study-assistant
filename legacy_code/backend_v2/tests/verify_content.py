import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

# Load Env
load_dotenv(project_root / ".env")

from src.infrastructure.supabase.client import SupabaseClient

async def verify_content():
    client = SupabaseClient.get_instance()
    
    # Check for "Chapter"
    print("Checking for 'Chapter' in content...")
    res = client.table('document_chunks').select('content, page_num').ilike('content', '%chapter%').execute()
    
    print(f"Chunks containing 'Chapter': {len(res.data)}")
    for c in res.data:
        print(f"[Page {c['page_num']}] ...{c['content'][:50]}...")

    # Check for "1"
    print("\nChecking for '1' in content (Page 1 only)...")
    res = client.table('document_chunks').select('content, page_num').eq('page_num', 1).execute()
    for c in res.data:
        print(f"[Page 1 Content]:\n{c['content']}")

if __name__ == "__main__":
    asyncio.run(verify_content())
