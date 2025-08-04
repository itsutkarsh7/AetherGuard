from cloudant.client import Cloudant
from dotenv import load_dotenv
import os

load_dotenv()

account = os.getenv("CLOUDANT_USERNAME")
apikey = os.getenv("CLOUDANT_APIKEY")
url = os.getenv("CLOUDANT_URL")
db_name = os.getenv("CLOUDANT_DBNAME", "SentinelAI")

client = Cloudant.iam(account_name=account, api_key=apikey, url=url, connect=True)
client.connect()

db = client[db_name]
