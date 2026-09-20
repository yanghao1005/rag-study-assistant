# Testing Guide

This directory contains comprehensive tests for all Phase 1 services of the RAG Study Assistant.

## Test Structure

Each test file corresponds to a specific service in the pipeline:

### 1. PDF Parser (`test_1_pdf_parser.py`)
Tests PDF validation and text extraction:
- ✅ PDF validation (file size, format)
- ✅ Metadata extraction (title, page count, file size)
- ✅ Text extraction from all pages
- ✅ Character count statistics

### 2. Chapter Detector (`test_2_chapter_detector.py`)
Tests chapter detection and page mapping:
- ✅ Chapter detection from page content
- ✅ Chapter boundary merging
- ✅ Page-to-chapter mapping

### 3. Text Chunker (`test_3_text_chunker.py`)
Tests text chunking with metadata:
- ✅ Basic text chunking with overlap
- ✅ PDF document chunking with chapters
- ✅ Chunk statistics (size, distribution)
- ✅ Small chunk merging

### 4. Embedding Service (`test_4_embedding_service.py`)
Tests embedding generation:
- ✅ Single text embedding
- ✅ Batch embedding generation
- ✅ PDF content embeddings
- ✅ Embedding validation

### 5. Vector Store (`test_5_vector_store.py`)
Tests Supabase vector operations:
- ✅ Store chunks in database
- ✅ Similarity search
- ✅ Delete document chunks
- ✅ Full pipeline (PDF → Database)

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Individual Tests
```bash
# Test PDF parser
python tests/test_1_pdf_parser.py

# Test chapter detector
python tests/test_2_chapter_detector.py

# Test text chunker
python tests/test_3_text_chunker.py

# Test embedding service
python tests/test_4_embedding_service.py

# Test vector store
python tests/test_5_vector_store.py
```

## Prerequisites

### 1. PDF Test Documents
Place test PDFs in `pdf_tests_documents/` directory:
```
backend/
  pdf_tests_documents/
    1_BMC_OBS.pdf
```

### 2. Environment Configuration
Configure `.env` file with:
```env
# Embedding provider (huggingface recommended)
EMBEDDING_PROVIDER=huggingface
HUGGINGFACE_EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Supabase connection
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
```

### 3. Database Schema
Ensure Supabase has the `document_chunks` table:
```sql
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_id UUID,
  document_id UUID,
  content TEXT NOT NULL,
  embedding VECTOR(768),  -- Match your model dimension
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

## Test Data

Each test uses:
- **Test PDF**: `1_BMC_OBS.pdf` (21 pages, ~6,930 characters)
- **Embedding Model**: BAAI/bge-base-en-v1.5 (768 dimensions)
- **Chunk Size**: 1000 characters with 200 overlap
- **Test IDs**: `test-subject-*` and `test-doc-*`

## Expected Results

✅ **All tests should pass** with Phase 1 implementation complete:

```
1 Pdf Parser                    ✅ PASSED
2 Chapter Detector              ✅ PASSED
3 Text Chunker                  ✅ PASSED
4 Embedding Service             ✅ PASSED
5 Vector Store                  ✅ PASSED

Total: 5/5 test suites passed
🎉 All tests passed!
```

## Troubleshooting

### Import Errors
```bash
# Install missing dependencies
pip install langchain-text-splitters sentence-transformers
```

### Database Connection Errors
- Check `.env` has correct Supabase credentials
- Verify database schema is created
- Check vector dimension matches model (768 for bge-base)

### Embedding Model Download
- First run downloads model (~438MB for bge-base)
- Cached in `~/.cache/huggingface/hub/`
- Requires internet connection on first run

### Memory Issues
- Tests use only first 3-5 chunks from PDF
- Reduce batch size in embedding tests if needed
- Close other applications if low memory

## Performance Benchmarks

Expected performance on typical hardware:

| Test | Duration | Notes |
|------|----------|-------|
| PDF Parser | ~0.5s | 21 pages |
| Chapter Detector | ~0.1s | Pattern matching |
| Text Chunker | ~0.2s | 21 chunks |
| Embedding Service | ~4-5s | 5 chunks, 768 dim |
| Vector Store | ~2-3s | Store + search + delete |

**Total runtime**: ~7-10 seconds for full suite

## Next Steps

After all tests pass:
1. ✅ Phase 1 complete (document processing)
2. 🔄 Phase 2: RAG pipeline service
3. 🔄 Phase 3: Content generation (flashcards, quizzes)
4. 🔄 Phase 4: API endpoints
5. 🔄 Phase 5: Frontend integration
