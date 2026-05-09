#!/usr/bin/env python3
"""
Vague 3 — cleanup post-API-Football.

Supprime les champs résiduels apifootball_* / source-payload sur les collections
players / teams / leagues, ainsi que tsdb_id (legacy TheSportsDB).

Utilisation :
    python backend/scripts/drop_apifootball_fields.py            # dry-run
    python backend/scripts/drop_apifootball_fields.py --apply    # exécution
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import db, client  # noqa: E402

DRY_RUN = "--apply" not in sys.argv

# Mapping collection → liste de champs à $unset
FIELDS_TO_UNSET: dict[str, list[str]] = {
    "players":  ["apifootball_id", "tsdb_id"],
    "teams":    ["apifootball_team_id"],
    "leagues":  ["apifootball_league_id", "apifootball_logo", "source_payload"],
}

# Indexes à dropper (au cas où le startup hook ne tournerait pas)
INDEXES_TO_DROP: list[tuple[str, str]] = [
    ("teams",   "apifootball_team_id_1"),
    ("leagues", "apifootball_league_id_1"),
]


async def run():
    print(f"Mode : {'DRY-RUN' if DRY_RUN else 'APPLY'}")
    print()

    # 1) Comptage + $unset par collection
    for coll_name, fields in FIELDS_TO_UNSET.items():
        coll = db[coll_name]
        unset_doc = {f: "" for f in fields}
        match = {"$or": [{f: {"$exists": True}} for f in fields]}
        count = await coll.count_documents(match)
        print(f"[{coll_name}] {count} documents avec au moins un champ parmi {fields}")
        if count == 0:
            continue
        if DRY_RUN:
            print(f"  → DRY-RUN : $unset {fields} sur {count} docs")
        else:
            res = await coll.update_many(match, {"$unset": unset_doc})
            print(f"  → modified_count = {res.modified_count}")
    print()

    # 2) Drop des indexes
    for coll_name, index_name in INDEXES_TO_DROP:
        if DRY_RUN:
            print(f"[index] DRY-RUN : drop {coll_name}.{index_name}")
            continue
        try:
            await db[coll_name].drop_index(index_name)
            print(f"[index] {coll_name}.{index_name} supprimé")
        except Exception as e:
            print(f"[index] {coll_name}.{index_name} : {e}")

    print()
    if DRY_RUN:
        print("Dry-run terminé. Relancer avec --apply pour exécuter.")
    else:
        print("Cleanup terminé.")

    client.close()


if __name__ == "__main__":
    asyncio.run(run())
