import asyncio
import sys
import os
from datetime import datetime

# Permet d'importer les modules backend depuis ce script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient

# ── Config ──────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB",  "topkit")

# ── Codes a seeder ──────────────────────────────────────────────────────────
CODES = [
    {"code": "BETAKIT",   "note": "code general beta",   "max_uses": 100},
    {"code": "TKTESTER",  "note": "testeurs internes",    "max_uses": 20},
    {"code": "MEXES",     "note": "batch amis proches",   "max_uses": None},
    {"code": "KITBETA26", "note": "batch beta 2026",      "max_uses": 50},
]

# ── Seed ────────────────────────────────────────────────────────────────────
async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]

    # Index unique sur le champ code
    await db.beta_codes.create_index("code", unique=True)

    for c in CODES:
        existing = await db.beta_codes.find_one({"code": c["code"]})
        if not existing:
            await db.beta_codes.insert_one({
                **c,
                "active": True,
                "uses": 0,
                "created_at": datetime.utcnow(),
            })
            print(f"[OK] Code cree : {c['code']}")
        else:
            print(f"[--] Deja present : {c['code']}")

    client.close()
    print("\nSeed termine.")

if __name__ == "__main__":
    asyncio.run(seed())
