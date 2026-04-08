#!/usr/bin/env python3
"""
Seed des principales ligues par confédération via API-Football.

Usage :
    python backend/scripts/seed_leagues_apifootball.py           # dry-run
    python backend/scripts/seed_leagues_apifootball.py --apply   # insert/upsert en base

Logique :
  - Liste statique des league_id API-Football les plus importants par région
  - Appel GET /leagues?id=<id> pour chaque entrée
  - Upsert en base sur apifootball_league_id (insert si absent, update si présent)
  - Après chaque insert/update : télécharge le logo via POST /api/upload/from-url
    et met à jour logo_url en base avec le chemin Freebox retourné
  - Rate limit plan gratuit : 10 req/min → sleep 7s entre chaque appel API
"""
import sys
import os
import time
from datetime import datetime, timezone

import httpx
from pymongo import MongoClient
from dotenv import load_dotenv

# ── Path + env ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGO_URL         = os.environ["MONGO_URL"]
DB_NAME           = os.environ["DB_NAME"]
API_FOOTBALL_KEY  = os.environ.get("API_FOOTBALL_KEY", "")
API_BASE          = "https://v3.football.api-sports.io"
DRY_RUN           = "--apply" not in sys.argv
API_SLEEP         = 7.0   # 7s entre chaque appel → ~8 req/min (safe sous 10/min)

# ── Backend interne pour upload médias ───────────────────────────────────────
BACKEND_URL = os.environ.get("BACKEND_INTERNAL_URL", "http://localhost:8000")
UPLOAD_FROM_URL_ENDPOINT = f"{BACKEND_URL}/api/upload/from-url"

# ── Ligues cibles ────────────────────────────────────────────────────────────
TARGET_LEAGUES = [
    # UEFA — top 5 (= CSV)
    {"id": 39,  "name": "Premier League",        "region": "england",       "scope": "domestic",      "country_name": "England",      "country_code": "GB",      "weight": 10.0},
    {"id": 140, "name": "La Liga",               "region": "spain",         "scope": "domestic",      "country_name": "Spain",        "country_code": "ES",      "weight": 10.0},
    {"id": 135, "name": "Serie A",               "region": "italy",         "scope": "domestic",      "country_name": "Italy",        "country_code": "IT",      "weight": 10.0},
    {"id": 78,  "name": "Bundesliga",            "region": "germany",       "scope": "domestic",      "country_name": "Germany",      "country_code": "DE",      "weight": 10.0},
    {"id": 61,  "name": "Ligue 1",               "region": "france",        "scope": "domestic",      "country_name": "France",       "country_code": "FR",      "weight": 10.0},
    # UEFA — autres majeures
    {"id": 88,  "name": "Eredivisie",            "region": "netherlands",   "scope": "domestic",      "country_name": "Netherlands",  "country_code": "NL",      "weight": 7.0},
    {"id": 94,  "name": "Primeira Liga",         "region": "portugal",      "scope": "domestic",      "country_name": "Portugal",     "country_code": "PT",      "weight": 7.0},
    {"id": 144, "name": "Pro League",            "region": "belgium",       "scope": "domestic",      "country_name": "Belgium",      "country_code": "BE",      "weight": 6.0},
    {"id": 179, "name": "Scottish Premiership",  "region": "scotland",      "scope": "domestic",      "country_name": "Scotland",     "country_code": "GB-SCT",  "weight": 5.0},
    {"id": 203, "name": "Süper Lig",             "region": "turkey",        "scope": "domestic",      "country_name": "Turkey",       "country_code": "TR",      "weight": 6.0},
    # UEFA — coupes
    {"id": 2,   "name": "UEFA Champions League", "region": "europe",        "scope": "international", "country_name": None,           "country_code": None,      "weight": 10.0},
    {"id": 3,   "name": "UEFA Europa League",    "region": "europe",        "scope": "international", "country_name": None,           "country_code": None,      "weight": 8.0},
    {"id": 848, "name": "UEFA Conference League","region": "europe",       "scope": "international", "country_name": None,           "country_code": None,      "weight": 6.0},
    # CONMEBOL
    {"id": 71,  "name": "Brasileirão Série A",   "region": "brazil",        "scope": "domestic",      "country_name": "Brazil",       "country_code": "BR",      "weight": 9.0},
    {"id": 128, "name": "Liga Profesional",      "region": "argentina",     "scope": "domestic",      "country_name": "Argentina",    "country_code": "AR",      "weight": 8.0},
    {"id": 13,  "name": "Copa Libertadores",     "region": "south_america", "scope": "international", "country_name": None,           "country_code": None,      "weight": 9.0},
    # CONCACAF
    {"id": 253, "name": "MLS",                   "region": "usa",           "scope": "domestic",      "country_name": "USA",          "country_code": "US",      "weight": 7.0},
    {"id": 262, "name": "Liga MX",               "region": "mexico",        "scope": "domestic",      "country_name": "Mexico",       "country_code": "MX",      "weight": 7.0},
    # CAF
    {"id": 233, "name": "Premier Soccer League", "region": "south_africa",  "scope": "domestic",      "country_name": "South Africa", "country_code": "ZA",      "weight": 5.0},
    {"id": 12,  "name": "CAF Champions League",  "region": "africa",        "scope": "international", "country_name": None,           "country_code": None,      "weight": 7.0},
    # AFC
    {"id": 307, "name": "Saudi Pro League",      "region": "saudi_arabia",  "scope": "domestic",      "country_name": "Saudi Arabia", "country_code": "SA",      "weight": 7.0},
    {"id": 98,  "name": "J1 League",             "region": "japan",         "scope": "domestic",      "country_name": "Japan",        "country_code": "JP",      "weight": 6.0},
    {"id": 169, "name": "A-League",              "region": "australia",     "scope": "domestic",      "country_name": "Australia",    "country_code": "AU",      "weight": 5.0},
    # FIFA
    {"id": 1,   "name": "World Cup",             "region": "world",         "scope": "international", "country_name": None,           "country_code": None,      "weight": 10.0},
    {"id": 5,   "name": "UEFA Euro",             "region": "europe",        "scope": "international", "country_name": None,           "country_code": None,      "weight": 9.0},
    {"id": 9,   "name": "Copa America",          "region": "south_america", "scope": "international", "country_name": None,           "country_code": None,      "weight": 9.0},
    {"id": 6,   "name": "Africa Cup of Nations", "region": "africa",        "scope": "international", "country_name": None,           "country_code": None,      "weight": 8.0},
]

HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}


def slugify(name: str) -> str:
    import re
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")


def fetch_league(league_id: int) -> dict | None:
    try:
        resp = httpx.get(
            f"{API_BASE}/leagues",
            headers=HEADERS,
            params={"id": league_id},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        items = data.get("response", [])
        return items[0] if items else None
    except Exception as e:
        print(f"  [ERR] API-Football erreur pour id={league_id} : {e}")
        return None


def store_logo_on_freebox(image_url: str, api_id: int) -> str | None:
    """
    Appelle POST /api/upload/from-url pour télécharger l'image externe
    et la stocker sur la Freebox.
    Retourne le chemin relatif /api/images/leagues/logos/{id}.ext
    ou None en cas d'échec.
    """
    if not image_url:
        return None
    try:
        resp = httpx.post(
            UPLOAD_FROM_URL_ENDPOINT,
            params={
                "image_url": image_url,
                "folder": "league",
                "entity_id": str(api_id),
            },
            timeout=30.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            freebox_path = data.get("url")  # ex: /api/images/leagues/logos/39.png
            print(f"  [MEDIA] Logo stocké sur Freebox → {freebox_path}")
            return freebox_path
        else:
            print(f"  [WARN] Upload logo échoué (status {resp.status_code}) : {resp.text}")
            return None
    except Exception as e:
        print(f"  [WARN] Erreur upload logo pour id={api_id} : {e}")
        return None


def build_doc(target: dict, api_data: dict | None, now: str) -> dict:
    league_info  = (api_data or {}).get("league", {})
    country_info = (api_data or {}).get("country", {})
    return {
        "league_id":             f"league_{target['id']}",
        "slug":                  slugify(target["name"]),
        "name":                  league_info.get("name") or target["name"],
        "entity_type":           "league",
        "scope":                 target["scope"],
        "region":                target["region"],
        "country_name":          target.get("country_name") or country_info.get("name"),
        "country_code":          target.get("country_code") or country_info.get("code"),
        "country_flag":          country_info.get("flag") or "",
        "country_or_region":     target.get("country_name") or target["region"],
        "level":                 "domestic" if target["scope"] == "domestic" else "international",
        "organizer":             "",
        # logo_url sera remplacé après upload Freebox
        "logo_url":              league_info.get("logo") or "",
        "apifootball_league_id": target["id"],
        "apifootball_logo":      league_info.get("logo") or "",
        "scoring_weight":        target["weight"],
        "source_payload":        api_data,
        "kit_count":             0,
        "status":                "approved",
        "created_at":            now,
        "updated_at":            now,
    }


def run():
    if not API_FOOTBALL_KEY:
        print("❌ API_FOOTBALL_KEY manquante dans .env")
        sys.exit(1)

    client = MongoClient(MONGO_URL)
    db     = client[DB_NAME]
    col    = db["leagues"]
    now    = datetime.now(timezone.utc).isoformat()
    inserted = updated = errors = logo_ok = logo_fail = 0

    print(f"{'='*60}")
    print(f"  SEED LEAGUES — {'DRY-RUN' if DRY_RUN else 'APPLY'} | {len(TARGET_LEAGUES)} ligues cibles")
    if not DRY_RUN:
        print(f"  Backend upload : {UPLOAD_FROM_URL_ENDPOINT}")
        print(f"  Rate limit : 1 appel toutes les {API_SLEEP}s (~8 req/min)")
    print(f"{'='*60}\n")

    for i, target in enumerate(TARGET_LEAGUES):
        league_id = target["id"]
        name      = target["name"]
        existing  = col.find_one({"apifootball_league_id": league_id})

        # ── UPDATE ────────────────────────────────────────────────────────────
        if existing:
            if DRY_RUN:
                print(f"[UPDATE dry] {name} (id={league_id})")
                updated += 1
                continue

            api_data = fetch_league(league_id)
            if i < len(TARGET_LEAGUES) - 1:
                time.sleep(API_SLEEP)

            doc = build_doc(target, api_data, now)
            # on ne touche pas au league_id ni created_at sur update
            doc.pop("league_id", None)
            doc.pop("created_at", None)

            external_logo = doc.get("logo_url") or ""
            freebox_path = store_logo_on_freebox(external_logo, league_id)
            if freebox_path:
                doc["logo_url"] = freebox_path
                logo_ok += 1
            else:
                logo_fail += 1  # fallback: on garde l'URL externe

            col.update_one({"apifootball_league_id": league_id}, {"$set": doc})
            print(f"[UPDATE] {name} (id={league_id}) → logo_url={doc['logo_url']}")
            updated += 1
            continue

        # ── INSERT ───────────────────────────────────────────────────────────
        if DRY_RUN:
            print(f"[INSERT dry] {name} (id={league_id}, scope={target['scope']}, region={target['region']})")
            inserted += 1
            continue

        api_data = fetch_league(league_id)
        if i < len(TARGET_LEAGUES) - 1:
            time.sleep(API_SLEEP)

        if api_data is None:
            print(f"[SKIP]   {name} (id={league_id}) → API n'a rien retourné")
            errors += 1
            continue

        doc = build_doc(target, api_data, now)

        external_logo = doc.get("logo_url") or ""
        freebox_path = store_logo_on_freebox(external_logo, league_id)
        if freebox_path:
            doc["logo_url"] = freebox_path
            logo_ok += 1
        else:
            logo_fail += 1  # fallback: URL externe

        col.insert_one(doc)
        print(f"[INSERT] {name} (id={league_id}) → logo_url={doc['logo_url']}")
        inserted += 1

    print(f"\n{'='*60}")
    if DRY_RUN:
        print(f"Dry-run : {inserted} à insérer, {updated} à mettre à jour.")
        print("Relancer avec --apply pour écrire en base.")
    else:
        print(f"Terminé : {inserted} insérés, {updated} mis à jour, {errors} erreurs.")
        print(f"Logos  : {logo_ok} stockés sur Freebox, {logo_fail} en fallback URL externe.")
    print(f"{'='*60}\n")
    client.close()


if __name__ == "__main__":
    run()