-- Isra.Peptides — Research Journal backend (Supabase)
-- Run this once in Supabase: SQL Editor -> New query -> paste -> Run.
-- It creates a private, code-addressed store. A journal is only reachable
-- with its exact code; the table itself is not directly readable by the public key.

create table if not exists public.journals (
  code       text primary key,
  data       jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.journals enable row level security;
-- No RLS policies are created on purpose: the public key cannot read/write the
-- table directly. All access goes through the two functions below.

create or replace function public.journal_load(p_code text)
returns jsonb
language sql
security definer
set search_path = public
as $$
  select data from public.journals where code = p_code;
$$;

create or replace function public.journal_save(p_code text, p_data jsonb)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_code !~ '^IPJ-[A-Z0-9-]{8,48}$' then
    raise exception 'invalid code';
  end if;
  if length(p_data::text) > 200000 then
    raise exception 'payload too large';
  end if;
  insert into public.journals(code, data, updated_at)
    values (p_code, p_data, now())
  on conflict (code) do update set data = excluded.data, updated_at = now();
end;
$$;

revoke all on function public.journal_load(text)        from public;
revoke all on function public.journal_save(text, jsonb) from public;
grant execute on function public.journal_load(text)        to anon, authenticated;
grant execute on function public.journal_save(text, jsonb) to anon, authenticated;

-- After running this, open index.html and set:
--   var SUPA_URL = 'https://YOUR-REF.supabase.co';
-- (Project Settings -> API -> Project URL). The publishable key is already set.
