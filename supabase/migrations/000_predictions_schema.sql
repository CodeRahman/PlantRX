-- Baseline setup for a NEW Supabase project.
-- Existing configured projects do not need to rerun this file.

create table public.predictions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    image text not null,
    label text not null,
    confidence double precision not null
        check (confidence >= 0 and confidence <= 1),
    created_at timestamptz not null default now()
);

create index predictions_user_created_at_idx
on public.predictions (user_id, created_at desc);

alter table public.predictions enable row level security;

revoke all on table public.predictions from anon;
grant usage on schema public to authenticated;
grant select, insert on table public.predictions to authenticated;

create policy "Users can view their own predictions"
on public.predictions
for select
to authenticated
using ((select auth.uid()) = user_id);

create policy "Users can create their own predictions"
on public.predictions
for insert
to authenticated
with check ((select auth.uid()) = user_id);
