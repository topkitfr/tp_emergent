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
    collections_to_clear = [
        "teams", "leagues", "brands", "players",
        "master_kits", "versions",
        "submissions", "reports",
        "collections", "reviews", "wishlist"
    ]
    for col in collections_to_clear:
        result = await db[col].delete_many({})
        print(f"✅ {col} : {result.deleted_count} supprimé(s)")

    now = datetime.now(timezone.utc).isoformat()

    # IDs au bon format : entity_{hex12}
    team_id   = f"team_{uuid.uuid4().hex[:12]}"
    brand_id  = f"brand_{uuid.uuid4().hex[:12]}"
    league_id = f"league_{uuid.uuid4().hex[:12]}"
    player_id = f"player_{uuid.uuid4().hex[:12]}"
    kit_id    = f"kit_{uuid.uuid4().hex[:12]}"

    # Team — champs exacts du modèle TeamOut
    await db.teams.insert_one({
        "team_id": team_id,
        "name": "FC Test",
        "slug": "fc-test",
        "country": "France",
        "city": "Paris",
        "founded": 2024,
        "primary_color": "#E30613",
        "secondary_color": "#FFFFFF",
        "crest_url": "",
        "aka": [],
        "created_at": now,
        "updated_at": now,
    })
    print(f"\n🏟️  Team    → {team_id}")

    # Brand — champs exacts du modèle BrandOut
    await db.brands.insert_one({
        "brand_id": brand_id,
        "name": "Nike",
        "slug": "nike",
        "country": "USA",
        "founded": 1964,
        "logo_url": "",
        "created_at": now,
        "updated_at": now,
    })
    print(f"👟  Brand   → {brand_id}")

    # League — champs exacts du modèle LeagueOut (country_or_region, pas country !)
    await db.leagues.insert_one({
        "league_id": league_id,
        "name": "Ligue 1",
        "slug": "ligue-1",
        "country_or_region": "France",
        "level": "domestic",
        "organizer": "LFP",
        "logo_url": "",
        "created_at": now,
        "updated_at": now,
    })
    print(f"🏆  League  → {league_id}")

    # Player — champs exacts du modèle PlayerOut (full_name, pas name !)
    await db.players.insert_one({
        "player_id": player_id,
        "full_name": "Test Player",
        "slug": "test-player",
        "nationality": "French",
        "birth_year": 1990,
        "positions": ["Attaquant"],
        "preferred_number": 10,
        "photo_url": "",
        "created_at": now,
        "updated_at": now,
    })
    print(f"👤  Player  → {player_id}")

    # Master Kit
    await db.master_kits.insert_one({
        "kit_id": kit_id,
        "club": "FC Test",
        "season": "2025/2026",
        "kit_type": "Home",
        "brand": "Nike",
        "league": "Ligue 1",
        "front_photo": "https://cdn.footballkitarchive.com/2021/05/04/TzkvR8j6OKtxDhR.jpg",
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
    print(f"🎽  Kit     → {kit_id}")
    print(f"\n🚀 Reset terminé !")

    client.close()

asyncio.run(reset())
