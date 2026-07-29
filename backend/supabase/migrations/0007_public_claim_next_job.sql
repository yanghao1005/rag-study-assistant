-- ============================================================================
-- 0007_public_claim_next_job.sql
-- Expose job claim to service_role via PostgREST (wrapper over private.claim_next_job)
-- ============================================================================

create or replace function public.claim_next_job(p_job_types text[] default null)
returns public.jobs
language sql
security definer
set search_path = public
as $$
  select * from private.claim_next_job(p_job_types);
$$;

revoke all on function public.claim_next_job(text[]) from public, anon, authenticated;
grant execute on function public.claim_next_job(text[]) to service_role;
