# Supabase Migrations (backend_v3)

This folder contains production-ready migrations for backend_v3.

## Apply to your project

Run these commands from `backend_v3`:

```bash
supabase link --project-ref hbkxzfhmqmfsszizeelt
supabase migration new new-migration
supabase db push
```

If you already have the SQL migration file created in `supabase/migrations/`, you can skip creating an empty migration and run only `supabase db push`.

## Notes

- Embedding dimension is `1536` to match OpenAI `text-embedding-3-small`.
- All core tables are user-owned (`user_id`) with RLS policies.
- Admin users (`profiles.role = 'admin'`) bypass quota checks through `check_and_consume_quota`.
- Usage limits are defined by `subscription_plans` + `plan_limits` and tracked in `usage_events`.
- JS table contract is available at `supabase/table_schema.js` for backend/frontend alignment.
- Frontend contract types are available at `../frontend/src/types/db_contract.types.ts`.

## Migration order in this repo

1. `20260226151000_init_production_schema.sql`
2. `20260226152500_hardening_consistency.sql`

## Recommended deployment flow

1. Apply migration in a staging Supabase project first.
2. Run backend integration tests against staging.
3. Promote same migration to production.
4. Never edit schema manually in Supabase UI without migration.

## Sync checklist (DB -> backend -> frontend)

1. Update SQL migration(s) in `supabase/migrations`.
2. Update `supabase/table_schema.js`.
3. Update `frontend/src/types/db_contract.types.ts`.
4. Run backend tests and frontend type check.
