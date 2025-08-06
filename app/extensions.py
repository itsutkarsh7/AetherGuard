# app/extensions.py

from pymongo import MongoClient
from flask import current_app
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Load environment variables from .env
load_dotenv()

mongo_client = None
db = None

def init_mongo(app):
    global mongo_client, db

    # Fetch MongoDB URI
    mongodb_uri = os.getenv("MONGODB_URI")

    if not mongodb_uri:
        raise ValueError("MONGODB_URI not found in environment variables")

    # Optional: log for debug
    print("Connecting to MongoDB URI:", mongodb_uri)

    # Assign URI to app config
    app.config["MONGODB_URI"] = mongodb_uri

    # Initialize client
    mongo_client = MongoClient(mongodb_uri)

    # ⚠️ Fix: Use specific database name if get_default_database() fails
    try:
        db = mongo_client.get_default_database()
    except Exception:
        # fallback: extract db from URI
        db_name = mongodb_uri.rsplit("/", 1)[-1].split("?")[0]
        db = mongo_client[db_name]

    # Store client and db on app object
    app.mongo_client = mongo_client
    app.db = db
