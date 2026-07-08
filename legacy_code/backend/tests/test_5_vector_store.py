"""
Test 5: Vector Store Service
Tests Supabase vector storage and similarity search
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings, EmbeddingProvider
from app.services.pdf_parser import parse_pdf
from app.services.chapter_detector import detect_and_merge_chapters
from app.services.text_chunker import chunk_pages_text
from app.services.embedding_service import generate_embeddings_batch
from app.services.vector_store import (
    store_chunks,
    similarity_search,
    delete_document_chunks,
    get_document_chunks_count,
)


async def test_store_chunks():
    """Test storing chunks in vector database"""
    print("="*60)
    print("TEST 1: STORE CHUNKS")
    print("="*60)
    
    try:
        # Generate test UUIDs
        import uuid
        from app.core.database import get_db
        
        test_subject_id = str(uuid.uuid4())
        test_doc_id = str(uuid.uuid4())
        
        # Prepare test data
        print("\n1. Preparing test data...")
        print(f"   Subject ID: {test_subject_id}")
        print(f"   Document ID: {test_doc_id}")
        
        # Create subject and document in database first
        db = get_db()
        
        # Insert subject
        db.table("subjects").insert({
            "id": test_subject_id,
            "name": "Test Subject",
            "description": "Test subject for unit tests"
        }).execute()
        
        # Insert document
        db.table("documents").insert({
            "id": test_doc_id,
            "subject_id": test_subject_id,
            "title": "Test Document",
            "status": "completed"
        }).execute()
        
        print("   ✅ Created test subject and document")
        
        print("\n2. Preparing test chunks...")
        
        # Create sample chunks with embeddings
        test_chunks = [
            {
                "content": "Machine learning is a subset of artificial intelligence.",
                "metadata": {
                    "page_num": 1,
                    "chunk_index": 0,
                    "subject_id": test_subject_id,
                    "document_id": test_doc_id,
                }
            },
            {
                "content": "Deep learning uses neural networks with multiple layers.",
                "metadata": {
                    "page_num": 1,
                    "chunk_index": 1,
                    "subject_id": test_subject_id,
                    "document_id": test_doc_id,
                }
            },
        ]
        
        # Generate embeddings
        settings.embedding_provider = EmbeddingProvider.HUGGINGFACE
        settings.huggingface_embedding_model = "BAAI/bge-base-en-v1.5"
        
        enriched = await generate_embeddings_batch(test_chunks, batch_size=2)
        print(f"   ✅ Generated {len(enriched)} embeddings (dimension: {len(enriched[0]['embedding'])})")
        
        # Store in database
        print("\n3. Storing chunks in Supabase...")
        stored_count = await store_chunks(enriched, document_id=test_doc_id)
        
        print(f"   ✅ Stored {stored_count} chunks")
        
        # Verify storage
        count = await get_document_chunks_count(test_doc_id)
        print(f"\n4. Verification:")
        print(f"   Chunks in database: {count}")
        
        # Store for cleanup in other tests
        global stored_test_doc_id, stored_test_subject_id
        stored_test_doc_id = test_doc_id
        stored_test_subject_id = test_subject_id
        
        return True
        
    except Exception as e:
        print(f"❌ Error storing chunks: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_similarity_search():
    """Test similarity search"""
    print("\n" + "="*60)
    print("TEST 2: SIMILARITY SEARCH")
    print("="*60)
    
    try:
        # Use stored doc ID from previous test
        global stored_test_doc_id
        if 'stored_test_doc_id' not in globals():
            print("⚠️  Skipping: No test data from previous test")
            return False
        
        # Test query
        query = "What is deep learning?"
        
        print(f"\n   Query: '{query}'")
        print(f"   Searching in document: {stored_test_doc_id}")
        
        # Generate query embedding
        from app.services.embedding_service import generate_single_embedding
        query_embedding = await generate_single_embedding(query)
        
        # Perform search
        results = await similarity_search(
            query_embedding=query_embedding,
            document_id=stored_test_doc_id,
            top_k=5,
            similarity_threshold=0.0,
        )
        
        print(f"\n✅ Found {len(results)} results:")
        
        for idx, result in enumerate(results):
            print(f"\n   Result {idx + 1}:")
            print(f"      Similarity: {result['similarity']:.4f}")
            print(f"      Page: {result['metadata'].get('page_num', 'N/A')}")
            print(f"      Content: {result['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during similarity search: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_delete_chunks():
    """Test deleting document chunks"""
    print("\n" + "="*60)
    print("TEST 3: DELETE CHUNKS")
    print("="*60)
    
    try:
        # Use stored doc ID from previous test
        global stored_test_doc_id
        if 'stored_test_doc_id' not in globals():
            print("⚠️  Skipping: No test data from previous test")
            return False
        
        document_id = stored_test_doc_id
        
        # Check count before
        count_before = await get_document_chunks_count(document_id)
        print(f"\n   Chunks before deletion: {count_before}")
        
        # Delete
        print(f"\n   Deleting chunks for document: {document_id}")
        deleted_count = await delete_document_chunks(document_id)
        
        # Check count after
        count_after = await get_document_chunks_count(document_id)
        
        print(f"\n✅ Deletion complete:")
        print(f"   Deleted: {deleted_count} chunks")
        print(f"   Remaining: {count_after} chunks")
        
        # Cleanup: Delete document and subject
        from app.core.database import get_db
        db = get_db()
        
        # Get subject_id from stored test data
        if 'stored_test_subject_id' in globals():
            # Delete document (cascade will delete any remaining chunks)
            db.table("documents").delete().eq("id", document_id).execute()
            # Delete subject
            db.table("subjects").delete().eq("id", stored_test_subject_id).execute()
            print(f"   ✅ Cleaned up test subject and document")
        
        return True
        
    except Exception as e:
        print(f"❌ Error deleting chunks: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_pipeline():
    """Test full pipeline with real PDF"""
    print("\n" + "="*60)
    print("TEST 4: FULL PIPELINE (PDF → VECTOR DB)")
    print("="*60)
    
    pdf_path = "pdf_tests_documents/1_BMC_OBS.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        import uuid
        from app.core.database import get_db
        
        subject_id = str(uuid.uuid4())
        document_id = str(uuid.uuid4())
        
        print(f"   Subject ID: {subject_id}")
        print(f"   Document ID: {document_id}")
        
        # Create subject and document in database
        db = get_db()
        
        db.table("subjects").insert({
            "id": subject_id,
            "name": "Full Pipeline Test Subject",
            "description": "Subject for full pipeline test"
        }).execute()
        
        db.table("documents").insert({
            "id": document_id,
            "subject_id": subject_id,
            "title": "1_BMC_OBS.pdf",
            "status": "processing"
        }).execute()
        
        print("   ✅ Created test subject and document\n")
        
        # Parse PDF
        print("1. Parsing PDF...")
        metadata, pages = parse_pdf(pdf_path)
        print(f"   ✅ Extracted {len(pages)} pages")
        
        # Detect chapters
        print("\n2. Detecting chapters...")
        chapters = detect_and_merge_chapters(pages)
        print(f"   ✅ Found {len(chapters)} chapters")
        
        # Chunk (limit to first 3 for testing)
        print("\n3. Chunking text...")
        all_chunks = chunk_pages_text(
            pages_text=pages,
            chapters=chapters,
            subject_id=subject_id,
            document_id=document_id,
        )
        test_chunks = all_chunks[:3]  # Only test with 3 chunks
        print(f"   ✅ Created {len(all_chunks)} chunks (storing {len(test_chunks)})")
        
        # Generate embeddings
        print("\n4. Generating embeddings...")
        settings.embedding_provider = EmbeddingProvider.HUGGINGFACE
        settings.huggingface_embedding_model = "BAAI/bge-base-en-v1.5"
        
        enriched = await generate_embeddings_batch(test_chunks, batch_size=3)
        print(f"   ✅ Generated {len(enriched)} embeddings")
        
        # Store in database
        print("\n5. Storing in vector database...")
        stored_count = await store_chunks(enriched, document_id=document_id)
        print(f"   ✅ Stored {stored_count} chunks")
        
        # Test search
        print("\n6. Testing similarity search...")
        query = "What is the main topic?"
        from app.services.embedding_service import generate_single_embedding
        query_embedding = await generate_single_embedding(query)
        results = await similarity_search(query_embedding, document_id=document_id, top_k=2)
        print(f"   ✅ Found {len(results)} results for: '{query}'")
        
        if results:
            print(f"\n   Top result:")
            print(f"      Similarity: {results[0]['similarity']:.4f}")
            print(f"      Content: {results[0]['content'][:100]}...")
        
        # Cleanup
        print("\n7. Cleanup...")
        deleted = await delete_document_chunks(document_id)
        print(f"   ✅ Deleted {deleted} chunks")
        
        # Delete document and subject
        db.table("documents").delete().eq("id", document_id).execute()
        db.table("subjects").delete().eq("id", subject_id).execute()
        print(f"   ✅ Cleaned up test subject and document")
        
        print("\n✅ Full pipeline test successful")
        return True
        
    except Exception as e:
        print(f"❌ Error in full pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all vector store tests"""
    print("\n" + "="*60)
    print("VECTOR STORE SERVICE TESTS")
    print("="*60 + "\n")
    
    print(f"Configuration:")
    print(f"   Supabase URL: {settings.supabase_url}")
    print(f"   Embedding model: {settings.huggingface_embedding_model}\n")
    
    results = []
    
    # Test 1: Store chunks
    results.append(("Store Chunks", await test_store_chunks()))
    
    # Test 2: Similarity search
    results.append(("Similarity Search", await test_similarity_search()))
    
    # Test 3: Delete chunks
    results.append(("Delete Chunks", await test_delete_chunks()))
    
    # Test 4: Full pipeline
    results.append(("Full Pipeline", await test_full_pipeline()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(p for _, p in results)


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
