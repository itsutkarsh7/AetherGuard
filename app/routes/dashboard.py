from flask import Blueprint, render_template, session, redirect, url_for
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
def dashboard():
    if "user" not in session and "email" not in session:
        return redirect(url_for("landing.landing"))

    # Build user object based on available session data
    user = session.get("user", {
        "name": session.get("email", "Guest"),
        "email": session.get("email", "Not Provided"),
        "provider": "email"
    })

    # Query logs collection from MongoDB
    logs = list(db.logs.find().limit(10))  # replace 'logs' with your actual collection

    return render_template("dashboard.html", user=user, logs=logs)
