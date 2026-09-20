# Plan: Backend RAG Strategy (TFM MVP, Debug-First)

## 1) Goal

Build a maintainable backend RAG system that is easy to debug, easy to test, and easy to evolve.

Primary direction:
- Use deterministic hierarchical + hybrid RAG now.
- Keep Agentic RAG as a gated, optional advanced mode.

Key practical requirement:
- Every pipeline stage can run independently (parse, chapter detect, chunk, embed, store, retrieve, generate), so debugging never requires running the full flow.

## 2) Architecture Principles

- Single responsibility per module: parsing, chunking, embeddings, retrieval, generation, validation.
- Explicit contracts between stages using typed DTOs (Pydantic models).
- Stateless services where possible; side effects isolated in repository/adapters.
- Deterministic defaults for reproducibility (fixed thresholds, explicit top_k, strict schema validation).
- Observability built-in: request_id, document_id, stage, timing, token/cost metrics.

## 3) Step-Selectable Pipeline (Core Requirement)

Implement a pipeline runner with stage flags so you can execute only what you need:

- Stage A: validate_input
- Stage B: parse_document
- Stage C: detect_chapters
- Stage D: split_chunks
- Stage E: generate_embeddings
- Stage F: store_vectors
- Stage G: build_document_index
- Stage H: retrieve_context
- Stage I: generate_output

Execution modes:
- Full mode: A → I
- Stage mode: run only one stage (for debugging)
- Range mode: run B → F, etc.
- Resume mode: continue from last successful stage using persisted stage state.

Suggested interface:
- API debug endpoint for internal use, plus CLI runner command.
- Example CLI pattern: python -m backend_v3.tools.pipeline --document-id <id> --from split_chunks --to store_vectors --debug

## 4) Retrieval Strategy

Use a two-layer deterministic approach:

1. Hierarchical layer
- Build document-level synopsis/index at ingestion.
- For broad queries (example: summarize full document), read index first.

2. Evidence layer
- Retrieve scoped chunks with metadata filters.
- Enforce scope strictly: subject, document, chapter, summary.
- Include metadata always: subject_id, document_type, page (null for summaries), chapter_name.

3. Hybrid and rerank layer
- Vector retrieval + lexical fallback.
- Rerank top candidates before final context assembly.

Fallback policy:
- If context is weak (below threshold), return explicit insufficient-context response.
- For summary documents allow lower retrieval threshold than PDFs.

## 5) Output Reliability

- Enforce strict JSON output for flashcards/quiz.
- Validate with Pydantic schema.
- If invalid: one correction retry, then return standardized error.
- Include source attribution per item whenever possible.

## 6) Maintainability and Best Practices

- Code style: Ruff + Black + MyPy.
- Layering:
	- domain: entities, ports, rules
	- application: use cases/orchestration
	- infrastructure: Supabase, OpenAI, parser adapters
	- presentation: API routes/schemas
- Dependency injection for repositories and providers.
- No hardcoded keys, models, thresholds, or URLs.
- Centralized config + environment validation at startup.
- Feature flags:
	- ENABLE_AGENTIC_RAG
	- ENABLE_HYBRID_RETRIEVAL
	- ENABLE_DEBUG_ENDPOINTS

## 7) Debug and Observability Plan

- Structured logs (JSON) with fields:
	- request_id, subject_id, document_id, stage, duration_ms, retrieved_count, model, prompt_tokens, completion_tokens, estimated_cost.
- Stage timing dashboard-ready logs.
- Debug artifact storage per run:
	- parsed text snapshot
	- chapter detection output
	- chunk preview
	- retrieval candidates and scores
	- final prompt payload (safe/redacted)
- Correlation IDs propagated across all services.

## 8) Test Strategy (Easy to Run)

Create a dedicated test structure in backend_v3/tests with clear separation:

- tests/unit
	- parser tests
	- chapter detector tests
	- chunker tests
	- output schema validation tests
- tests/integration
	- ingestion pipeline tests
	- retrieval scope tests (subject/document/chapter)
	- generation JSON retry tests
- tests/e2e
	- full upload → generate flashcards/quiz flow
- tests/fixtures
	- sample PDFs
	- sample summaries
	- expected outputs

Developer-friendly execution:
- One command quick test: pytest -q
- Stage-specific test runs:
	- pytest tests/unit -q
	- pytest tests/integration -q
	- pytest tests/e2e -q

Quality gates:
- Minimum coverage target for critical modules.
- No merge if schema validation or scope isolation tests fail.

## 9) Phased Delivery

Phase 1 (Foundation)
- Set project skeleton, configuration, DI, logging, and stage-selectable pipeline runner.
- Implement parse/chunk/embed/store with test coverage.

Phase 2 (Retrieval + Reliability)
- Add hierarchical + hybrid retrieval and strict scope enforcement.
- Add strict JSON output validator + one retry.

Phase 3 (Evaluation + Optional Agentic)
- Add benchmark suite and acceptance thresholds (quality, p95 latency, cost).
- Enable Agentic RAG behind feature flag only if deterministic baseline is stable.

## 10) Decisions

- Primary now: deterministic hierarchical + hybrid RAG.
- Deferred: Agentic RAG after passing quality/latency/cost gates.
- Mandatory engineering qualities: stage-selectable debugging, maintainable architecture, and easy test execution.