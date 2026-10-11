create policy "Users can upload their own prediction images"
on storage.objects
for insert
to authenticated
with check (
    bucket_id = 'prediction-images'
    and (storage.foldername(name))[1] = (select auth.uid()::text)
);

create policy "Users can view their own prediction images"
on storage.objects
for select
to authenticated
using (
    bucket_id = 'prediction-images'
    and (storage.foldername(name))[1] = (select auth.uid()::text)
);

create policy "Users can delete their own prediction images"
on storage.objects
for delete
to authenticated
using (
    bucket_id = 'prediction-images'
    and (storage.foldername(name))[1] = (select auth.uid()::text)
);