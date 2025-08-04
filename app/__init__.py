# app/__init__.py
from flask import Flask
from app.routes.landing import landing_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')

    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

    return app
