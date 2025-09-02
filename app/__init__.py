# app/__init__.py

from flask import Flask, session, render_template
import os
from dotenv import load_dotenv  
from .extensions import init_mongo
from .routes.auth import auth_bp, init_oauth
from .routes.landing import landing_bp
from .routes.dashboard import dashboard_bp

def create_app():
    # Load environment variables
    load_dotenv()

    # Get absolute paths - templates should be at project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, 'templates')
    static_dir = os.path.join(project_root, 'static')
    
    print(f"Project root: {project_root}")
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    print(f"Template directory exists: {os.path.exists(template_dir)}")
    print(f"Landing.html exists: {os.path.exists(os.path.join(template_dir, 'landing.html'))}")
    print(f"Login.html exists: {os.path.exists(os.path.join(template_dir, 'login.html'))}")
    print(f"Base.html exists: {os.path.exists(os.path.join(template_dir, 'base.html'))}")
    
    # Create Flask app instance
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    # Configuration
    app.secret_key = os.environ.get('SECRET_KEY', '85543ded3e058db2547377c9e132bc71fd328ab15e053086bc150ad74747d86f')
    
    # OAuth configuration
    app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    app.config['GITHUB_OAUTH_CLIENT_ID'] = os.environ.get('GITHUB_OAUTH_CLIENT_ID')
    app.config['GITHUB_OAUTH_CLIENT_SECRET'] = os.environ.get('GITHUB_OAUTH_CLIENT_SECRET')
    
    # MongoDB configuration
    app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI')

    # Initialize MongoDB
    try:
        init_mongo(app)
        print("✅ MongoDB initialized successfully")
    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")

    # Initialize OAuth
    try:
        init_oauth(app)
        print("✅ OAuth initialized successfully")
    except Exception as e:
        print(f"❌ OAuth initialization failed: {e}")

    # Register Blueprints
    try:
        app.register_blueprint(auth_bp)
        app.register_blueprint(landing_bp)
        app.register_blueprint(dashboard_bp)
        print("✅ Blueprints registered successfully")
    except Exception as e:
        print(f"❌ Blueprint registration failed: {e}")

    # Add context processors for templates
    @app.context_processor
    def utility_processor():
        return {
            'user_logged_in': 'user_id' in session,
            'current_user': session.get('user_name', '')
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'app': 'AetherGuard'}, 200

    print("=" * 60)
    print("🛡️  AetherGuard Flask App Initialized Successfully")
    print("=" * 60)

    return app
