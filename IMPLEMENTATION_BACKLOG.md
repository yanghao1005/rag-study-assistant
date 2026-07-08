# IMPLEMENTATION_BACKLOG.md

Purpose: turn `FINAL_SPEC.md` into an executable backlog with clear sequencing, dependencies, and definition of done.

Reference: `FINAL_SPEC.md`

---

## 1) Execution Rules

- Canonical targets: `frontend_v2` and `backend_v5`.
- No new feature work before Phase 0 and Phase 1 are complete.
- Contract-breaking changes require an entry in `CONTRACT_CHANGELOG.md`.
- A task is done only when code, tests, and docs are aligned.

---

## 2) Phase Backlog

## Phase 0 - Consolidation and Contract Freeze

Goal: remove ambiguity and lock final implementation direction.

### P0.1 Repository Hygiene
- [ ] Confirm what code must be tracked and what is generated.
- [ ] Remove or scope risky ignore rules that hide backend app code.
- [ ] Verify there is one active target path for frontend and backend.
Dependencies: none  
Done when: repository tracking strategy is explicit and no critical runtime code is silently ignored.

### P0.2 Contract Baseline Lock
- [ ] Freeze endpoint list, auth behavior, and error envelope from `FINAL_SPEC.md`.
- [ ] Align frontend schemas and backend contract tests with the same baseline.
- [ ] Open initial baseline entry in `CONTRACT_CHANGELOG.md`.
Dependencies: P0.1  
Done when: team can point to one authoritative contract set.

### P0.3 Delivery Workflow Setup
- [ ] Confirm branch naming and PR policy.
- [ ] Confirm required CI checks before merge.
- [ ] Publish dev workflow in `DELIVERY_RUNBOOK.md`.
Dependencies: P0.1  
Done when: everyone follows one repeatable delivery flow.

---

## Phase 1 - Backend Foundation

Goal: stable service skeleton with security and observability defaults.

### P1.1 App Skeleton and DI
- [ ] Ensure app factory and DI container patterns are consistent.
- [ ] Ensure route handlers stay thin and use use-case boundaries.
Dependencies: Phase 0  
Done when: service starts and architecture boundaries are enforceable.

### P1.2 Auth and Ownership
- [ ] Enforce bearer auth on protected endpoints.
- [ ] Resolve identity from token claims only.
- [ ] Validate ownership checks in repository methods and RLS.
Dependencies: P1.1  
Done when: protected flows do not trust client user identity fields.

### P1.3 Error and Middleware Baseline
- [ ] Standardize error envelope and status mapping.
- [ ] Ensure request tracing fields are present in logs.
- [ ] Validate payload size and abuse guards.
Dependencies: P1.1  
Done when: API errors are consistent and traceable.

---

## Phase 2 - Data and Ingestion Runtime

Goal: robust ingestion with asynchronous execution and diagnostics.

### P2.1 Migration and Repository Hardening
- [ ] Validate migration coverage for required entities.
- [ ] Confirm indexes and RLS policy behavior.
- [ ] Validate repository interfaces and implementations.
Dependencies: Phase 1  
Done when: persistence layer is stable and ownership-safe.

### P2.2 Async Ingestion Jobs
- [ ] Upload path returns quickly with job tracking.
- [ ] Worker updates status and stage run details.
- [ ] Jobs endpoint returns deterministic status payload.
Dependencies: P2.1  
Done when: upload workflow is non-blocking and observable.

### P2.3 Stage Diagnostics
- [ ] Store stage-level duration and details.
- [ ] Capture recoverable error diagnostics.
- [ ] Define replay/debug flow in `DELIVERY_RUNBOOK.md`.
Dependencies: P2.2  
Done when: ingestion failures are diagnosable without guesswork.

---

## Phase 3 - Retrieval and Generation

Goal: reliable outputs for flashcards, quizzes, summary, and history.

### P3.1 Retrieval Core
- [ ] Implement/verify retrieval pipeline with diagnostics.
- [ ] Ensure source metadata required by UI is always present.
Dependencies: Phase 2  
Done when: retrieval payload supports grounded generation.

### P3.2 Structured Generation Reliability
- [ ] Enforce schema-valid output for flashcards and quizzes.
- [ ] Add repair retry policy for malformed model output.
- [ ] Standardize insufficient-context behavior.
Dependencies: P3.1  
Done when: structured generation passes contract tests.

### P3.3 History and Group Lifecycle
- [ ] Validate create/read/update/delete behavior for generated groups.
- [ ] Validate history filtering by scope and limits.
Dependencies: P3.2  
Done when: generated assets are safely reusable and editable.

---

## Phase 4 - Frontend Workspace Delivery

Goal: complete end-user flow on App Router with typed integration.

### P4.1 Route Composition and Shell
- [ ] Implement/complete route groups for onboarding and workspace.
- [ ] Keep shell and sidebar behavior consistent with feature registry.
Dependencies: Phase 0, Phase 1  
Done when: navigation model is stable and context-aware.

### P4.2 Documents Flow
- [ ] Upload, list, rename, delete, and job polling flows.
- [ ] Ensure status and error states are user-friendly.
Dependencies: P4.1, Phase 2  
Done when: document flow is fully usable without manual API calls.

### P4.3 Generation, Chat, History
- [ ] Integrate generation and chat forms with schema-safe responses.
- [ ] Integrate history and generated-group management.
Dependencies: P4.2, Phase 3  
Done when: full learning workflow works end-to-end.

---

## Phase 5 - Quality Hardening and Release

Goal: production readiness and regression protection.

### P5.1 Backend Quality Gates
- [ ] Unit, integration, contract, benchmark gate all passing.
- [ ] Benchmark reports generated and archived in CI artifacts.
Dependencies: Phase 3  
Done when: backend can be merged without manual quality exceptions.

### P5.2 Frontend Quality Gates
- [ ] Add/complete unit and component tests for critical hooks/components.
- [ ] Add smoke E2E flow: onboarding -> upload -> generate -> chat -> history.
Dependencies: Phase 4  
Done when: frontend merge quality is enforceable in CI.

### P5.3 Release Readiness
- [ ] Validate operational checklist and rollback basics.
- [ ] Confirm outstanding risks are accepted or mitigated.
Dependencies: P5.1, P5.2  
Done when: candidate build can be promoted with confidence.

---

## 3) Suggested Parallelism

- Backend team can run P1/P2 while frontend team prepares P4 shell/routes.
- Contract owner should review every API-related PR to avoid drift.
- Testing tasks should start in parallel from first implementation phase, not at the end.

---

## 4) Tracking Cadence

- Daily: update task status and blockers.
- Every contract change: log it in `CONTRACT_CHANGELOG.md`.
- Every phase complete: update quality status in `TEST_EXECUTION_PLAN.md`.

