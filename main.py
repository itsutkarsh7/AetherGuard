from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
from blueprints.auth import auth_bp
app.register_blueprint(auth_bp)
