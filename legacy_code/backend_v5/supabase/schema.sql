-- backend_v5 baseline schema
-- Run in Supabase SQL editor or as a migration.

-- WARNING: This script deletes backend_v5 app data.
drop table if exists pipeline_stage_runs cascade;
drop table if exists jobs cascade;
drop table if exists generated_content cascade;
drop table if exists document_chunks cascade;
drop table if exists documents cascade;

create extension if not exists pgcrypto;
create extension if not exists vector;

create table documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  subject_id uuid,
  document_type text not null check (document_type in ('pdf', 'summary')),
  filename text not null,
  storage_path text,
  content_text text,
  status text not null default 'processing' check (status in ('processing', 'ready', 'error')),
  error_message text,
  total_pages integer not null default 0,
  file_size bigint not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  document_id uuid not null references documents(id) on delete cascade,
  chunk_index integer not null,
  content text not null,
  chapter_name text,
  page integer,
  metadata jsonb not null default '{}'::jsonb,
  embedding vector(1536),
  created_at timestamptz not null default now()
);

create index idx_document_chunks_document_id on document_chunks(document_id);
create index idx_document_chunks_user_id on document_chunks(user_id);

create table generated_content (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  scope text not null check (scope in ('subject', 'document', 'chapter', 'summary')),
  scope_id uuid not null,
  content_type text not null check (content_type in ('flashcard', 'quiz', 'summary', 'chat_answer')),
  content_json jsonb not null,
  created_at timestamptz not null default now()
);

create index idx_generated_user_scope on generated_content(user_id, scope, scope_id);

create table jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  job_type text not null,
  status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'failed')),
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table pipeline_stage_runs (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references jobs(id) on delete cascade,
  stage text not null,
  status text not null check (status in ('ok', 'error')),
  duration_ms integer not null default 0,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- RLS baseline
alter table documents enable row level security;
alter table document_chunks enable row level security;
alter table generated_content enable row level security;
alter table jobs enable row level security;
alter table pipeline_stage_runs enable row level security;

-- Policies assume auth.uid() is available (Supabase auth JWT).
drop policy if exists documents_owner_policy on documents;
create policy documents_owner_policy
on documents
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists chunks_owner_policy on document_chunks;
create policy chunks_owner_policy
on document_chunks
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists generated_owner_policy on generated_content;
create policy generated_owner_policy
on generated_content
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists jobs_owner_policy on jobs;
create policy jobs_owner_policy
on jobs
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists stage_runs_owner_policy on pipeline_stage_runs;
create policy stage_runs_owner_policy
on pipeline_stage_runs
for select
using (
  exists (
    select 1 from jobs j
    where j.id = pipeline_stage_runs.job_id
      and j.user_id = auth.uid()
  )
);
