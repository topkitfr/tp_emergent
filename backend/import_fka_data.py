import asyncio, csv, os, re, hashlib, pathlib
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️  httpx non installé — téléchargement images désactivé. Installe avec: pip install httpx")

MONGO_URL = "mongodb+srv://topkit:jUFgdXvN8baQslp4@cluster0.hhhrkiz.mongodb.net/topkit?retryWrites=true&w=majority"
CSV_PATH  = os.path.join(os.path.dirname(__file__), "Db_topkit-Data.csv")

# Répertoire de destination images sur la Freebox (via montage VM)
FREEBOX_IMG_DIR = os.environ.get("FREEBOX_IMG_DIR", "/mnt/freebox/images/kits")
DOWNLOAD_IMAGES = os.environ.get("DOWNLOAD_IMAGES", "false").lower() == "true"


def slugify(t):
    t = t.lower().strip()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s_-]+", "-", t).strip("-")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def stable_id(prefix: str, *parts: str) -> str:
    """Génère un ID déterministe basé sur le contenu.
    Même entrée → même ID à chaque import."""
    key = "|".join(p.strip().lower() for p in parts)
    h = hashlib.md5(key.encode()).hexdigest()[:12]
    return f"{prefix}_{h}"


def normalize_kit_type(raw: str) -> str:
    t = raw.strip()
    mapping = {
        "GK 1": "GK1",
        "GK 2": "GK2",
        "GK 3": "GK3",
        "Home": "Home",
        "Away": "Away",
        "Third": "Third",
        "Fourth": "Fourth",
    }
    if t in mapping:
        return mapping[t]
    return re.sub(r'\s+', '', t)


def fix_img_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    m = re.match(
        r'https(cdn\.footballkitarchive\.com)(\d{4})(\d{2})(\d{2})([\w]+\.jpg)',
        raw
    )
    if m:
        return f"https://{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}/{m.group(5)}"
    m2 = re.match(
        r'https(cdn\.footballkitarchive\.com)(\d{6})([\w]+\.jpg)',
        raw
    )
    if m2:
        year = m2.group(2)[:4]
        month = m2.group(2)[4:6]
        return f"https://{m2.group(1)}/{year}/{month}/{m2.group(3)}"
    m3 = re.match(r'https(www\.footballkitarchive\.com)(.*)', raw)
    if m3:
        return f"https://{m3.group(1)}{m3.group(2)}"
    return raw


async def download_image(kit_id: str, kit_type: str, img_url: str, dest_dir: str) -> str:
    if not img_url or not HTTPX_AVAILABLE:
        return ""
    norm_type = normalize_kit_type(kit_type)
    filename = f"master_{norm_type}_{kit_id}.jpg"
    dest = pathlib.Path(dest_dir) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return str(dest)
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(img_url)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return str(dest)
    except Exception as e:
        print(f"⚠️  Erreur téléchargement {filename}: {e}")
        return ""


