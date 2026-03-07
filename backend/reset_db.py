# backend/reset_db.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os, uuid
from datetime import datetime, timezone

# Charge .env à la racine backend (même dossier que reset_db.py)
load_dotenv(Path(__file__).parent / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]


async def reset_and_seed():
    # 1) VIDER TOUTES LES COLLECTIONS MÉTIER
    collections_to_clear = [
        "master_kits",
        "versions",
        "teams",
        "leagues",
        "brands",
        "players",
        "reviews",
        "collections",
        "submissions",
        "wishlists",
        "sponsors",
        "reports",
        "votes",
        "estimations",
        "uploads",
        "profiles",
    ]

    print("=== RESET DATABASE (collections métier) ===")
    for col in collections_to_clear:
        result = await db[col].delete_many({})
        print(f"🗑️  {col}: {result.deleted_count} supprimé(s)")

    now = datetime.now(timezone.utc).isoformat()

    # 2) RECRÉER UN JEU DE DONNÉES DE TEST PROPRE

    team_id   = f"team_{uuid.uuid4().hex[:12]}"
    brand_id  = f"brand_{uuid.uuid4().hex[:12]}"
    league_id = f"league_{uuid.uuid4().hex[:12]}"
    player_id = f"player_{uuid.uuid4().hex[:12]}"
    kit_id    = f"kit_{uuid.uuid4().hex[:12]}"
    version_id = f"ver_{uuid.uuid4().hex[:12]}"

    # Team — TeamOut
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
        "kit_count": 0,
    })
    print(f"\n🏟️  Team    → {team_id}")

    # Brand — BrandOut
    await db.brands.insert_one({
        "brand_id": brand_id,
        "name": "Nike",
        "slug": "nike",
        "country": "USA",
        "founded": 1964,
        "logo_url": "",
        "created_at": now,
        "updated_at": now,
        "kit_count": 0,
    })
    print(f"👟  Brand   → {brand_id}")

    # League — LeagueOut
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
        "kit_count": 0,
    })
    print(f"🏆  League  → {league_id}")

    # Player — PlayerOut
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
        "kit_count": 0,
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
        "version_count": 1,
        "avg_rating": 0.0,
        "review_count": 0,
    })
    print(f"🎽  Kit     → {kit_id}")

    # Version de test liée au kit
    await db.versions.insert_one({
        "version_id": version_id,
        "kit_id": kit_id,
        "competition": "Ligue 1",
        "model": "Replica",
        "sku_code": "",
        "ean_code": "",
        "front_photo": "https://cdn.footballkitarchive.com/2021/05/04/TzkvR8j6OKtxDhR.jpg",
        "back_photo": "",
        "main_player_id": player_id,
        "created_by": "reset_script",
        "created_at": now,
        "avg_rating": 0.0,
        "review_count": 0,
    })
    print(f"🔢 Version → {version_id}")

    print("\n🚀 Reset + seed terminé !")
    client.close()


asyncio.run(reset_and_seed())
