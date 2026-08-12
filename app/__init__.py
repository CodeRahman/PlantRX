import os

from flask import Flask
from app.routes import routes


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key"
    )

    app.register_blueprint(routes)

    return app