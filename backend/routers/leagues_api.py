# backend/routers/leagues_api.py
# Routes de recherche et d'import de leagues.
# GET  /api/leagues?search=...&limit=N  — recherche DB
# POST /api/leagues/import-from-apifootball — import depuis API-Football → DB

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from bson import ObjectId
import re

from ..database import db
from ..auth import get_current_user

router = APIRouter(prefix="/api/leagues", tags=["leagues"])


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


# ── Recherche DB ──────────────────────────────────────────────────────────────
@router.get("")
async def search_leagues(
    search: Optional[str] = Query(None, min_length=2),
    limit: int = Query(8, ge=1, le=50),
    skip: int = Query(0, ge=0),
):
    query = {}
    if search:
        query["name"] = {"$regex": re.escape(search.strip()), "$options": "i"}

    cursor = db.leagues.find(query).skip(skip).limit(limit).sort("name", 1)
    leagues = [_serialize(doc) async for doc in cursor]
    total = await db.leagues.count_documents(query)

    return {"leagues": leagues, "total": total}


# ── Import depuis API-Football ────────────────────────────────────────────────
@router.post("/import-from-apifootball")
async def import_league_from_apifootball(
    payload: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Importe (ou retrouve) une league depuis API-Football dans la DB Topkit.
    Si la league existe déjà (via apifootball_league_id), on la retourne sans doublon.
    """
    apifootball_id = payload.get("apifootball_league_id")
    if not apifootball_id:
        raise HTTPException(status_code=422, detail="apifootball_league_id requis")

    # Cherche si déjà importée
    existing = await db.leagues.find_one({"apifootball_league_id": apifootball_id})
    if existing:
        return _serialize(existing)

    # Génère un league_id lisible
    raw_name = payload.get("name", f"league_{apifootball_id}")
    slug_base = re.sub(r"[^a-z0-9]+", "_", raw_name.lower()).strip("_")

    # Vérifie l'unicité du slug
    slug = slug_base
    counter = 1
    while await db.leagues.find_one({"league_id": slug}):
        slug = f"{slug_base}_{counter}"
        counter += 1

    doc = {
        "league_id": slug,
        "name": raw_name,
        "logo_url": payload.get("logo_url"),
        "country": payload.get("country"),
        "country_flag": payload.get("country_flag"),
        "apifootball_league_id": apifootball_id,
        "source": "api-football",
    }

    result = await db.leagues.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc
