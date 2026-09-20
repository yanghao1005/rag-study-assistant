# Database Setup Guide

## Quick Setup for Supabase

### 1. Enable pgvector Extension

Go to your Supabase project → SQL Editor and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Run the Full Schema

Execute the complete schema from `database/schema.sql`:

```sql
-- Copy and paste the entire contents of schema.sql
-- Or upload it directly in Supabase SQL Editor
```

### 3. Verify Installation

Check that tables were created:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see:
- `subjects`
- `documents`
- `document_chunks`
- `flashcards`
- `quizzes`
- `quiz_questions`

### 4. Test Vector Search Function

```sql
SELECT match_documents(
    ARRAY[0.1, 0.2, ...]::vector(768), -- Replace with actual embedding
    0.7,  -- similarity threshold
    5,    -- top_k results
    NULL, -- subject_id filter (optional)
    NULL  -- document_id filter (optional)
);
```

## Schema Overview

### Core Tables

**subjects**
- Stores study subjects (e.g., "Machine Learning", "Data Structures")
- Links to documents and chunks

**documents**
- Stores uploaded PDF metadata
- Tracks processing status (pending/processing/completed/failed)

**document_chunks**
- Stores text chunks with 768-dimensional vector embeddings
- Uses pgvector for similarity search
- Indexed with IVFFlat for performance

**flashcards**
- AI-generated question/answer pairs
- Linked to subjects and documents

**quizzes**
- Quiz metadata and configuration

**quiz_questions**
- Multiple-choice questions with explanations

## Key Features

### Vector Embeddings
- **Dimension**: 768 (BAAI/bge-base-en-v1.5 model)
- **Similarity**: Cosine distance (`<=>` operator)
- **Index**: IVFFlat with 100 lists

### Search Function
The `match_documents()` function provides:
- Vector similarity search
- Optional filtering by subject/document
- Configurable threshold and result count
- Returns chunks sorted by similarity

### Automatic Timestamps
- `created_at`: Set on insert
- `updated_at`: Auto-updated on modification (via triggers)

## Migration from Different Embedding Dimensions

If you need to change embedding dimensions:

```sql
-- Drop existing vector column and index
DROP INDEX IF EXISTS idx_chunks_embedding;
ALTER TABLE document_chunks DROP COLUMN embedding;

-- Add new dimension (e.g., 1024 for bge-large)
ALTER TABLE document_chunks ADD COLUMN embedding VECTOR(1024);

-- Recreate index
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Update the match_documents function signature
-- Change VECTOR(768) to VECTOR(1024) in function definition
```

## Performance Tuning

### IVFFlat Index Lists
- **Small dataset (<10k vectors)**: 100 lists
- **Medium dataset (10k-100k)**: 1000 lists
- **Large dataset (>100k)**: 10000 lists

```sql
-- Recreate index with different list count
DROP INDEX idx_chunks_embedding;
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

### Query Optimization
```sql
-- Analyze table for better query plans
ANALYZE document_chunks;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'document_chunks';
```

## Troubleshooting

### Error: "extension vector does not exist"
```sql
CREATE EXTENSION vector;
```

### Error: "relation document_chunks does not exist"
Run the full schema.sql file

### Slow similarity searches
- Check if IVFFlat index exists
- Increase lists parameter for larger datasets
- Run ANALYZE on the table

### Connection issues
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check Supabase project is active
- Verify network connectivity
