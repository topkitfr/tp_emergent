"""
Seed des confédérations — Sprint 1

Insère UEFA, FIFA, CAF, CONMEBOL, AFC, CONCACAF, OFC dans la collection `leagues`
avec entity_type = "confederation".

Usage :
    python -m backend.scripts.seed_confederations          # dry-run (affiche ce qui serait créé)
    python -m backend.scripts.seed_confederations --apply  # applique en base

Idempotent : si le slug existe déjà, la confédération est ignorée (pas de doublon).
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone

import motor.motor_asyncio
from dotenv import load_dotenv
import os
import re
import unicodedata

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME    = os.getenv("DB_NAME", "topkit")

CONFEDERATIONS = [
    {
        "name": "FIFA",
        "organizer": "FIFA",
        "scope": "international",
        "region": "world",
        "country_or_region": "World",
        "logo_url": "https://media.api-sports.io/football/leagues/1.png",
    },
    {
        "name": "UEFA",
        "organizer": "UEFA",
        "scope": "international",
        "region": "europe",
        "country_or_region": "Europe",
        "logo_url": "https://media.api-sports.io/football/leagues/3.png",
    },
    {
        "name": "CAF",
        "organizer": "CAF",
        "scope": "international",
        "region": "africa",
        "country_or_region": "Africa",
        "logo_url": "",
    },
    {
        "name": "CONMEBOL",
        "organizer": "CONMEBOL",
        "scope": "international",
        "region": "south_america",
        "country_or_region": "South America",
        "logo_url": "",
    },
    {
        "name": "AFC",
        "organizer": "AFC",
        "scope": "international",
        "region": "asia",
        "country_or_region": "Asia",
        "logo_url": "",
    },
    {
        "name": "CONCACAF",
        "organizer": "CONCACAF",
        "scope": "international",
        "region": "north_america",
        "country_or_region": "North America & Caribbean",
        "logo_url": "",
    },
    {
        "name": "OFC",
        "organizer": "OFC",
        "scope": "international",
        "region": "oceania",
        "country_or_region": "Oceania",
        "logo_url": "",
    },
]


def _slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


async def seed(apply: bool = False):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db     = client[DB_NAME]
    now    = datetime.now(timezone.utc).isoformat()

    created = []
    skipped = []

    for conf in CONFEDERATIONS:
        slug = _slugify(conf["name"])
        existing = await db.leagues.find_one({"slug": slug}, {"_id": 0, "league_id": 1})
        if existing:
            skipped.append(conf["name"])
            continue

        doc = {
            **conf,
            "league_id":  f"league_{uuid.uuid4().hex[:12]}",
            "slug":       slug,
            "status":     "approved",
            "entity_type": "confederation",
            "level":      "international",
            "kit_count":  0,
            "created_at": now,
            "updated_at": now,
        }

        if apply:
            await db.leagues.insert_one(doc)
            print(f"  ✅ Créé : {conf['name']} ({doc['league_id']})")
        else:
            print(f"  [DRY-RUN] À créer : {conf['name']} (slug={slug})")

        created.append(conf["name"])

    print(f"\n{'Appliqué' if apply else 'Dry-run'} — {len(created)} à créer, {len(skipped)} déjà présents.")
    if skipped:
        print(f"  Ignorés : {', '.join(skipped)}")

    client.close()


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    asyncio.run(seed(apply=apply))
