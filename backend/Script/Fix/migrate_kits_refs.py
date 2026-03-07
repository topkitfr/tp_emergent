# backend/script/fix/migrate_kits_refs.py
import asyncio
import os
import sys

# Ajouter backend/ au PYTHONPATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from database import db  # noqa: E402


async def migrate():
    print("=== Migration master_kits → ajout team_id / brand_id / league_id ===")

    teams = await db.teams.find({}, {"_id": 0, "team_id": 1, "name": 1}).to_list(2000)
    brands = await db.brands.find({}, {"_id": 0, "brand_id": 1, "name": 1}).to_list(2000)
    leagues = await db.leagues.find({}, {"_id": 0, "league_id": 1, "name": 1}).to_list(2000)

    team_by_name = {t["name"]: t["team_id"] for t in teams if t.get("name") and t.get("team_id")}
    brand_by_name = {b["name"]: b["brand_id"] for b in brands if b.get("name") and b.get("brand_id")}
    league_by_name = {l["name"]: l["league_id"] for l in leagues if l.get("name") and l.get("league_id")}

    print(f"Loaded {len(team_by_name)} teams, {len(brand_by_name)} brands, {len(league_by_name)} leagues")

    kits = await db.master_kits.find({}).to_list(10000)
    updated_count = 0

    for kit in kits:
        updates = {}

        club = kit.get("club")
        brand = kit.get("brand")
        league = kit.get("league")

        if club and not kit.get("team_id"):
            team_id = team_by_name.get(club)
            if team_id:
                updates["team_id"] = team_id

        if brand and not kit.get("brand_id"):
            brand_id = brand_by_name.get(brand)
            if brand_id:
                updates["brand_id"] = brand_id

        if league and not kit.get("league_id"):
            league_id = league_by_name.get(league)
            if league_id:
                updates["league_id"] = league_id

        if updates:
            await db.master_kits.update_one(
                {"_id": kit["_id"]},
                {"$set": updates}
            )
            updated_count += 1
            print(f"Updated kit {kit.get('kit_id')} with {updates}")

    print(f"Migration terminée. Kits mis à jour : {updated_count}")


if __name__ == "__main__":
    asyncio.run(migrate())
