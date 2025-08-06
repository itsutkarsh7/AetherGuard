# app/__init__.py

import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import init_mongo
from app.oauth import oauth
from app.routes.auth import auth_bp
from app.routes.landing import landing_bp
from app.routes.dashboard import dashboard_bp

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(
        __name__,
        template_folder="templates",  # Folder where Jinja2 HTML templates are stored
        static_folder="static"        # Folder for CSS, JS, images, etc.
    )

    # Secure Flask secret key
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    # Initialize MongoDB with app
    init_mongo(app)

    # Initialize OAuth (Google/GitHub)
    oauth.init_app(app)

    # Register all blueprints (modular routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app
