# backend_v5 Start-to-Finish Backend Plan (2026)

This document is the full execution guide to build backend_v5 from zero to production.

## 1. End Goal

Deliver a secure, observable, testable backend that supports:

- document ingestion (PDF and summary text)
- retrieval-augmented generation for flashcards, quiz, and summary
- interactive tutor chat agent for question answering
- deterministic fallbacks when agent confidence is low

## 2. Product Approach (Best Fit for This Project)

Use a hybrid architecture:

1. Deterministic Study Engine (default)

- best for stable outputs: flashcards, quiz, summary
- strict JSON schema validation
- citation-aware outputs

2. Tutor Agent Layer (optional but recommended)

- conversational Q and A across subject/document/chapter
- uses tools from deterministic engine
- can call retrieval, summarize, flashcards, quiz tools
- must fallback to deterministic answer path when confidence is weak

Why this is best in 2026:

- pure RAG is good for evidence retrieval but weaker for broad teaching interaction
- pure agentic systems are flexible but can be less predictable
- hybrid gives reliability plus better user experience

## 3. Scope and Non-Goals

In scope:

- secure auth and ownership checks
- async ingestion jobs
- hybrid retrieval with rerank
- generation endpoints
- tutor chat endpoint with tool-calling
- KPI-driven evaluation and benchmarks

Not in MVP scope:

- multi-tenant billing
- real-time collaborative editing
- fully autonomous multi-agent workflow as default

## 4. Required Capabilities Checklist

Functional:

- upload PDF and plain summary text
- parse, detect chapters, chunk semantically, embed, index
- generate flashcards with sources
- generate quiz with sources
- generate summaries from stored context
- chat with tutor agent and cite sources
- generation history per user and scope

Security:

- bearer token authentication
- server-resolved user identity
- no trust in request user_id for authorization
- row-level ownership checks for all protected data

Reliability:

- schema-valid structured outputs
- one retry on malformed JSON
- insufficient_context response when evidence is weak

Observability:

- request_id and job_id tracing
- per-stage timing and diagnostics
- token and cost metrics
- debug artifact snapshots for pipeline and generation

Quality:

- contract tests for API shape
- benchmark suite for retrieval and generation
- acceptance gates for relevance, latency, and reliability

## 5. Target Architecture

Architecture style:

- FastAPI + layered architecture + ports and adapters

Layers:

- presentation: routes, request and response schemas
- application: use cases and orchestration services
- domain: entities, policies, interfaces
- infrastructure: providers, repositories, parser, queue workers

Core subsystems:

- ingestion subsystem
- retrieval subsystem
- generation subsystem
- tutor agent subsystem
- observability subsystem

### 5.1 Retrieval Pipeline

1. dense retrieval
2. lexical retrieval
3. rank fusion
4. rerank top candidates
5. context assembly with citations

### 5.2 Tutor Agent Policy

- agent can only answer with retrieved evidence
- agent must cite source chunk or summary node
- if evidence is weak, respond with uncertainty and suggestion to ingest more material
- for structured tasks (flashcards and quiz), agent delegates to deterministic generators

## 6. Folder Structure To Implement

