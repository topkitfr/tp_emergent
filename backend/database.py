from motor.motor_asyncio import AsyncIOMotorClient
import os

mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME", "topkit")

if not mongo_url:
    raise RuntimeError("MONGO_URL environment variable is not set (Render env)")

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


def get_kits_collection():
    return db["kits"]