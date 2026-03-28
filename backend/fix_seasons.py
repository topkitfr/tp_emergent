"""
fix_seasons.py
──────────────
Migration : normalise toutes les valeurs du champ `season` dans la
collection `master_kits` vers le format YYYY/YYYY.

Usage :
    # Depuis la racine du projet, avec le venv activé :
    python fix_seasons.py

    # Dry-run (affiche sans modifier) :
    python fix_seasons.py --dry-run

Variables d'environnement requises (ou fichier .env) :
    MONGODB_URL   – URI MongoDB Atlas (ex: mongodb+srv://...)
    DB_NAME       – Nom de la base (défaut: topkit)
"""

import re
import asyncio
import argparse
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(".env")

MONGODB_URL = os.getenv("MONGODB_URL", "")
DB_NAME     = os.getenv("DB_NAME", "topkit")


# ─── Même logique que utils.py ────────────────────────────────────────────────
def normalize_season(raw: str) -> str:
    if not raw:
        return raw
    raw = raw.strip()
    parts = re.split(r"[\-\./ ]+", raw)
    if len(parts) == 2:
        y1, y2 = parts
        if len(y1) == 2:
            y1 = "20" + y1
        if len(y2) == 2:
            y2 = "20" + y2
        try:
            return f"{int(y1)}/{int(y2)}"
        except ValueError:
            return raw
    elif len(parts) == 1:
        try:
            y = int(parts[0])
            return f"{y}/{y + 1}"
        except ValueError:
            return raw
    return raw


def needs_fix(season: str) -> bool:
    """Retourne True si la saison n'est pas déjà au format YYYY/YYYY."""
    if not season:
        return False
    return not re.fullmatch(r"\d{4}/\d{4}", season.strip())


# ─── Migration ────────────────────────────────────────────────────────────────
async def run(dry_run: bool):
    if not MONGODB_URL:
        print("❌  MONGODB_URL non défini. Ajoutez-le dans votre fichier .env")
        return

    client = AsyncIOMotorClient(MONGODB_URL)
    db     = client[DB_NAME]

    total      = 0
    fixed      = 0
    skipped    = 0
    errors     = []

    print(f"{'[DRY-RUN] ' if dry_run else ''}Connexion à {DB_NAME}…\n")

    cursor = db.master_kits.find({}, {"_id": 0, "kit_id": 1, "season": 1})
    async for doc in cursor:
        total += 1
        kit_id  = doc.get("kit_id", "?")
        season  = doc.get("season", "")

        if not needs_fix(season):
            skipped += 1
            continue

        new_season = normalize_season(season)

        if new_season == season:
            # normalize_season n'a rien changé (valeur non reconnue)
            errors.append(f"  ⚠️  kit_id={kit_id}  season={repr(season)}  → non reconnu, ignoré")
            skipped += 1
            continue

        print(f"  {'[DRY] ' if dry_run else ''}kit_id={kit_id}  {repr(season)} → {repr(new_season)}")

        if not dry_run:
            await db.master_kits.update_one(
                {"kit_id": kit_id},
                {"$set": {"season": new_season}}
            )

        fixed += 1

    client.close()

    print(f"\n{'─'*50}")
    print(f"Total documents scannés : {total}")
    print(f"Déjà au bon format      : {skipped}")
    print(f"{'À corriger' if dry_run else 'Corrigés'}           : {fixed}")
    if errors:
        print(f"\nValeurs non reconnues ({len(errors)}) :")
        for e in errors:
            print(e)
    print(f"{'─'*50}")
    if dry_run:
        print("\n⚠️  Mode dry-run : aucune modification effectuée.")
        print("   Relancez sans --dry-run pour appliquer les corrections.")
    else:
        print("\n✅  Migration terminée.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalise les saisons dans master_kits")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les changements sans modifier la DB")
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run))
