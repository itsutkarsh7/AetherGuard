from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from cloudant.client import Cloudant
import os

auth_bp = Blueprint("auth", __name__)

# IBM Cloudant credentials (use environment variables in production)
client = Cloudant.iam(
    username=os.getenv("CLOUDANT_USERNAME"),
    api_key=os.getenv("CLOUDANT_APIKEY"),
    connect=True,
)
db = client["SentinelAI"]

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in db:
            user = db[username]
            if check_password_hash(user["password"], password):
                session["user"] = {"name": user["name"], "email": user["email"]}
                return redirect(url_for("dashboard.dashboard"))
            else:
                flash("Invalid password")
        else:
            flash("User not found")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if username in db:
            flash("Username already exists.")
        else:
            hashed_password = generate_password_hash(password)
            db[username] = {
                "name": username,
                "email": email,
                "password": hashed_password,
            }
            session["user"] = {"name": username, "email": email}
            return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing.landing"))

# Optional: OAuth routes can be added here using flask-dance or manually
@auth_bp.route("/auth/google")
def google_login():
    flash("Google OAuth not implemented yet.")
    return redirect(url_for("auth.login"))

@auth_bp.route("/auth/github")
def github_login():
    flash("GitHub OAuth not implemented yet.")
    return redirect(url_for("auth.login"))
