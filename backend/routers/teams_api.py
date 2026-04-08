"""Router teams_api — recherche clubs avec DB-first + API-Football fallback.

Routes :
  GET  /api/teams-api/search?name=...  → recherche DB + API-Football
  POST /api/teams-api/upsert           → upsert depuis API-Football en DB
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import uuid
import unicodedata
import re

from ..database import db
from ..services.thesportsdb import search_teams_db_first

router = APIRouter(prefix="/api/teams-api", tags=["teams-api"])


def _slugify(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


@router.get("/search")
async def search_teams(name: str = Query(..., min_length=2)):
    """Recherche DB-first puis API-Football."""
    try:
        results = await search_teams_db_first(name, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search error: {str(e)}")
    return results


@router.post("/upsert")
async def upsert_team(body: dict):
    """Crée ou met à jour un club depuis les données API-Football.

    Body:
      {
        apifootball_team_id: int,
        name: str,
        country: str,
        founded: int | None,
        is_national: bool,
        logo: str,
        city: str | None,
        stadium_name: str | None,
        stadium_capacity: int | None,
        stadium_surface: str | None,
        stadium_image_url: str | None
      }
    """
    apifootball_id = body.get("apifootball_team_id")
    name = body.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name requis")

    now = datetime.now(timezone.utc).isoformat()
    slug = _slugify(name)

    # Cherche si déjà en DB par apifootball_team_id ou slug
    existing = None
    if apifootball_id:
        existing = await db["teams"].find_one({"apifootball_team_id": apifootball_id})
    if not existing:
        existing = await db["teams"].find_one({"slug": slug})

    update_fields = {
        "name": name,
        "slug": slug,
        "country": body.get("country", ""),
        "crest_url": body.get("logo", ""),
        "city": body.get("city") or "",
        "stadium_name": body.get("stadium_name") or "",
        "stadium_capacity": body.get("stadium_capacity"),
        "stadium_surface": body.get("stadium_surface") or "",
        "stadium_image_url": body.get("stadium_image_url") or "",
        "updated_at": now,
    }
    if apifootball_id is not None:
        update_fields["apifootball_team_id"] = apifootball_id
    if body.get("founded") is not None:
        update_fields["founded"] = body["founded"]
    if body.get("is_national") is not None:
        update_fields["is_national"] = bool(body["is_national"])

    if existing:
        await db["teams"].update_one(
            {"_id": existing["_id"]},
            {"$set": update_fields}
        )
        team_id = existing["team_id"]
        created = False
    else:
        team_id = str(uuid.uuid4())
        update_fields.update({
            "team_id": team_id,
            "status": "approved",
            "kit_count": 0,
            "created_at": now,
        })
        await db["teams"].insert_one(update_fields)
        created = True

    return {"team_id": team_id, "created": created, "slug": slug}
