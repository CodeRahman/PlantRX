# Supabase setup

These instructions provision a new Supabase project for PlantRX. The SQL files are intended to be run manually in the Dashboard SQL Editor, in numerical order; they are not a configured Supabase CLI migration workflow.

If you already configured the current PlantRX project, do not rerun the SQL blindly: tables and policy names may already exist. This guide records the setup for someone creating their own project.

## 1. Create the project and configure Auth

Create a Supabase project, then obtain its project URL and legacy anon key from the project API settings. Put these values in `.env` using the names in `.env.example`.

The pinned Python client uses the legacy anon key. Keep the service-role key out of this app; requests should be subject to user ownership policies.

Under Authentication → URL Configuration:

- For local testing, set the Site URL to `http://127.0.0.1:5001/login`.
- Add that exact URL to the allowed Redirect URLs.
- When deploying, use the deployed HTTPS `/login` URL as the Site URL and add it to the allowed redirects. Keep the local URL allowed if you still develop locally.

The current signup implementation uses the Site URL as the default email-confirmation destination. Sharing one Supabase project between local and deployed apps means this default applies to both.

Leave email confirmation enabled when testing the normal signup flow. For public signup, configure custom SMTP: the built-in sender has restrictive rate limits and recipient restrictions. See [Supabase's SMTP guide](https://supabase.com/docs/guides/auth/auth-smtp).

## 2. Create the predictions table and ownership policies

In the SQL Editor, run these files in order:

1. [`000_predictions_schema.sql`](../supabase/migrations/000_predictions_schema.sql): table, index, read/insert privileges, and owner policies.
2. [`001_prediction_delete_policy.sql`](../supabase/migrations/001_prediction_delete_policy.sql): delete privilege and owner policy.

The `image` column holds an object path, such as `USER_UUID/random-filename.jpg`, rather than an expiring viewing URL. Confidence is stored on a 0–1 scale and converted to a percentage for display.

## 3. Create the private image bucket

Under Storage, create a bucket with:

| Setting | Value |
| --- | --- |
| Bucket name / ID | `prediction-images` |
| Public | Disabled |
| Allowed MIME types | `image/jpeg` |

The backend accepts JPEG and PNG, then converts the validated image to JPEG before uploading. Flask limits the incoming request body to 5 MiB and images to 20 million pixels. A re-encoded image can differ in size from the original upload; if you add a bucket file-size limit, account for that difference.

Then run [`002_prediction_image_storage_policies.sql`](../supabase/migrations/002_prediction_image_storage_policies.sql).

The policies permit authenticated upload, read, and delete operations only when the object's first folder matches the user's ID. Do not add a broad public-read policy.

## 4. Configure the application

Copy `.env.example` to `.env` and fill in the project URL, anon key, and a generated secret. Use `SESSION_COOKIE_SECURE=false` for local HTTP and `true` for deployed HTTPS.

For hosting, set these as environment variables in the hosting dashboard rather than committing `.env`. Local and hosted `SECRET_KEY` values may differ.

Use a single server instance initially because the current session cache is local to that server. New deployments do not need `instance/legacy_uploads`; that folder only supports historical uploads from the previous local-storage implementation.

## 5. Verify the setup

- Sign up, confirm the email, and log in; check that the display name appears.
- Upload a small JPEG and PNG; check results, history, and Storage paths.
- Refresh history to check that the record persists and its image displays.
- Delete a prediction and verify both its row and object are removed.
- Clear history and check that older records beyond the displayed 10 are removed too.
- Test with two accounts: one account's actions must not remove the other's records or images.
- Log out and visit `/index`; it should redirect to `/login`.

A signed image link can be used by anyone holding it until it expires (currently 10 minutes). Copying that link to an incognito window is not an ownership-policy test.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Port 5000 returns 403 on macOS | Start Flask on port 5001 and use that URL. |
| Confirmation returns to the wrong port | Update Auth's Site URL/allowed redirects and request a fresh email. |
| `otp_expired` | Check whether the account is already confirmed; otherwise request a fresh confirmation link. |
| Email rate limit exceeded | Check Auth email limits and SMTP setup; repeated retries won't bypass the limit. |
| Storage upload is denied | Check the private bucket's ID, policies, user-folder path, and client Authorization header. |
| Login fails only over local HTTP | Check that `SESSION_COOKIE_SECURE` is not set to `true` locally. |
| Analysis hangs on hosted service | Use the diagnostic logs to find the stalled stage and inspect CPU/memory. Hosted inference on Render is currently unresolved. |

The current dependency pins do not expose every method shown in newer Supabase documentation; `auth.resend()` was unavailable in the installed Auth client during testing. Check version compatibility before implementing examples from the latest documentation.
