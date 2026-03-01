import asyncio
import csv
import os
import re
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

def normalize_season(season: str) -> str:
    if not season:
        return season
    s = re.sub(r'\s*\(carry-over\)', '', season, flags=re.IGNORECASE).strip()
    m = re.match(r'(\d{2,4})[\-/](\d{2,4})$', s)
    if m:
        y1_str = m.group(1)
        if len(y1_str) == 2:
            n1 = int(y1_str)
            full_y1 = 1900 + n1 if n1 >= 85 else 2000 + n1
        else:
            full_y1 = int(y1_str)
        return f"{full_y1}/{full_y1 + 1}"
    return s

def normalize_gender(gender: str) -> str:
    g = (gender or "").strip().upper()
    mapping = {
        "MAN": "MEN", "MALE": "MEN",
        "WOMAN": "WOMEN", "FEMALE": "WOMEN",
        "KID": "YOUTH", "KIDS": "YOUTH", "CHILD": "YOUTH",
        "": "MEN"
    }
    if g in ("MEN", "WOMEN", "YOUTH", "UNISEX"):
        return g
    return mapping.get(g, "MEN")

async def get_or_create(collection, slug_field, slug_value, doc):
    existing = await db[collection].find_one({slug_field: slug_value})
    if existing:
        return existing.get('team_id') or existing.get('brand_id') or existing.get('league_id') or existing.get('id', '')
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
            season_raw  = row.get('season', '').strip()
            kit_type    = row.get('type', '').strip()
            design      = row.get('design', '').strip()
            colors      = row.get('colors', '').strip()
            brand_name  = row.get('brand', '').strip()
            sponsor     = row.get('sponsor', '').strip()
            league_name = row.get('league', '').strip()
            gender_raw  = row.get('gender', '').strip()
            release_raw = row.get('release_date', '').strip()
            img_url     = row.get('img_url', '').strip()
            source_url  = row.get('source_url', '').strip()

            if not team_name or not season_raw:
                skipped_kits += 1
                continue

            season = normalize_season(season_raw)
            gender = normalize_gender(gender_raw)

            # --- TEAM ---
            team_slug = make_slug(team_name)
            team_id = await get_or_create('teams', 'slug', team_slug, {
                'id':              new_id('team'),
                'team_id':         new_id('team'),
                'name':            team_name,
                'slug':            team_slug,
                'crest_url':       '',
                'country':         '',
                'city':            '',
                'founded':         None,
                'primary_color':   '',
                'secondary_color': '',
                'aka':             [],
                'kit_count':       0,
                'status':          'approved',
                'created_at':      datetime.now(timezone.utc).isoformat(),
                'updated_at':      datetime.now(timezone.utc).isoformat()
            })

            # --- BRAND ---
            brand_id = ''
            if brand_name:
                brand_slug = make_slug(brand_name)
                brand_id = await get_or_create('brands', 'slug', brand_slug, {
                    'id':         new_id('brand'),
                    'brand_id':   new_id('brand'),
                    'name':       brand_name,
                    'slug':       brand_slug,
                    'logo_url':   '',
                    'country':    '',
                    'founded':    None,
                    'kit_count':  0,
                    'status':     'approved',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                })

            # --- LEAGUE ---
            league_id = ''
            if league_name:
                league_slug = make_slug(league_name)
                league_id = await get_or_create('leagues', 'slug', league_slug, {
                    'id':                new_id('league'),
                    'league_id':         new_id('league'),
                    'name':              league_name,
                    'slug':              league_slug,
                    'country_or_region': '',
                    'level':             'domestic',
                    'organizer':         '',
                    'logo_url':          '',
                    'kit_count':         0,
                    'status':            'approved',
                    'created_at':        datetime.now(timezone.utc).isoformat(),
                    'updated_at':        datetime.now(timezone.utc).isoformat()
                })

            # --- MASTER KIT ---
            kit_slug = make_slug(f"{team_name}-{season}-{kit_type}")
            if await db['master_kits'].find_one({'slug': kit_slug}):
                skipped_kits += 1
                continue

            kit_id = new_id('kit')
            await db['master_kits'].insert_one({
                'kit_id':       kit_id,
                'id':           kit_id,
                'slug':         kit_slug,
                'team_id':      team_id,
                'brand_id':     brand_id,
                'league_id':    league_id,
                'club':         team_name,
                'brand':        brand_name,
                'league':       league_name,
                'season':       season,
                'kit_type':     kit_type,
                'type':         kit_type,
                'design':       design,
                'colors':       colors,
                'sponsor':      sponsor,
                'gender':       gender,
                'front_photo':  img_url,
                'img_url':      img_url,
                'source_url':   source_url,
                'release_date': release_raw,
                'status':       'approved',
                'avg_rating':   0.0,
                'created_at':   datetime.now(timezone.utc).isoformat(),
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
