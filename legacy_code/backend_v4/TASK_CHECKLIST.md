# backend_v4 Immediate Implementation Checklist

This checklist converts the planning docs into executable work.

## 1. Setup and Baseline

- [ ] Create Python virtual environment and install dependencies.
- [ ] Add `.env` from `.env.example` and validate required variables.
- [ ] Start app locally and verify [app/main.py](app/main.py) health endpoint.
- [ ] Enable Ruff/Black/MyPy and ensure checks pass.

## 2. Foundation Layer

- [x] Implement settings in [app/core/config.py](app/core/config.py).
- [x] Implement request-id middleware in [app/core/middleware.py](app/core/middleware.py).
- [x] Implement standardized error contract in [app/core/exceptions.py](app/core/exceptions.py).
- [x] Implement structured logger setup in [app/core/logging.py](app/core/logging.py).

## 3. API and Contracts

- [x] Implement `GET /api/health` in [app/presentation/api/routes/health.py](app/presentation/api/routes/health.py).
- [x] Implement `POST /api/pipeline/run` (debug-gated) in [app/presentation/api/routes/pipeline.py](app/presentation/api/routes/pipeline.py).
- [x] Implement `POST /api/generate/flashcards` in [app/presentation/api/routes/generation.py](app/presentation/api/routes/generation.py).
- [x] Implement `POST /api/generate/quiz` in [app/presentation/api/routes/generation.py](app/presentation/api/routes/generation.py).
- [x] Implement `POST /api/generate/summary` in [app/presentation/api/routes/generation.py](app/presentation/api/routes/generation.py).
- [x] Implement `GET /api/generate/history` in [app/presentation/api/routes/generation.py](app/presentation/api/routes/generation.py).

## 4. Domain and Application

- [x] Define generation/retrieval DTOs in [app/domain/models/contracts.py](app/domain/models/contracts.py).
- [x] Define repository/provider ports in [app/domain/ports/repositories.py](app/domain/ports/repositories.py).
- [x] Implement pipeline runner use case in [app/application/use_cases/pipeline_runner.py](app/application/use_cases/pipeline_runner.py).
- [x] Implement generation service use case in [app/application/use_cases/generation_service.py](app/application/use_cases/generation_service.py).

## 5. Infrastructure Adapters

- [x] Implement vector repository adapter in [app/infrastructure/repositories/vector_repository.py](app/infrastructure/repositories/vector_repository.py).
- [x] Implement embeddings provider adapter in [app/infrastructure/providers/embeddings_provider.py](app/infrastructure/providers/embeddings_provider.py).
- [x] Implement LLM provider adapter in [app/infrastructure/providers/llm_provider.py](app/infrastructure/providers/llm_provider.py).
- [x] Implement PDF parser adapter in [app/infrastructure/parsing/pdf_parser.py](app/infrastructure/parsing/pdf_parser.py).

## 6. Tests and Validation

- [x] Add smoke test for health endpoint in [tests/e2e/test_smoke.py](tests/e2e/test_smoke.py).
- [x] Add API contract tests for generation endpoints in [tests/integration/test_generation_api.py](tests/integration/test_generation_api.py).
- [x] Add unit tests for pipeline stage selection in [tests/unit/test_pipeline_runner.py](tests/unit/test_pipeline_runner.py).
- [x] Add unit tests for schema validation/retry behavior in [tests/unit/test_generation_validation.py](tests/unit/test_generation_validation.py).

## 7. Acceptance Gate

- [x] All contract fields in [API_CONTRACTS.md](API_CONTRACTS.md) match frontend request/response types.
- [x] Structured error payload includes `error`, `message`, `details`, and `request_id`.
- [x] Diagnostics and source citations are present for generation responses.
- [x] p95 metrics and debug artifacts are recorded during benchmark runs.
