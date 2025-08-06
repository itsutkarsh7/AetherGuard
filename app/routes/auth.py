from flask import Blueprint, redirect, url_for, session
from app.oauth import oauth
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/login/github")
def login_github():
    redirect_uri = url_for("auth.github_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route("/callback/google")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    if not user_info:
        return redirect(url_for("landing.landing"))  # Optional safety check
    session["user"] = user_info
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/callback/github")
def github_callback():
    token = oauth.github.authorize_access_token()
    user = oauth.github.get("user").json()
    if not user:
        return redirect(url_for("landing.landing"))  # Optional safety check
    session["user"] = user
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing.landing"))
