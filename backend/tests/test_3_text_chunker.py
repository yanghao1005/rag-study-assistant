"""
Test 3: Text Chunking Service
Tests text chunking with metadata enrichment
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_parser import parse_pdf
from app.services.chapter_detector import detect_and_merge_chapters
from app.services.text_chunker import (
    chunk_pages_text,
    chunk_text_with_metadata,
    get_chunk_stats,
    merge_small_chunks,
)


def test_basic_chunking():
    """Test basic text chunking functionality"""
    print("="*60)
    print("TEST 1: BASIC TEXT CHUNKING")
    print("="*60)
    
    sample_text = """
    This is a sample paragraph that demonstrates text chunking functionality.
    The text splitter will attempt to break this text at natural boundaries.
    
    This is a second paragraph. It contains multiple sentences. Each sentence
    provides some information. The chunker should respect paragraph breaks.
    
    And here is a third paragraph with additional content that extends
    the total length of the text to ensure multiple chunks are created.
    """ * 3
    
    try:
        chunks = chunk_text_with_metadata(
            text=sample_text,
            page_num=1,
            chapter={"name": "Test Chapter", "order_index": 0},
            chunk_size=300,
            chunk_overlap=50,
        )
        
        print(f"\n✅ Created {len(chunks)} chunks")
        
        # Show chunk details
        for idx, chunk in enumerate(chunks[:3]):  # Show first 3
            print(f"\n   Chunk {idx + 1}:")
            print(f"      Size: {chunk['metadata']['char_count']} chars")
            print(f"      Page: {chunk['metadata']['page_num']}")
            print(f"      Chapter: {chunk['metadata'].get('chapter_name', 'N/A')}")
            print(f"      Preview: {chunk['content'][:80].strip()}...")
        
        if len(chunks) > 3:
            print(f"\n   ... and {len(chunks) - 3} more chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during basic chunking: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_chunking():
    """Test chunking with real PDF content"""
    print("\n" + "="*60)
    print("TEST 2: PDF DOCUMENT CHUNKING")
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
        
        # Chunk all pages
        print("\n3. Chunking all pages...")
        chunks = chunk_pages_text(
            pages_text=pages,
            chapters=chapters,
            subject_id="test-subject-123",
            document_id="test-doc-456",
            chunk_size=1000,
            chunk_overlap=200,
        )
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # Get statistics
        stats = get_chunk_stats(chunks)
        print(f"\n📊 Chunk Statistics:")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Average size: {stats['avg_size']} chars")
        print(f"   Size range: {stats['min_size']}-{stats['max_size']} chars")
        print(f"   Pages covered: {stats['pages_covered']}")
        
        # Show sample chunks
        print(f"\n📝 Sample Chunks:")
        for idx in [0, len(chunks)//2, -1]:  # First, middle, last
            chunk = chunks[idx]
            print(f"\n   Chunk {idx + 1 if idx >= 0 else len(chunks)}:")
            print(f"      Page: {chunk['metadata']['page_num']}")
            print(f"      Size: {chunk['metadata']['char_count']} chars")
            print(f"      Chapter: {chunk['metadata'].get('chapter_name', 'N/A')}")
            print(f"      Preview: {chunk['content'][:100].strip()}...")
        
        print(f"\n✅ PDF chunking successful")
        return True
        
    except Exception as e:
        print(f"❌ Error during PDF chunking: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunk_merging():
    """Test merging small chunks"""
    print("\n" + "="*60)
    print("TEST 3: CHUNK MERGING")
    print("="*60)
    
    try:
        # Create some test chunks with varying sizes
        test_chunks = [
            {"content": "Small chunk 1", "metadata": {"char_count": 13}},
            {"content": "Small chunk 2", "metadata": {"char_count": 13}},
            {"content": "This is a larger chunk with more content that exceeds minimum size", "metadata": {"char_count": 67}},
            {"content": "Tiny", "metadata": {"char_count": 4}},
            {"content": "Another sufficient size chunk for testing purposes", "metadata": {"char_count": 51}},
        ]
        
        print(f"\n   Original chunks: {len(test_chunks)}")
        for idx, chunk in enumerate(test_chunks):
            print(f"      {idx + 1}. {chunk['metadata']['char_count']} chars")
        
        merged = merge_small_chunks(test_chunks, min_chunk_size=50, max_chunk_size=200)
        
        print(f"\n   Merged chunks: {len(merged)}")
        for idx, chunk in enumerate(merged):
            print(f"      {idx + 1}. {chunk['metadata']['char_count']} chars: {chunk['content'][:50]}...")
        
        print(f"\n✅ Chunk merging successful")
        return True
        
    except Exception as e:
        print(f"❌ Error during chunk merging: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("TEXT CHUNKING SERVICE TESTS")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Basic chunking
    results.append(("Basic Text Chunking", test_basic_chunking()))
    
    # Test 2: PDF chunking
    results.append(("PDF Document Chunking", test_pdf_chunking()))
    
    # Test 3: Chunk merging
    results.append(("Chunk Merging", test_chunk_merging()))
    
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


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
