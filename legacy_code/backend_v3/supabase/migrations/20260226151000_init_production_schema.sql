-- backend_v3 production-ready schema for Supabase
-- Includes: user ownership, RLS, subscription plans, usage limits, admin bypass,
-- and pgvector retrieval aligned with text-embedding-3-small (1536 dims).

create extension if not exists pgcrypto;
create extension if not exists vector;

-- =========================================================
-- Enums
-- =========================================================

create type public.app_role as enum ('student', 'admin');
create type public.plan_tier as enum ('free', 'pro', 'enterprise');
create type public.document_type as enum ('pdf', 'summary');
create type public.document_status as enum ('processing', 'ready', 'error');
create type public.generated_type as enum ('flashcard', 'quiz');
create type public.generation_scope as enum ('subject', 'document', 'chapter', 'summary');
create type public.usage_metric as enum (
  'upload_requests',
  'flashcard_requests',
  'quiz_requests',
  'embedding_tokens',
  'generation_tokens'
);

-- =========================================================
-- Utility trigger/function
-- =========================================================

create or replace function public.update_updated_at_column()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- =========================================================
-- Identity / Billing / Plans
-- =========================================================

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text,
  role public.app_role not null default 'student',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.billing_customers (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references public.profiles(id) on delete cascade,
  provider text not null default 'stripe',
  provider_customer_id text not null unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.subscription_plans (
  id uuid primary key default gen_random_uuid(),
  tier public.plan_tier not null unique,
  name text not null,
  monthly_price_cents integer not null default 0,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.plan_limits (
  id uuid primary key default gen_random_uuid(),
  plan_id uuid not null references public.subscription_plans(id) on delete cascade,
  metric public.usage_metric not null,
  monthly_limit bigint,
  created_at timestamptz not null default now(),
  unique(plan_id, metric)
);

create table public.user_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  plan_id uuid not null references public.subscription_plans(id),
  status text not null default 'active',
  provider_subscription_id text unique,
  current_period_start timestamptz not null,
  current_period_end timestamptz not null,
  cancel_at_period_end boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (current_period_end > current_period_start)
);

create index idx_user_subscriptions_user_id on public.user_subscriptions(user_id);
create index idx_user_subscriptions_status on public.user_subscriptions(status);

create table public.usage_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  metric public.usage_metric not null,
  amount bigint not null default 1,
  period_start date not null,
  source text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  check (amount > 0)
);

create index idx_usage_events_user_metric_period on public.usage_events(user_id, metric, period_start);

-- =========================================================
-- Core app tables (all user-owned)
-- =========================================================

create table public.subjects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  name text not null,
  description text,
  color text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, name)
);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  subject_id uuid not null references public.subjects(id) on delete cascade,
  document_type public.document_type not null default 'pdf',
  filename text not null,
  file_size bigint,
  total_pages int,
  content_text text,
  status public.document_status not null default 'processing',
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_documents_user_id on public.documents(user_id);
create index idx_documents_subject_id on public.documents(subject_id);
create index idx_documents_type on public.documents(document_type);
create index idx_documents_status on public.documents(status);

create table public.chapters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  document_id uuid not null references public.documents(id) on delete cascade,
  name text not null,
  start_page int,
  end_page int,
  order_index int,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (start_page is null or end_page is null or end_page >= start_page)
);

create index idx_chapters_user_id on public.chapters(user_id);
create index idx_chapters_document_id on public.chapters(document_id);

create table public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  document_id uuid not null references public.documents(id) on delete cascade,
  chapter_id uuid references public.chapters(id) on delete set null,
  content text not null,
  embedding vector(1536) not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index idx_document_chunks_user_id on public.document_chunks(user_id);
create index idx_document_chunks_document_id on public.document_chunks(document_id);
create index idx_document_chunks_chapter_id on public.document_chunks(chapter_id);
create index idx_document_chunks_metadata on public.document_chunks using gin(metadata);
create index idx_document_chunks_embedding on public.document_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create table public.generated_content (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  subject_id uuid references public.subjects(id) on delete cascade,
  document_id uuid references public.documents(id) on delete cascade,
  chapter_id uuid references public.chapters(id) on delete cascade,
  scope public.generation_scope not null,
  type public.generated_type not null,
  content_json jsonb not null,
  created_at timestamptz not null default now(),
  check ((subject_id is not null) or (document_id is not null) or (chapter_id is not null))
);

