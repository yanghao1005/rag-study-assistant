# backend_v5

2026 strategy and execution guide for the RAG Study Assistant backend.

## Full Build Guide

For the complete end-to-end implementation plan (requirements, phases, tasks, commands, KPIs, and rollout), see:

- [START_TO_FINISH_BACKEND_PLAN.md](START_TO_FINISH_BACKEND_PLAN.md)

## Future Backlog

For post-TFM feature ideas and rollout priorities beyond current MVP scope, see:

- [FUTURE_IMPLEMENTATION_IDEAS.md](FUTURE_IMPLEMENTATION_IDEAS.md)

## 1. Executive Direction

Build backend_v5 as a production-oriented, evaluation-driven backend with these principles:

- Deterministic Hybrid RAG is the default path.
- Agentic behaviors are optional and guarded by feature flags.
- Security and ownership are enforced on the server, never from client-provided user ids.
- Every major flow is observable, testable, and benchmarked.

This keeps the thesis and product aligned: reliable educational outputs first, advanced orchestration second.

## 2. What To Keep From Existing Versions

Keep these strengths from backend_v3 and backend_v4:

- Layered architecture: presentation, application, domain, infrastructure.
- Stage-based ingestion pipeline and debug artifacts.
- Strict output contracts for quiz and flashcards.
- Feature flags for expensive or experimental capabilities.
- Supabase-ready integration and local fallback mode.

## 3. What Must Change In backend_v5

Priority improvements:

1. Auth and ownership hardening

- Remove trust in request body/query user_id for protected operations.
- Resolve user identity from bearer token at API boundary.
- Enforce ownership in all repository methods.

2. Strongly typed service boundaries

- Replace dict-based use case inputs with explicit DTOs.
- Keep validation in schema layer and application layer.

3. Route thinness

- Move route-level persistence/orchestration logic into use cases.
- Routes should only map HTTP to DTOs and return responses.

4. Async job orchestration for ingestion

- Upload should create a job and return quickly.
- Worker performs parse/chunk/embed/index steps.
- API provides job status and stage diagnostics.

5. Evaluation and benchmark as first-class modules

- Build offline and online quality checks.
- Gate releases by KPI thresholds (quality, latency, cost, reliability).

## 4. 2026 Recommended Technical Approach

### 4.1 Operating Modes

- Mode A (default): Deterministic Hybrid RAG
- Mode B (optional): Summary-aware retrieval for global conceptual questions
- Mode C (experimental): Agentic planner/evaluator loop behind flag

Mode C should never be on by default until benchmark evidence proves it beats Mode A and B on your datasets.

### 4.2 Retrieval Strategy

Use a three-stage retrieval stack:

1. Candidate generation

- Dense retrieval (embeddings)
- Lexical retrieval (BM25 or full-text)

2. Candidate fusion

- Reciprocal rank fusion or weighted score merge

3. Reranking

- Cross-encoder or hosted reranker on fused top N

Context assembly should include:

- compact chunk text
- source metadata (document_id, page, chapter)
- confidence and score diagnostics

### 4.3 Generation Reliability

For structured outputs (flashcards, quiz):

- schema-constrained JSON output
- one repair retry on invalid JSON/schema mismatch
- explicit insufficient_context fallback
- citation mapping for each generated item when possible

### 4.4 Storage Strategy

Pragmatic default:

- Supabase Postgres + pgvector for metadata and vectors in one platform

Optional scale path:

- Postgres for metadata
- dedicated vector DB (Qdrant) for high-volume retrieval workloads

Start with one-store simplicity unless benchmark data justifies split infrastructure.

### 4.5 Observability and Operations

Mandatory telemetry:

- request_id, user_id, scope_id, job_id
- stage, duration_ms, retrieved_count
- prompt_tokens, completion_tokens, estimated_cost
- model and provider info

Adopt:

- structured JSON logs
- OpenTelemetry tracing
- metrics endpoint for dashboards

## 5. Suggested backend_v5 Structure

Use this as the target folder shape:

