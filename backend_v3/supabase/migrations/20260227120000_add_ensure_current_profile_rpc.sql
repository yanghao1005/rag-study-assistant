-- Ensure authenticated users can self-heal missing profile rows under RLS
create or replace function public.ensure_current_profile()
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  v_user_id uuid := auth.uid();
  v_email text := (auth.jwt() ->> 'email');
  v_full_name text := coalesce(auth.jwt() -> 'user_metadata' ->> 'full_name', '');
begin
  if v_user_id is null then
    return false;
  end if;

  insert into public.profiles (id, email, full_name)
  values (v_user_id, v_email, v_full_name)
  on conflict (id)
  do update set
    email = coalesce(excluded.email, public.profiles.email),
    full_name = case
      when coalesce(public.profiles.full_name, '') = '' then excluded.full_name
      else public.profiles.full_name
    end,
    updated_at = now();

  return true;
end;
$$;

grant execute on function public.ensure_current_profile() to authenticated;
