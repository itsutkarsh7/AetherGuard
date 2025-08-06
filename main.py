import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Detect environment
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("PORT", 5000))  # For Render or local
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
