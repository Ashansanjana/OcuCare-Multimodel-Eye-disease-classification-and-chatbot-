-- Run this migration if you already executed the original OcuCare schema.

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

create index if not exists patient_summaries_generated_idx
  on public.patient_summaries(last_generated_at desc);

drop trigger if exists patient_summaries_set_updated_at on public.patient_summaries;
create trigger patient_summaries_set_updated_at
before update on public.patient_summaries
for each row execute function public.set_updated_at();

alter table public.patient_summaries enable row level security;

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
