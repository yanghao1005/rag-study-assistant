# backend_v4 Risks and Metrics

## 1. Key Risks and Mitigations

### R1 - Retrieval noise degrades answer quality

- Risk: irrelevant chunks pollute generation context.
- Mitigation: hybrid retrieval + rerank + max context cap.
- Verification: top-k relevance benchmark and error analysis.

### R2 - Hallucinated quiz/flashcard content

- Risk: generated items not grounded in source materials.
- Mitigation: mandatory source attribution + evaluator checks + insufficient_context fallback.
- Verification: sampled manual audit and automated grounding checks.

### R3 - Cost and latency spikes

- Risk: recursive summaries and graph operations increase inference cost.
- Mitigation: async indexing, caching, and feature flags for expensive subsystems.
- Verification: p95 latency/cost dashboard and load-test thresholds.

### R4 - Debug complexity in multi-stage pipeline

- Risk: difficult issue isolation across parse/retrieve/generate components.
- Mitigation: stage-selectable runs, debug artifacts, correlation IDs.
- Verification: mean time to diagnose tracked during integration testing.

### R5 - Schema instability for frontend integration

- Risk: response shape drift breaks frontend rendering.
- Mitigation: strict DTO validation and contract tests in CI.
- Verification: API contract test suite against fixtures.

## 2. KPI Targets (Initial)

Quality:

- top-5 relevance >= 0.85 on benchmark set
- grounded generation pass rate >= 0.90 on audited samples

Reliability:

- schema-valid structured output rate = 1.00
- pipeline failure rate < 0.03 on standard test corpus

Performance:

- p95 generation latency <= 8s
- p95 retrieval latency <= 1.5s

Cost:

- average generation cost per request within thesis-defined budget
- indexing cost per document tracked and compared by document size

Developer Experience:

- end-to-end local setup <= 20 minutes
- deterministic reproduction path for failures via run_id and debug artifacts

## 3. Measurement Strategy

- Store benchmark datasets and expected outcomes under tests/fixtures.
- Run weekly benchmark snapshots and keep trend history.
- Include KPI table in thesis results section with methodology notes.
