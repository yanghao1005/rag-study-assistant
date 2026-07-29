-- ============================================================================
-- 0005_rls_and_storage.sql
-- Row Level Security + Storage bucket for PDF uploads
-- Best practices:
--   - RLS on every public table (security-rls-basics)
--   - (select auth.uid()) wrapper for policy performance (security-rls-performance)
--   - Policies scoped TO authenticated (least privilege)
-- ============================================================================

alter table public.profiles enable row level security;
alter table public.subjects enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.study_artifacts enable row level security;
alter table public.flashcards enable row level security;
alter table public.quiz_questions enable row level security;
alter table public.chat_threads enable row level security;
alter table public.chat_messages enable row level security;
alter table public.jobs enable row level security;
alter table public.pipeline_stage_runs enable row level security;

-- Force RLS even for table owners (defense in depth)
alter table public.profiles force row level security;
alter table public.subjects force row level security;
alter table public.documents force row level security;
alter table public.document_chunks force row level security;
alter table public.study_artifacts force row level security;
alter table public.flashcards force row level security;
alter table public.quiz_questions force row level security;
alter table public.chat_threads force row level security;
alter table public.chat_messages force row level security;
alter table public.jobs force row level security;
alter table public.pipeline_stage_runs force row level security;

-- ---------------------------------------------------------------------------
-- profiles
-- ---------------------------------------------------------------------------
create policy profiles_select_own on public.profiles
  for select to authenticated
  using ((select auth.uid()) = id);

create policy profiles_update_own on public.profiles
  for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- ---------------------------------------------------------------------------
-- subjects
-- ---------------------------------------------------------------------------
create policy subjects_select_own on public.subjects
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy subjects_insert_own on public.subjects
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy subjects_update_own on public.subjects
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy subjects_delete_own on public.subjects
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- documents
-- ---------------------------------------------------------------------------
create policy documents_select_own on public.documents
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy documents_insert_own on public.documents
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy documents_update_own on public.documents
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy documents_delete_own on public.documents
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- document_chunks
-- ---------------------------------------------------------------------------
create policy chunks_select_own on public.document_chunks
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy chunks_insert_own on public.document_chunks
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy chunks_update_own on public.document_chunks
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy chunks_delete_own on public.document_chunks
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- study_artifacts
-- ---------------------------------------------------------------------------
create policy artifacts_select_own on public.study_artifacts
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy artifacts_insert_own on public.study_artifacts
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy artifacts_update_own on public.study_artifacts
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy artifacts_delete_own on public.study_artifacts
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- flashcards
-- ---------------------------------------------------------------------------
create policy flashcards_select_own on public.flashcards
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy flashcards_insert_own on public.flashcards
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy flashcards_update_own on public.flashcards
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy flashcards_delete_own on public.flashcards
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- quiz_questions
-- ---------------------------------------------------------------------------
create policy quiz_select_own on public.quiz_questions
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy quiz_insert_own on public.quiz_questions
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy quiz_update_own on public.quiz_questions
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy quiz_delete_own on public.quiz_questions
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- chat_threads / chat_messages
-- ---------------------------------------------------------------------------
create policy threads_select_own on public.chat_threads
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy threads_insert_own on public.chat_threads
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy threads_update_own on public.chat_threads
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy threads_delete_own on public.chat_threads
  for delete to authenticated
  using ((select auth.uid()) = user_id);

create policy messages_select_own on public.chat_messages
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy messages_insert_own on public.chat_messages
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy messages_delete_own on public.chat_messages
  for delete to authenticated
  using ((select auth.uid()) = user_id);

-- ---------------------------------------------------------------------------
-- jobs / pipeline_stage_runs
-- ---------------------------------------------------------------------------
create policy jobs_select_own on public.jobs
  for select to authenticated
  using ((select auth.uid()) = user_id);

create policy jobs_insert_own on public.jobs
  for insert to authenticated
  with check ((select auth.uid()) = user_id);

create policy jobs_update_own on public.jobs
  for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

create policy jobs_delete_own on public.jobs
  for delete to authenticated
  using ((select auth.uid()) = user_id);

create policy stage_runs_select_own on public.pipeline_stage_runs
  for select to authenticated
  using (
    exists (
      select 1 from public.jobs j
      where j.id = pipeline_stage_runs.job_id
        and j.user_id = (select auth.uid())
    )
  );

create policy stage_runs_insert_own on public.pipeline_stage_runs
  for insert to authenticated
  with check (
    exists (
      select 1 from public.jobs j
      where j.id = pipeline_stage_runs.job_id
        and j.user_id = (select auth.uid())
    )
  );

-- ---------------------------------------------------------------------------
-- Grants (least privilege for authenticated; service_role for workers)
-- ---------------------------------------------------------------------------
grant usage on schema public to authenticated, service_role;

grant select, update on public.profiles to authenticated;
grant select, insert, update, delete on public.subjects to authenticated;
grant select, insert, update, delete on public.documents to authenticated;
grant select, insert, update, delete on public.document_chunks to authenticated;
grant select, insert, update, delete on public.study_artifacts to authenticated;
grant select, insert, update, delete on public.flashcards to authenticated;
grant select, insert, update, delete on public.quiz_questions to authenticated;
grant select, insert, update, delete on public.chat_threads to authenticated;
grant select, insert, delete on public.chat_messages to authenticated;
grant select, insert, update, delete on public.jobs to authenticated;
grant select, insert on public.pipeline_stage_runs to authenticated;

grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant execute on all functions in schema public to service_role;

-- ---------------------------------------------------------------------------
-- Storage: private bucket for user documents
-- Path convention: {user_id}/{subject_id}/{document_id}/{filename}
-- Upsert needs INSERT + SELECT + UPDATE
-- ---------------------------------------------------------------------------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'documents',
  'documents',
  false,
  26214400,
  array['application/pdf', 'text/plain']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

create policy documents_storage_select on storage.objects
  for select to authenticated
  using (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy documents_storage_insert on storage.objects
  for insert to authenticated
  with check (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy documents_storage_update on storage.objects
  for update to authenticated
  using (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  )
  with check (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

create policy documents_storage_delete on storage.objects
  for delete to authenticated
  using (
    bucket_id = 'documents'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );
