from flask import Blueprint, redirect, url_for, session, request, current_app, flash
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__)
oauth = OAuth()

def init_app(app):
    oauth.init_app(app)

    # Google OAuth config
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # GitHub OAuth config
    oauth.register(
        name='github',
        client_id=app.config['GITHUB_CLIENT_ID'],
        client_secret=app.config['GITHUB_CLIENT_SECRET'],
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'}
    )

# ----------------- Google OAuth -----------------

@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.authorize_google", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/authorize/google")
def authorize_google():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)

    if user_info:
        save_user_to_db(user_info, provider='google')
        session["user"] = {
            "provider": "google",
            "id": user_info["sub"],
            "name": user_info["name"],
            "email": user_info["email"],
        }
        return redirect(url_for("dashboard.dashboard_view"))

    flash("Google login failed", "error")
    return redirect(url_for("landing.landing_page"))

# ----------------- GitHub OAuth -----------------

@auth_bp.route("/login/github")
def login_github():
    redirect_uri = url_for("auth.authorize_github", _external=True)
    return oauth.github.authorize_redirect(redirect_uri)

@auth_bp.route("/authorize/github")
def authorize_github():
    token = oauth.github.authorize_access_token()
    user_info = oauth.github.get("user").json()

    if user_info:
        email = user_info.get("email")
        if not email:
            # Fetch primary email if missing
            emails = oauth.github.get("user/emails").json()
            for e in emails:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break

        user_record = {
            "id": user_info["id"],
            "name": user_info["name"] or user_info["login"],
            "email": email,
        }

        save_user_to_db(user_record, provider='github')
        session["user"] = {
            "provider": "github",
            "id": user_info["id"],
            "name": user_record["name"],
            "email": email,
        }
        return redirect(url_for("dashboard.dashboard_view"))

    flash("GitHub login failed", "error")
    return redirect(url_for("landing.landing_page"))

# ----------------- Logout -----------------

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("landing.landing_page"))

# ----------------- Save to MongoDB -----------------

def save_user_to_db(user_info, provider):
    db = current_app.db
    users = db["users"]

    query = {"provider": provider, "id": user_info.get("sub") or user_info.get("id")}
    existing_user = users.find_one(query)

    if existing_user:
        return  # Already exists

    new_user = {
        "provider": provider,
        "id": user_info.get("sub") or user_info.get("id"),
        "name": user_info.get("name") or user_info.get("login"),
        "email": user_info.get("email"),
    }
    users.insert_one(new_user)
