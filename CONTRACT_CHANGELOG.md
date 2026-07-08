# CONTRACT_CHANGELOG.md

Purpose: keep a strict history of API contract changes affecting frontend/backend compatibility.

References:
- `FINAL_SPEC.md`
- `frontend_v2/src/lib/schemas/backend.ts`
- `backend_v5/tests/unit/test_api_contracts.py`

---

## 1) Change Policy

- Every contract change must be logged before merge.
- No breaking change without migration strategy and rollout note.
- Contract PRs must update:
  - backend route behavior and tests
  - frontend schemas/parsers
  - frontend API client mappings

---

## 2) Versioning Approach

- Contract baseline: `v5-final-baseline`
- Use semantic labels:
  - `PATCH`: non-breaking clarifications/additions
  - `MINOR`: additive changes requiring optional frontend support
  - `MAJOR`: breaking changes requiring coordinated rollout

---

## 3) Baseline Snapshot

Date: 2026-07-08  
Label: `v5-final-baseline`  
Status: active

### Baseline endpoints

- `GET /api/health`
- `POST /api/documents/upload`
- `POST /api/documents/summary`
- `GET /api/documents`
- `PATCH /api/documents/{document_id}`
- `DELETE /api/documents/{document_id}`
- `GET /api/documents/{document_id}/download`
- `POST /api/pipeline/run`
- `GET /api/jobs/{job_id}`
- `POST /api/generate/flashcards`
- `POST /api/generate/quiz`
- `POST /api/generate/summary`
- `GET /api/generate/history`
- `GET /api/generate/groups/{group_id}`
- `PATCH /api/generate/groups/{group_id}`
- `DELETE /api/generate/groups/{group_id}`
- `POST /api/chat/ask`

### Baseline contract rules

- Protected endpoints require bearer auth.
- User identity resolved server-side from JWT.
- Scope literals supported: `subject`, `document`, `chapter`, `summary`.
- Error envelope standardized with machine-readable `error` code.

---

## 4) Changelog Entries

Use one entry per merged contract change.

## [TEMPLATE] YYYY-MM-DD - <change title>

- Type: PATCH | MINOR | MAJOR
- PR: <link-or-id>
- Owner: <name>
- Affected endpoints:
  - `<method path>`
- Request changes:
  - Added:
  - Changed:
  - Removed:
- Response changes:
  - Added:
  - Changed:
  - Removed:
- Error model changes:
  - Added:
  - Changed:
  - Removed:
- Frontend impact:
  - Required schema updates:
  - Required UI updates:
- Backend impact:
  - Required route/use-case updates:
  - Required migration updates:
- Rollout strategy:
  - Flagged?:
  - Backward compatibility window:
  - Cutover date:
- Validation checklist:
  - [ ] Backend contract tests updated
  - [ ] Frontend schema parsers updated
  - [ ] Frontend API client updated
  - [ ] CI passed
  - [ ] `FINAL_SPEC.md` reviewed for consistency

---

## 5) Deprecated Contract Register

Track fields/endpoints marked for removal.

| Deprecated Item | Replacement | Deprecation Date | Planned Removal | Status |
|---|---|---|---|---|
| N/A | N/A | N/A | N/A | active |

---

## 6) Open Contract Questions

Track unresolved decisions requiring explicit closure.

| Topic | Question | Owner | Due Date | Status |
|---|---|---|---|---|
| Error envelope | Should `message` be optional in some 4xx cases? | API Owner | TBD | open |
| Download auth | Any signed URL flow needed later? | Backend Lead | TBD | open |