```text
backend_v5/
  README.md
  ARCHITECTURE.md
  API_CONTRACTS.md
  IMPLEMENTATION_PLAN.md
  .env.example
  docker-compose.yml
  pyproject.toml

  app/
    main.py
    container.py

    core/
      config.py
      auth.py
      errors.py
      logging.py
      telemetry.py
      middleware.py

    presentation/
      api/
        router.py
        deps/
          auth.py
          request_context.py
        routes/
          health.py
          documents.py
          pipeline.py
          jobs.py
          generation.py
          retrieval.py
        schemas/
          common.py
          documents.py
          generation.py
          pipeline.py

    application/
      dto/
        documents.py
        generation.py
        pipeline.py
      use_cases/
        upload_document.py
        create_summary.py
        run_pipeline_stage.py
        generate_flashcards.py
        generate_quiz.py
        get_generation_history.py
      services/
        retrieval_service.py
        context_builder.py
        output_validator.py

    domain/
      models/
      value_objects/
      policies/
      ports/
        repositories.py
        providers.py
        queue.py

    infrastructure/
      persistence/
        supabase/
          documents_repo.py
          chunks_repo.py
          generated_repo.py
      retrieval/
        dense_retriever.py
        lexical_retriever.py
        reranker.py
        fusion.py
      llm/
        model_registry.py
        openai_provider.py
      embeddings/
        openai_embeddings.py
      parsing/
        pdf_parser.py
        chapter_detector.py
        semantic_chunker.py
      queue/
        broker.py
        jobs.py

    workers/
      ingestion_worker.py
      maintenance_worker.py

  tests/
    unit/
    integration/
    contract/
    e2e/
    benchmark/
    fixtures/

  tools/
    run_pipeline.py
    benchmark_generation.py
    benchmark_retrieval.py
    e2e_check.py

  docs/
    decisions/
    runbooks/
    benchmarks/
```

## 6. API Design Baseline

Keep API contracts stable and versioned.

Suggested core endpoints:

- GET /api/health
- POST /api/documents/upload
- POST /api/documents/summary
- GET /api/documents/{document_id}/download
- POST /api/pipeline/run
- GET /api/jobs/{job_id}
- POST /api/generate/flashcards
- POST /api/generate/quiz
- POST /api/generate/summary
- GET /api/generate/history

Rules:

- all mutating endpoints require auth
- user identity comes from token, not request payload
- contract tests must run in CI for these endpoints

## 7. Data Model Baseline

Recommended baseline entities:

- users
- subjects
- documents
- document_chunks
- summary_nodes
- generated_content
- pipeline_runs
- pipeline_stage_runs

Useful additions:

- retrieval_events (candidate scores, rerank outcomes)
- generation_events (model, tokens, latency, validation_retries)
- benchmark_runs (quality and latency snapshots)

## 8. How To Start backend_v5

### 8.1 Prerequisites

- Python 3.12+
- Docker Desktop
- Supabase project (or local Postgres for development)
- API key(s) for chosen model providers

### 8.2 Initial Setup

```bash
cd backend_v5
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
copy .env.example .env
```

Fill .env minimum values:

- APP_NAME
- API_PREFIX
- SUPABASE_URL
- SUPABASE_SERVICE_KEY
- OPENAI_API_KEY
- VECTOR_REPOSITORY_PROVIDER
- LLM_PROVIDER
- EMBEDDINGS_PROVIDER

### 8.3 Run Services

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If using background workers for ingestion:

```bash
python -m app.workers.ingestion_worker
```