```text
backend_v5/
  README.md
  START_TO_FINISH_BACKEND_PLAN.md
  ARCHITECTURE.md
  API_CONTRACTS.md
  IMPLEMENTATION_PLAN.md
  RISKS_AND_METRICS.md
  MILESTONES.md
  .env.example
  docker-compose.yml
  requirements.txt

  app/
    main.py
    container.py

    core/
      config.py
      auth.py
      errors.py
      middleware.py
      logging.py
      telemetry.py

    presentation/
      api/
        router.py
        deps/
          auth.py
          request_context.py
        schemas/
          common.py
          documents.py
          generation.py
          retrieval.py
          chat.py
          jobs.py
        routes/
          health.py
          documents.py
          pipeline.py
          jobs.py
          generation.py
          chat.py

    application/
      dto/
        documents.py
        generation.py
        retrieval.py
        chat.py
      use_cases/
        upload_document.py
        create_summary_document.py
        run_pipeline.py
        generate_flashcards.py
        generate_quiz.py
        generate_summary.py
        answer_chat.py
        get_generation_history.py
      services/
        retrieval_service.py
        context_builder.py
        output_validator.py
        chat_orchestrator.py

    domain/
      models/
      value_objects/
      policies/
      ports/
        repositories.py
        providers.py
        queue.py

    infrastructure/
      parsing/
        pdf_parser.py
        chapter_detector.py
        semantic_chunker.py
      embeddings/
        openai_embeddings.py
      llm/
        openai_llm.py
      retrieval/
        dense_retriever.py
        lexical_retriever.py
        fusion.py
        reranker.py
      persistence/
        supabase/
          documents_repository.py
          chunks_repository.py
          generated_repository.py
          jobs_repository.py
      queue/
        broker.py
        ingestion_jobs.py

    workers/
      ingestion_worker.py

  tests/
    unit/
    integration/
    contract/
    e2e/
    benchmark/
    fixtures/

  tools/
    run_pipeline.py
    benchmark_retrieval.py
    benchmark_generation.py
    benchmark_chat.py
```

## 7. API Contracts (Minimum)

Core endpoints:

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
- POST /api/chat/ask

Rules:

- all protected endpoints require auth
- ownership checks enforced server-side
- response schemas versioned and tested

## 8. Environment and Dependencies

Minimum runtime:

- Python 3.12+
- FastAPI
- Pydantic v2
- Uvicorn
- Supabase client
- OpenAI SDK
- PyMuPDF or pypdf parser stack
- pytest, ruff, black, mypy

Optional but recommended:

- redis + rq (or celery) for async jobs
- OpenTelemetry exporter

## 9. Phase Plan (Start to Finish)

## Phase 0: Planning Freeze (Day 1 to Day 3)

Goal:

- freeze scope, contracts, and success metrics

Tasks:

- finalize API contracts and error shapes
- define auth model and ownership rules
- define benchmark datasets and KPIs

Deliverables:

- API_CONTRACTS.md complete
- RISKS_AND_METRICS.md complete
- test acceptance checklist

Done criteria:

- no unresolved contract/security ambiguity

## Phase 1: Foundation (Week 1)

Goal:

- create production-ready skeleton

Tasks:

- app factory, middleware, exception handlers
- DI container
- settings with env validation
- structured logging and request_id middleware

Deliverables:

- service boots with /api/health
- base unit tests

Done criteria:

- lint, typing, and base tests pass

## Phase 2: Data and Security Layer (Week 1 to Week 2)

Goal:

- enforce secure data ownership from start

Tasks:

- auth dependency reads bearer token claims
- remove client user_id trust in protected routes
- repository ownership filters for read/write
- create documents/chunks/generated/jobs repository interfaces

Deliverables:

- secure route guards
- ownership contract tests

Done criteria:

- zero protected flow relies on request user_id

## Phase 3: Ingestion V1 (Week 2 to Week 3)

Goal:

- stable indexing pipeline

Tasks:

- parse document
- chapter detection
- semantic chunking
- embedding generation
- vector persistence
- summary node build

Deliverables:

- stage-selectable pipeline run endpoint
- debug artifacts per stage

Done criteria:

- sample corpus ingestion success rate above 97 percent

## Phase 4: Async Jobs and Worker (Week 3)

Goal:

- decouple ingestion from request lifecycle

Tasks:

- document upload creates job and returns quickly
- worker executes pipeline and updates status
- /api/jobs/{job_id} returns stage progress and errors

Deliverables:

- ingestion_worker process
- jobs table and repository

Done criteria:

- upload endpoint p95 latency under 1 second (without file transfer time)

## Phase 5: Retrieval Engine V1 (Week 4)

Goal:

- strong relevance and diagnostics

Tasks:

- dense retrieval
- lexical retrieval
- fusion and rerank
- context assembly and token budget policy

Deliverables:

- retrieval diagnostics in API response
- benchmark script for retrieval relevance

Done criteria:

- top-5 relevance meets agreed KPI

## Phase 6: Study Generation Endpoints (Week 5)

Goal:

- reliable flashcards, quiz, summary

Tasks:

