"""Router leagues_api — recherche compétitions avec DB-first + API-Football fallback.

Routes :
  GET  /api/leagues-api/search?name=...  → recherche DB + API-Football
  POST /api/leagues-api/upsert           → upsert depuis API-Football en DB
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import uuid
import unicodedata
import re

from ..database import db
from ..services.thesportsdb import search_leagues_db_first

router = APIRouter(prefix="/api/leagues-api", tags=["leagues-api"])


def _slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


@router.get("/search")
async def search_leagues(name: str = Query(..., min_length=2)):
    """Recherche DB-first puis API-Football."""
    try:
        results = await search_leagues_db_first(name, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search error: {str(e)}")
    return results


@router.post("/upsert")
async def upsert_league(body: dict):
    """Crée ou met à jour une league depuis les données API-Football.

    Body:
      {
        apifootball_league_id: int,
        name: str,
        country: str,
        logo: str,
        scoring_weight: float  (optionnel)
      }
    """
    apifootball_id = body.get("apifootball_league_id")
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name requis")

    now = datetime.now(timezone.utc).isoformat()

    # Cherche si déjà en DB par apifootball_league_id ou slug
    slug = _slugify(name)
    existing = None
    if apifootball_id:
        existing = await db["leagues"].find_one({"apifootball_league_id": apifootball_id})
    if not existing:
        existing = await db["leagues"].find_one({"slug": slug})

    update_fields = {
        "name": name,
        "slug": slug,
        "country_or_region": body.get("country", ""),
        "apifootball_logo": body.get("logo", ""),
        "updated_at": now,
    }
    if apifootball_id is not None:
        update_fields["apifootball_league_id"] = apifootball_id
    if body.get("scoring_weight") is not None:
        update_fields["scoring_weight"] = float(body["scoring_weight"])

    if existing:
        await db["leagues"].update_one(
            {"_id": existing["_id"]},
            {"$set": update_fields}
        )
        league_id = existing["league_id"]
        created = False
    else:
        league_id = str(uuid.uuid4())
        update_fields.update({
            "league_id": league_id,
            "status": "approved",
            "level": "domestic",
            "organizer": "",
            "logo_url": body.get("logo", ""),
            "kit_count": 0,
            "created_at": now,
        })
        await db["leagues"].insert_one(update_fields)
        created = True

    return {"league_id": league_id, "created": created, "slug": slug}
