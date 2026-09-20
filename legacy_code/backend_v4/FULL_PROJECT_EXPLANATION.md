# backend_v4 Full Project Explanation

This document explains the full implemented backend_v4 project: what it does, how it is organized, how data flows end-to-end, and how to run/extend it.

## 1. What backend_v4 is

backend_v4 is a FastAPI backend for a RAG Study Assistant with:

- Stage-based ingestion pipeline (debuggable per stage).
- Generation APIs for flashcards, quiz, and summary.
- Provider switching for:
  - Vector repository: in-memory or Supabase.
  - LLM provider: stub or OpenAI.
  - Embeddings provider: stub or OpenAI.
- Artifact generation for debugging and benchmarking.
- Layered architecture with explicit domain ports and infrastructure adapters.

Main entry point: `app/main.py`

## 2. High-level architecture

The project follows ports-and-adapters (hexagonal style) with clean layering:

- Presentation layer:
  - FastAPI routes and request/response handling.
- Application layer:
  - Use cases (`PipelineRunner`, `GenerationService`).
- Domain layer:
  - Contracts (Pydantic models) + interfaces (ports).
- Infrastructure layer:
  - Repositories (Supabase and in-memory), providers (OpenAI and stubs), PDF parsing.

Dependency wiring is centralized in `app/container.py` using cached factory functions.

## 3. Directory map

Key folders:

- `app/core`
  - Cross-cutting concerns: config, exceptions, middleware, artifact utilities.
- `app/presentation/api`
  - API router and route handlers.
- `app/application/use_cases`
  - Main business workflows.
- `app/domain/models`
  - Request/response contracts.
- `app/domain/ports`
  - Protocol interfaces for repositories/providers.
- `app/infrastructure/repositories`
  - Data adapters (Supabase + in-memory).
- `app/infrastructure/providers`
  - LLM + embeddings adapters (OpenAI + stubs).
- `app/infrastructure/parsing`
  - PDF parser implementation.
- `tests`
  - Unit, integration, e2e tests.
- `tools`
  - Operational CLI scripts.
- `debug_artifacts`
  - Stage-by-stage and generation debugging outputs.

## 4. Runtime bootstrap and request lifecycle

### 4.1 App creation

In `app/main.py`:

1. Load settings from env via `get_settings()`.
2. Build FastAPI app with configured title.
3. Register `RequestIdMiddleware`.
4. Register global exception handlers.
5. Mount API router under `settings.api_prefix` (default `/api`).

### 4.2 Middleware and error handling

- `RequestIdMiddleware`:
  - Reads `X-Request-ID` header or generates UUID.
  - Stores it in `request.state.request_id`.
  - Returns it in response headers.

- Exception model (`app/core/exceptions.py`):
  - `AppError` for controlled business/API errors.
  - Global handlers return consistent JSON with:
    - `error`
    - `message`
    - `details`
    - `request_id`

## 5. Configuration model

`app/core/config.py` uses `pydantic-settings` and `.env`.

Important settings:

- App and API:
  - `APP_NAME`, `API_PREFIX`, `DEBUG`
- Feature flags:
  - `ENABLE_DEBUG_ENDPOINTS`
  - `ENABLE_HYBRID_RETRIEVAL`
  - `ENABLE_SUMMARY_INDEX`
  - `ENABLE_GRAPH_RAG`
  - `ENABLE_AGENTIC_RAG`
- Provider selection:
  - `VECTOR_REPOSITORY_PROVIDER=memory|supabase`
  - `LLM_PROVIDER=stub|openai`
  - `EMBEDDINGS_PROVIDER=stub|openai`
- Supabase:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY` (preferred) or `SUPABASE_KEY`
  - table names (`SUPABASE_GENERATED_TABLE`, `SUPABASE_CHUNKS_TABLE`)
- OpenAI:
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL` (optional)
  - `OPENAI_LLM_MODEL`
  - `OPENAI_EMBEDDING_MODEL`
- Outputs:
  - `DEBUG_ARTIFACTS_DIR`
  - `BENCHMARK_REPORTS_DIR`

## 6. Dependency injection container

`app/container.py` is the central assembly point.

It exposes cached providers:

- `get_vector_repository()`
  - Supabase when selected and configured.
  - Falls back to in-memory on missing config/init error.
- `get_llm_provider()`
  - OpenAI when selected and key present.
  - Falls back to stub on errors.
- `get_embeddings_provider()`
  - OpenAI embeddings when selected and key present.
  - Falls back to stub on errors.
- `get_generation_service()`
  - Uses configured vector repo + llm provider.
- `get_pipeline_runner()`
  - Uses configured vector repo + embeddings provider + PDF parser.

