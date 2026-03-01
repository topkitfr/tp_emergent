import asyncio
import re
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

def name_from_slug(slug: str) -> str:
    if not slug:
        return ""
    match = re.search(r'-\d{2}-\d{2}', slug)
    team_part = slug[:match.start()] if match else slug
    return team_part.replace('-', ' ').title()

async def fix():
    kits = await db.master_kits.find({}, {"_id": 1, "slug": 1, "club": 1, "brand": 1, "league": 1, "created_at": 1, "type": 1, "kit_type": 1}).to_list(10000)
    updated = 0
    for kit in kits:
        updates = {}

        # Fix club : si c'est un ID ou ObjectId → extraire depuis slug
        club = kit.get("club", "")
        if not club or club.startswith("team_") or (len(club) > 20 and " " not in club):
            updates["club"] = name_from_slug(kit.get("slug", ""))

        # Fix brand : si c'est un ID → vider (on règlera après)
        brand = kit.get("brand", "")
        if brand and (brand.startswith("brand_") or (len(brand) > 20 and " " not in brand)):
            updates["brand"] = ""

        # Fix league : si c'est un ID → vider
        league = kit.get("league", "")
        if league and (league.startswith("league_") or (len(league) > 20 and " " not in league)):
            updates["league"] = ""

        # Fix kit_type : si manquant, copier depuis type
        if not kit.get("kit_type") and kit.get("type"):
            updates["kit_type"] = kit.get("type", "")

        # Fix created_at : si datetime → convertir en string ISO
        ca = kit.get("created_at")
        if isinstance(ca, datetime):
            updates["created_at"] = ca.isoformat()

        if updates:
            await db.master_kits.update_one({"_id": kit["_id"]}, {"$set": updates})
            updated += 1

    print(f"✅ {updated} kits mis à jour sur {len(kits)}")
    client.close()

asyncio.run(fix())
