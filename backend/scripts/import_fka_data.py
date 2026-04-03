"""
import_fka_data.py
------------------
1. Lit le CSV  backend/Db_topkit-Data.csv
2. Importe master_kits, versions, teams, brands, leagues, sponsors dans MongoDB
3. (Optionnel) Télécharge les images vers le NAS Freebox
   → Lance avec : DOWNLOAD_IMAGES=true python3 scripts/import_fka_data.py
   → Chemin NAS  : /mnt/freebox/topkit-media/photos  (montage VM)
   → Nommage     : master_{kit_type}_{kit_id}.jpg
"""

import asyncio, csv, os, re, hashlib, pathlib, sys
from datetime import datetime, timezone

try:
    from dotenv import load_dotenv
    for env_path in [
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        os.path.expanduser('~/tp_emergent/backend/.env'),
    ]:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"[OK] .env chargé depuis : {env_path}")
            break
except ImportError:
    pass

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("❌ motor non installé. Lance : pip install motor")
    sys.exit(1)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️  httpx non installé — téléchargement images désactivé. Installe avec: pip install httpx")

# ── Config ──────────────────────────────────────────────────────────────────
MONGO_URL = os.environ.get("MONGO_URL") or os.environ.get("MONGODB_URI")
if not MONGO_URL:
    print("❌ Variable MONGO_URL introuvable.")
    print("   Lance : export MONGO_URL='mongodb+srv://...' puis relance.")
    sys.exit(1)

DB_NAME = os.environ.get("DB_NAME", "topkit")

# CSV à la racine du dossier backend (un niveau au-dessus de scripts/)
CSV_PATH = os.environ.get(
    "CSV_PATH",
    os.path.join(os.path.dirname(__file__), "..", "Db_topkit-Data.csv")
)

# Répertoire NAS Freebox monté sur la VM
FREEBOX_IMG_DIR = os.environ.get("FREEBOX_IMG_DIR", "/mnt/freebox/topkit-media/photos")
DOWNLOAD_IMAGES = os.environ.get("DOWNLOAD_IMAGES", "false").lower() == "true"


# ── Helpers ──────────────────────────────────────────────────────────────────
def slugify(t: str) -> str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s_-]+", "-", t).strip("-")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(prefix: str, *parts: str) -> str:
    """ID déterministe basé sur le contenu — même entrée → même ID."""
    key = "|".join(p.strip().lower() for p in parts)
    h = hashlib.md5(key.encode()).hexdigest()[:12]
    return f"{prefix}_{h}"


def normalize_kit_type(raw: str) -> str:
    mapping = {
        "GK 1": "GK1", "GK 2": "GK2", "GK 3": "GK3",
        "Home": "Home", "Away": "Away", "Third": "Third", "Fourth": "Fourth",
    }
    t = raw.strip()
    return mapping.get(t, re.sub(r'\s+', '', t))


def fix_img_url(raw: str) -> str:
    """Tente de reconstruire une URL valide si elle est malformée."""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    # Cas fréquent : 'https' collé sans ://
    m = re.match(r'https(cdn\.footballkitarchive\.com)(\d{4})(\d{2})(\d{2})([\w]+\.jpg)', raw)
    if m:
        return f"https://{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}/{m.group(5)}"
    m2 = re.match(r'https(cdn\.footballkitarchive\.com)(\d{6})([\w]+\.jpg)', raw)
    if m2:
        year, month = m2.group(2)[:4], m2.group(2)[4:6]
        return f"https://{m2.group(1)}/{year}/{month}/{m2.group(3)}"
    m3 = re.match(r'https(www\.footballkitarchive\.com)(.*)', raw)
    if m3:
        return f"https://{m3.group(1)}{m3.group(2)}"
    return raw


