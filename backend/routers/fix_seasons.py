import asyncio
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

def normalize_season(season: str) -> str:
    if not season:
        return season
    m = re.match(r'(\d{2,4})[/\-](\d{2,4})', season)
    if m:
        y1 = m.group(1)[-2:]
        y2 = m.group(2)[-2:]
        suffix = season[m.end():].strip()
        return f"{y1}-{y2}{(' ' + suffix) if suffix else ''}"
    return season

async def main():
    kits = await db.master_kits.find({}, {"_id": 1, "season": 1}).to_list(10000)
    updated = 0
    for kit in kits:
        new_season = normalize_season(kit.get("season", ""))
        if new_season != kit.get("season", ""):
            await db.master_kits.update_one({"_id": kit["_id"]}, {"$set": {"season": new_season}})
            updated += 1
    print(f"✅ {updated} saisons corrigées sur {len(kits)}")
    client.close()

asyncio.run(main())
