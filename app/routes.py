from flask import Blueprint, render_template, request, redirect, session
from app.database import get_supabase
from functools import wraps
from app.ML.predictor import predict_image
import os
import time
from flask import current_app
import secrets
from flask import abort
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from app.history import (
    save_prediction,
    get_user_predictions,
    delete_prediction,
)

routes = Blueprint("routes", __name__)

"""Blue print allows routees to be defined seperately. Makes navigation easier"""
#  wrapper for the login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user")
        access_token = session.get("access_token")
        expires_at = session.get("expires_at", 0)

        if (
            not user_id
            or not access_token
            or time.time() >= expires_at
        ):
            session.clear()
            return redirect("/login")

        return f(*args, **kwargs)

    return wrapper

def remove_prediction_image(filename):
    upload_folder = (
        Path(current_app.static_folder) / "uploads"
    ).resolve()

    image_path = (upload_folder / filename).resolve()

    if image_path.parent != upload_folder:
        current_app.logger.warning(
            "Skipped prediction image outside the upload folder"
        )
        return

    try:
        image_path.unlink(missing_ok=True)
    except OSError:
        current_app.logger.exception(
            "Could not remove a deleted prediction's image"
        )


@routes.route("/")
def home():
    if "user" in session:
        return redirect("/index")
    return redirect("/login")

# Route for the Sign up page. Redirects user to login after signing up
@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")

        try:
            get_supabase().auth.sign_up({
                "email": email,
                "password": password
            })
            return redirect("/login")
        #  error for failed signup
        except Exception as e:
            print("SIGNUP ERROR:", e)
            return render_template("signup.html", error="Signup failed")

    return render_template("signup.html")

# Route for the login page. Redirects to the index/homepage if login is successful
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "login.html",
                error="Enter your email and password",
            ), 400

        try:
            result = get_supabase().auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception:
            current_app.logger.warning(
                "Supabase sign-in did not complete"
            )
            return render_template(
                "login.html",
                error=(
                    "Could not sign in. Check your credentials "
                    "and email confirmation, then try again."
                ),
            ), 401

        if not result.user or not result.session:
            return render_template(
                "login.html",
                error="Could not establish a login session",
            ), 401

        session.clear()
        session["user"] = result.user.id
        session["access_token"] = result.session.access_token
        session["expires_at"] = result.session.expires_at

        current_app.session_interface.regenerate(session)

        return redirect("/index")

    return render_template("login.html")


# Route to the homepage. User needs to be logged in to access this page. 
@routes.route("/index")
@login_required
def index():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    past_predictions = get_user_predictions(
        user_id=session["user"],
        limit=10,
    )

    return render_template(
        "index.html",
        past_predictions=past_predictions,
        csrf_token=session["csrf_token"],
    )

@routes.route(
    "/predictions/<uuid:prediction_id>/delete",
    methods=["POST"],
)
@login_required
def delete_prediction_route(prediction_id):
    expected_token = session.get("csrf_token")
    submitted_token = request.form.get("csrf_token", "")

    if not expected_token or not secrets.compare_digest(
        expected_token,
        submitted_token,
    ):
        abort(400, description="Invalid deletion request")

    deleted_prediction = delete_prediction(
        user_id=session["user"],
        prediction_id=str(prediction_id),
    )

    if deleted_prediction is None:
        abort(404, description="Prediction not found")

    remove_prediction_image(deleted_prediction["image"])

    return redirect("/index", code=303)

@routes.route("/logout", methods=["POST"])
@login_required
def logout():
    expected_token = session.get("csrf_token")
    submitted_token = request.form.get("csrf_token", "")

    if not expected_token or not secrets.compare_digest(
        expected_token,
        submitted_token,
    ):
        abort(400, description="Invalid logout request")

    session.clear()
    return redirect("/login")

# Route to the prediction page. requires users to be logged in
@routes.route("/predict", methods=["POST"])
@login_required
def predict_route():
    expected_token = session.get("csrf_token")
    submitted_token = request.form.get("csrf_token", "")

    if not expected_token or not secrets.compare_digest(
        expected_token,
        submitted_token,
    ):
        abort(400, description="Invalid upload request")

    file = request.files.get("image")

    if file is None or not file.filename:
        return "Choose an image before submitting.", 400

    try:
        with Image.open(file.stream) as uploaded_image:
            if uploaded_image.format not in {"JPEG", "PNG"}:
                return "Upload a JPEG or PNG image.", 400

            width, height = uploaded_image.size
            if width * height > 20_000_000:
                return "The image must contain at most 20 million pixels.", 400

            uploaded_image.load()

            image = ImageOps.exif_transpose(uploaded_image)
            image = image.convert("RGB")

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ):
        return "The file could not be read as a valid image.", 400

    upload_folder = Path(current_app.static_folder) / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.jpg"
    file_path = upload_folder / filename

    image.save(file_path, format="JPEG", quality=95)

    label, confidence, top3 = predict_image(file_path)

    save_prediction(
        user_id=session["user"],
        image=filename,
        label=label,
        confidence=confidence,
    )

    return render_template(
        "classification_result.html",
        label=label,
        confidence=round(confidence * 100, 2),
        top3=top3,
        image=filename,
    )


