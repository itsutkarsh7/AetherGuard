from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.get_database("sentinelAI")  # Use database name explicitly

def init_db(app):
    app.mongo_client = client
    app.db = db
