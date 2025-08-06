from flask import Blueprint, render_template

landing_bp = Blueprint("landing", __name__, url_prefix="/")

@landing_bp.route("/")
def home():
    return render_template("landing.html")
