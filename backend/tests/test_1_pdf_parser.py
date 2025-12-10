"""
Test 1: PDF Parser Service
Tests PDF validation, text extraction, and metadata extraction
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_parser import validate_pdf, parse_pdf


def test_pdf_validation():
    """Test PDF validation"""
    print("="*60)
    print("TEST 1: PDF VALIDATION")
    print("="*60)
    
    pdf_path = "pdf_tests_documents/1_BMC_OBS.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        return False
    
    try:
        is_valid = validate_pdf(pdf_path)
        if is_valid:
            print(f"✅ PDF validation passed: {pdf_path}")
            return True
        else:
            print(f"❌ PDF validation failed: {pdf_path}")
            return False
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False


def test_pdf_parsing():
    """Test PDF text extraction"""
    print("\n" + "="*60)
    print("TEST 2: PDF PARSING")
    print("="*60)
    
    pdf_path = "pdf_tests_documents/1_BMC_OBS.pdf"
    
    try:
        metadata, pages = parse_pdf(pdf_path)
        
        print(f"\n📄 Metadata:")
        print(f"   Title: {metadata.get('title', 'N/A')}")
        print(f"   Pages: {metadata['total_pages']}")
        print(f"   Author: {metadata.get('author', 'N/A')}")
        
        print(f"\n📝 Pages extracted: {len(pages)}")
        
        # Show first 3 pages
        for i, page in enumerate(pages[:3]):
            print(f"\n   Page {page['page_num']}:")
            print(f"      Characters: {page['char_count']}")
            print(f"      Preview: {page['text'][:100].strip()}...")
        
        # Stats
        total_chars = sum(p['char_count'] for p in pages)
        avg_chars = total_chars // len(pages) if pages else 0
        print(f"\n📊 Statistics:")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Average per page: {avg_chars:,}")
        
        print(f"\n✅ PDF parsing successful")
        return True
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*60)
    print("PDF PARSER SERVICE TESTS")
    print("="*60 + "\n")
    
    results = []
    
    # Test 1: Validation
    results.append(("PDF Validation", test_pdf_validation()))
    
    # Test 2: Parsing
    results.append(("PDF Parsing", test_pdf_parsing()))
    
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
