-- ============================================================================
-- 0006_cleanup_legacy.sql
-- Remove leftover RPCs from previous schemas + harden rrf_merge search_path
-- ============================================================================

create or replace function public.rrf_merge(
  dense_ids uuid[],
  lexical_ids uuid[],
  k integer default 60,
  result_limit integer default 10
)
returns table (
  chunk_id uuid,
  rrf_score float
)
language sql
immutable
set search_path = public
as $$
  with dense as (
    select id, ordinality::int as r
    from unnest(dense_ids) with ordinality as t(id, ordinality)
  ),
  lex as (
    select id, ordinality::int as r
    from unnest(lexical_ids) with ordinality as t(id, ordinality)
  ),
  scored as (
    select id, 1.0 / (k + r) as score from dense
    union all
    select id, 1.0 / (k + r) as score from lex
  )
  select id as chunk_id, sum(score)::float as rrf_score
  from scored
  group by id
  order by rrf_score desc
  limit greatest(result_limit, 1);
$$;

drop function if exists public.handle_new_user() cascade;
drop function if exists public.ensure_current_profile() cascade;
drop function if exists public.check_and_consume_quota(public.usage_metric, bigint, text, jsonb) cascade;
drop function if exists public.get_effective_plan(uuid) cascade;
drop function if exists public.get_monthly_limit(uuid, public.usage_metric) cascade;
drop function if exists public.get_usage_amount(uuid, public.usage_metric, date) cascade;
drop function if exists public.is_admin(uuid) cascade;
drop function if exists public.match_document_chunks(public.vector, double precision, integer, uuid, uuid, uuid, uuid) cascade;
drop function if exists public.match_documents cascade;
drop function if exists public.update_updated_at_column() cascade;
drop function if exists public.current_period_start() cascade;
drop type if exists public.usage_metric cascade;
