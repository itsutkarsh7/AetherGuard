from flask import Flask
from .extensions import init_mongo
from .routes.auth import auth_bp
from .routes.landing import landing_bp
from .routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)

    # Load config from config.py
    app.config.from_pyfile("../config.py", silent=True)

    # Initialize MongoDB
    init_mongo(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app