create index idx_generated_content_user_id on public.generated_content(user_id);
create index idx_generated_content_subject_id on public.generated_content(subject_id);
create index idx_generated_content_document_id on public.generated_content(document_id);
create index idx_generated_content_chapter_id on public.generated_content(chapter_id);

-- =========================================================
-- Triggers
-- =========================================================

create trigger trg_profiles_updated_at
before update on public.profiles
for each row execute function public.update_updated_at_column();

create trigger trg_billing_customers_updated_at
before update on public.billing_customers
for each row execute function public.update_updated_at_column();

create trigger trg_subscription_plans_updated_at
before update on public.subscription_plans
for each row execute function public.update_updated_at_column();

create trigger trg_user_subscriptions_updated_at
before update on public.user_subscriptions
for each row execute function public.update_updated_at_column();

create trigger trg_subjects_updated_at
before update on public.subjects
for each row execute function public.update_updated_at_column();

create trigger trg_documents_updated_at
before update on public.documents
for each row execute function public.update_updated_at_column();

create trigger trg_chapters_updated_at
before update on public.chapters
for each row execute function public.update_updated_at_column();

-- Auto-create profile when auth user is created
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, coalesce(new.raw_user_meta_data ->> 'full_name', ''))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

-- =========================================================
-- Role, plan, and quota helper functions
-- =========================================================

create or replace function public.is_admin(p_user_id uuid default auth.uid())
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.profiles p
    where p.id = p_user_id
      and p.role = 'admin'
      and p.is_active = true
  );
$$;

create or replace function public.current_period_start()
returns date
language sql
stable
as $$
  select date_trunc('month', now())::date;
$$;

create or replace function public.get_effective_plan(p_user_id uuid)
returns public.plan_tier
language sql
stable
security definer
set search_path = public
as $$
  with active_sub as (
    select sp.tier
    from public.user_subscriptions us
    join public.subscription_plans sp on sp.id = us.plan_id
    where us.user_id = p_user_id
      and us.status = 'active'
      and now() >= us.current_period_start
      and now() < us.current_period_end
    order by us.current_period_end desc
    limit 1
  )
  select coalesce((select tier from active_sub), 'free'::public.plan_tier);
$$;

create or replace function public.get_monthly_limit(p_user_id uuid, p_metric public.usage_metric)
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  with plan_row as (
    select public.get_effective_plan(p_user_id) as tier
  )
  select pl.monthly_limit
  from plan_row pr
  join public.subscription_plans sp on sp.tier = pr.tier
  join public.plan_limits pl on pl.plan_id = sp.id and pl.metric = p_metric
  limit 1;
$$;

create or replace function public.get_usage_amount(
  p_user_id uuid,
  p_metric public.usage_metric,
  p_period_start date default public.current_period_start()
)
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(sum(ue.amount), 0)::bigint
  from public.usage_events ue
  where ue.user_id = p_user_id
    and ue.metric = p_metric
    and ue.period_start = p_period_start;
$$;

create or replace function public.check_and_consume_quota(
  p_metric public.usage_metric,
  p_amount bigint default 1,
  p_source text default 'api',
  p_metadata jsonb default '{}'::jsonb
)
returns table (
  allowed boolean,
  remaining bigint,
  quota_limit bigint,
  used bigint,
  reason text
)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_user_id uuid := auth.uid();
  v_period date := public.current_period_start();
  v_limit bigint;
  v_used bigint;
begin
  if v_user_id is null then
    return query select false, 0::bigint, 0::bigint, 0::bigint, 'unauthenticated'::text;
    return;
  end if;

  if public.is_admin(v_user_id) then
    insert into public.usage_events(user_id, metric, amount, period_start, source, metadata)
    values (v_user_id, p_metric, p_amount, v_period, p_source, p_metadata || jsonb_build_object('admin_bypass', true));

    return query select true, 9223372036854775807::bigint, null::bigint, 0::bigint, 'admin_bypass'::text;
    return;
  end if;

  v_limit := public.get_monthly_limit(v_user_id, p_metric);
  v_used := public.get_usage_amount(v_user_id, p_metric, v_period);

  if v_limit is not null and (v_used + p_amount) > v_limit then
    return query select false, greatest(v_limit - v_used, 0), v_limit, v_used, 'quota_exceeded'::text;
    return;
  end if;

  insert into public.usage_events(user_id, metric, amount, period_start, source, metadata)
  values (v_user_id, p_metric, p_amount, v_period, p_source, p_metadata);

  v_used := v_used + p_amount;

  if v_limit is null then
    return query select true, 9223372036854775807::bigint, null::bigint, v_used, 'ok_unlimited'::text;
  else
    return query select true, greatest(v_limit - v_used, 0), v_limit, v_used, 'ok'::text;
  end if;
