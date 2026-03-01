import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent.parent.parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

async def create_replica_versions():
    kits = await db['master_kits'].find({}, {'_id': 0}).to_list(10000)
    print(f"{len(kits)} kits trouves\n")

    created = 0
    skipped = 0

    for kit in kits:
        kit_id = kit.get('kit_id')
        if not kit_id:
            skipped += 1
            continue

        # Vérifie si une version Replica existe déjà
        existing = await db['versions'].find_one({'kit_id': kit_id, 'model': 'Replica'})
        if existing:
            skipped += 1
            continue

        version_id = new_id('ver')
        await db['versions'].insert_one({
            'version_id':   version_id,
            'kit_id':       kit_id,
            'competition':  'National Championship',
            'model':        'Replica',
            'sku_code':     '',
            'ean_code':     '',
            'front_photo':  kit.get('front_photo') or kit.get('img_url', ''),
            'back_photo':   '',
            'avg_rating':   0.0,
            'review_count': 0,
            'created_by':   'import',
            'created_at':   datetime.now(timezone.utc).isoformat()
        })
        created += 1

        if created % 50 == 0:
            print(f"  {created} versions creees...")

    print(f"\nTermine !")
    print(f"  {created} versions creees")
    print(f"  {skipped} skippes (deja existantes ou kit_id manquant)")
    client.close()

asyncio.run(create_replica_versions())
