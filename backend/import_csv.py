import asyncio
import csv
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

def make_slug(text):
    return text.lower().strip().replace(' ', '-').replace('/', '-').replace('.', '').replace("'", '')

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

async def get_or_create(collection, slug_field, slug_value, doc):
    existing = await db[collection].find_one({slug_field: slug_value})
    if existing:
        return existing.get('id', str(existing['_id']))
    await db[collection].insert_one(doc)
    return doc['id']

async def import_csv(filepath='Topkit_Data.csv'):
    print(f"Lecture de {filepath}...")
    with open(filepath, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} kits a importer\n")

    created_kits = 0
    skipped_kits = 0
    errors = 0

    for i, row in enumerate(rows, 1):
        try:
            team_name   = row.get('team', '').strip()
            season      = row.get('season', '').strip()
            kit_type    = row.get('type', '').strip()
            design      = row.get('design', '').strip()
            colors      = row.get('colors', '').strip()
            brand_name  = row.get('brand', '').strip()
            sponsor     = row.get('sponsor', '').strip()
            league_name = row.get('league', '').strip()
            release_raw = row.get('release_date', '').strip()
            img_url     = row.get('img_url', '').strip()
            source_url  = row.get('source_url', '').strip()

            if not team_name or not season:
                skipped_kits += 1
                continue

            # --- TEAM ---
            team_slug = make_slug(team_name)
            team_id = await get_or_create('teams', 'slug', team_slug, {
                'id': new_id('team'), 'name': team_name, 'slug': team_slug,
                'crest_url': '', 'country': '', 'founded': None,
                'status': 'approved', 'created_at': datetime.now(timezone.utc)
            })

            # --- BRAND ---
            brand_id = ''
            if brand_name:
                brand_slug = make_slug(brand_name)
                brand_id = await get_or_create('brands', 'slug', brand_slug, {
                    'id': new_id('brand'), 'name': brand_name, 'slug': brand_slug,
                    'logo_url': '', 'status': 'approved',
                    'created_at': datetime.now(timezone.utc)
                })

            # --- LEAGUE ---
            league_id = ''
            if league_name:
                league_slug = make_slug(league_name)
                league_id = await get_or_create('leagues', 'slug', league_slug, {
                    'id': new_id('league'), 'name': league_name, 'slug': league_slug,
                    'country_or_region': '', 'logo_url': '', 'status': 'approved',
                    'created_at': datetime.now(timezone.utc)
                })

            # --- MASTER KIT (évite les doublons) ---
            kit_slug = make_slug(f"{team_name}-{season}-{kit_type}")
            if await db['master_kits'].find_one({'slug': kit_slug}):
                skipped_kits += 1
                continue

            await db['master_kits'].insert_one({
                'id':           new_id('kit'),
                'slug':         kit_slug,
                'team_id':      team_id,
                'brand_id':     brand_id,
                'league_id':    league_id,
                'season':       season,
                'type':         kit_type,
                'design':       design,
                'colors':       colors,
                'sponsor':      sponsor,
                'img_url':      img_url,
                'source_url':   source_url,
                'release_date': release_raw,
                'status':       'approved',
                'avg_rating':   0.0,
                'created_at':   datetime.now(timezone.utc)
            })
            created_kits += 1

            if i % 50 == 0:
                print(f"  {i}/{len(rows)} traites...")

        except Exception as e:
            if errors < 5:
                print(f"  ERREUR ligne {i} ({row.get('team','')}) -> {type(e).__name__}: {e}")
            errors += 1

    print(f"\nImport termine !")
    print(f"  {created_kits} kits crees")
    print(f"  {skipped_kits} skippes")
    print(f"  {errors} erreurs")
    client.close()

asyncio.run(import_csv('Topkit_Data.csv'))
