from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")


# app/landing.py
from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__)

@landing_bp.route("/")
def landing():
    return render_template("landing.html")
