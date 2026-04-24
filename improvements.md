# Full-Stack Improvement Review (Backend v4 + Frontend)

Date: 2026-04-21

## Executive Direction

Use a hybrid model:
- Keep backend as the source of truth for writes, ingestion, generation, and protected downloads.
- Allow direct frontend reads only for simple user-scoped lists when Row Level Security (RLS) is strict and no business logic is needed.

## Priority Findings

### P0 - Security and Data Ownership

1. User identity is accepted from request data in document routes.
	- Current state:
	  - `upload` receives `user_id` from multipart form.
	  - `download` receives `user_id` in query params.
	- Risk: user impersonation by modifying `user_id` client-side.
	- Affected file: `backend_v4/app/presentation/api/routes/documents.py`

2. Generation persistence falls back to `anonymous` user IDs.
	- Current state: generated content can be saved with user_id=`anonymous`.
	- Risk: broken ownership/audit and potential RLS mismatch.
	- Affected file: `backend_v4/app/application/use_cases/generation_service.py`

### P1 - Architecture and Maintainability

3. Business/persistence logic is in the presentation layer (`documents.py`).
	- Current state: Supabase client creation and document insert/status updates are route-local helpers.
	- Risk: hard to test, duplicated policy logic, fragile growth.
	- Affected file: `backend_v4/app/presentation/api/routes/documents.py`

4. Service boundaries are weakly typed in generation flow.
	- Current state: route passes `request.model_dump()` into service methods that accept `dict[str, Any]`.
	- Risk: contract drift and hidden runtime errors.
	- Affected files:
	  - `backend_v4/app/presentation/api/routes/generation.py`
	  - `backend_v4/app/application/use_cases/generation_service.py`

### P2 - Product Flow and UX

5. Subject detail page is overloaded and catches errors silently for history.
	- Current state: one large page handling subject header, generation controls, history viewer, and document tabs.
	- Risk: difficult evolution and inconsistent user feedback.
	- Affected file: `frontend/src/app/(main)/subjects/[id]/page.tsx`

6. Document actions include placeholder `onView` handlers.
	- Current state: `onView={(docId) => console.log("View", docId)}` in three tabs.
	- Risk: broken user expectation and incomplete workflow.
	- Affected file: `frontend/src/app/(main)/subjects/[id]/page.tsx`

### P3 - Documentation Quality

7. API contracts have mixed response section content under download endpoint.
	- Current state: `Response shape` with pipeline fields appears under the document download section.
	- Risk: integration confusion and client misuse.
	- Affected file: `backend_v4/API_CONTRACTS.md`

## Ownership Split: Frontend Direct vs Backend API

### Keep Backend API (mandatory)

- `POST /documents/upload`
- `POST /documents/summary`
- `GET /documents/{id}/download`
- `POST /generate/flashcards`
- `POST /generate/quiz`
- `POST /generate/summary`
- `GET /generate/history`
- `POST /pipeline/run` (debug)

Reason: these involve orchestration, provider calls, file system, cross-table effects, and security policies.

### Allow Direct Frontend Reads (optional, with strict RLS)

- Read-only subject list/details (`subjects`) for current user.
- Read-only document list (`documents`) and chapter list (`chapters`) for current user.

Rules:
- No direct writes from frontend for domain mutations that have side effects.
- Do not use service-role keys in frontend.
- Keep fallback API endpoints ready for future policy changes.

### Move to Backend (recommended)

- Subject create/delete currently done directly from frontend store and offline queue.
- Document delete currently done directly from frontend store and offline queue.

Target API additions:
- `POST /subjects`
- `DELETE /subjects/{id}`
- `DELETE /documents/{id}`

## Implementation Plan

### Phase 1 (Security First)

1. Add backend auth dependency that extracts user identity from Bearer token.
2. Remove trust in request-provided `user_id` for protected operations.
3. Enforce ownership server-side for upload/download/generation save.
4. Reject generation saves when user identity is missing.

Expected impact:
- closes impersonation risk
- consistent ownership in persisted content

### Phase 2 (Architecture Cleanup)

1. Move document route helper logic into application use cases.
2. Inject repositories/providers via container dependencies (no route-local client creation).
3. Convert generation service methods to typed request DTOs.

Expected impact:
- cleaner boundaries
- easier tests and safer refactors

### Phase 3 (Frontend Flow + UX)

1. Split subject detail page into focused feature components:
	- `SubjectHeader`
	- `SubjectGenerationPanel`
	- `GeneratedHistoryPanel`
	- `SubjectDocumentsPanel`
2. Replace placeholder `onView` actions with real document preview/open behavior.
3. Surface history fetch failures with retry and toast.
4. Add per-action loading states (`downloading`, `deleting`) on document cards.

Expected impact:
- better clarity and maintainability
- less user confusion
- fewer accidental duplicate actions

### Phase 4 (Contract and Quality)

1. Fix `API_CONTRACTS.md` section ordering/content.
2. Add contract tests for critical endpoints:
	- upload/summary/download
	- generate flashcards/quiz/history
3. Add frontend integration checks for error paths (auth fail, 404 download, offline replay failures).

## Success Metrics

- 0 endpoints that trust client-provided user IDs for authorization decisions.
- 100% generated content rows persisted with real authenticated user IDs.
- Subject detail page reduced in complexity (smaller components, simpler state graph).
- Contract docs and runtime behavior fully aligned.

## Immediate Next Action

Start with Phase 1 and implement auth-enforced identity in `documents` and `generation` routes before adding any new feature surface.
