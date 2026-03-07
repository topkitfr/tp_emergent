# backend/script/fix/reset_database.py
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


# Charger la config
ENV_PATH = Path(__file__).parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


async def reset():
    # Liste élargie des collections à vider
    collections = [
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
        "uploads",      # si tu as une collection pour les fichiers
        "profiles",     # si profils utilisateurs stockés à part
        # ajoute ici toute autre collection métier que tu veux wipe
    ]

    print(f"=== RESET DATABASE {DB_NAME} ===")
    for col in collections:
        result = await db[col].delete_many({})
        print(f"🗑️  {col}: {result.deleted_count} documents supprimés")

    print("\n✅ Base applicative complètement vidée (collections listées).")
    client.close()


if __name__ == "__main__":
    asyncio.run(reset())
