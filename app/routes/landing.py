from flask import Blueprint, render_template, session, redirect, url_for

landing_bp = Blueprint("landing", __name__, url_prefix="/landing")

@landing_bp.route("/")
def landing():
    if "user" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("landing.html")
