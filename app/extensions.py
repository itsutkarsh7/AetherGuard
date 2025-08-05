# app/extensions.py
from pymongo import MongoClient
from flask import current_app

mongo_client = None
db = None

def init_mongo(app):
    global mongo_client, db
    mongo_client = MongoClient(app.config["MONGODB_URI"])
    db = mongo_client.get_default_database()
