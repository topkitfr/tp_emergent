import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def main():
    kits = await db.master_kits.find({}, {"_id": 1, "id": 1, "kit_id": 1}).to_list(10000)
    updated = 0
    for kit in kits:
        if not kit.get("kit_id") and kit.get("id"):
            await db.master_kits.update_one(
                {"_id": kit["_id"]},
                {"$set": {"kit_id": kit["id"]}}
            )
            updated += 1
    print(f"✅ {updated} kit_id corrigés sur {len(kits)}")
    client.close()

asyncio.run(main())
