import os
from datetime import timedelta
from pathlib import Path

from cachelib.file import FileSystemCache
from dotenv import load_dotenv
from flask import Flask
from flask_session import Session


def create_app():
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY must be configured in .env")

    session_dir = Path(app.instance_path) / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    app.config.update(
        SECRET_KEY=secret_key,
        SESSION_TYPE="cachelib",
        SESSION_CACHELIB=FileSystemCache(
            cache_dir=str(session_dir),
            threshold=500,
        ),
        SESSION_PERMANENT=False,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )

    Session(app)

    from app.routes import routes
    app.register_blueprint(routes)

    return app