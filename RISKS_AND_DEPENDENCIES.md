# RISKS_AND_DEPENDENCIES.md

Purpose: maintain a live view of delivery risks and cross-team dependencies during the final rewrite.

Reference: `FINAL_SPEC.md`

---

## 1) Current Critical Risks

| ID | Risk | Impact | Likelihood | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R1 | Hidden runtime code due to broad ignore rules | High | Medium | Scope/adjust ignore rules and verify tracked runtime paths | Repo Owner | Open |
| R2 | Frontend/backend contract drift | High | Medium | Enforce `CONTRACT_CHANGELOG.md` + contract tests + schema updates | API Owner | Open |
| R3 | Async ingestion instability | High | Medium | Stage diagnostics, retries, and integration tests | Backend Lead | Open |
| R4 | Missing frontend CI checks | High | High | Add merge-blocking workflow for `frontend_v2` | Frontend Lead | Open |
| R5 | Performance regressions in generation | Medium | Medium | Benchmark gates and trend review in CI | Backend Lead | Open |

---

## 2) Dependency Matrix

| Dependency | Needed By | Type | Blocking? | Notes |
|---|---|---|---|---|
| Auth contract finalized | Frontend API integration | Backend -> Frontend | Yes | Token and error behavior must be stable |
| Jobs endpoint stability | Documents UI flow | Backend -> Frontend | Yes | Polling and status states depend on this |
| Generation response schema | Flashcards/Quiz UI | Backend -> Frontend | Yes | UI parser and rendering depend on shape |
| Frontend route completion | End-to-end smoke tests | Frontend -> QA | Yes | E2E cannot be stabilized without route tree |
| Benchmark thresholds | Release candidate | Backend -> Release | Yes | CI gate must be green |

---

## 3) Phase Risk Review Checklist

Use this at each phase boundary:

- [ ] Any new high-risk dependency introduced?
- [ ] Any unresolved contract question blocking next phase?
- [ ] Any CI check consistently flaky?
- [ ] Any known migration risk for data model?
- [ ] Any unresolved auth/ownership edge case?

If yes, log action item in `IMPLEMENTATION_BACKLOG.md`.

---

## 4) Escalation Rules

- Escalate immediately if a risk is both High impact and High likelihood.
- Freeze new feature work when contract drift is detected.
- Require owner and due date for every unresolved dependency.

---

## 5) Risk Update Template

Use for new/changed risks:

- ID:
- Date:
- Description:
- Impact:
- Likelihood:
- Affected phase:
- Mitigation plan:
- Owner:
- Target resolution date:
- Status:

---

## 6) Open Questions Tracker

| Topic | Question | Owner | Due Date | Status |
|---|---|---|---|---|
| Contract evolution | How to version future breaking contract changes? | API Owner | TBD | Open |
| Frontend CI | Which E2E tooling and environment strategy is final? | Frontend Lead | TBD | Open |
| Data migration | How to reconcile legacy schema artifacts if reused? | Backend Lead | TBD | Open |

