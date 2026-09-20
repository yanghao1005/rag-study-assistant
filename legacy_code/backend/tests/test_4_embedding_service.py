"""
Test 4: Embedding Service
Tests embedding generation with different providers
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings, EmbeddingProvider
from app.services.pdf_parser import parse_pdf
from app.services.chapter_detector import detect_and_merge_chapters
from app.services.text_chunker import chunk_pages_text
from app.services.embedding_service import (
    generate_embeddings_batch,
    generate_single_embedding,
    get_embedding_stats,
    validate_embeddings,
)


async def test_single_embedding():
    """Test generating a single embedding"""
    print("="*60)
    print("TEST 1: SINGLE EMBEDDING GENERATION")
    print("="*60)
    
    try:
        test_text = "This is a test sentence for embedding generation."
        
        print(f"\n   Text: '{test_text}'")
        print(f"   Provider: {settings.embedding_provider.value}")
        print(f"   Model: {settings.huggingface_embedding_model}")
        
        embedding = await generate_single_embedding(test_text)
        
        print(f"\n✅ Generated embedding:")
        print(f"   Dimension: {len(embedding)}")
        print(f"   First 5 values: {embedding[:5]}")
        print(f"   L2 norm: {sum(x*x for x in embedding)**0.5:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating single embedding: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_embeddings():
    """Test batch embedding generation"""
    print("\n" + "="*60)
    print("TEST 2: BATCH EMBEDDING GENERATION")
    print("="*60)
    
    try:
        # Create sample chunks
        sample_chunks = [
            {
                "content": "Machine learning is a subset of artificial intelligence.",
                "metadata": {"page_num": 1, "chunk_index": 0}
            },
            {
                "content": "Deep learning uses neural networks with multiple layers.",
                "metadata": {"page_num": 1, "chunk_index": 1}
            },
            {
                "content": "Natural language processing enables computers to understand text.",
                "metadata": {"page_num": 2, "chunk_index": 0}
            },
        ]
        
        print(f"\n   Processing {len(sample_chunks)} chunks...")
        print(f"   Provider: {settings.embedding_provider.value}")
        
        enriched_chunks = await generate_embeddings_batch(
            sample_chunks,
            batch_size=3
        )
        
        # Get stats
        stats = get_embedding_stats(enriched_chunks)
        
        print(f"\n✅ Batch embedding results:")
        print(f"   Successful: {stats['successful']}/{stats['total']}")
        print(f"   Dimension: {stats['dimension']}")
        print(f"   Average L2 norm: {stats['avg_norm']:.4f}")
        
        # Validate embeddings
        warnings = validate_embeddings(enriched_chunks)
        print(f"\n   Validation:")
        if warnings:
            print(f"      Warnings: {len(warnings)}")
            for warning in warnings:
                print(f"         - {warning}")
        else:
            print(f"      ✅ All embeddings valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating batch embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_pdf_embeddings():
    """Test embedding generation with real PDF content"""
    print("\n" + "="*60)
    print("TEST 3: PDF CONTENT EMBEDDINGS")
    print("="*60)
    
    pdf_path = "pdf_tests_documents/1_BMC_OBS.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        # Parse PDF
        print("\n1. Parsing PDF...")
        metadata, pages = parse_pdf(pdf_path)
        print(f"   ✅ Extracted {len(pages)} pages")
        
        # Detect chapters
        print("\n2. Detecting chapters...")
        chapters = detect_and_merge_chapters(pages)
        print(f"   ✅ Found {len(chapters)} chapters")
        
        # Chunk pages (limit to first 5 chunks for testing)
        print("\n3. Chunking text...")
        all_chunks = chunk_pages_text(
            pages_text=pages,
            chapters=chapters,
            subject_id="test-subject",
            document_id="test-doc",
        )
        test_chunks = all_chunks[:5]  # Only test first 5
        print(f"   ✅ Created {len(all_chunks)} chunks (testing with {len(test_chunks)})")
        
        # Generate embeddings
        print(f"\n4. Generating embeddings...")
        print(f"   Provider: {settings.embedding_provider.value}")
        print(f"   Model: {settings.huggingface_embedding_model}")
        
        import time
        start = time.time()
        enriched = await generate_embeddings_batch(test_chunks, batch_size=5)
        elapsed = time.time() - start
        
        # Get stats
        stats = get_embedding_stats(enriched)
        
        print(f"\n✅ Embedding generation complete:")
        print(f"   Time: {elapsed:.2f}s ({elapsed/len(test_chunks)*1000:.0f}ms per chunk)")
        print(f"   Successful: {stats['successful']}/{stats['total']}")
        print(f"   Dimension: {stats['dimension']}")
        print(f"   Average L2 norm: {stats['avg_norm']:.4f}")
        
        # Show sample
        print(f"\n   Sample embedded chunk:")
        sample = enriched[0]
        print(f"      Content preview: {sample['content'][:80]}...")
        print(f"      Embedding dimension: {len(sample['embedding'])}")
        print(f"      Page: {sample['metadata']['page_num']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all embedding tests"""
    print("\n" + "="*60)
    print("EMBEDDING SERVICE TESTS")
    print("="*60 + "\n")
    
    # Configure embedding provider
    settings.embedding_provider = EmbeddingProvider.HUGGINGFACE
    settings.huggingface_embedding_model = "BAAI/bge-base-en-v1.5"
    
    print(f"Configuration:")
    print(f"   Provider: {settings.embedding_provider.value}")
    print(f"   Model: {settings.huggingface_embedding_model}\n")
    
    results = []
    
    # Test 1: Single embedding
    results.append(("Single Embedding", await test_single_embedding()))
    
    # Test 2: Batch embeddings
    results.append(("Batch Embeddings", await test_batch_embeddings()))
    
    # Test 3: PDF embeddings
    results.append(("PDF Content Embeddings", await test_pdf_embeddings()))
    
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
