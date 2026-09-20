-- ============================================================================
-- 0004_search_functions.sql
-- Hybrid retrieval: dense (pgvector) + lexical (Postgres FTS / BM25-style ranking)
-- ============================================================================

-- Dense ANN search (cosine distance). Lower distance = more similar.
create or replace function public.match_chunks_dense(
  query_embedding vector(1536),
  match_count integer default 10,
  filter_user_id uuid default null,
  filter_subject_id uuid default null,
  filter_document_id uuid default null
)
returns table (
  id uuid,
  document_id uuid,
  subject_id uuid,
  chunk_index integer,
  content text,
  chapter_name text,
  page_start integer,
  page_end integer,
  metadata jsonb,
  distance float
)
language sql
stable
security invoker
set search_path = public
as $$
  select
    c.id,
    c.document_id,
    c.subject_id,
    c.chunk_index,
    c.content,
    c.chapter_name,
    c.page_start,
    c.page_end,
    c.metadata,
    (c.embedding <=> query_embedding) as distance
  from public.document_chunks c
  where c.embedding is not null
    and (filter_user_id is null or c.user_id = filter_user_id)
    and (filter_subject_id is null or c.subject_id = filter_subject_id)
    and (filter_document_id is null or c.document_id = filter_document_id)
  order by c.embedding <=> query_embedding
  limit greatest(match_count, 1);
$$;

-- Lexical / BM25-style ranking via ts_rank_cd + websearch_to_tsquery
create or replace function public.match_chunks_lexical(
  query_text text,
  match_count integer default 10,
  filter_user_id uuid default null,
  filter_subject_id uuid default null,
  filter_document_id uuid default null
)
returns table (
  id uuid,
  document_id uuid,
  subject_id uuid,
  chunk_index integer,
  content text,
  chapter_name text,
  page_start integer,
  page_end integer,
  metadata jsonb,
  rank float
)
language sql
stable
security invoker
set search_path = public
as $$
  with q as (
    select websearch_to_tsquery('spanish_unaccent', query_text) as tsq
  )
  select
    c.id,
    c.document_id,
    c.subject_id,
    c.chunk_index,
    c.content,
    c.chapter_name,
    c.page_start,
    c.page_end,
    c.metadata,
    ts_rank_cd(c.content_tsv, q.tsq) as rank
  from public.document_chunks c, q
  where q.tsq is not null
    and c.content_tsv @@ q.tsq
    and (filter_user_id is null or c.user_id = filter_user_id)
    and (filter_subject_id is null or c.subject_id = filter_subject_id)
    and (filter_document_id is null or c.document_id = filter_document_id)
  order by rank desc
  limit greatest(match_count, 1);
$$;

-- Reciprocal Rank Fusion merge of dense + lexical candidate lists
-- Call from app after fetching both sides, or use this when you already
-- have candidate ids. Primary hybrid merge lives in the backend adapter;
-- this helper is useful for SQL-side experiments.
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

grant execute on function public.match_chunks_dense to authenticated, service_role;
grant execute on function public.match_chunks_lexical to authenticated, service_role;
grant execute on function public.rrf_merge to authenticated, service_role;