async def download_image(kit_id: str, kit_type: str, img_url: str, dest_dir: str) -> str:
    """Télécharge une image et la nomme master_{kit_type}_{kit_id}.jpg"""
    if not img_url or not HTTPX_AVAILABLE:
        return ""
    norm_type = normalize_kit_type(kit_type)
    filename = f"master_{norm_type}_{kit_id}.jpg"
    dest = pathlib.Path(dest_dir) / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return str(dest)
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            r = await client.get(img_url)
            r.raise_for_status()
            dest.write_bytes(r.content)
        return str(dest)
    except Exception as e:
        print(f"  ⚠️  Erreur téléchargement {filename}: {e}")
        return ""


# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    print(f"[OK] Connexion à MongoDB : {MONGO_URL[:40]}...")
    db = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=10000)[DB_NAME]

    try:
        await db.command("ping")
        print("[OK] MongoDB connecté !")
    except Exception as e:
        print(f"❌ Impossible de se connecter : {e}")
        sys.exit(1)

    csv_path = os.path.abspath(CSV_PATH)
    if not os.path.exists(csv_path):
        print(f"❌ CSV introuvable : {csv_path}")
        print("   Vérifie que Db_topkit-Data.csv est bien dans backend/")
        sys.exit(1)

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    print(f"📄 {len(rows)} lignes lues depuis {os.path.basename(csv_path)}")

    # Dédoublonnage sur team+season+type
    seen, unique = {}, []
    for r in rows:
        key = f"{slugify(r['team'])}|{slugify(r['season'])}|{slugify(r['type'])}"
        if key not in seen:
            seen[key] = True
            unique.append(r)
    print(f"🎽 {len(unique)} master_kits uniques")

    # Vider les collections
    for col in ["master_kits", "versions", "teams", "brands", "leagues", "sponsors"]:
        await db[col].delete_many({})
    print("🗑️  Collections vidées.")

    # ── Entités référentielles ────────────────────────────────────────────────
    teams_map, brands_map, leagues_map, sponsors_map = {}, {}, {}, {}
    t_docs, b_docs, l_docs, s_docs = [], [], [], []

    for r in unique:
        for name, mapping, docs, id_prefix in [
            (r["team"],             teams_map,    t_docs, "team"),
            (r["brand"],            brands_map,   b_docs, "brand"),
            (r["league"],           leagues_map,  l_docs, "league"),
            (r.get("sponsor", ""), sponsors_map, s_docs, "sponsor"),
        ]:
            name = name.strip()
            if name and slugify(name) not in mapping:
                eid = stable_id(id_prefix, name)
                mapping[slugify(name)] = eid
                docs.append({
                    f"{id_prefix}_id": eid,
                    "name": name,
                    "slug": slugify(name),
                    "status": "approved",
                    "created_at": now_iso(),
                })

    if t_docs: await db.teams.insert_many(t_docs)
    if b_docs: await db.brands.insert_many(b_docs)
    if l_docs: await db.leagues.insert_many(l_docs)
    if s_docs: await db.sponsors.insert_many(s_docs)
    print(f"✅ {len(t_docs)} teams | {len(b_docs)} brands | {len(l_docs)} leagues | {len(s_docs)} sponsors")

    # ── master_kits + versions ────────────────────────────────────────────────
    kit_docs, ver_docs = [], []
    download_tasks = []   # (kit_id, kit_type, img_url)

    for r in unique:
        kit_type     = normalize_kit_type(r["type"].strip())
        kid          = stable_id("kit", r["team"], r["season"], r["type"])
        vid_auth     = stable_id("ver", r["team"], r["season"], r["type"], "authentic")
        vid_rep      = stable_id("ver", r["team"], r["season"], r["type"], "replica")
        img          = fix_img_url(r.get("img_url", "").strip())
        src_url      = fix_img_url(r.get("source_url", "").strip())
        sponsor_name = r.get("sponsor", "").strip()

        # Année pour la logique replica (>=2000)
        season_raw = str(r.get("season", "") or "1900")
        try:
            season_year = int(season_raw[:4])
        except ValueError:
            season_year = 1900

        kit_docs.append({
            "kit_id":        kid,
            "club":          r["team"].strip(),
            "team_id":       teams_map.get(slugify(r["team"]), ""),
            "season":        r["season"].strip(),
            "kit_type":      kit_type,
            "design":        r.get("design", "").strip(),
            "colors":        r.get("colors", "").strip(),
            "brand":         r["brand"].strip(),
            "brand_id":      brands_map.get(slugify(r["brand"]), ""),
            "sponsor":       sponsor_name,
            "sponsor_id":    sponsors_map.get(slugify(sponsor_name), "") if sponsor_name else "",
            "league":        r["league"].strip(),
            "league_id":     leagues_map.get(slugify(r["league"]), ""),
            "front_photo":   "",        # sera mis à jour après téléchargement
            "img_url":       img,       # URL source conservée pour référence
            "source_url":    src_url,
            "gender":        "Male",
            "avg_rating":    0.0,
            "review_count":  0,
            "version_count": 1 + (1 if season_year >= 2000 else 0),
            "created_at":    now_iso(),
        })

        # Version authentique (toujours)
        ver_docs.append({
            "version_id":   vid_auth,
            "kit_id":       kid,
            "version_type": "authentic",
            "competition":  "National Championship",
            "front_photo":  "",
            "back_photo":   "",
            "avg_rating":   0.0,
            "review_count": 0,
            "created_at":   now_iso(),
        })

        # Version replica uniquement à partir de 2000
        if season_year >= 2000:
            ver_docs.append({
                "version_id":   vid_rep,
                "kit_id":       kid,
                "version_type": "replica",
                "competition":  "National Championship",
                "front_photo":  "",
                "back_photo":   "",
                "avg_rating":   0.0,
                "review_count": 0,
                "created_at":   now_iso(),
            })

        if DOWNLOAD_IMAGES and img:
            download_tasks.append((kid, kit_type, img))

    # Insertion par batch de 500
    for i in range(0, len(kit_docs), 500):
        await db.master_kits.insert_many(kit_docs[i:i+500])
    for i in range(0, len(ver_docs), 500):
        await db.versions.insert_many(ver_docs[i:i+500])

    total_kits = await db.master_kits.count_documents({})
    total_vers = await db.versions.count_documents({})
    print(f"\n✅ {total_kits} master_kits | {total_vers} versions insérés en DB")

    # ── Téléchargement images → Freebox NAS ──────────────────────────────────
    if download_tasks:
        print(f"\n📸 Téléchargement de {len(download_tasks)} images vers {FREEBOX_IMG_DIR}...")
        ok, fail = 0, 0
        for kid, kit_type, img_url in download_tasks:
            local_path = await download_image(kid, kit_type, img_url, FREEBOX_IMG_DIR)
            if local_path:
                norm_type = normalize_kit_type(kit_type)
                filename = f"master_{norm_type}_{kid}.jpg"
                # Met à jour front_photo dans master_kits ET versions
                await db.master_kits.update_one(
                    {"kit_id": kid},
                    {"$set": {"front_photo": filename}}
                )
                await db.versions.update_many(
                    {"kit_id": kid},
                    {"$set": {"front_photo": filename}}
                )
                ok += 1
            else:
                fail += 1
            if (ok + fail) % 100 == 0:
                print(f"  ... {ok + fail}/{len(download_tasks)} traités ({ok} OK, {fail} erreurs)")

        print(f"\n✅ {ok} images téléchargées, {fail} erreurs")
        print(f"   Nommage : master_{{type}}_{{kit_id}}.jpg (ex: master_Home_kit_abc123.jpg)")
    else:
        if not DOWNLOAD_IMAGES:
            print("\nℹ️  Téléchargement images désactivé.")
            print("   Pour télécharger : DOWNLOAD_IMAGES=true python3 scripts/import_fka_data.py")

    # ── Résumé final ──────────────────────────────────────────────────────────
    print(f"\n--- Résumé ---")
    print(f"  Master kits : {total_kits}")
    print(f"  Versions    : {total_vers}")
    if DOWNLOAD_IMAGES:
        print(f"  Images DL   : {ok} OK / {fail} erreurs")
        print(f"  Chemin NAS  : {FREEBOX_IMG_DIR}")


asyncio.run(main())
