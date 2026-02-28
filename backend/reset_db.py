import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os, uuid
from datetime import datetime, timezone

load_dotenv(Path(__file__).parent / '.env')

client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def reset():
    # 1. Vider toutes les collections
    collections_to_clear = [
        "teams", "leagues", "brands", "players",
        "master_kits", "versions",
        "submissions", "reports",
        "collections", "reviews", "wishlist"
    ]
    for col in collections_to_clear:
        result = await db[col].delete_many({})
        print(f"✅ {col} : {result.deleted_count} document(s) supprimé(s)")

    # 2. Créer un maillot de test propre
    now = datetime.now(timezone.utc).isoformat()
    kit_id = str(uuid.uuid4())

    test_kit = {
        "kit_id": kit_id,
        "club": "FC Test",
        "season": "2025/2026",
        "kit_type": "Home",
        "brand": "Nike",
        "front_photo": "https://cdn.footballkitarchive.com/2021/05/04/TzkvR8j6OKtxDhR.jpg",
        "league": "",
        "design": "",
        "sponsor": "",
        "gender": "M",
        "team_id": "",
        "league_id": "",
        "brand_id": "",
        "created_by": "reset_script",
        "created_at": now,
        "version_count": 0,
        "avg_rating": 0.0,
    }

    await db.master_kits.insert_one(test_kit)
    print(f"\n🎽 Maillot de test créé !")
    print(f"   → kit_id : {kit_id}")
    print(f"   → Club   : FC Test")
    print(f"   → Saison : 2025/2026")
    print(f"   → Type   : Home / Nike")

    client.close()

asyncio.run(reset())
