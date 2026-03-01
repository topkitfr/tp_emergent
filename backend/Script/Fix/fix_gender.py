import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

def normalize_gender(gender: str) -> str:
    g = (gender or "").strip().upper()
    mapping = {
        "MAN":    "MEN",
        "MALE":   "MEN",
        "WOMAN":  "WOMEN",
        "FEMALE": "WOMEN",
        "KID":    "YOUTH",
        "KIDS":   "YOUTH",
        "CHILD":  "YOUTH",
        "":       "MEN",
    }
    if g in ("MEN", "WOMEN", "YOUTH", "UNISEX"):
        return g
    return mapping.get(g, "MEN")

async def main():
    kits = await db.master_kits.find({}, {"_id": 1, "gender": 1}).to_list(10000)
    updated = 0
    for kit in kits:
        new_gender = normalize_gender(kit.get("gender", ""))
        if new_gender != kit.get("gender", ""):
            await db.master_kits.update_one({"_id": kit["_id"]}, {"$set": {"gender": new_gender}})
            updated += 1
    print(f"✅ {updated} genders corrigés sur {len(kits)}")
    client.close()

asyncio.run(main())
