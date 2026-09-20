-- ============================================================================
-- 0001_extensions.sql
-- Extensions required by RAG Study Assistant
-- ============================================================================

create schema if not exists extensions;

create extension if not exists "pgcrypto" with schema extensions;
create extension if not exists "vector" with schema extensions;
create extension if not exists "unaccent" with schema extensions;

-- Private schema for security-definer helpers (not exposed via Data API)
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
grant usage on schema private to postgres, service_role;

-- Spanish FTS config with unaccent (advanced-full-text-search)
do $$
begin
  if not exists (
    select 1 from pg_ts_config where cfgname = 'spanish_unaccent'
  ) then
    create text search configuration public.spanish_unaccent (copy = spanish);
    alter text search configuration public.spanish_unaccent
      alter mapping for hword, hword_part, word
      with unaccent, spanish_stem;
  end if;
end $$;

-- Shared updated_at trigger helper
create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;
