# Supabase schema — RAG Study Assistant (reconstructed)

Greenfield schema for the rebuilt `backend/` + `frontend/` stacks.
Designed for a wiped Supabase project (no leftover tables).

## Ownership model

Each authenticated user owns their data (`auth.uid() = user_id`).
RLS is enabled on every public table. Storage paths are scoped as:

```text
documents/{user_id}/{subject_id}/{document_id}/{filename}
```

## Entity relationship (logical)

```text
auth.users
   └── profiles (1:1)
   └── subjects (1:N)
         ├── documents (1:N)
         │     └── document_chunks (1:N)  [embedding + content_tsv]
         ├── study_artifacts (1:N)
         │     ├── flashcards
         │     └── quiz_questions
         ├── chat_threads (1:N)
         │     └── chat_messages
         └── jobs (async ingestion / generation)
               └── pipeline_stage_runs
```

## Improvements vs legacy `backend_v5`

| Gap in legacy | New schema |
|---|---|
| No `subjects` table (`subject_id` was orphan UUID) | Real `subjects` + FK cascade |
| No FTS / BM25 | `content_tsv` + `match_chunks_lexical` |
| No vector index | HNSW cosine on `embedding vector(1536)` |
| Single `generated_content` JSON blob | Normalized `study_artifacts` + `flashcards` + `quiz_questions` |
| No chat persistence | `chat_threads` / `chat_messages` with citations |
| Weak job typing | Typed `job_type` / pipeline `stage` enums |
| No Storage policies | Private `documents` bucket + path RLS |
| `security definer` in public | `private.handle_new_user()` |

## Hybrid retrieval (3 stages)

1. **Dense** — `match_chunks_dense(query_embedding, ...)`
2. **Lexical** — `match_chunks_lexical(query_text, ...)` via Spanish FTS
3. **Merge / rerank** — app-side RRF (helper: `rrf_merge(dense_ids, lexical_ids)`) then optional LLM rerank

## Migrations (apply in order)

| File | Purpose |
|---|---|
| `0001_extensions.sql` | `pgcrypto`, `vector`, `unaccent`, private schema |
| `0002_core_tables.sql` | profiles, subjects, documents, chunks |
| `0003_study_and_jobs.sql` | artifacts, flashcards, quizzes, chat, jobs |
| `0004_search_functions.sql` | dense + lexical + RRF helpers |
| `0005_rls_and_storage.sql` | RLS policies, grants, storage bucket |

## How to apply

### Option A — Supabase SQL Editor (fastest on empty project)

1. Open Dashboard → SQL → New query
2. Paste and run each file **in order** `0001` → `0007`
3. Confirm tables under Table Editor and bucket `documents` under Storage

### Option B — Supabase MCP / CLI

```bash
# Via Cursor agent (MCP apply_migration) or:
cd backend
supabase link --project-ref <your-ref>
supabase db push
```

## Provider configuration (Phase 4)

| Env | Default | Notes |
|---|---|---|
| `LLM_PROVIDER` | `openai` | `openai` or `gemini` |
| `EMBEDDING_PROVIDER` | `openai` | fixed to 1536-dim schema |
| `RERANK_PROVIDER` | `none` | RRF merge; optional `llm` later |
| `OPENAI_MODEL` | `gpt-4.1-mini` | generation |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | embeddings |
| `GEMINI_MODEL` | `gemini-2.5-flash` | when `LLM_PROVIDER=gemini` |

## Best-practice audit (supabase-postgres-best-practices)

Applied / verified:

| Rule | Status |
|---|---|
| RLS on all public tables | Yes + `FORCE ROW LEVEL SECURITY` |
| `(select auth.uid())` in policies | Yes (RLS performance) |
| Policies `TO authenticated` | Yes |
| FK indexes | Yes (incl. jobs.subject_id) |
| Partial + composite queue index | `idx_jobs_queued_created` |
| SKIP LOCKED job claim | `private.claim_next_job` + optional `public` wrapper `0007` |
| FTS tsvector + GIN | `content_tsv` + `spanish_unaccent` |
| HNSW vector index | cosine ops |
| security definer outside public | `private.*` |
| Least privilege grants | no table grants to `anon` |
| Storage upsert trio | SELECT+INSERT+UPDATE |