### 8.4 Validate Quickly

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/contract -q
```

### 8.5 Run Benchmarks and Gates

Generate benchmark reports for retrieval, generation, and chat:

```bash
python tools/benchmark_retrieval.py --output benchmark_reports/retrieval_benchmark.json --iterations 12
python tools/benchmark_generation.py --output benchmark_reports/generation_benchmark.json --iterations 12
python tools/benchmark_chat.py --output benchmark_reports/chat_benchmark.json --iterations 12
```

Run CI profile gate (conservative thresholds):

```bash
python tools/ci_benchmark_gate.py --output-dir benchmark_reports --benchmark-profile ci --retrieval-iterations 12 --generation-iterations 12 --chat-iterations 12
```

Run production profile gate (stricter thresholds):

```bash
python tools/ci_benchmark_gate.py --output-dir benchmark_reports --benchmark-profile prod --retrieval-iterations 12 --generation-iterations 12 --chat-iterations 12
```

## 9. Delivery Plan (Execution Phases)

### Phase 0: Contract and Security Freeze

Deliver:

- API contracts and auth model finalized
- ownership policy documented and tested

Exit criteria:

- zero endpoint trusts client user_id for authorization

### Phase 1: Foundation

Deliver:

- app skeleton, config, DI container, request middleware
- standardized error contract
- telemetry plumbing

Exit criteria:

- health endpoint and base tests pass

### Phase 2: Ingestion Pipeline V1

Deliver:

- parse, chapter detect, chunk, embed, persist
- stage-selectable runs and debug artifacts
- async job status endpoint

Exit criteria:

- upload to indexed flow is stable on fixture corpus

### Phase 3: Retrieval Core V1

Deliver:

- dense + lexical retrieval
- score fusion + rerank
- retrieval diagnostics payload

Exit criteria:

- top-5 relevance meets target on benchmark set

### Phase 4: Generation Reliability V1

Deliver:

- flashcards/quiz/summary endpoints
- strict schema validation + single retry repair
- citation and insufficient_context behaviors

Exit criteria:

- 100 percent schema-valid structured responses

### Phase 5: Hardening and Benchmark

Deliver:

- load and latency tests
- cost profiling and caching policy
- CI gates for contracts and critical benchmarks

Exit criteria:

- p95 latency and cost targets met or documented

### Phase 6: Optional Advanced Paths

Deliver (optional):

- summary-tree retrieval upgrades
- graph retrieval for relation-heavy questions
- agentic planner/evaluator in experimental mode

Exit criteria:

- advanced mode outperforms deterministic baseline in controlled evaluation

## 10. Brainstorm Backlog (High-Value Ideas)

### A. Retrieval Quality Ideas

- Dynamic chunk size by heading density and document type.
- Query rewriting before retrieval for abstract questions.
- Multi-query retrieval then deduplicate with MMR.
- Retrieval budget manager: limit context by evidence quality, not only token count.
- Auto-fallback from chapter scope to document scope when evidence is too weak.

### B. Study Output Ideas

- Flashcard difficulty calibration based on historical user mistakes.
- Quiz distractor quality scoring to avoid obviously wrong options.
- Citation confidence badge per item.
- Explain-why mode for each answer with compact evidence snippets.

### C. Developer Velocity Ideas

- Golden dataset for deterministic regression checks.
- One-command local bootstrap script.
- Scenario-based benchmark presets (small doc, large doc, noisy PDF).
- Replay tool: rerun a failed request by request_id with same settings.

### D. Cost and Performance Ideas

- Embedding cache by chunk hash.
- Generation cache for repeated scope + query combinations.
- Batch embedding for ingestion jobs.
- Background summary index refresh after first ingestion.

### E. Safety and Governance Ideas

- PII redaction pass for logs and artifacts.
- Prompt and model version stamping in outputs.
- Explicit uncertainty statements when confidence is low.
- Config guardrails to block risky production settings.

## 11. Anti-Patterns To Avoid

- Putting DB writes and business rules directly inside route handlers.
- Passing untyped dict payloads across application services.
- Enabling expensive agentic workflows by default.
- Shipping without contract tests for frontend-critical endpoints.
- Mixing auth identity and domain ids from client payloads.

## 12. KPI Targets For v5

Quality:

- top-5 relevance >= 0.88
- grounded generation pass rate >= 0.92

Reliability:

- schema-valid structured output rate = 1.00
- ingestion pipeline failure rate < 0.03

Performance:

- p95 generation latency <= 6 seconds
- p95 retrieval latency <= 1.2 seconds

Developer experience:

- fresh local setup <= 20 minutes
- reproducible failure replay by request_id and run_id

## 13. Immediate Next 10 Tasks

1. Create backend_v5 skeleton from the structure above.
2. Add auth dependency and remove request user_id trust in mutating endpoints.
3. Define typed DTOs for generation and pipeline use cases.
4. Implement async ingestion job model with job status endpoint.
5. Port and improve pipeline runner with stage checks and artifacts.
6. Add contract tests for document and generation endpoints.
7. Implement retrieval diagnostics schema and logging fields.
8. Add benchmark fixtures and baseline retrieval benchmark script.
9. Add generation schema validator with retry-repair flow.
10. Create CI quality gates for tests, contracts, and benchmark smoke checks.

## 14. Practical Recommendation

For this project stage and thesis scope in 2026, the best approach is:

- Build a robust deterministic backend first.
- Keep advanced agentic/graph features optional and benchmark-gated.
- Prioritize security, typed contracts, observability, and evaluation rigor.

This gives you stronger academic evidence, easier debugging, safer production behavior, and faster feature iteration.
