from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
oauth = OAuth()

# Initialize OAuth with app
def init_oauth(app):
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'}
    )

# -------------------- Routes --------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = current_app.db
        user = db.users.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard.dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    db = current_app.db

    if db.users.find_one({"email": email}):
        flash("User already exists.", "warning")
        return redirect(url_for("auth.login"))

    hashed_password = generate_password_hash(password)
    user_id = db.users.insert_one({"email": email, "password": hashed_password}).inserted_id
    session["user_id"] = str(user_id)
    session["email"] = email
    flash("Registration successful!", "success")
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You’ve been logged out.", "info")
    return redirect(url_for("landing.landing"))

# -------------------- Google OAuth --------------------

@auth_bp.route("/google")
def google_login():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get("userinfo")
    email = user_info["email"]
    db = current_app.db

    user = db.users.find_one({"email": email})
    if not user:
        user_id = db.users.insert_one({"email": email}).inserted_id
        session["user_id"] = str(user_id)
    else:
        session["user_id"] = str(user["_id"])

    session["email"] = email
    flash("Logged in with Google!", "success")
    return redirect(url_for("dashboard.dashboard"))

# -------------------- GitHub OAuth --------------------

@auth_bp.route("/github")
def github_login():
    redirect_uri = url_for("auth.github_callback", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route("/github/callback")
def github_callback():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get("user", token=token)
    user_info = resp.json()
    email = user_info.get("email")

    # Fallback: fetch emails if primary email is not public
    if not email:
        emails = oauth.github.get("user/emails", token=token).json()
        email = next((e["email"] for e in emails if e["primary"] and e["verified"]), None)

    if not email:
        flash("GitHub email not found.", "danger")
        return redirect(url_for("auth.login"))

    db = current_app.db
    user = db.users.find_one({"email": email})
    if not user:
        user_id = db.users.insert_one({"email": email}).inserted_id
        session["user_id"] = str(user_id)
    else:
        session["user_id"] = str(user["_id"])

    session["email"] = email
    flash("Logged in with GitHub!", "success")
    return redirect(url_for("dashboard.dashboard"))
