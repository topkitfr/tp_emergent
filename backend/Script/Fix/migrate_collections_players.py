# backend/script/fix/migrate_collections_players.py
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
    print("=== Migration collections → flocking_player_id vers players.player_id ===")

    # Charger tous les joueurs
    players = await db.players.find(
        {},
        {"_id": 0, "player_id": 1, "full_name": 1}
    ).to_list(5000)

    # Index par nom complet (exact)
    player_by_name = {
        p["full_name"]: p["player_id"]
        for p in players
        if p.get("full_name") and p.get("player_id")
    }

    print(f"Loaded {len(player_by_name)} players with full_name → player_id")

    # Récupérer toutes les collections où flocking_player_id est un nom texte
    collections = await db.collections.find({}).to_list(50000)
    updated = 0
    skipped = 0

    for c in collections:
        flocking_player_id = c.get("flocking_player_id")
        if not flocking_player_id:
            continue

        # Si c'est déjà un id de type "player_xxx", on skip
        if isinstance(flocking_player_id, str) and flocking_player_id.startswith("player_"):
            skipped += 1
            continue

        # On suppose ici que flocking_player_id contient un nom (ex "Lionel Messi")
        player_id = player_by_name.get(flocking_player_id)
        if not player_id:
            print(f"[WARN] No player match for flocking_player_id='{flocking_player_id}' in collection {c.get('collection_id')}")
            continue

        await db.collections.update_one(
            {"_id": c["_id"]},
            {"$set": {"flocking_player_id": player_id}}
        )
        updated += 1
        print(f"Updated collection {c.get('collection_id')} → flocking_player_id={player_id} (was '{flocking_player_id}')")

    print(f"Migration terminée. Collections mises à jour : {updated}, déjà OK (id) : {skipped}")


if __name__ == "__main__":
    asyncio.run(migrate())
