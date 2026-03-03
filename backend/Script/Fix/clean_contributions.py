import asyncio
import os
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "topkit")

client = AsyncIOMotorClient(MONGO_URL)
db     = client[DB_NAME]

async def clean():
    print("🧹 Nettoyage des contributions...\n")

    # 1) Supprimer toutes les submissions
    res = await db.submissions.delete_many({})
    print(f"[submissions] 🗑️  {res.deleted_count} supprimée(s)")

    # 2) Supprimer tous les reports
    res = await db.reports.delete_many({})
    print(f"[reports]     🗑️  {res.deleted_count} supprimé(s)")

    # 3) Remettre toutes les entités for_review / rejected en for_review
    #    (utile si tu veux juste repartir de zéro sur les votes)
    for collection in ["teams", "leagues", "brands", "players"]:
        res = await db[collection].update_many(
            {"status": {"$in": ["for_review", "rejected", "approved"]}},
            {"$unset": {"submission_id": ""}, "$set": {
                "status":     "for_review",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        print(f"[{collection}] 🔄  {res.modified_count} entité(s) remise(s) en for_review")

    print("\n✅ Nettoyage terminé.")
    client.close()

if __name__ == "__main__":
    asyncio.run(clean())
