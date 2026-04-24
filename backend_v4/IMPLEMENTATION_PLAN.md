# backend_v4 Implementation Plan

## Phase 0: Specification Freeze

Objective:

- lock objective, scope, architecture, and contracts before coding.

Deliverables:

- finalized docs in backend_v4 folder.
- approval checklist signed for MVP scope.

## Phase 1: Foundation and Skeleton

Tasks:

- create backend_v4 project skeleton with layer separation.
- centralize settings and environment validation.
- implement request-id middleware, error handlers, and structured logging.
- define domain/application DTO contracts.

Exit criteria:

- service boots and health endpoint passes.
- static checks and base tests pass.

## Phase 2: Ingestion Pipeline

Tasks:

- implement parse, chapter detection, and semantic chunking.
- implement embeddings and vector persistence.
- implement asynchronous indexing queue/status tracking.
- persist stage-level debug artifacts.

Exit criteria:

- upload to indexed document flow is stable.
- stage-selectable pipeline debug endpoint works.

## Phase 3: Retrieval Core

Tasks:

- implement vector + lexical candidate retrieval.
- implement reranking integration.
- implement intent router (direct/global/action).
- add summary index retrieval path.

Exit criteria:

- benchmarked relevance meets threshold targets.
- retrieval diagnostics returned consistently.

## Phase 4: Generation Endpoints

Tasks:

- implement summary, flashcards, and quiz generation use cases.
- enforce strict JSON schema validation and one retry policy.
- add source attribution mapping.

Exit criteria:

- generation endpoints return valid contracts.
- insufficient_context behavior validated by tests.

## Phase 5: Optional GraphRAG and Agentic Mode

Tasks:

- implement graph extraction + storage.
- add graph retrieval for relation-heavy questions.
- add planner/evaluator loop behind feature flag.

Exit criteria:

- deterministic baseline remains default.
- optional mode can be disabled without side effects.

## Phase 6: Hardening and Thesis Benchmark

Tasks:

- run latency, quality, and cost benchmarks.
- tune thresholds, chunk sizes, and reranker configuration.
- document final evidence for thesis methodology/results.

Exit criteria:

- KPI targets met or deviations clearly documented.
- release candidate prepared for frontend integration.
