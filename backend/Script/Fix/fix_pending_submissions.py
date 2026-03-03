import asyncio
import uuid
import os
import sys
from datetime import datetime, timezone

# ── Remonter à backend/ (3 niveaux au-dessus de Script/Fix/) ──
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "topkit")

client = AsyncIOMotorClient(MONGO_URL)
db     = client[DB_NAME]

ENTITY_CONFIG = {
    "team":   {"collection": "teams",   "id_field": "team_id",   "name_field": "name"},
    "league": {"collection": "leagues", "id_field": "league_id", "name_field": "name"},
    "brand":  {"collection": "brands",  "id_field": "brand_id",  "name_field": "name"},
    "player": {"collection": "players", "id_field": "player_id", "name_field": "full_name"},
}

async def fix():
    total_fixed = 0

    for entity_type, config in ENTITY_CONFIG.items():
        docs = await db[config["collection"]].find(
            {"status": "for_review", "submission_id": {"$exists": False}},
            {"_id": 0}
        ).to_list(500)

        if not docs:
            print(f"[{entity_type}] ✅ Rien à patcher")
            continue

        for doc in docs:
            entity_id     = doc.get(config["id_field"])
            name          = doc.get(config["name_field"], "?")
            submission_id = f"sub_{uuid.uuid4().hex[:12]}"
            now           = datetime.now(timezone.utc).isoformat()

            # 1) Patcher l'entité avec submission_id
            await db[config["collection"]].update_one(
                {config["id_field"]: entity_id},
                {"$set": {"submission_id": submission_id}}
            )

            # 2) Créer la submission liée
            await db.submissions.insert_one({
                "submission_id":   submission_id,
                "submission_type": entity_type,
                "data": {
                    "mode":               "create",
                    config["name_field"]: name,
                    "entity_id":          entity_id,
                },
                "status":     "pending",
                "votes_up":   0,
                "votes_down": 0,
                "voters":     [],
                "created_at": now,
            })

            print(f"[{entity_type}] ✅ {name} → {submission_id}")
            total_fixed += 1

    print(f"\n🎉 {total_fixed} entité(s) patchée(s).")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix())