Design note: fallbacks keep local dev and test runs resilient even when external services are unavailable.

## 7. Domain contracts and ports

### 7.1 Contracts (`app/domain/models/contracts.py`)

Defines all API contracts and diagnostics:

- Generation requests:
  - `GenerateFlashcardsRequest`
  - `GenerateQuizRequest`
  - `GenerateSummaryRequest`
- Generation responses:
  - flashcards/quiz/summary + retrieval diagnostics.
- History contracts:
  - `GeneratedHistoryItem`, `GenerateHistoryResponse`.
- Pipeline contracts:
  - `PipelineRunRequest` (includes `document_id`, `user_id`, stage selectors, debug flag).
  - `PipelineRunResponse`, `PipelineStageResult`.

Supported scope literal: `subject | document | chapter | summary`.

### 7.2 Ports (`app/domain/ports`)

- `VectorRepository` protocol:
  - `save_chunks`, `retrieve`, `save_generated`, `list_generated`.
- `LLMProvider` protocol:
  - `generate_json(prompt)`.
- `EmbeddingsProvider` protocol:
  - `embed(text)`.

These contracts isolate business logic from infrastructure choices.

## 8. API endpoints

API router (`app/presentation/api/router.py`) mounts:

- `GET /api/health`
  - Simple liveness endpoint.

- `POST /api/pipeline/run`
  - Executes all or selected ingestion stages.
  - Guarded by `ENABLE_DEBUG_ENDPOINTS`; otherwise returns 403.

- `POST /api/generate/flashcards`
  - Generates flashcards based on retrieved context.

- `POST /api/generate/quiz`
  - Generates quiz questions based on retrieved context.

- `POST /api/generate/summary`
  - Returns summary scaffold response for provided scope id.

- `GET /api/generate/history`
  - Lists saved generated content by `user_id`, `scope`, `scope_id`.

## 9. Application use cases

### 9.1 PipelineRunner (`app/application/use_cases/pipeline_runner.py`)

`PipelineRunner` orchestrates deterministic stages:

1. `validate_input`
2. `parse_document`
3. `detect_sections`
4. `semantic_chunking`
5. `build_embeddings`
6. `persist_vectors`
7. `build_summary_index`
8. `extract_graph_triplets`

Capabilities:

- Full run or targeted execution:
  - Single stage: `stage`
  - Range: `from` + `to` (or `from_stage` + `to_stage`)
- Per-stage checks via `_check_stage`.
- Stops on first failed check.
- Writes JSON artifact per executed stage with duration, output, and check.
- Returns `checks_passed`, `run_id`, and stage-level diagnostics.

Persistence behavior:

- `persist_vectors` passes `document_id`, `scope`, `scope_id`, and `user_id` into repository `save_chunks`.

### 9.2 GenerationService (`app/application/use_cases/generation_service.py`)

Main responsibilities:

- Retrieve candidate chunks from vector repository.
- Build retrieval diagnostics.
- Generate structured JSON via LLM provider.
- Validate model output with Pydantic response schemas.
- Retry once on invalid/malformed generation.
- Fall back to deterministic scaffold content if model output remains invalid.
- Optionally save generated content for history.
- Optionally write debug artifacts with retrieval + raw model output.

Implemented methods:

- `generate_flashcards(payload)`
- `generate_quiz(payload)`
- `get_summary(scope_id)`
- `get_history(user_id, scope, scope_id, limit)`

## 10. Infrastructure adapters

### 10.1 Repositories

- `InMemoryVectorRepository`:
  - Stores chunks and generated items in process memory.
  - Provides deterministic pseudo-candidates when no chunks exist.
  - Ideal for tests and offline local runs.

- `SupabaseVectorRepository`:
  - Uses `supabase-py` client.
  - Retrieves chunks filtered by `scope` and `scope_id` (and optional content ilike query).
  - Persists chunk rows into Supabase.
  - Persists and lists generated content history.
  - Current implementation safely returns empty/default values on exceptions.

### 10.2 LLM providers

- `LLMProvider` (stub):
  - Returns deterministic flashcards/quiz JSON by prompt keywords.

- `OpenAILLMProvider`:
  - Calls `chat.completions.create` with `response_format={"type":"json_object"}`.
  - Parses response content to dict.

### 10.3 Embeddings providers

- `EmbeddingsProvider` (stub):
  - Deterministic small vector from SHA-256 digest.

- `OpenAIEmbeddingsProvider`:
  - Calls `embeddings.create` and returns first embedding vector.

### 10.4 Parser

- `PDFParser`:
  - Reads text directly for non-PDF files.
  - Uses `pypdf.PdfReader` for PDFs.
  - Returns extracted text per page.