end;
$$;

-- =========================================================
-- Vector search function with ownership filters
-- =========================================================

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
    and (filter_subject_id is null or (dc.metadata ->> 'subject_id')::uuid = filter_subject_id)
    and (filter_document_id is null or dc.document_id = filter_document_id)
    and (filter_chapter_id is null or dc.chapter_id = filter_chapter_id)
    and (1 - (dc.embedding <=> query_embedding)) >= match_threshold
  order by dc.embedding <=> query_embedding
  limit match_count;
$$;

-- =========================================================
-- RLS
-- =========================================================

alter table public.profiles enable row level security;
alter table public.billing_customers enable row level security;
alter table public.subscription_plans enable row level security;
alter table public.plan_limits enable row level security;
alter table public.user_subscriptions enable row level security;
alter table public.usage_events enable row level security;
alter table public.subjects enable row level security;
alter table public.documents enable row level security;
alter table public.chapters enable row level security;
alter table public.document_chunks enable row level security;
alter table public.generated_content enable row level security;

-- profiles
create policy profiles_select_own_or_admin on public.profiles
for select using (auth.uid() = id or public.is_admin(auth.uid()));

create policy profiles_update_own_or_admin on public.profiles
for update using (auth.uid() = id or public.is_admin(auth.uid()))
with check (auth.uid() = id or public.is_admin(auth.uid()));

-- billing
create policy billing_select_own_or_admin on public.billing_customers
for select using (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy billing_write_own_or_admin on public.billing_customers
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

-- plans and limits are readable by authenticated users, writable by admin only
create policy plans_select_authenticated on public.subscription_plans
for select using (auth.role() = 'authenticated');

create policy plans_write_admin on public.subscription_plans
for all using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

create policy plan_limits_select_authenticated on public.plan_limits
for select using (auth.role() = 'authenticated');

create policy plan_limits_write_admin on public.plan_limits
for all using (public.is_admin(auth.uid()))
with check (public.is_admin(auth.uid()));

-- subscriptions + usage
create policy user_subscriptions_own_or_admin on public.user_subscriptions
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy usage_events_own_or_admin on public.usage_events
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

-- core content tables
create policy subjects_own_or_admin on public.subjects
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy documents_own_or_admin on public.documents
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy chapters_own_or_admin on public.chapters
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy document_chunks_own_or_admin on public.document_chunks
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

create policy generated_content_own_or_admin on public.generated_content
for all using (auth.uid() = user_id or public.is_admin(auth.uid()))
with check (auth.uid() = user_id or public.is_admin(auth.uid()));

-- =========================================================
-- Seed plans and limits
-- =========================================================

insert into public.subscription_plans (tier, name, monthly_price_cents)
values
  ('free', 'Free', 0),
  ('pro', 'Pro', 1999),
  ('enterprise', 'Enterprise', 9999)
on conflict (tier) do update
set name = excluded.name,
    monthly_price_cents = excluded.monthly_price_cents,
    active = true,
    updated_at = now();

with plans as (
  select tier, id from public.subscription_plans
)
insert into public.plan_limits(plan_id, metric, monthly_limit)
select p.id, x.metric::public.usage_metric, x.monthly_limit
from plans p
join (
  values
    ('free', 'upload_requests', 50),
    ('free', 'flashcard_requests', 300),
    ('free', 'quiz_requests', 150),
    ('free', 'embedding_tokens', 1000000),
    ('free', 'generation_tokens', 300000),

    ('pro', 'upload_requests', 500),
    ('pro', 'flashcard_requests', 5000),
    ('pro', 'quiz_requests', 3000),
    ('pro', 'embedding_tokens', 20000000),
    ('pro', 'generation_tokens', 10000000),

    ('enterprise', 'upload_requests', null),
    ('enterprise', 'flashcard_requests', null),
    ('enterprise', 'quiz_requests', null),
    ('enterprise', 'embedding_tokens', null),
    ('enterprise', 'generation_tokens', null)
) as x(tier, metric, monthly_limit)
  on x.tier::public.plan_tier = p.tier
on conflict (plan_id, metric) do update
set monthly_limit = excluded.monthly_limit;