- generate flashcards with strict schema
- generate quiz with strict schema
- generate summary from summary index plus chunks
- one-retry JSON repair flow
- save generated results and history

Deliverables:

- /api/generate/flashcards
- /api/generate/quiz
- /api/generate/summary
- /api/generate/history

Done criteria:

- structured responses are schema-valid in contract tests

## Phase 7: Tutor Agent Endpoint (Week 6)

Goal:

- conversational Q and A with tool orchestration

Tasks:

- implement /api/chat/ask
- implement agent toolset:
  - retrieve_context
  - summarize_scope
  - generate_flashcards
  - generate_quiz
- enforce source citation and fallback policy
- log tool call trace in debug artifacts

Deliverables:

- chat endpoint with cited answers
- agent trace diagnostics

Done criteria:

- tutor answers pass grounding checks on benchmark set

## Phase 8: Full Testing and Evaluation (Week 7)

Goal:

- validate quality, reliability, and performance

Tasks:

- unit and integration coverage for critical logic
- contract tests for all frontend-critical routes
- e2e tests for upload to generation and upload to chat
- benchmark runs for retrieval, generation, chat

Deliverables:

- benchmark reports with trend history
- release acceptance report

Done criteria:

- KPI gates met or deviations documented with mitigation

## Phase 9: Hardening and Release (Week 8)

Goal:

- production readiness

Tasks:

- error budget and retry tuning
- rate limiting and abuse protection
- runbooks for incident response
- deployment and rollback plan

Deliverables:

- release candidate
- operational runbook

Done criteria:

- smoke tests and rollback drill pass

## 10. Testing Strategy (Mandatory)

Unit tests:

- parser, chapter detector, chunker
- retrieval scoring and fusion
- schema validation and retry logic
- auth and ownership policy helpers

Integration tests:

- ingestion stage transitions
- repository ownership filtering
- generation persistence and history
- chat tool orchestration flow

Contract tests:

- request and response shape per endpoint
- error envelope consistency

E2E tests:

- upload PDF to flashcards
- upload summary to quiz
- ask tutor question with citations

Benchmark tests:

- retrieval relevance
- generation grounding pass rate
- chat grounding and latency

## 11. KPI Targets

Quality:

- top-5 relevance >= 0.88
- grounding pass rate >= 0.92

Reliability:

- schema-valid structured outputs = 1.00
- pipeline failure rate < 0.03

Performance:

- p95 retrieval <= 1.2s
- p95 generation <= 6.0s
- p95 chat <= 7.0s

Developer experience:

- clean setup <= 20 minutes
- reproducible failure replay by request_id and run_id

## 12. Step-by-Step Execution Commands

Bootstrap:

```bash
cd backend_v5
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
copy .env.example .env
```

Run API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run worker:

```bash
python -m app.workers.ingestion_worker
```

Run tests:

```bash
pytest tests/unit -q
pytest tests/integration -q
pytest tests/contract -q
pytest tests/e2e -q
```

Run benchmarks:

```bash
python -m tools.benchmark_retrieval
python -m tools.benchmark_generation
python -m tools.benchmark_chat
```

## 13. Risks and Mitigation

Risk: weak retrieval for abstract questions

- Mitigation: summary-aware retrieval plus multi-query expansion and rerank

Risk: hallucinated educational outputs

- Mitigation: strict schema, citations, grounding checks, insufficient_context fallback

Risk: agent unpredictability

- Mitigation: deterministic tools, bounded toolset, feature-flag rollout, benchmark gate

Risk: latency and cost growth

- Mitigation: caching, batching, async jobs, budget-aware context assembly

## 14. Definition of Done (Project Complete)

Project is complete when all are true:

- all target endpoints are implemented and contract-tested
- auth and ownership checks pass security tests
- ingestion and generation pipelines are observable and benchmarked
- tutor agent answers are grounded and cited
- KPI thresholds are met or deviations are accepted with documented rationale
- release runbook and rollback plan are documented

## 15. Practical Rollout Strategy

Rollout order:

1. deterministic generation only
2. enable chat endpoint internally
3. enable tutor agent for limited users
4. full rollout after benchmark and incident-free period

This sequence minimizes risk while delivering value early.
