from flask import Flask
from app.db import db  # Ensure this imports your MongoDB setup

app = Flask(__name__)

@app.route("/test-db")
def test_db():
    try:
        # Try inserting a test document
        test_result = db.test.insert_one({"status": "connected"})
        return "✅ Connected to MongoDB: Document ID = " + str(test_result.inserted_id)
    except Exception as e:
        return "❌ Failed to connect: " + str(e)
