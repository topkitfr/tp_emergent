import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def main():
    # Charger toutes les brands et leagues en mémoire
    brands = await db.brands.find({}, {"_id": 0, "brand_id": 1, "name": 1}).to_list(1000)
    leagues = await db.leagues.find({}, {"_id": 0, "league_id": 1, "name": 1}).to_list(1000)
    teams = await db.teams.find({}, {"_id": 0, "team_id": 1, "name": 1}).to_list(10000)

    brand_map  = {b["brand_id"]: b["name"] for b in brands if b.get("brand_id")}
    league_map = {l["league_id"]: l["name"] for l in leagues if l.get("league_id")}
    team_map   = {t["team_id"]: t["name"] for t in teams if t.get("team_id")}

    print(f"Brands chargées : {len(brand_map)}")
    print(f"Leagues chargées : {len(league_map)}")
    print(f"Teams chargées : {len(team_map)}")

    kits = await db.master_kits.find({}, {"_id": 1, "brand_id": 1, "league_id": 1, "team_id": 1, "brand": 1, "league": 1, "club": 1}).to_list(10000)
    updated = 0

    for kit in kits:
        updates = {}

        # Résoudre brand
        brand_id = kit.get("brand_id", "")
        if brand_id and brand_id in brand_map:
            updates["brand"] = brand_map[brand_id]

        # Résoudre league
        league_id = kit.get("league_id", "")
        if league_id and league_id in league_map:
            updates["league"] = league_map[league_id]

        # Résoudre club depuis team_id si encore vide
        team_id = kit.get("team_id", "")
        club = kit.get("club", "")
        if team_id and team_id in team_map and (not club or club.startswith("team_")):
            updates["club"] = team_map[team_id]

        if updates:
            await db.master_kits.update_one({"_id": kit["_id"]}, {"$set": updates})
            updated += 1

    print(f"✅ {updated} kits mis à jour sur {len(kits)}")
    client.close()

asyncio.run(main())
