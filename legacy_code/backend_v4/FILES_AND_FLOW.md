# backend_v4 Files and Flow Guide

This document explains:

- what each important file does,
- how requests move through the system,
- where data is read/written,
- how provider switching and fallbacks work.

Use this together with `FULL_PROJECT_EXPLANATION.md`.

## 1. File Map (What each file is for)

## 1.1 App bootstrap

- `app/main.py`
  - Creates the FastAPI app.
  - Adds middleware and exception handlers.
  - Mounts API router under `/api` (default).

- `app/container.py`
  - Dependency injection and wiring.
  - Chooses repository/provider implementations from env config.
  - Applies fallback to in-memory/stub implementations if external provider setup fails.

## 1.2 Core utilities

- `app/core/config.py`
  - Environment-backed settings (`pydantic-settings`).
  - Feature flags and provider toggles.

- `app/core/middleware.py`
  - Request ID middleware.
  - Injects/returns `X-Request-ID`.

- `app/core/exceptions.py`
  - `AppError` model and global handlers.
  - Standardizes error JSON response shape.

- `app/core/artifacts.py`
  - Writes JSON debug artifacts to disk.

- `app/core/logging.py`
  - Central logging setup support.

## 1.3 API layer

- `app/presentation/api/router.py`
  - Registers and combines route groups.

- `app/presentation/api/routes/health.py`
  - `GET /health`.

- `app/presentation/api/routes/pipeline.py`
  - `POST /pipeline/run`.
  - Debug endpoint gate (`ENABLE_DEBUG_ENDPOINTS`).
  - Calls `PipelineRunner`.

- `app/presentation/api/routes/generation.py`
  - `POST /generate/flashcards`
  - `POST /generate/quiz`
  - `POST /generate/summary`
  - `GET /generate/history`
  - Calls `GenerationService`.

## 1.4 Application use cases

- `app/application/use_cases/pipeline_runner.py`
  - Orchestrates indexing pipeline stages.
  - Runs per-stage checks.
  - Writes stage artifacts.

- `app/application/use_cases/generation_service.py`
  - Retrieval + LLM generation for flashcards/quiz.
  - Response validation and retry.
  - Optional save to history and debug artifacts.

## 1.5 Domain contracts and ports

- `app/domain/models/contracts.py`
  - Pydantic request/response schemas.
  - Includes pipeline request model and diagnostics contracts.

- `app/domain/ports/repositories.py`
  - `VectorRepository` interface.

- `app/domain/ports/providers.py`
  - `LLMProvider` and `EmbeddingsProvider` interfaces.

## 1.6 Infrastructure adapters

- `app/infrastructure/repositories/vector_repository.py`
  - In-memory repository (dev/test fallback).

- `app/infrastructure/repositories/supabase_repository.py`
  - Supabase repository for chunks and generated history persistence.

- `app/infrastructure/providers/llm_provider.py`
  - Stub LLM provider.

- `app/infrastructure/providers/openai_llm_provider.py`
  - Real OpenAI chat completion JSON provider.

- `app/infrastructure/providers/embeddings_provider.py`
  - Stub embeddings provider.

- `app/infrastructure/providers/openai_embeddings_provider.py`
  - Real OpenAI embeddings provider.

- `app/infrastructure/parsing/pdf_parser.py`
  - PDF/text parsing utility.

## 1.7 Tooling and tests

- `tools/run_pipeline.py`
  - CLI for pipeline endpoint debugging.

- `tools/benchmark_generation.py`
  - Measures endpoint latency and writes benchmark report.

- `tests/unit/test_pipeline_runner.py`
  - Pipeline behavior checks.

- `tests/unit/test_generation_validation.py`
  - Generation retry/validation checks.

- `tests/unit/test_container_providers.py`
  - Provider selection and fallback checks.

- `tests/integration/test_generation_api.py`
  - API contract shape checks.

- `tests/e2e/test_smoke.py`
  - Health smoke check.

## 2. Startup Flow

1. App starts in `app/main.py`.
2. Settings loaded from `app/core/config.py`.
3. Middleware and exception handlers registered.
4. API routers attached.
5. On first request needing a service, `app/container.py` lazily instantiates and caches dependencies.

