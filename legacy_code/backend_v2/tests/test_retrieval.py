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
from src.domain.entities import Subject

async def run_retrieval_test(query: str):
    print(f"--- Setting up Container ---")
    container = Container.get_instance()
    
    # 1. Get Subject
    print(f"--- Fetching Benchmark Subject ---")
    subjects = await container.subject_repository.get_all()
    # Find the one named "Benchmark Test Subject"
    subject = next((s for s in subjects if s.name == "Benchmark Test Subject"), None)
    
    if not subject:
        print("ERROR: 'Benchmark Test Subject' not found. Run test_benchmark.py first to create it.")
        return

    print(f"Using Subject: {subject.name} ({subject.id})")

    # 2. Embed Query
    print(f"\n--- Embedding Query: '{query}' ---")
    query_embedding = await container.embedding_service.embed_text(query)
    print(f"Embedding generated (Dimensions: {len(query_embedding)})")

    # 3. Search
    print(f"\n--- Searching Vector Store (Top 5) ---")
    results = await container.vector_store.search(
        query_embedding=query_embedding,
        top_k=5,
        subject_id=subject.id,
        threshold=0.01 # Lower threshold to debug visibility
    )

    # 4. Print Results
    print(f"\n--- Results ({len(results)} chunks found) ---")
    for i, chunk in enumerate(results):
        # Handle dict or object
        content = chunk.get("content") if isinstance(chunk, dict) else chunk.content
        meta = chunk.get("metadata") if isinstance(chunk, dict) else chunk.metadata
        score = chunk.get("similarity") if isinstance(chunk, dict) else getattr(chunk, "similarity", "N/A")
        
        print(f"\nResult {i+1}:")
        print(f"Similarity: {score}")
        print(f"Metadata: {meta}")
        print(f"Content Preview: {content[:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Vector Retrieval")
    parser.add_argument("query", help="The query string to search for")
    args = parser.parse_args()
    
    asyncio.run(run_retrieval_test(args.query))
