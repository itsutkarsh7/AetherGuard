from flask import Blueprint, render_template, session, redirect, url_for, current_app

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login_google"))  # or your login page

    db = current_app.mongo_db
    threats = list(db.threats.find())

    return render_template("dashboard.html", user=session["user"], threats=threats)
