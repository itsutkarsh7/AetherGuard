# app/extensions.py

from pymongo import MongoClient
from flask import current_app
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

mongo_client = None
db = None

def init_mongo(app):
    global mongo_client, db

    # Load the MongoDB URI from environment
    mongodb_uri = os.getenv("MONGODB_URI")

    # Optional debug print
    print("Using MongoDB URI:", mongodb_uri)

    # Assign to Flask config (optional, if needed elsewhere)
    app.config["MONGODB_URI"] = mongodb_uri

    # Connect to MongoDB
    mongo_client = MongoClient(mongodb_uri)

    # Set global db reference
    db = mongo_client.get_default_database()
    app.mongo_client = mongo_client
    app.db = db
