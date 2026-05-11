# backend/routers/leagues.py
"""Routes CRUD pour les leagues (championnats, coupes, confédérations)."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import LeagueCreate, LeagueOut
from ..auth import get_moderator_user
from ..utils import slugify, safe_regex
from ..image_mirror import mirror_entity_images
from ._entity_helpers import assert_not_locked


router = APIRouter(prefix="/api", tags=["leagues"])


@router.get("/leagues")
async def list_leagues(
    search: Optional[str] = None,
    country_or_region: Optional[str] = None,
    level: Optional[str] = None,
    entity_type: Optional[str] = None,   # "league" | "cup" | "confederation"
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": safe_regex(search), "$options": "i"}
    if country_or_region:
        query["country_or_region"] = {"$regex": safe_regex(country_or_region), "$options": "i"}
    if level:
        query["level"] = level
    if entity_type:
        query["entity_type"] = entity_type
    total = await db.leagues.count_documents(query)
    leagues = await db.leagues.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for l in leagues:
        lid = l.get("league_id", "")
        l["kit_count"] = await db.master_kits.count_documents({"league_id": lid}) if lid else 0
    return {"results": leagues, "total": total}


@router.get("/leagues/{league_id}")
async def get_league(league_id: str):
    league = await db.leagues.find_one({"$or": [{"league_id": league_id}, {"slug": league_id}]}, {"_id": 0})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    lid = league.get("league_id", "")
    league["kit_count"] = await db.master_kits.count_documents({"league_id": lid}) if lid else 0
    kits = await db.master_kits.find({"league_id": lid}, {"_id": 0}).sort("season", -1).to_list(500) if lid else []
    league["kits"] = kits
    return league


@router.post("/leagues", response_model=LeagueOut)
async def create_league(league: LeagueCreate, _user: dict = Depends(get_moderator_user)):
    slug = slugify(league.name)
    if await db.leagues.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="League already exists")
    doc = league.model_dump()
    doc["league_id"]  = f"league_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "league", doc["league_id"])
    await db.leagues.insert_one(doc)
    result = await db.leagues.find_one({"league_id": doc["league_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/leagues/pending", response_model=LeagueOut)
async def create_league_pending(
    league: LeagueCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(league.name)
    existing = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    league_id     = f"league_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = league.model_dump()
    doc["league_id"]     = league_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "league", league_id)
    await db.leagues.insert_one(doc)

    # sub_data inclut les champs image après mirroring pour affichage dans la review
    sub_data = {
        "mode":       "create",
        "name":       league.name,
        "entity_id":  league_id,
        "logo_url":   doc.get("logo_url"),
    }
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "league",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/leagues/{league_id}", response_model=LeagueOut)
async def update_league(league_id: str, league: LeagueCreate, _user: dict = Depends(get_moderator_user)):
    await assert_not_locked("leagues", "league_id", league_id)
    existing = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="League not found")
    update_data = {k: v for k, v in league.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(league.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "league", league_id)
    await db.leagues.update_one({"league_id": league_id}, {"$set": update_data})
    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"league_id": league_id})
    return result
