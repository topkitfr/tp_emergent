# backend/reset_DB.py
import asyncio
import argparse
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # → backend/
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
    print(f"✅ .env chargé : {ENV_PATH}")
else:
    print(f"⚠️  Pas de .env trouvé à {ENV_PATH} — variables système utilisées")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME   = os.environ.get("DB_NAME")

if not MONGO_URL or not DB_NAME:
    print("❌ MONGO_URL ou DB_NAME manquant dans le .env")
    sys.exit(1)

from motor.motor_asyncio import AsyncIOMotorClient

SOFT_COLLECTIONS = [
    "submissions",
    "votes",
    "reports",
    "notifications",
]

FULL_COLLECTIONS = [
    "master_kits",
    "versions",
    "teams",
    "leagues",
    "brands",
    "players",
    "sponsors",
    "reviews",
    "collections",
    "submissions",
    "wishlists",
    "reports",
    "votes",
    "estimations",
    "notifications",
]

async def drop_collections(db, collections: list) -> int:
    total = 0
    for col in collections:
        try:
            result = await db[col].delete_many({})
            n = result.deleted_count
            total += n
            print(f"  🗑️  {col:<25} {n} doc(s) supprimé(s)")
        except Exception as e:
            print(f"  ⚠️  {col:<25} ERREUR : {e}")
    return total

async def main(mode: str):
    client = AsyncIOMotorClient(MONGO_URL)
    db     = client[DB_NAME]

    print(f"\n{'='*55}")
    print(f"  CLEAN DB — mode={mode.upper()} | base={DB_NAME}")
    print(f"{'='*55}\n")

    if mode == "soft":
        print("Collections ciblées :", ", ".join(SOFT_COLLECTIONS))
        print("→ Kits, entités, collections et users sont PRÉSERVÉS.\n")
        confirm = input("Tape 'SOFT' pour confirmer : ").strip()
        if confirm != "SOFT":
            print("❌ Annulé."); client.close(); return
        total = await drop_collections(db, SOFT_COLLECTIONS)

    elif mode in ("full", "reset"):
        print("Collections ciblées :", ", ".join(FULL_COLLECTIONS))
        print("→ Seule la collection `users` est PRÉSERVÉE.\n")
        confirm = input("Tape 'FULL' pour confirmer : ").strip()
        if confirm != "FULL":
            print("❌ Annulé."); client.close(); return
        total = await drop_collections(db, FULL_COLLECTIONS)

        if mode == "reset":
            print("\n🔧 Recréation des index...")
            await db["master_kits"].create_index("kit_id",   unique=True)
            await db["versions"].create_index("version_id",  unique=True)
            await db["teams"].create_index("team_id",        unique=True)
            await db["brands"].create_index("brand_id",      unique=True)
            await db["leagues"].create_index("league_id",    unique=True)
            await db["players"].create_index("player_id",    unique=True)
            await db["sponsors"].create_index("sponsor_id",  unique=True)
            print("  ✅ Index recréés")

    print(f"\n{'='*55}")
    print(f"✅ Terminé — {total} documents supprimés")
    print(f"   Base : {DB_NAME}")
    print(f"{'='*55}\n")
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nettoyage base Topkit")
    parser.add_argument(
        "--mode",
        choices=["soft", "full", "reset"],
        default="soft",
        help="soft = contributions only | full = tout sauf users | reset = full + index"
    )
    args = parser.parse_args()
    asyncio.run(main(args.mode))