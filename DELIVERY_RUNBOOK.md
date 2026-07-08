# DELIVERY_RUNBOOK.md

Purpose: define a repeatable daily workflow to ship safely and quickly during the final rewrite.

References:
- `FINAL_SPEC.md`
- `IMPLEMENTATION_BACKLOG.md`
- `CONTRACT_CHANGELOG.md`
- `TEST_EXECUTION_PLAN.md`

---

## 1) Daily Development Loop

1. Pick one backlog task with clear dependencies.
2. Confirm contract impact (if any) before coding.
3. Implement in small, reviewable increments.
4. Run local checks relevant to the change.
5. Update docs/changelog if contract or behavior changed.
6. Open PR with explicit validation evidence.

---

## 2) Branch and PR Convention

## Branch naming

- `feat/<area>-<short-description>`
- `fix/<area>-<short-description>`
- `chore/<area>-<short-description>`

Examples:

- `feat/backend-jobs-status-endpoint`
- `feat/frontend-documents-flow`
- `fix/backend-auth-ownership-check`

## PR size rule

- Prefer small PRs focused on one backlog item.
- Avoid mixing backend contract changes with unrelated UI polish.

---

## 3) Definition of Ready (Task Start)

Before starting a task:

- [ ] Task objective is clear.
- [ ] Dependencies are satisfied.
- [ ] Required files/components are identified.
- [ ] Contract impact assessed.
- [ ] Test expectation defined.

If any is missing, refine task first.

---

## 4) Definition of Done (Task Complete)

For each task:

- [ ] Code implemented with architecture boundaries respected.
- [ ] Relevant tests added/updated and passing.
- [ ] Lint/type checks passing for touched areas.
- [ ] Contract update logged if request/response changed.
- [ ] User-facing behavior documented when needed.

---

## 5) Contract Change Workflow

If API contract changes:

1. Add/change backend behavior and tests.
2. Update frontend Zod schema.
3. Update frontend API client mapping.
4. Add entry to `CONTRACT_CHANGELOG.md`.
5. Mention migration/compat notes in PR.

No exceptions.

---

## 6) Incident and Hotfix Workflow

When a blocker/bug appears:

1. Reproduce with minimal steps.
2. Create a short failing test or deterministic repro note.
3. Apply fix in the smallest safe change.
4. Re-run impacted tests and smoke flow.
5. Add root cause + prevention note under "Postmortem Notes".

---

## 7) Postmortem Notes

Template for major issues:

- Date:
- Scope:
- Symptom:
- Root cause:
- Fix:
- Added test/guardrail:
- Follow-up tasks:

---

## 8) Weekly Cadence

## Monday
- Review backlog priorities and dependencies.
- Lock this week's contract-sensitive tasks.

## Midweek
- Check CI health and flaky tests.
- Review benchmark trend deltas.

## Friday
- Validate phase progress against acceptance gates.
- Update risks and next-week priorities.

---

## 9) Communication Notes

- Always link code changes to backlog item IDs.
- Surface blockers early; do not wait until PR stage.
- Keep PR descriptions concise and evidence-based.

