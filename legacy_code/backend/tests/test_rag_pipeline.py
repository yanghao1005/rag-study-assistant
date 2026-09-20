"""
Integration test for RAG pipeline
"""
import asyncio
import os
from app.services.rag_service import RAGService
from app.services.content_generator import ContentGenerator

async def test_rag_pipeline():
    print("=== Testing RAG Pipeline ===")
    
    # 1. Test RAG Service Retrieval
    print("\n1. Testing Context Retrieval...")
    rag = RAGService()
    
    # Note: This assumes we have some data in the DB.
    # If the DB is empty, this will just return empty list (which is valid for a test run)
    # We use a broad query to try and hit something
    results = await rag.retrieve_context(
        query="summary", 
        scope="subject", 
        scope_id="00000000-0000-0000-0000-000000000000", # Dummy ID
        top_k=1
    )
    print(f"   Retrieval call successful. Found {len(results)} chunks.")

    # 2. Test Content Generation (Mocking retrieval to avoid empty context)
    print("\n2. Testing Content Generator (Flashcards)...")
    generator = ContentGenerator()
    
    # Mock context
    mock_context = [
        {
            "id": "mock-1",
            "content": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar.",
            "metadata": {"chapter_name": "Biology 101", "page_num": 10}
        },
        {
            "id": "mock-2",
            "content": "Mitochondria are known as the powerhouses of the cell. They produce the energy necessary for the cell's survival and functioning.",
            "metadata": {"chapter_name": "Biology 101", "page_num": 12}
        }
    ]
    
    # We patch the retrieve_context method to return our mock
    future = asyncio.Future()
    future.set_result(mock_context)
    generator.rag_service.retrieve_context = lambda *args, **kwargs: future
    
    try:
        # Check OPENAI_API_KEY presence
        from app.core.config import settings
        if not settings.openai_api_key:
            print("❌ SKIPPING GENERATION: No OpenAI API Key found in settings.")
        else:
            flashcards = await generator.generate_flashcards(
                scope="subject",
                scope_id="dummy",
                topic="Biology",
                count=2
            )
            print(f"   Generated {len(flashcards['flashcards'])} flashcards.")
            for card in flashcards['flashcards']:
                print(f"   - Q: {card['front']} | A: {card['back']}")
                
    except Exception as e:
        print(f"❌ Error during generation: {e}")
    finally:
         # Restore
         # generator.rag_service.retrieve_context = original_retrieve # Not strictly needed as script ends
         pass

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_rag_pipeline())
