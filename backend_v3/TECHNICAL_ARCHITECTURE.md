# backend_v3 Technical Architecture

## 1. Purpose

`backend_v3` is a debug-first FastAPI backend for document ingestion and study-content generation (flashcards, quiz, summary retrieval) using a RAG-style pipeline.

Core goals:
- deterministic, stage-by-stage execution for debugging,
- strong request tracing and diagnostics,
- Supabase-backed persistence with user ownership,
- structured generation controls (query, profile, length caps).

---

## 2. High-Level Module Structure

- `app/main.py`
  - FastAPI app factory, middleware registration, exception handlers, API router mount.
- `app/api/v1/`
  - HTTP endpoints (`/health`, `/pipeline/run`, `/generate/*`).
- `app/domain/`
  - Pydantic contracts for pipeline and generation requests/responses.
- `app/application/`
  - Orchestration logic:
    - `PipelineRunner` for stage execution,
    - `GenerationService` for retrieval + prompting + persistence.
- `app/infrastructure/`
  - Adapters/services for parsing, chunking, embeddings, repository persistence.
- `app/core/`
  - Config, DB client bootstrap, middleware, exception format, debug artifact persistence.
- `tools/`
  - Operational scripts for E2E validation and CLI pipeline runs.

---

## 3. Request Lifecycle

### 3.1 App Boot

At startup (`app/main.py`):
1. Load settings from `.env` via `pydantic-settings`.
2. Create FastAPI app with metadata.
3. Register:
   - `RequestIdMiddleware` (injects/returns `X-Request-ID`),
   - CORS middleware,
   - global exception handlers.
4. Mount API under `settings.api_prefix` (default `/api`).

### 3.2 Error Contract

All custom errors use `AppError` and return JSON:
- `error`
- `message`
- `details`
- `request_id`

Unhandled exceptions return a standardized 500 payload with error type metadata.

---

## 4. API Surface

### 4.1 Health
- `GET /api/health`
- Returns `{ "status": "ok" }`.

### 4.2 Pipeline
- `POST /api/pipeline/run`
- Executes full pipeline, a single stage, or a stage range.
- Supports debug artifact persistence (`debug=true`).

### 4.3 Generation
- `POST /api/generate/flashcards`
- `POST /api/generate/quiz`
- `POST /api/generate/summary`

Generation endpoints include retrieval diagnostics in response and optional debug trace header (`X-Debug-Trace`).

---

## 5. Pipeline Orchestration (`PipelineRunner`)

Pipeline stages (`PIPELINE_ORDER`):
1. `validate_input`
2. `parse_document`
3. `detect_chapters`
4. `split_chunks`
5. `generate_embeddings`
6. `store_vectors`
7. `build_document_index`
8. `retrieve_context`
9. `generate_output`

Execution modes:
- Full run (default)
- Single stage (`stage`)
- Stage range (`from` + `to`)

### 5.1 Stage Responsibilities

- `validate_input`
  - Validates required fields by document type.
  - Requires `user_id` when storing vectors.

- `parse_document`
  - PDF: parse via PyMuPDF (`file_path`).
  - Summary text: normalized single-page content.

- `detect_chapters`
  - Heuristic chapter extraction from parsed pages.

- `split_chunks`
  - Creates metadata-rich chunks (document type, page, chapter, subject).

- `generate_embeddings`
  - Primary: OpenAI embeddings model.
  - Fallback: deterministic SHA-based 1536-dim vectors.

- `store_vectors`
  - Persists chunks + embeddings into vector storage (`document_chunks`).

- `build_document_index`
  - Builds a short synopsis and chunk count.
  - Persists synopsis into `documents.content_text`.

- `retrieve_context`
  - Scope-filtered top-k retrieval via repository.

- `generate_output`
  - Returns concise answer + source previews from retrieved context.

### 5.2 Debug Artifacts

If `debug=true`, `PipelineRunner` writes structured run output to `debug_artifacts_dir` (default `./.debug_runs`).

---

## 6. Generation Flow (`GenerationService`)

### 6.1 Input Strategy (system-owned prompting)

Generation requests enforce structured user intent:
- `query` is required for flashcards and quiz.
- User does not provide raw free-form system prompt.

This keeps prompt templates controlled and predictable while allowing per-request customization.

### 6.2 Retrieval and Grounding

For flashcards/quiz:
1. Retrieve scope-filtered rows from repository.
2. Compute relevance score + threshold acceptance.
3. If no accepted rows, return `insufficient_context` with diagnostics.

Thresholds:
- PDF threshold: `similarity_threshold_pdf`
- Summary threshold: `similarity_threshold_summary`

### 6.3 Summary + Chunks Combined Context

