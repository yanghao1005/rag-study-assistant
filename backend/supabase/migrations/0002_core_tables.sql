-- ============================================================================
-- 0002_core_tables.sql
-- Profiles, subjects, documents, chunks (ingestion + vector store)
-- Ownership model: each auth user owns their subjects/documents (RLS by auth.uid())
-- ============================================================================

-- ---------------------------------------------------------------------------
-- profiles (1:1 with auth.users)
-- ---------------------------------------------------------------------------
create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  avatar_url text,
  onboarding_completed boolean not null default false,
  preferences jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

-- Auto-create profile on signup (security definer lives in private schema)
create or replace function private.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.email)
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function private.handle_new_user();

-- ---------------------------------------------------------------------------
-- subjects (study topics / courses)
-- ---------------------------------------------------------------------------
create table public.subjects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  description text,
  color text,
  sort_order integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint subjects_name_not_blank check (char_length(trim(name)) > 0)
);

create index idx_subjects_user_id on public.subjects (user_id);
create unique index uq_subjects_user_name on public.subjects (user_id, lower(name));

create trigger subjects_set_updated_at
before update on public.subjects
for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- documents (uploaded PDFs / imported text)
-- ---------------------------------------------------------------------------
create table public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid not null references public.subjects (id) on delete cascade,
  document_type text not null default 'pdf'
    check (document_type in ('pdf', 'text', 'summary')),
  filename text not null,
  storage_path text,
  mime_type text,
  status text not null default 'queued'
    check (status in ('queued', 'processing', 'ready', 'error')),
  error_message text,
  total_pages integer not null default 0 check (total_pages >= 0),
  file_size bigint not null default 0 check (file_size >= 0),
  checksum text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_documents_user_id on public.documents (user_id);
create index idx_documents_subject_id on public.documents (subject_id);
create index idx_documents_status on public.documents (status) where status <> 'ready';

create trigger documents_set_updated_at
before update on public.documents
for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- document_chunks (semantic units + dense embedding + lexical FTS)
-- ---------------------------------------------------------------------------
create table public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid not null references public.subjects (id) on delete cascade,
  document_id uuid not null references public.documents (id) on delete cascade,
  chunk_index integer not null check (chunk_index >= 0),
  content text not null check (char_length(content) > 0),
  content_tsv tsvector generated always as (
    to_tsvector('spanish_unaccent', coalesce(content, ''))
  ) stored,
  chapter_name text,
  page_start integer,
  page_end integer,
  token_count integer,
  metadata jsonb not null default '{}'::jsonb,
  -- text-embedding-3-small
  embedding vector(1536),
  created_at timestamptz not null default now(),
  constraint uq_document_chunks_doc_index unique (document_id, chunk_index)
);

create index idx_document_chunks_document_id on public.document_chunks (document_id);
create index idx_document_chunks_subject_id on public.document_chunks (subject_id);
create index idx_document_chunks_user_id on public.document_chunks (user_id);
create index idx_document_chunks_content_tsv on public.document_chunks using gin (content_tsv);

-- HNSW for dense ANN search (cosine distance)
create index idx_document_chunks_embedding_hnsw
  on public.document_chunks
  using hnsw (embedding vector_cosine_ops)
  with (m = 16, ef_construction = 64);
