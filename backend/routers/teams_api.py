"""Router teams_api — recherche clubs avec DB-first + API-Football fallback.

Routes :
  GET  /api/teams-api/search?name=...  → recherche DB + API-Football
  POST /api/teams-api/upsert           → upsert depuis API-Football en DB
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import unicodedata
import re

from ..database import db
from ..auth import get_moderator_user
from ..services.thesportsdb import search_teams_db_first

router = APIRouter(prefix="/api/teams-api", tags=["teams-api"])


class TeamUpsertBody(BaseModel):
    apifootball_team_id: Optional[int] = None
    name: str
    country: Optional[str] = ""
    founded: Optional[int] = None
    is_national: Optional[bool] = None
    logo: Optional[str] = ""
    city: Optional[str] = None
    stadium_name: Optional[str] = None
    stadium_capacity: Optional[int] = None
    stadium_surface: Optional[str] = None
    stadium_image_url: Optional[str] = None


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


@router.post("/upsert", dependencies=[Depends(get_moderator_user)])
async def upsert_team(body: TeamUpsertBody):
    """Crée ou met à jour un club depuis les données API-Football.

    Réservé aux modérateurs/admins.
    """
    apifootball_id = body.apifootball_team_id
    name = body.name.strip()
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
        "country": body.country or "",
        "crest_url": body.logo or "",
        "city": body.city or "",
        "stadium_name": body.stadium_name or "",
        "stadium_capacity": body.stadium_capacity,
        "stadium_surface": body.stadium_surface or "",
        "stadium_image_url": body.stadium_image_url or "",
        "updated_at": now,
    }
    if apifootball_id is not None:
        update_fields["apifootball_team_id"] = apifootball_id
    if body.founded is not None:
        update_fields["founded"] = body.founded
    if body.is_national is not None:
        update_fields["is_national"] = bool(body.is_national)

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
