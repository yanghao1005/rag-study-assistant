# DB Consistency Guide (Supabase + Backend + Frontend)

## Goal
Keep one canonical schema so Supabase, backend, and frontend always use the same structure.

## 1) Single source of truth
- Treat SQL migrations as the source of truth (not ad-hoc table edits in UI).
- Store all schema changes in versioned SQL files (example: `migrations/0001_init.sql`, `migrations/0002_add_indexes.sql`).
- Apply migrations in order for local, staging, and production.

## 2) Contract ownership
- Database schema: migration SQL files.
- Backend contract: Pydantic models and API responses.
- Frontend contract: generated types from backend OpenAPI (or Supabase generated types for direct DB access).

## 3) Required consistency checks
- Every migration must include:
  - new/changed columns
  - constraints
  - indexes
  - rollback notes
- Backend PR must include model updates for changed fields.
- Frontend PR must include updated generated types.

## 4) Recommended workflow per schema change
1. Create migration SQL file.
2. Apply migration to local DB.
3. Update backend models/repositories.
4. Regenerate frontend/backend types.
5. Run integration tests against migrated schema.
6. Promote same migration to staging/prod.

## 5) Vector-specific rules
- Embedding model and vector dimension must match DB column dimensions.
- If embedding model changes (example: 1536 -> 768), create migration before deploying new app code.
- Keep retrieval RPC/functions versioned in migrations too.

## 6) Environment discipline
- Use separate Supabase projects (or schemas) for dev/staging/prod.
- Keep `.env` per environment and never hardcode credentials.
- Add startup checks in backend to validate required env vars in production.

## 7) CI guardrails (recommended)
- Run migration validation in CI.
- Run backend tests that touch repositories and retrieval filters.
- Fail CI if generated types are outdated.

## 8) Minimal operational checklist
- [ ] Migration file created and reviewed
- [ ] Backend models updated
- [ ] Frontend types regenerated
- [ ] Local tests pass
- [ ] Staging migration applied
- [ ] Production migration approved

