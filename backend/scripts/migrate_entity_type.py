"""
Migration entity_type — Sprint 1

Pose entity_type = "club" sur tous les master_kits qui n'ont pas encore ce champ
(ou qui l'ont à null/vide).

Usage :
    python -m backend.scripts.migrate_entity_type          # dry-run
    python -m backend.scripts.migrate_entity_type --apply  # applique en base

Idempotent : ne touche pas les documents qui ont déjà entity_type renseigné.
"""

import asyncio
import sys
from datetime import datetime, timezone

import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME    = os.getenv("DB_NAME", "topkit")


async def migrate(apply: bool = False):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db     = client[DB_NAME]
    now    = datetime.now(timezone.utc).isoformat()

    # Cibler uniquement les docs sans entity_type ou avec valeur nulle/vide
    query = {
        "$or": [
            {"entity_type": {"$exists": False}},
            {"entity_type": None},
            {"entity_type": ""},
        ]
    }

    count = await db.master_kits.count_documents(query)
    print(f"master_kits à migrer : {count}")

    if count == 0:
        print("Rien à faire.")
        client.close()
        return

    if apply:
        result = await db.master_kits.update_many(
            query,
            {"$set": {"entity_type": "club", "updated_at": now}}
        )
        print(f"✅ {result.modified_count} documents mis à jour (entity_type = 'club').")
    else:
        print(f"[DRY-RUN] {count} documents seraient mis à jour avec entity_type = 'club'.")
        # Aperçu des 5 premiers
        samples = await db.master_kits.find(query, {"_id": 0, "kit_id": 1, "club": 1, "season": 1}).limit(5).to_list(5)
        print("  Exemples :")
        for s in samples:
            print(f"    - {s.get('club')} {s.get('season')} (kit_id={s.get('kit_id')})")

    client.close()


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    asyncio.run(migrate(apply=apply))
