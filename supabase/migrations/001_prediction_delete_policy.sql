-- Allow authenticated users to delete predictions.
grant delete on table public.predictions to authenticated;

-- Restrict deletion to predictions owned by the signed-in user.
create policy "Users can delete their own predictions"
on public.predictions
for delete
to authenticated
using (
    (select auth.uid()) = user_id
);