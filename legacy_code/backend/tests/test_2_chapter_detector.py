"""
Test 2: Chapter Detection Service
Tests chapter detection and boundary merging
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_parser import parse_pdf
from app.services.chapter_detector import detect_and_merge_chapters, find_chapter_for_page


def test_chapter_detection():
    """Test chapter detection from PDF pages"""
    print("="*60)
    print("TEST: CHAPTER DETECTION")
    print("="*60)
    
    pdf_path = "pdf_tests_documents/1_BMC_OBS.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        # First parse the PDF
        print("\n1. Parsing PDF...")
        metadata, pages = parse_pdf(pdf_path)
        print(f"   ✅ Extracted {len(pages)} pages")
        
        # Detect chapters
        print("\n2. Detecting chapters...")
        chapters = detect_and_merge_chapters(pages)
        print(f"   ✅ Found {len(chapters)} chapters")
        
        # Display chapter info
        if chapters:
            print(f"\n📚 Chapter Details:")
            for ch in chapters:
                print(f"\n   Chapter {ch['order_index'] + 1}: {ch['name']}")
                print(f"      Pages: {ch['start_page']}-{ch['end_page']}")
                print(f"      Total pages: {ch['end_page'] - ch['start_page'] + 1}")
        else:
            print(f"\n   ℹ️ No chapters detected (single chapter document)")
        
        # Test page lookup
        print(f"\n3. Testing page-to-chapter mapping...")
        test_pages = [1, 5, 10, len(pages)]
        for page_num in test_pages:
            if page_num <= len(pages):
                chapter = find_chapter_for_page(page_num, chapters)
                if chapter:
                    print(f"   Page {page_num} → {chapter['name']}")
                else:
                    print(f"   Page {page_num} → No chapter")
        
        print(f"\n✅ Chapter detection successful")
        return True
        
    except Exception as e:
        print(f"❌ Error during chapter detection: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("CHAPTER DETECTION SERVICE TESTS")
    print("="*60 + "\n")
    
    success = test_chapter_detection()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"Chapter Detection Test: {status}")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
