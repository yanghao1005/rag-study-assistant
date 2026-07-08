# TEST_EXECUTION_PLAN.md

Purpose: define how quality is validated across local development and CI for the final rewrite.

References:
- `FINAL_SPEC.md`
- `.github/workflows/backend_v5-ci.yml`

---

## 1) Quality Strategy

- Shift-left testing: tests start in Phase 1, not after feature completion.
- Contract-first validation for frontend-critical API behavior.
- CI must block merges on failed critical checks.
- Benchmarks are gates for backend quality/performance regressions.

---

## 2) Test Layers and Ownership

## Backend

- Unit tests: core logic, policies, parsers, DTO validation.
- Integration tests: repository + ingestion + job orchestration.
- Contract tests: endpoint shape and auth/error behavior.
- Benchmark tests: retrieval/generation/chat quality and latency.

## Frontend

- Unit tests: feature hooks, API adapters, helpers.
- Component tests: high-risk interactions and state transitions.
- E2E smoke: onboarding -> upload -> generate -> chat -> history.

---

## 3) Local Execution Checklist

## 3.1 Backend local checklist

- [ ] Install dependencies
- [ ] Configure `.env`
- [ ] Run test suites
- [ ] Run benchmark gate profile (`ci`) before PR

Suggested commands:

```bash
cd backend_v5
pytest tests/unit -q
pytest tests/integration -q
pytest tests/contract -q
pytest tests/e2e -q
python tools/ci_benchmark_gate.py --output-dir benchmark_reports --benchmark-profile ci --retrieval-iterations 12 --generation-iterations 12 --chat-iterations 12
```

## 3.2 Frontend local checklist

- [ ] Install dependencies
- [ ] Run lint
- [ ] Run unit/component tests
- [ ] Run smoke E2E on main flow

Suggested commands (adjust to configured tooling):

```bash
cd frontend_v2
pnpm install
pnpm lint
pnpm test
pnpm test:e2e
```

---

## 4) CI Requirements (Merge Blocking)

## 4.1 Backend CI (mandatory)

Minimum blocking checks:

- backend tests pass
- contract tests pass
- benchmark gate passes

Current baseline workflow:

- `.github/workflows/backend_v5-ci.yml`

## 4.2 Frontend CI (must be added/kept active)

Minimum blocking checks:

- lint
- unit/component tests
- smoke e2e on critical flow
- typecheck

Recommendation: add workflow `frontend_v2-ci.yml` with explicit required checks in branch protection.

---

## 5) Exit Criteria by Phase

| Phase | Required Quality Exit |
|---|---|
| Phase 0 | Contract baseline validated and documented |
| Phase 1 | Auth and error contract tests passing |
| Phase 2 | Ingestion + jobs integration tests stable |
| Phase 3 | Generation contracts + reliability tests passing |
| Phase 4 | Frontend smoke flow stable against backend |
| Phase 5 | Full CI gates green for release candidate |

---

## 6) Regression Policy

- No silent contract changes.
- Any flaky test repeated and triaged before merge.
- Benchmark regression above threshold requires mitigation note or rollback.
- Production fix PRs must include at least one test that reproduces the issue.

---

## 7) Test Data and Fixtures

- Keep deterministic fixtures for ingestion and generation scenarios.
- Maintain at least:
  - one short clean PDF
  - one noisy/complex PDF
  - one summary-text-only case
- Add expected contract snapshots for key API responses.

---

## 8) Release Readiness Checklist

- [ ] All required CI checks green
- [ ] No open critical defects
- [ ] Benchmarks within target envelope
- [ ] Security checks passed for auth/ownership flows
- [ ] Rollback/recovery instructions updated in `DELIVERY_RUNBOOK.md`

