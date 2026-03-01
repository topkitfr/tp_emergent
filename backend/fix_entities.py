import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def fix_collection(collection_name, id_field):
    docs = await db[collection_name].find({}, {"_id": 1}).to_list(10000)
    updated = 0
    for doc in docs:
        full = await db[collection_name].find_one({"_id": doc["_id"]})
        updates = {}

        # Fix id → team_id / league_id / brand_id
        if not full.get(id_field) and full.get("id"):
            updates[id_field] = full["id"]

        # Fix created_at datetime → string
        ca = full.get("created_at")
        if isinstance(ca, datetime):
            updates["created_at"] = ca.isoformat()

        # Fix updated_at datetime → string
        ua = full.get("updated_at")
        if isinstance(ua, datetime):
            updates["updated_at"] = ua.isoformat()

        if updates:
            await db[collection_name].update_one({"_id": doc["_id"]}, {"$set": updates})
            updated += 1

    print(f"✅ {collection_name} : {updated} docs mis à jour sur {len(docs)}")

async def main():
    await fix_collection("teams",   "team_id")
    await fix_collection("leagues", "league_id")
    await fix_collection("brands",  "brand_id")
    await fix_collection("players", "player_id")
    client.close()

asyncio.run(main())
