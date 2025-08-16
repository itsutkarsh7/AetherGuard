from flask import Flask
import os
from dotenv import load_dotenv  
from .extensions import init_mongo
from .routes.auth import auth_bp
from .routes.landing import landing_bp
from .routes.dashboard import dashboard_bp

def create_app():
    # Load environment variables
    load_dotenv()  # Add this line

    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    print(f"Landing.html exists: {os.path.exists(os.path.join(template_dir, 'landing.html'))}")
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    # Set secret key from environment
    app.secret_key = os.environ.get('SECRET_KEY', '85543ded3e058db2547377c9e132bc71fd328ab15e053086bc150ad74747d86f')

    # Load config from oauth.py
    app.config.from_pyfile("../oauth.py", silent=True)

    # Initialize MongoDB
    init_mongo(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)

    return app