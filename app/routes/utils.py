import os
from cloudant.client import Cloudant
from dotenv import load_dotenv

load_dotenv()

def get_db():
    client = Cloudant.iam(
        account_name=os.getenv("CLOUDANT_ACCOUNT_NAME"),
        api_key=os.getenv("CLOUDANT_API_KEY"),
        connect=True
    )
    db = client.create_database(os.getenv("CLOUDANT_DB_NAME"), throw_on_exists=False)
    return db

def register_user(email, name):
    db = get_db()
    if email and name:
        if email not in db:
            doc = {
                '_id': email,
                'name': name,
                'type': 'user'
            }
            db.create_document(doc)
            return True
    return False
