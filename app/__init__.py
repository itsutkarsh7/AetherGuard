from flask import Flask
import os
from .extensions import init_mongo
from .routes.auth import auth_bp
from .routes.landing import landing_bp
from .routes.dashboard import dashboard_bp

def create_app():

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    print(f"Landing.html exists: {os.path.exists(os.path.join(template_dir, 'landing.html'))}")
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    # Load config from config.py
    app.config.from_pyfile("../config.py", silent=True)

    # Initialize MongoDB
    init_mongo(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app