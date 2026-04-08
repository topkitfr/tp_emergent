"""Script one-shot : migration entity_type sur tous les master_kits existants.

Ajoute entity_type='club' sur tous les documents qui n'ont pas encore ce champ.

Usage (depuis la VM dans le container backend) :
  python -m backend.scripts.migrate_master_kits_entity_type
"""

import asyncio
from datetime import datetime, timezone

from ..database import db


async def migrate():
    now = datetime.now(timezone.utc).isoformat()

    result = await db["master_kits"].update_many(
        {"entity_type": {"$exists": False}},
        {"$set": {
            "entity_type": "club",
            "confederation_id": None,
            "color": [],
            "updated_at": now,
        }}
    )

    print(f"Migration terminée : {result.modified_count} master_kits mis à jour.")


if __name__ == "__main__":
    asyncio.run(migrate())
