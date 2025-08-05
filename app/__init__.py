# app/__init__.py

from flask import Flask
from app.routes.auth import auth_bp
from app.routes.landing import landing_bp
from app.routes.dashboard import dashboard_bp
from app.extensions import init_mongo
from app.oauth import oauth
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    
    # Load secret key and DB URI directly from .env
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    
    init_mongo(app)
    oauth.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app