async def main():
    db = AsyncIOMotorClient(MONGO_URL)["topkit"]

    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV introuvable: {CSV_PATH}")
        return

    rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8")))
    print(f"📄 {len(rows)} lignes lues depuis {os.path.basename(CSV_PATH)}")

    # Dédoublonnage sur team+season+type
    seen, unique = {}, []
    for r in rows:
        key = f"{slugify(r['team'])}|{slugify(r['season'])}|{slugify(r['type'])}"
        if key not in seen:
            seen[key] = True
            unique.append(r)
    print(f"🎽 {len(unique)} master_kits uniques (GK1 et GK2 comptent séparément)")

    # Vider les collections
    for col in ["master_kits", "versions", "teams", "brands", "leagues", "sponsors"]:
        await db[col].delete_many({})

    # Entités (teams, brands, leagues, sponsors)
    # IDs déterministes basés sur le nom → stables entre imports
    teams_map, brands_map, leagues_map, sponsors_map = {}, {}, {}, {}
    t_docs, b_docs, l_docs, s_docs = [], [], [], []

    for r in unique:
        for name, mapping, docs, id_prefix, id_field in [
            (r["team"],    teams_map,    t_docs, "team",    "team_id"),
            (r["brand"],   brands_map,   b_docs, "brand",   "brand_id"),
            (r["league"],  leagues_map,  l_docs, "league",  "league_id"),
            (r.get("sponsor", ""), sponsors_map, s_docs, "sponsor", "sponsor_id"),
        ]:
            name = name.strip()
            if name and slugify(name) not in mapping:
                eid = stable_id(id_prefix, name)
                mapping[slugify(name)] = eid
                docs.append({
                    id_field: eid, "name": name, "slug": slugify(name),
                    "status": "approved", "created_at": now_iso()
                })

    if t_docs: await db.teams.insert_many(t_docs)
    if b_docs: await db.brands.insert_many(b_docs)
    if l_docs: await db.leagues.insert_many(l_docs)
    if s_docs: await db.sponsors.insert_many(s_docs)
    print(f"✅ {len(t_docs)} teams, {len(b_docs)} brands, {len(l_docs)} leagues, {len(s_docs)} sponsors")

    # master_kits + versions
    # kit_id stable : hash(team + season + type)
    # version_id stable : hash(team + season + type + "version")
    kit_docs, ver_docs = [], []
    download_tasks = []

    for r in unique:
        kit_type     = normalize_kit_type(r["type"].strip())
        kid          = stable_id("kit",  r["team"], r["season"], r["type"])
        vid          = stable_id("ver",  r["team"], r["season"], r["type"], "version")
        raw_img      = r.get("img_url", "").strip()
        raw_src      = r.get("source_url", "").strip()
        img          = fix_img_url(raw_img)
        src_url      = fix_img_url(raw_src)
        sponsor_name = r.get("sponsor", "").strip()

        kit_docs.append({
            "kit_id":       kid,
            "club":         r["team"].strip(),
            "team_id":      teams_map.get(slugify(r["team"]), ""),
            "season":       r["season"].strip(),
            "kit_type":     kit_type,
            "design":       r.get("design", "").strip(),
            "colors":       r.get("colors", "").strip(),
            "brand":        r["brand"].strip(),
            "brand_id":     brands_map.get(slugify(r["brand"]), ""),
            "sponsor":      sponsor_name,
            "sponsor_id":   sponsors_map.get(slugify(sponsor_name), "") if sponsor_name else "",
            "league":       r["league"].strip(),
            "league_id":    leagues_map.get(slugify(r["league"]), ""),
            "front_photo":  img,
            "img_url":      img,
            "source_url":   src_url,
            "gender":       "Male",
            "avg_rating":   0.0,
            "review_count": 0,
            "version_count": 1,
            "created_at":   now_iso(),
        })
        ver_docs.append({
            "version_id":   vid,
            "kit_id":       kid,
            "competition":  "National Championship",
            "model":        "Replica",
            "sku_code":     "",
            "ean_code":     "",
            "front_photo":  img,
            "back_photo":   "",
            "avg_rating":   0.0,
            "review_count": 0,
            "created_at":   now_iso(),
        })
        if DOWNLOAD_IMAGES and img:
            download_tasks.append((kid, kit_type, img))

    for i in range(0, len(kit_docs), 500):
        await db.master_kits.insert_many(kit_docs[i:i+500])
    for i in range(0, len(ver_docs), 500):
        await db.versions.insert_many(ver_docs[i:i+500])

    total_kits = await db.master_kits.count_documents({})
    total_vers = await db.versions.count_documents({})
    print(f"✅ {total_kits} master_kits, {total_vers} versions importés en DB")

    # Téléchargement images vers Freebox (optionnel)
    if download_tasks:
        print(f"\n📸 Téléchargement de {len(download_tasks)} images vers {FREEBOX_IMG_DIR}...")
        ok, fail = 0, 0
        for kid, kit_type, img_url in download_tasks:
            path = await download_image(kid, kit_type, img_url, FREEBOX_IMG_DIR)
            if path:
                ok += 1
            else:
                fail += 1
        print(f"✅ {ok} images téléchargées, {fail} erreurs")
        print(f"   Naming: master_{{type}}_{{kit_id}}.jpg (ex: master_GK1_kit_abc123.jpg)")
    else:
        if not DOWNLOAD_IMAGES:
            print("\nℹ️  Téléchargement images désactivé. Lance avec DOWNLOAD_IMAGES=true pour copier sur la Freebox.")


asyncio.run(main())
