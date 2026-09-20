-- ============================================================================
-- 0003_study_and_jobs.sql
-- Generated study content (normalized), chat, async jobs pipeline
-- ============================================================================

-- ---------------------------------------------------------------------------
-- study_artifacts: container for a generation run (deck / quiz / summary)
-- ---------------------------------------------------------------------------
create table public.study_artifacts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid not null references public.subjects (id) on delete cascade,
  document_id uuid references public.documents (id) on delete set null,
  artifact_type text not null
    check (artifact_type in ('flashcard_deck', 'quiz', 'summary')),
  title text not null,
  status text not null default 'ready'
    check (status in ('generating', 'ready', 'error')),
  source_scope text not null default 'subject'
    check (source_scope in ('subject', 'document', 'chapter')),
  source_ref text,
  content_json jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_study_artifacts_user_subject
  on public.study_artifacts (user_id, subject_id);
create index idx_study_artifacts_type
  on public.study_artifacts (artifact_type);
create index idx_study_artifacts_document_id
  on public.study_artifacts (document_id)
  where document_id is not null;

create trigger study_artifacts_set_updated_at
before update on public.study_artifacts
for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- flashcards
-- ---------------------------------------------------------------------------
create table public.flashcards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  artifact_id uuid not null references public.study_artifacts (id) on delete cascade,
  front text not null,
  back text not null,
  hint text,
  difficulty text check (difficulty in ('easy', 'medium', 'hard')),
  tags text[] not null default '{}',
  source_chunk_ids uuid[] not null default '{}',
  position integer not null default 0,
  created_at timestamptz not null default now()
);

create index idx_flashcards_artifact_id on public.flashcards (artifact_id);
create index idx_flashcards_user_id on public.flashcards (user_id);

-- ---------------------------------------------------------------------------
-- quiz_questions
-- ---------------------------------------------------------------------------
create table public.quiz_questions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  artifact_id uuid not null references public.study_artifacts (id) on delete cascade,
  question text not null,
  options jsonb not null default '[]'::jsonb,
  correct_option_index integer,
  correct_answer text,
  explanation text,
  question_type text not null default 'multiple_choice'
    check (question_type in ('multiple_choice', 'true_false', 'short_answer')),
  difficulty text check (difficulty in ('easy', 'medium', 'hard')),
  source_chunk_ids uuid[] not null default '{}',
  position integer not null default 0,
  created_at timestamptz not null default now(),
  constraint quiz_questions_has_answer check (
    correct_option_index is not null or correct_answer is not null
  )
);

create index idx_quiz_questions_artifact_id on public.quiz_questions (artifact_id);
create index idx_quiz_questions_user_id on public.quiz_questions (user_id);

-- ---------------------------------------------------------------------------
-- chat_threads / chat_messages (RAG Q&A with citations)
-- ---------------------------------------------------------------------------
create table public.chat_threads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid not null references public.subjects (id) on delete cascade,
  title text not null default 'New chat',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_chat_threads_user_subject
  on public.chat_threads (user_id, subject_id);

create trigger chat_threads_set_updated_at
before update on public.chat_threads
for each row execute function public.set_updated_at();

create table public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  thread_id uuid not null references public.chat_threads (id) on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  citations jsonb not null default '[]'::jsonb,
  model text,
  token_usage jsonb,
  created_at timestamptz not null default now()
);

create index idx_chat_messages_thread_id on public.chat_messages (thread_id);
create index idx_chat_messages_user_id on public.chat_messages (user_id);

-- ---------------------------------------------------------------------------
-- jobs + pipeline_stage_runs (async ingestion / generation)
-- ---------------------------------------------------------------------------
create table public.jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  subject_id uuid references public.subjects (id) on delete set null,
  document_id uuid references public.documents (id) on delete set null,
  job_type text not null
    check (job_type in (
      'ingest_document',
      'generate_flashcards',
      'generate_quiz',
      'generate_summary',
      'reindex_document'
    )),
  status text not null default 'queued'
    check (status in ('queued', 'running', 'completed', 'failed', 'cancelled')),
  progress numeric(5, 2) not null default 0
    check (progress >= 0 and progress <= 100),
  payload jsonb not null default '{}'::jsonb,
  result jsonb,
  error_message text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_jobs_user_status on public.jobs (user_id, status);
-- Composite partial index for worker queue (query-composite + query-partial)
create index idx_jobs_queued_created on public.jobs (status, created_at)
  where status = 'queued';
create index idx_jobs_subject_id on public.jobs (subject_id)
  where subject_id is not null;
create index idx_jobs_document_id on public.jobs (document_id)
  where document_id is not null;

create trigger jobs_set_updated_at
before update on public.jobs
for each row execute function public.set_updated_at();

create table public.pipeline_stage_runs (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references public.jobs (id) on delete cascade,
  stage text not null
    check (stage in (
      'download',
      'parse',
      'chunk',
      'embed',
      'store',
      'retrieve',
      'generate',
      'validate'
    )),
  status text not null check (status in ('ok', 'error', 'skipped')),
  duration_ms integer not null default 0 check (duration_ms >= 0),
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_pipeline_stage_runs_job_id on public.pipeline_stage_runs (job_id);

-- Atomic job claim for async workers (lock-skip-locked)
-- security definer stays in private schema
create or replace function private.claim_next_job(
  p_job_types text[] default null
)
returns public.jobs
language plpgsql
security definer
set search_path = public
as $$
declare
  claimed public.jobs;
begin
  update public.jobs j
  set
    status = 'running',
    started_at = now(),
    updated_at = now()
  where j.id = (
    select id
    from public.jobs
    where status = 'queued'
      and (p_job_types is null or job_type = any (p_job_types))
    order by created_at
    limit 1
    for update skip locked
  )
  returning * into claimed;

  return claimed;
end;
$$;

revoke all on function private.claim_next_job(text[]) from public, anon, authenticated;
grant execute on function private.claim_next_job(text[]) to service_role;