## 3. Dependency/Provider Flow

Container decision path:

1. Read env settings.
2. If Supabase selected and credentials valid -> use `SupabaseVectorRepository`.
3. Otherwise -> use `InMemoryVectorRepository`.
4. If OpenAI selected and key valid -> use OpenAI providers.
5. Otherwise -> use stub providers.

This guarantees the app still runs in local/test mode even without cloud keys.

## 4. Request Flows

## 4.1 Health flow

1. Client calls `GET /api/health`.
2. Route returns `{ "status": "ok" }`.

## 4.2 Pipeline flow (`POST /api/pipeline/run`)

1. Request enters `pipeline.py` route.
2. If debug endpoint disabled -> 403 error.
3. Route validates payload via `PipelineRunRequest`.
4. Route calls `PipelineRunner.run(payload)`.
5. Runner executes selected stages in order:
   - validate_input
   - parse_document
   - detect_sections
   - semantic_chunking
   - build_embeddings
   - persist_vectors
   - build_summary_index
   - extract_graph_triplets
6. Each stage writes one artifact file.
7. After each stage, check result is evaluated.
8. On first failed check, run stops and returns `checks_passed=false`.
9. Response includes stage-by-stage status, artifacts, and run id.

## 4.3 Generation flow (`POST /api/generate/flashcards` / `quiz`)

1. Request enters generation route.
2. Payload validated by Pydantic schema.
3. Route calls `GenerationService` method.
4. Service retrieves candidates from repository by scope/scope_id/query.
5. Service builds prompt and requests JSON from LLM provider.
6. Service validates generated structure.
7. If invalid, retries once with stricter retry prompt.
8. If still invalid, returns deterministic fallback output.
9. If `save=true`, writes generated result to repository history table/store.
10. If `debug=true`, writes debug artifact with query, candidates, and raw model output.
11. Response returns generated content + diagnostics.

## 4.4 History flow (`GET /api/generate/history`)

1. Request enters history route with `user_id`, `scope`, `scope_id`, `limit`.
2. Service calls repository `list_generated(...)`.
3. Repository returns most recent matching generated items.
4. API returns `{ items: [...] }`.

## 5. Data Write Points

Main persistent writes happen in:

- `SupabaseVectorRepository.save_chunks(...)`
  - During pipeline `persist_vectors` stage.
- `SupabaseVectorRepository.save_generated(...)`
  - During generation when `save=true`.
- `write_json_artifact(...)`
  - Pipeline/generation benchmark/debug artifacts to local filesystem.

If memory repository is active, writes stay in process memory only.

## 6. Flow of IDs and traceability

- Request-level trace: `X-Request-ID` from middleware.
- Pipeline run trace: `run_id` generated by `PipelineRunner`.
- Generation debug trace: `debug_trace_id` in diagnostics when debug is enabled.

These IDs map API responses to artifact files for debugging.

## 7. Typical debug workflow

1. Reproduce request with `debug=true`.
2. Capture `request_id` / `run_id` / `debug_trace_id`.
3. Open corresponding artifact JSON under `debug_artifacts/`.
4. Inspect stage output/check failure details (pipeline) or candidate/raw model payload (generation).
5. Fix at the appropriate layer:
   - route contract,
   - use case logic,
   - repository/provider adapter,
   - env configuration.

## 8. Quick reference: Where to edit what

- Add/change endpoint: `app/presentation/api/routes/*.py`
- Change business behavior: `app/application/use_cases/*.py`
- Change payload schema: `app/domain/models/contracts.py`
- Add provider/repository backend: `app/infrastructure/*` + `app/container.py`
- Add feature flag/env: `app/core/config.py`
- Add debug output format: `app/core/artifacts.py`
- Add tests: `tests/unit`, `tests/integration`, `tests/e2e`

---

If the project grows, split this file into:

- `FILES_REFERENCE.md` (file map)
- `REQUEST_FLOWS.md` (runtime flows)
- `DEBUG_PLAYBOOK.md` (troubleshooting steps)

to keep each guide short and focused.