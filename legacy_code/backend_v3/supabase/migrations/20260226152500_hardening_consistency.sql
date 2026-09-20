-- Hardening migration: enforce cross-table user consistency and safer retrieval filters.

-- Composite uniqueness for ownership-safe FKs
alter table public.subjects
  add constraint subjects_id_user_unique unique (id, user_id);

alter table public.documents
  add constraint documents_id_user_unique unique (id, user_id);

alter table public.chapters
  add constraint chapters_id_user_unique unique (id, user_id);

-- Ensure hierarchy always belongs to same user
alter table public.documents
  add constraint documents_subject_user_fk
  foreign key (subject_id, user_id)
  references public.subjects (id, user_id)
  on delete cascade;

alter table public.chapters
  add constraint chapters_document_user_fk
  foreign key (document_id, user_id)
  references public.documents (id, user_id)
  on delete cascade;

alter table public.document_chunks
  add constraint chunks_document_user_fk
  foreign key (document_id, user_id)
  references public.documents (id, user_id)
  on delete cascade;

alter table public.document_chunks
  add constraint chunks_chapter_user_fk
  foreign key (chapter_id, user_id)
  references public.chapters (id, user_id)
  on delete set null;

alter table public.generated_content
  add constraint generated_subject_user_fk
  foreign key (subject_id, user_id)
  references public.subjects (id, user_id)
  on delete cascade;

alter table public.generated_content
  add constraint generated_document_user_fk
  foreign key (document_id, user_id)
  references public.documents (id, user_id)
  on delete cascade;

alter table public.generated_content
  add constraint generated_chapter_user_fk
  foreign key (chapter_id, user_id)
  references public.chapters (id, user_id)
  on delete cascade;

-- Data quality checks
alter table public.subjects
  add constraint subjects_color_hex_check
  check (color is null or color ~ '^#[A-Fa-f0-9]{6}$');

alter table public.documents
  add constraint documents_pdf_size_check
  check (file_size is null or file_size >= 0);

alter table public.documents
  add constraint documents_pages_check
  check (total_pages is null or total_pages >= 0);

-- Safer vector match function (avoid UUID cast errors when metadata key is absent)
create or replace function public.match_document_chunks(
  query_embedding vector(1536),
  match_threshold float default 0.7,
  match_count int default 5,
  filter_user_id uuid default auth.uid(),
  filter_subject_id uuid default null,
  filter_document_id uuid default null,
  filter_chapter_id uuid default null
)
returns table (
  id uuid,
  user_id uuid,
  document_id uuid,
  chapter_id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language sql
stable
security definer
set search_path = public
as $$
  select
    dc.id,
    dc.user_id,
    dc.document_id,
    dc.chapter_id,
    dc.content,
    dc.metadata,
    1 - (dc.embedding <=> query_embedding) as similarity
  from public.document_chunks dc
  where (filter_user_id is null or dc.user_id = filter_user_id)
    and (
      filter_subject_id is null
      or nullif(dc.metadata ->> 'subject_id', '')::uuid = filter_subject_id
    )
    and (filter_document_id is null or dc.document_id = filter_document_id)
    and (filter_chapter_id is null or dc.chapter_id = filter_chapter_id)
    and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
$$;
