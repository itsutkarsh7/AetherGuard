import os
from flask import Flask
from dotenv import load_dotenv
from cloudant.client import Cloudant

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')

    from .auth import auth_bp
    from .landing import landing_bp
    from .dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app
