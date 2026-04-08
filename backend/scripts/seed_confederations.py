#!/usr/bin/env python3
"""
Seed des 7 confédérations footballistiques dans la collection `leagues`.
Utilisation :
    python backend/scripts/seed_confederations.py [--apply]

Par défaut : dry-run (affiche ce qui serait créé, n'écrit rien).
Passer --apply pour insérer réellement en base.
"""
import sys
import os
from datetime import datetime, timezone

# ── Ajout du répertoire backend au path ──────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import db

DRY_RUN = "--apply" not in sys.argv

CONFEDERATIONS = [
    {
        "name": "FIFA",
        "slug": "fifa",
        "entity_type": "confederation",
        "scope": "international",
        "region": "world",
        "organizer": "FIFA",
        "country_or_region": "World",
        "logo_url": "https://media.api-sports.io/football/leagues/1.png",
        "apifootball_league_id": None,
        "level": "international",
        "status": "approved",
    },
    {
        "name": "UEFA",
        "slug": "uefa",
        "entity_type": "confederation",
        "scope": "international",
        "region": "europe",
        "organizer": "UEFA",
        "country_or_region": "Europe",
        "logo_url": "https://media.api-sports.io/football/leagues/2.png",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
    {
        "name": "CONMEBOL",
        "slug": "conmebol",
        "entity_type": "confederation",
        "scope": "international",
        "region": "south_america",
        "organizer": "CONMEBOL",
        "country_or_region": "South America",
        "logo_url": "",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
    {
        "name": "CAF",
        "slug": "caf",
        "entity_type": "confederation",
        "scope": "international",
        "region": "africa",
        "organizer": "CAF",
        "country_or_region": "Africa",
        "logo_url": "",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
    {
        "name": "AFC",
        "slug": "afc",
        "entity_type": "confederation",
        "scope": "international",
        "region": "asia",
        "organizer": "AFC",
        "country_or_region": "Asia",
        "logo_url": "",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
    {
        "name": "CONCACAF",
        "slug": "concacaf",
        "entity_type": "confederation",
        "scope": "international",
        "region": "north_central_america",
        "organizer": "CONCACAF",
        "country_or_region": "North & Central America",
        "logo_url": "",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
    {
        "name": "OFC",
        "slug": "ofc",
        "entity_type": "confederation",
        "scope": "international",
        "region": "oceania",
        "organizer": "OFC",
        "country_or_region": "Oceania",
        "logo_url": "",
        "apifootball_league_id": None,
        "level": "continental",
        "status": "approved",
    },
]


def run():
    leagues_col = db["leagues"]
    now = datetime.now(timezone.utc).isoformat()
    created = 0
    skipped = 0

    for conf in CONFEDERATIONS:
        existing = leagues_col.find_one({"slug": conf["slug"]})
        if existing:
            print(f"[SKIP]   {conf['name']} déjà en base (id={existing.get('_id')})")
            skipped += 1
            continue

        doc = {
            **conf,
            "kit_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        if DRY_RUN:
            print(f"[DRY-RUN] Créerait : {conf['name']} ({conf['region']})")
        else:
            result = leagues_col.insert_one(doc)
            print(f"[OK]     {conf['name']} inséré → _id={result.inserted_id}")
        created += 1

    print()
    if DRY_RUN:
        print(f"Dry-run terminé : {created} à créer, {skipped} déjà présents.")
        print("Relancer avec --apply pour insérer.")
    else:
        print(f"Seed terminé : {created} insérés, {skipped} ignorés.")


if __name__ == "__main__":
    run()
