from flask import Flask
from dotenv import load_dotenv
from flask_session import Session
import os

from .blueprints.auth import auth_bp, configure_oauth
from .dashboard import dashboard_bp
from .landing import landing_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Secret key for session management
    app.secret_key = os.getenv("SECRET_KEY")
    
    # Session config
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    # OAuth setup (Google, GitHub)
    configure_oauth(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(landing_bp, url_prefix="/")

    return app
