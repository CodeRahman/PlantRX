# PlantRX

A Flask application that classifies plant leaf images and keeps a personal prediction history. PlantRX combines a TensorFlow image classifier with Supabase authentication, database access policies, and private image storage.

## Project status

The upload-to-prediction flow has been tested locally, including image storage and history management. A Render deployment is available at [plantrx-pmmy.onrender.com](https://plantrx-pmmy.onrender.com), but **image analysis currently stalls on that deployment**. Login and the dashboard work; the hosted prediction flow is not a working end-to-end demo yet. Deployment troubleshooting is paused.

The latest implementation is on [`maintenance/setup-cleanup`](https://github.com/CodeRahman/PlantRX/tree/maintenance/setup-cleanup). Use that branch for the setup instructions below until it is merged into `main`.

## Features

- Email/password signup and login, with display names and personalized greetings.
- JPEG and PNG uploads with server-side format and image-size validation.
- Classification across 38 labels covering 14 plant categories, with a top-three prediction breakdown.
- Private image storage with temporary viewing links.
- Account-specific history showing the latest 10 predictions.
- Individual prediction deletion and a clear-history action covering all of the user's predictions.
- A responsive dark green interface across authentication, dashboard, and result pages.

## My contribution

PlantRX began as a team project. My original contribution focused primarily on the frontend. I now maintain this repository and have continued work on the interface, authentication and session handling, Supabase setup, private image storage, and prediction-history management.

The current classifier is an existing model artifact from the team project. I have worked on its inference integration; I do not claim to have independently trained or validated the original model.

## How it works

1. Flask validates the uploaded image and converts it to JPEG.
2. The classifier resizes the image to 224 × 224 pixels, applies MobileNetV2 preprocessing, and runs inference.
3. The JPEG is uploaded to the private `prediction-images` bucket under the user's ID.
4. The prediction label, confidence, owner, and storage path are saved in Supabase Postgres.
5. The result and history pages display images through signed links that expire after 10 minutes.

The browser submits forms to Flask. Supabase enforces account ownership through Row Level Security policies, using the user's access token on database and Storage requests.

## Stack

| Area | Technology |
| --- | --- |
| Backend | Python 3.11, Flask, Gunicorn |
| Templates and styling | Jinja, HTML, CSS |
| Inference | TensorFlow/Keras, NumPy, Pillow |
| Authentication | Supabase Auth |
| Prediction records | Supabase Postgres with Row Level Security |
| Images | Supabase Storage, private bucket |
| Sessions | Flask-Session with a filesystem-backed CacheLib cache |

## Run locally

### 1. Clone the current implementation

```bash
git clone --branch maintenance/setup-cleanup https://github.com/CodeRahman/PlantRX.git
cd PlantRX
```

### 2. Create an isolated Python environment

Use Python 3.11. The runtime version is recorded in `.python-version`.

With Conda:

```bash
conda create -n plantrx python=3.11 -y
conda activate plantrx
python -m pip install -r requirements.txt
python -m pip check
```

Alternatively, with Python 3.11 already installed:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
```

On Windows, activate the virtual environment with `.venv\Scripts\activate` instead.

### 3. Configure Supabase and environment variables

Follow [the Supabase setup guide](docs/SETUP.md) to create the predictions table, private image bucket, and access policies.

Copy the example configuration:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Fill in `.env` with your project's URL and legacy anon key, then paste the generated value into `SECRET_KEY`. Keep `.env` out of version control. The app does not require a service-role key.

### 4. Start the app

```bash
python -m flask --app run:app run --debug --port 5001
```

Open [http://127.0.0.1:5001/login](http://127.0.0.1:5001/login). Create an account, confirm the email if required by your Supabase configuration, and log in to upload a leaf image.

Port 5001 avoids the port-5000 conflict encountered during macOS development. Debug mode is for local development only.

## Repository guide

| Path | Responsibility |
| --- | --- |
| `run.py` | Application entry point |
| `app/__init__.py` | App configuration, sessions, template filter |
| `app/routes.py` | Authentication, uploads, results, history actions |
| `app/database.py` | Request-scoped Supabase client |
| `app/history.py` | Prediction record queries and deletion |
| `app/storage.py` | Image uploads, signed links, and removal |
| `app/ML/` | Classifier artifact, label mapping, and inference code |
| `app/templates/` | Login, signup, dashboard, and result templates |
| `app/static/` | Stylesheet and application images |
| `supabase/migrations/` | SQL setup and policy changes |
| `docs/SETUP.md` | Supabase configuration and troubleshooting |

## Model and application limitations

- The model predicts one of its supported classes; it does not currently reject unrelated images or unsupported plants.
- Confidence is a model output score, not a demonstrated probability that a diagnosis is correct.
- Dataset provenance, training procedure, and independent evaluation results are not currently documented in this repository. No real-world accuracy claim is made.
- Sessions are stored on the app server. Server restarts or ephemeral hosting can require users to log in again, and automatic access-token refresh is not implemented.
- Database deletion and image removal are separate operations. A failed image removal is logged and can leave a file needing cleanup.
- Supabase email delivery must be configured appropriately before opening signup to the public.

## Next steps

- Resolve the hosted inference stall and verify the complete deployed workflow.
- Add clearer upload and signup error messages and confirmation-email resend support.
- Improve inference observability and measure CPU/memory requirements.
- Document model provenance and evaluate predictions on representative images.
- Practice an EC2 deployment as part of my AWS Solutions Architect learning.

The repository currently has no license file; no new license is implied by this documentation update.