## 11. Artifacts and observability

Artifact helper: `app/core/artifacts.py`

- Writes timestamped JSON files to:
  - `<root_dir>/<run_id>/<name>_<timestamp>.json`

Used by:

- Pipeline stages (one artifact per stage).
- Generation debug mode (trace-level artifacts).
- Benchmark reports (under benchmark directory).

Observability primitives included:

- Request IDs propagated in headers and responses.
- Stage durations and check outcomes.
- Structured debug artifacts for reproducing behavior.

## 12. Tests and quality gates

Test layout:

- `tests/e2e/test_smoke.py`
  - Basic service liveness smoke test (`/api/health`).
- `tests/integration/test_generation_api.py`
  - API response shape contracts and debug endpoint gating.
- `tests/unit/test_pipeline_runner.py`
  - Stage execution modes, artifact creation, input validation behavior.
- `tests/unit/test_generation_validation.py`
  - LLM output validation + retry behavior.
- `tests/unit/test_container_providers.py`
  - Provider selection and fallback mechanics.

Current test philosophy:

- Fast deterministic tests by default (memory + stubs).
- External dependencies are optional and guarded by fallback behavior.

## 13. Operational tools

### 13.1 `tools/run_pipeline.py`

CLI for invoking pipeline endpoint with:

- `--document-id` (required)
- optional stage/range selectors
- optional file path

Prints full JSON response for stage diagnostics and artifact paths.

### 13.2 `tools/benchmark_generation.py`

Latency benchmark script for generation endpoints:

- Repeatedly calls flashcards or quiz endpoint.
- Computes `p50` and `p95` latency.
- Persists JSON report via artifact utility.

## 14. Data model expectations (Supabase side)

The runtime assumes at least:

- Chunks table (default `document_chunks`) with fields compatible with:
  - `user_id`, `document_id`, `content`, `embedding`, `metadata`,
  - `scope`, `scope_id`, `page`, `chapter_name`, `document_type`, `score`.
- Generated table (default `generated_content`) with fields compatible with:
  - `user_id`, `scope`, `scope_id`, `type`, `subject_id`, `document_id`, `chapter_id`, `content_json`, `created_at`.

Also ensure:

- Any FK/RLS constraints are aligned with API payload values.
- For pipeline persistence, valid `user_id` and `document_id` should exist where required by DB constraints.

## 15. Typical end-to-end flows

### Flow A: Pipeline indexing

1. Client calls `POST /api/pipeline/run`.
2. Runner executes selected stages.
3. Embeddings are generated.
4. Chunks are persisted via selected repository.
5. Per-stage artifacts are written.
6. Response includes stage status/check results and run id.

### Flow B: Flashcards generation

1. Client calls `POST /api/generate/flashcards`.
2. Service retrieves candidates by scope/scope_id.
3. LLM provider returns structured flashcards JSON.
4. Output is schema-validated; retry/fallback if needed.
5. Optional save to generated history table.
6. Optional debug artifact generated.

### Flow C: Quiz generation and history

1. Client calls `POST /api/generate/quiz`.
2. Process mirrors flashcards generation.
3. Client queries `GET /api/generate/history` to fetch saved items.

## 16. How to extend safely

Recommended extension pattern:

1. Add or update contracts in `domain/models/contracts.py`.
2. Extend/use cases in `application/use_cases`.
3. Add/extend ports if behavior changes.
4. Implement new adapter in `infrastructure`.
5. Wire through `container.py` with env-based selection.
6. Expose route in `presentation/api/routes`.
7. Add unit + integration tests before/with implementation.

## 17. Known design tradeoffs

- Some infrastructure adapter exceptions are intentionally swallowed and converted to empty/fallback behavior to preserve API availability in development.
- Generation summary endpoint is currently scaffold-level (returns placeholder summary shape).
- Feature flags for advanced retrieval/graph/agentic modes exist but are not fully activated in the current deterministic baseline.

## 18. Quick run checklist

1. Create/verify `.env`.
2. Enable desired providers (`supabase`/`openai` or stubs).
3. Start API.
4. Check `GET /api/health`.
5. If debugging pipeline, set `ENABLE_DEBUG_ENDPOINTS=true`.
6. Run pipeline and generation endpoints.
7. Inspect `debug_artifacts/` for detailed traces.

---

If you want, this file can be split into:

- `DEVELOPER_GUIDE.md` (architecture + extension rules)
- `OPERATIONS_GUIDE.md` (setup, env, tools, debugging)
- `API_PLAYBOOK.md` (endpoint-by-endpoint examples)

for easier long-term maintenance.