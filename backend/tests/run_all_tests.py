"""
Run all tests in sequence
"""
import subprocess
import sys
from pathlib import Path


def run_test(test_file: str) -> bool:
    """Run a single test file"""
    print(f"\n{'='*80}")
    print(f"Running: {test_file}")
    print(f"{'='*80}\n")
    
    result = subprocess.run(
        [sys.executable, test_file],
        cwd=Path(__file__).parent.parent,
        capture_output=False,
    )
    
    return result.returncode == 0


def main():
    print("="*80)
    print("RAG STUDY ASSISTANT - FULL TEST SUITE")
    print("="*80)
    
    tests = [
        "tests/test_1_pdf_parser.py",
        "tests/test_2_chapter_detector.py",
        "tests/test_3_text_chunker.py",
        "tests/test_4_embedding_service.py",
        "tests/test_5_vector_store.py",
    ]
    
    results = []
    
    for test_file in tests:
        test_name = Path(test_file).stem.replace("test_", "").replace("_", " ").title()
        passed = run_test(test_file)
        results.append((test_name, passed))
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<40} {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\n{'='*80}")
    print(f"Total: {passed_count}/{total} test suites passed")
    print(f"{'='*80}")
    
    if passed_count == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed_count} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
