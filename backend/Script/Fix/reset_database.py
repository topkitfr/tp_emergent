# backend/Script/Fix/reset_database.py
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# ─────────────────────────────────────────────
# Charger le .env depuis backend/ (3 niveaux au-dessus de ce fichier)
# Structure : backend/Script/Fix/reset_database.py → backend/.env
# ─────────────────────────────────────────────
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"✅ .env chargé depuis : {ENV_PATH}")
else:
    print(f"⚠️  Aucun .env trouvé à {ENV_PATH} — variables d'environnement système utilisées")

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

if not MONGO_URL or not DB_NAME:
    raise RuntimeError(
        "❌ MONGO_URL ou DB_NAME manquant. "
        "Vérifie ton fichier backend/.env"
    )

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ─────────────────────────────────────────────
# Collections métier à vider
# (la collection `users` est intentionnellement EXCLUE)
# ─────────────────────────────────────────────
COLLECTIONS = [
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

async def reset():
    print(f"\n{'='*50}")
    print(f"  RESET DATABASE → {DB_NAME}")
    print(f"{'='*50}")
    print("⚠️  Cette action est IRRÉVERSIBLE.")
    print("   La collection `users` est préservée.\n")

    confirm = input("Tape 'RESET' pour confirmer : ").strip()
    if confirm != "RESET":
        print("❌ Annulé.")
        client.close()
        return

    print()
    total = 0
    for col in COLLECTIONS:
        try:
            result = await db[col].delete_many({})
            count = result.deleted_count
            total += count
            status = f"🗑️  {col:<20} → {count} document(s) supprimé(s)"
        except Exception as e:
            status = f"⚠️  {col:<20} → ERREUR : {e}"
        print(status)

    print(f"\n{'='*50}")
    print(f"✅ Reset terminé — {total} documents supprimés au total.")
    print(f"   Base : {DB_NAME} | Collections vidées : {len(COLLECTIONS)}")
    print(f"{'='*50}\n")
    client.close()

if __name__ == "__main__":
    asyncio.run(reset())