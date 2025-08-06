from flask import Blueprint, render_template, session, redirect, url_for
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
def dashboard():
    if "user" not in session:
        return redirect(url_for("landing.landing"))

    logs = list(db.logs.find().limit(10))  # Real MongoDB logs
    return render_template("dashboard.html", user=session["user"], logs=logs)
