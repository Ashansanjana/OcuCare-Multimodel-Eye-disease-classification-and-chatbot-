-- OcuCare Supabase schema
-- Run this in the Supabase SQL Editor after creating a project.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'New eye-health chat',
  mode text not null default 'text-only',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null default '',
  image_name text,
  image_present boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.patient_summaries (
  user_id uuid primary key references auth.users(id) on delete cascade,
  summary_text text not null default '',
  symptoms jsonb not null default '[]'::jsonb,
  topics jsonb not null default '[]'::jsonb,
  red_flags jsonb not null default '[]'::jsonb,
  image_history jsonb not null default '[]'::jsonb,
  recommended_next_steps jsonb not null default '[]'::jsonb,
  safety_note text not null default 'This is not a diagnosis. It summarizes user-reported information and AI screening-support outputs.',
  last_generated_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists chat_sessions_user_updated_idx
  on public.chat_sessions(user_id, updated_at desc);

create index if not exists chat_messages_session_created_idx
  on public.chat_messages(session_id, created_at asc);

create index if not exists patient_summaries_generated_idx
  on public.patient_summaries(last_generated_at desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists chat_sessions_set_updated_at on public.chat_sessions;
create trigger chat_sessions_set_updated_at
before update on public.chat_sessions
for each row execute function public.set_updated_at();

drop trigger if exists patient_summaries_set_updated_at on public.patient_summaries;
create trigger patient_summaries_set_updated_at
before update on public.patient_summaries
for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1))
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

alter table public.profiles enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.patient_summaries enable row level security;

drop policy if exists "Users can read own profile" on public.profiles;
create policy "Users can read own profile"
on public.profiles for select
using (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.profiles;
create policy "Users can update own profile"
on public.profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

drop policy if exists "Users can read own chat sessions" on public.chat_sessions;
create policy "Users can read own chat sessions"
on public.chat_sessions for select
using (auth.uid() = user_id);

drop policy if exists "Users can insert own chat sessions" on public.chat_sessions;
create policy "Users can insert own chat sessions"
on public.chat_sessions for insert
with check (auth.uid() = user_id);

drop policy if exists "Users can update own chat sessions" on public.chat_sessions;
create policy "Users can update own chat sessions"
on public.chat_sessions for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users can delete own chat sessions" on public.chat_sessions;
create policy "Users can delete own chat sessions"
on public.chat_sessions for delete
using (auth.uid() = user_id);

drop policy if exists "Users can read own chat messages" on public.chat_messages;
create policy "Users can read own chat messages"
on public.chat_messages for select
using (auth.uid() = user_id);

drop policy if exists "Users can insert own chat messages" on public.chat_messages;
create policy "Users can insert own chat messages"
on public.chat_messages for insert
with check (
  auth.uid() = user_id
  and exists (
    select 1
    from public.chat_sessions s
    where s.id = session_id
      and s.user_id = auth.uid()
  )
);

drop policy if exists "Users can delete own chat messages" on public.chat_messages;
create policy "Users can delete own chat messages"
on public.chat_messages for delete
using (auth.uid() = user_id);

drop policy if exists "Users can read own patient summary" on public.patient_summaries;
create policy "Users can read own patient summary"
on public.patient_summaries for select
using (auth.uid() = user_id);

drop policy if exists "Users can insert own patient summary" on public.patient_summaries;
create policy "Users can insert own patient summary"
on public.patient_summaries for insert
with check (auth.uid() = user_id);

drop policy if exists "Users can update own patient summary" on public.patient_summaries;
create policy "Users can update own patient summary"
on public.patient_summaries for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users can delete own patient summary" on public.patient_summaries;
create policy "Users can delete own patient summary"
on public.patient_summaries for delete
using (auth.uid() = user_id);
