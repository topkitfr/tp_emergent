# backend/reset_db.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


async def reset_db():
    collections_to_clear = [
        "master_kits",
        "versions",
        "teams",
        "leagues",
        "brands",
        "players",
        "reviews",
        "collections",
        "submissions",
        "wishlists",
        "sponsors",
        "reports",
        "votes",
        "estimations",
        "uploads",
        "profiles",
    ]

    print("=== RESET DATABASE ONLY ===")
    for col in collections_to_clear:
        result = await db[col].delete_many({})
        print(f"🗑️  {col}: {result.deleted_count} supprimé(s)")

    print("\n✅ Database vidée. Aucun seed recréé.")
    client.close()


asyncio.run(reset_db())

