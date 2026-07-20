from flask import Blueprint, render_template, request, redirect, session
from app.database import supabase
from functools import wraps
from app.ML.predictor import predict_image
import os

from app.history import save_prediction, get_user_predictions

routes = Blueprint("routes", __name__)

"""Blue print allows routees to be defined seperately. Makes navigation easier"""
#  wrapper for the login
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

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
            supabase.auth.sign_up({
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
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            #  create session for the user
            session["user"] = result.user.id
            return redirect("/index")
        #  login error message
        except Exception as e:
            print("LOGIN ERROR:", e)
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# Route to the homepage. User needs to be logged in to access this page. 
@routes.route("/index")
@login_required
def index():
    past_predictions = get_user_predictions(user_id=session["user"], limit=10)
    return render_template("index.html", past_predictions=past_predictions)

# Route to the prediction page. requires users to be logged in
@routes.route("/predict", methods=["POST"])
@login_required
def predict_route():
    if "image" not in request.files:
        return "No image uploaded", 400
    # file upload logic. Gets file from the directory and make sure the file exists. Adds it to the uplaods folder.
    file = request.files["image"]
    upload_folder = os.path.join("app/static/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # displays the label, confidence, and the top three possibilities for the image. 
    label, confidence, top3 = predict_image(file_path)

    # saves the prediction to the database with all information.
    save_prediction(
        user_id=session["user"],
        image=file.filename,
        label=label,
        confidence=confidence
    )

    # Shows the result of the classificaiton on the classify page. 
    return render_template(
        "classification_result.html",
        label=label,
        confidence=round(confidence * 100, 2),
        top3=top3,
        image=file.filename
    )

