from flask import Flask
from app.routes.auth import auth_bp
from app.routes.landing import landing_bp
from app.routes.dashboard import dashboard_bp
from app.extensions import init_mongo
from app.oauth import oauth
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object("config.Config")

    init_mongo(app)
    oauth.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app
