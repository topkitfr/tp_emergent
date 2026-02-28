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

    now = datetime.now(timezone.utc).isoformat()

    # 2. Créer les références
    team_id   = str(uuid.uuid4())
    brand_id  = str(uuid.uuid4())
    league_id = str(uuid.uuid4())
    player_id = str(uuid.uuid4())

    await db.teams.insert_one({
        "team_id": team_id,
        "name": "FC Test",
        "country": "France",
        "city": "Paris",
        "logo": "",
        "created_at": now,
        "status": "approved"
    })
    print(f"\n🏟️  Team créée    → {team_id}")

    await db.brands.insert_one({
        "brand_id": brand_id,
        "name": "Nike",
        "country": "USA",
        "logo": "",
        "created_at": now,
        "status": "approved"
    })
    print(f"👟  Brand créée   → {brand_id}")

    await db.leagues.insert_one({
        "league_id": league_id,
        "name": "Ligue 1",
        "country": "France",
        "logo": "",
        "created_at": now,
        "status": "approved"
    })
    print(f"🏆  League créée  → {league_id}")

    await db.players.insert_one({
        "player_id": player_id,
        "name": "Test Player",
        "nationality": "French",
        "position": "Attaquant",
        "created_at": now,
        "status": "approved"
    })
    print(f"👤  Player créé   → {player_id}")

    # 3. Créer le maillot de test lié aux références
    kit_id = str(uuid.uuid4())

    await db.master_kits.insert_one({
        "kit_id": kit_id,
        "club": "FC Test",
        "season": "2025/2026",
        "kit_type": "Home",
        "brand": "Nike",
        "league": "Ligue 1",
        "front_photo": "",
        "design": "",
        "sponsor": "",
        "gender": "M",
        "team_id": team_id,
        "brand_id": brand_id,
        "league_id": league_id,
        "created_by": "reset_script",
        "created_at": now,
        "version_count": 0,
        "avg_rating": 0.0,
    })
    print(f"\n🎽  Maillot créé  → {kit_id}")
    print(f"    Club   : FC Test")
    print(f"    Saison : 2025/2026")
    print(f"    Type   : Home / Nike / Ligue 1")
    print(f"    team_id   : {team_id}")
    print(f"    brand_id  : {brand_id}")
    print(f"    league_id : {league_id}")

    client.close()
    print("\n🚀 Reset terminé !")

asyncio.run(reset())