Generation composes context using both:
- persisted document summary (`documents.content_text`, if available), and
- retrieved chunks.

Context format:
- `Document Summary: ...`
- `Retrieved Chunks: ...`

### 6.4 Prompt Profiles and Length Controls

Per request controls:
- `prompt_profile`: `concise` | `exam` | `conceptual`
- flashcards: `front_max_chars`, `back_max_chars`
- quiz: `question_max_chars`, `explanation_max_chars`

Length caps are enforced post-generation to prevent oversized outputs.

### 6.5 LLM JSON Mode

- Uses strict JSON schema via OpenAI `response_format`.
- Includes compatibility logic for array schemas.
- One retry path on parsing/schema failure.

### 6.6 Persistence of Generated Results

On successful generation (when `save=true` and resolvable `user_id`):
- flashcards are inserted into `generated_content` with `type='flashcard'`,
- quizzes are inserted with `type='quiz'`.

Scope mapping:
- `subject` -> `subject_id`
- `document`/`summary` -> `document_id`
- `chapter` -> `chapter_id`

### 6.7 Summary Endpoint

`POST /api/generate/summary` returns the persisted document summary from `documents.content_text` for a given `scope_id` (document ID).

---

## 7. Repository Layer

The repository abstraction (`VectorRepository`) defines core operations:
- chunk/vector storage,
- retrieval,
- document index persistence,
- summary retrieval,
- generated content persistence.

Implementations:
- `InMemoryVectorRepository`
  - Used when Supabase client is unavailable.
  - Keeps rows/index/generated artifacts in process memory.
- `SupabaseVectorRepository`
  - Writes to and reads from Supabase tables:
    - `document_chunks`
    - `documents`
    - `generated_content`

---

## 8. Supabase Client Bootstrap and Security Behavior

`get_supabase_client()` behavior:
1. Prefer service key (`SUPABASE_SERVICE_KEY`).
2. Supports `sb_secret_` keys through PostgREST adapter fallback.
3. Optional anon fallback only if explicitly enabled (`SUPABASE_ALLOW_ANON_FALLBACK=true`).
4. Fails fast when URL is configured but secure key requirements are not met.

This protects RLS-protected write operations from silent anon misuse.

---

## 9. Data Model Usage (Operational View)

Main tables used by backend runtime:
- `documents`
  - source doc metadata, status, persisted summary in `content_text`.
- `document_chunks`
  - chunk text + embedding + metadata + ownership.
- `generated_content`
  - persisted flashcard/quiz payloads and scope linkage.

Read/write responsibilities:
- Ingestion pipeline writes `document_chunks` and `documents.content_text`.
- Generation writes `generated_content`.
- Summary endpoint reads `documents.content_text`.

---

## 10. Observability and Debugging

### 10.1 Correlation IDs

Every request has a `request_id` available in:
- response header `X-Request-ID`,
- error response body,
- debug artifacts.

### 10.2 Retrieval Diagnostics

Flashcard/quiz responses include diagnostics:
- scope and scope_id,
- total/accepted candidates,
- best score,
- per-row context scores,
- optional debug trace and artifact path.

### 10.3 Debug Artifact Files

`persist_debug_artifact()` stores JSON snapshots under `debug_artifacts_dir` for offline troubleshooting.

---

## 11. Testing Strategy

Current tests cover:
- unit: parser/chunker/generation behavior and constraints,
- integration: pipeline flow,
- API: endpoint contracts and diagnostics behavior.

Run all tests:

```bash
python -m pytest backend_v3/tests -q
```

---

## 12. Typical End-to-End Flow (PDF)

1. Create/identify user profile and subject.
2. Create `documents` row (`status='processing'`).
3. Call `/api/pipeline/run` through `build_document_index`.
4. Pipeline stores embeddings/chunks and writes synopsis to `documents.content_text`.
5. Call `/api/generate/flashcards` or `/api/generate/quiz` with:
   - `scope`, `scope_id`, `query`, `prompt_profile`, caps.
6. Generation uses summary + chunks and saves output to `generated_content`.

---

## 13. Recommended Client Request Pattern

For stable results, client should always send:
- `query` (required),
- `scope` + `scope_id`,
- generation controls (`count`, `difficulty`, `prompt_profile`, length caps),
- `save=true` for persistence.

Avoid exposing raw prompt editing in normal UI; keep prompt templates backend-owned and versioned.

---

## 14. Known Design Decisions

- Deterministic fallback generation/embeddings are intentionally available for resilience.
- Prompt profiles are configurable at request-time but templates are backend-controlled.
- Generated outputs persist by scope for downstream history/review.
- Summary retrieval is explicit via `/api/generate/summary` and implicitly used during flashcard/quiz context composition.
