-- ============================================================================
-- 0008_synopsis_and_reviews.sql
-- Hierarchical RAG (document synopsis) + spaced-repetition reviews
-- ============================================================================

alter table public.documents
  add column if not exists synopsis text;

comment on column public.documents.synopsis is
  'Short LLM-generated index of the document used as hierarchical retrieval layer.';

-- ---------------------------------------------------------------------------
-- flashcard_reviews (SM-2 lite)
-- ---------------------------------------------------------------------------
create table if not exists public.flashcard_reviews (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  flashcard_id uuid not null references public.flashcards (id) on delete cascade,
  ease numeric not null default 2.5 check (ease >= 1.3),
  interval_days integer not null default 0 check (interval_days >= 0),
  repetitions integer not null default 0 check (repetitions >= 0),
  next_review_at timestamptz not null default now(),
  last_reviewed_at timestamptz,
  last_quality integer check (last_quality is null or (last_quality >= 0 and last_quality <= 5)),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_flashcard_reviews_user_card unique (user_id, flashcard_id)
);

create index if not exists idx_flashcard_reviews_due
  on public.flashcard_reviews (user_id, next_review_at);

create trigger flashcard_reviews_set_updated_at
before update on public.flashcard_reviews
for each row execute function public.set_updated_at();

alter table public.flashcard_reviews enable row level security;
alter table public.flashcard_reviews force row level security;

create policy flashcard_reviews_select_own on public.flashcard_reviews
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy flashcard_reviews_insert_own on public.flashcard_reviews
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy flashcard_reviews_update_own on public.flashcard_reviews
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy flashcard_reviews_delete_own on public.flashcard_reviews
  for delete to authenticated
  using ((select auth.uid()) = user_id);

grant select, insert, update, delete on public.flashcard_reviews to authenticated;
grant all on public.flashcard_reviews to service_role;

-- Allow hierarchical synopsis as a recorded pipeline stage
alter table public.pipeline_stage_runs
  drop constraint if exists pipeline_stage_runs_stage_check;

alter table public.pipeline_stage_runs
  add constraint pipeline_stage_runs_stage_check
  check (
    stage = any (
      array[
        'download'::text,
        'parse'::text,
        'chunk'::text,
        'embed'::text,
        'store'::text,
        'synopsis'::text,
        'retrieve'::text,
        'generate'::text,
        'validate'::text
      ]
    )
  );
