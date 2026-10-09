-- Letify cloud progress. Run this once in the Supabase SQL editor (Dashboard -> SQL Editor -> New query).
--
-- One row per signed-in learner holds their whole progress as JSON. Row-level security makes sure a learner can
-- only ever read or change their own row, so the public "anon" key in the website is safe to publish.

create table if not exists public.user_data (
  user_id    uuid primary key references auth.users (id) on delete cascade,
  data       jsonb       not null default '{}'::jsonb,
  rev        integer     not null default 0,        -- bumped on every save; lets two devices detect a clash
  updated_at timestamptz not null default now(),
  constraint user_data_is_object check (jsonb_typeof(data) = 'object'),
  constraint user_data_size      check (pg_column_size(data) < 2000000)
);

alter table public.user_data enable row level security;

drop policy if exists "read own progress"   on public.user_data;
drop policy if exists "create own progress" on public.user_data;
drop policy if exists "update own progress" on public.user_data;
drop policy if exists "delete own progress" on public.user_data;

create policy "read own progress"   on public.user_data for select to authenticated using (auth.uid() = user_id);
create policy "create own progress" on public.user_data for insert to authenticated with check (auth.uid() = user_id);
create policy "update own progress" on public.user_data for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "delete own progress" on public.user_data for delete to authenticated using (auth.uid() = user_id);

-- Nobody who is signed out can touch the table at all.
revoke all on public.user_data from anon;
grant select, insert, update, delete on public.user_data to authenticated;
