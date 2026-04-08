"""Script one-shot : seed des 7 confédérations dans la collection leagues.

Usage (depuis la VM dans le container backend) :
  python -m backend.scripts.seed_confederations

Idempotent : upsert sur le champ 'name', ne crée pas de doublon.
"""

import asyncio
import uuid
import re
import unicodedata
from datetime import datetime, timezone

from ..database import db


def _slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


CONFEDERATIONS = [
    {"name": "UEFA",     "region": "europe",        "organizer": "UEFA"},
    {"name": "FIFA",     "region": "world",          "organizer": "FIFA"},
    {"name": "CAF",      "region": "africa",         "organizer": "CAF"},
    {"name": "CONMEBOL", "region": "south_america",  "organizer": "CONMEBOL"},
    {"name": "AFC",      "region": "asia",           "organizer": "AFC"},
    {"name": "CONCACAF", "region": "north_america",  "organizer": "CONCACAF"},
    {"name": "OFC",      "region": "oceania",        "organizer": "OFC"},
]


async def seed():
    now = datetime.now(timezone.utc).isoformat()
    created = 0
    skipped = 0

    for conf in CONFEDERATIONS:
        slug = _slugify(conf["name"])
        existing = await db["leagues"].find_one({"name": conf["name"]})

        if existing:
            # Met à jour les nouveaux champs si absents
            await db["leagues"].update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "entity_type": "confederation",
                    "scope": "international",
                    "region": conf["region"],
                    "organizer": conf["organizer"],
                    "updated_at": now,
                }}
            )
            print(f"  ↺  {conf['name']} — déjà en DB, champs mis à jour")
            skipped += 1
        else:
            league_id = str(uuid.uuid4())
            await db["leagues"].insert_one({
                "league_id": league_id,
                "name": conf["name"],
                "slug": slug,
                "status": "approved",
                "entity_type": "confederation",
                "scope": "international",
                "region": conf["region"],
                "organizer": conf["organizer"],
                "country_name": None,
                "country_code": None,
                "country_flag": None,
                "country_or_region": conf["region"],
                "level": "international",
                "logo_url": "",
                "apifootball_logo": "",
                "apifootball_league_id": None,
                "scoring_weight": None,
                "kit_count": 0,
                "created_at": now,
                "updated_at": now,
            })
            print(f"  ✓  {conf['name']} — créée (id: {league_id})")
            created += 1

    print(f"\nSeed terminé : {created} créées, {skipped} mises à jour.")


if __name__ == "__main__":
    asyncio.run(seed())
