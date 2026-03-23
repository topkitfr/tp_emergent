import asyncio, csv, os, re, uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://topkit:jUFgdXvN8baQslp4@cluster0.hhhrkiz.mongodb.net/topkit?retryWrites=true&w=majority"
CSV_PATH  = os.path.join(os.path.dirname(__file__), "FKA-Scrap-Data.csv")

def slugify(t):
    t = t.lower().strip()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s_-]+", "-", t).strip("-")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

async def main():
    db = AsyncIOMotorClient(MONGO_URL)["topkit"]

    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    print(f"📄 {len(rows)} lignes lues")

    # Dédoublonnage sur team+season+type
    seen, unique = {}, []
    for r in rows:
        key = f"{slugify(r['team'])}|{slugify(r['season'])}|{slugify(r['type'])}"
        if key not in seen:
            seen[key] = True
            unique.append(r)
    print(f"🎽 {len(unique)} master_kits uniques")

    # Vider les collections
    for col in ["master_kits","versions","teams","brands","leagues"]:
        await db[col].delete_many({})

    # Entités
    teams_map, brands_map, leagues_map = {}, {}, {}
    t_docs, b_docs, l_docs = [], [], []
    for r in unique:
        for name, mapping, docs, id_prefix, id_field in [
            (r["team"],   teams_map,   t_docs, "team",   "team_id"),
            (r["brand"],  brands_map,  b_docs, "brand",  "brand_id"),
            (r["league"], leagues_map, l_docs, "league", "league_id"),
        ]:
            name = name.strip()
            if name and slugify(name) not in mapping:
                eid = f"{id_prefix}_{uuid.uuid4().hex[:12]}"
                mapping[slugify(name)] = eid
                docs.append({id_field: eid, "name": name, "slug": slugify(name), "status": "approved", "created_at": now_iso()})

    if t_docs: await db.teams.insert_many(t_docs)
    if b_docs: await db.brands.insert_many(b_docs)
    if l_docs: await db.leagues.insert_many(l_docs)
    print(f"✅ {len(t_docs)} teams, {len(b_docs)} brands, {len(l_docs)} leagues")

    # master_kits + versions
    kit_docs, ver_docs = [], []
    for r in unique:
        kid = f"kit_{uuid.uuid4().hex[:12]}"
        img = r.get("img_url","").strip()
        kit_docs.append({
            "kit_id": kid, "club": r["team"].strip(), "team_id": teams_map.get(slugify(r["team"]),""),
            "season": r["season"].strip(), "kit_type": r["type"].strip(), "design": r.get("design","").strip(),
            "colors": r.get("colors","").strip(), "brand": r["brand"].strip(), "brand_id": brands_map.get(slugify(r["brand"]),""),
            "sponsor": r.get("sponsor","").strip(), "league": r["league"].strip(), "league_id": leagues_map.get(slugify(r["league"]),""),
            "front_photo": img, "img_url": img, "source_url": r.get("source_url","").strip(),
            "gender": "Male", "avg_rating": 0.0, "review_count": 0, "version_count": 1, "created_at": now_iso(),
        })
        ver_docs.append({
            "version_id": f"ver_{uuid.uuid4().hex[:12]}", "kit_id": kid,
            "competition": "National Championship", "model": "Replica",
            "sku_code": "", "ean_code": "", "front_photo": img, "back_photo": "",
            "avg_rating": 0.0, "review_count": 0, "created_at": now_iso(),
        })

    for i in range(0, len(kit_docs), 500):
        await db.master_kits.insert_many(kit_docs[i:i+500])
    for i in range(0, len(ver_docs), 500):
        await db.versions.insert_many(ver_docs[i:i+500])

    print(f"✅ {await db.master_kits.count_documents({})} master_kits, {await db.versions.count_documents({})} versions importés")

asyncio.run(main())