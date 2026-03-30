"""
Script de seed pour initialiser la collection beta_codes dans MongoDB.
Usage : python -m backend.scripts.seed_beta_codes
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = "topkit"
COLLECTION = "beta_codes"

BETA_CODES = [
    "BETAKIT",
    "TKTESTER",
    "MEXES",
    "KITBETA26",
]


async def seed():
    if not MONGO_URL:
        raise ValueError("Variable d'environnement MONGODB_URL manquante.")

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    col = db[COLLECTION]

    # Supprime les anciens codes pour éviter les doublons
    deleted = await col.delete_many({})
    print(f"🗑️  {deleted.deleted_count} ancien(s) code(s) supprimé(s).")

    docs = [{"code": c, "active": True} for c in BETA_CODES]
    result = await col.insert_many(docs)
    print(f"✅ {len(result.inserted_ids)} code(s) bêta insérés dans '{DB_NAME}.{COLLECTION}' :")
    for c in BETA_CODES:
        print(f"   - {c}")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
