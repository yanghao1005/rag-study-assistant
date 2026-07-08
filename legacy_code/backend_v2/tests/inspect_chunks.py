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

from src.container import Container
from src.infrastructure.supabase.client import SupabaseClient

async def inspect_chunks():
    print(f"--- Connecting to Supabase ---")
    container = Container.get_instance()
    client = SupabaseClient.get_instance()
    
    # 1. Get Benchmark Subject
    subjects = await container.subject_repository.get_all()
    subject = next((s for s in subjects if s.name == "Benchmark Test Subject"), None)
    
    if not subject:
        print("Subject not found.")
        return

    print(f"Subject: {subject.name} ({subject.id})")
    
    # 2. Get Documents
    documents = await container.document_repository.get_by_subject(subject.id)
    print(f"Found {len(documents)} documents.")
    
    for doc in documents:
        print(f"\nDocument: {doc.title} ({doc.id})")
        
        # 3. Get Chunks (Raw Query)
        response = client.table("document_chunks").select("chunk_index, content, page_num, metadata").eq("document_id", str(doc.id)).execute()
        chunks = response.data
        
        print(f"Chunks Count: {len(chunks)}")
        
        # Print first 3 chunks and last 3 chunks
        if chunks:
            print("\n-- First 3 Chunks --")
            for c in chunks[:3]:
                print(f"[Page {c['page_num']} Index {c['chunk_index']}] Content ({len(c['content'])} chars):")
                print(f"'{c['content'][:100]}...'") # First 100 chars
            
            print("\n-- Last 3 Chunks --")
            for c in chunks[-3:]:
                print(f"[Page {c['page_num']} Index {c['chunk_index']}] Content ({len(c['content'])} chars):")
                print(f"'{c['content'][:100]}...'")

if __name__ == "__main__":
    asyncio.run(inspect_chunks())
