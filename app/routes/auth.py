from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os, requests
from urllib.parse import urlencode
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

# 🧠 Login Page with mode toggle
@auth_bp.route("/login", methods=["GET"])
def login_page():
    mode = request.args.get("mode", "login")
    return render_template("login.html", mode=mode)

# 🧠 Handle Email Login/Register Logic
@auth_bp.route("/auth", methods=["POST"])
def handle_auth():
    mode = request.form.get("mode")
    email = request.form.get("email")
    password = request.form.get("password")

    db = current_app.mongo_db
    user = db.users.find_one({"email": email})

    if mode == "register":
        if user:
            flash("User already exists. Try logging in.")
            return redirect(url_for("auth.login_page", mode="register"))
        db.users.insert_one({
            "email": email,
            "password": generate_password_hash(password)
        })
        session["user"] = email
        return redirect(url_for("dashboard.dashboard"))

    elif mode == "login":
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials.")
            return redirect(url_for("auth.login_page", mode="login"))
        session["user"] = email
        return redirect(url_for("dashboard.dashboard"))

    flash("Something went wrong.")
    return redirect(url_for("auth.login_page"))

# 🧠 Logout
@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login_page"))

# 🌐 Google OAuth
@auth_bp.route("/login/google")
def login_google():
    params = {
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        "redirect_uri": url_for("auth.google_callback", _external=True),
        "response_type": "code",
        "scope": "openid email profile"
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")

@auth_bp.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        "redirect_uri": url_for("auth.google_callback", _external=True),
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=data).json()
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_response['access_token']}"}
    ).json()
    session["user"] = userinfo["email"]
    return redirect(url_for("dashboard.dashboard"))

# 🌐 GitHub OAuth
@auth_bp.route("/login/github")
def login_github():
    params = {
        "client_id": os.getenv("GITHUB_OAUTH_CLIENT_ID"),
        "redirect_uri": url_for("auth.github_callback", _external=True),
        "scope": "user:email"
    }
    return redirect(f"https://github.com/login/oauth/authorize?{urlencode(params)}")

@auth_bp.route("/login/github/callback")
def github_callback():
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": os.getenv("GITHUB_OAUTH_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
        "code": code
    }
    headers = {"Accept": "application/json"}
    token_response = requests.post(token_url, data=data, headers=headers).json()
    userinfo = requests.get(
        "https://api.github.com/user",
        headers={"Authorization": f"token {token_response['access_token']}"}
    ).json()
    session["user"] = userinfo["login"]
    return redirect(url_for("dashboard.dashboard"))
