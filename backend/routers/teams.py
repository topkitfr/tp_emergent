# backend/routers/teams.py
"""Routes CRUD pour les teams (clubs ou nations)."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import TeamCreate, TeamOut
from ..auth import get_moderator_user
from ..utils import slugify, safe_regex
from ..image_mirror import mirror_entity_images
from ._entity_helpers import assert_not_locked


router = APIRouter(prefix="/api", tags=["teams"])


@router.get("/teams")
async def list_teams(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {}
    if search:
        s = safe_regex(search)
        query["$or"] = [
            {"name": {"$regex": s, "$options": "i"}},
            {"aka":  {"$regex": s, "$options": "i"}},
        ]
    if country:
        query["country"] = {"$regex": safe_regex(country), "$options": "i"}
    total = await db.teams.count_documents(query)
    teams = await db.teams.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for t in teams:
        tid = t.get("team_id", "")
        t["kit_count"] = await db.master_kits.count_documents({"team_id": tid}) if tid else 0
    return {"results": teams, "total": total}


@router.get("/teams/{team_id}")
async def get_team(team_id: str):
    team = await db.teams.find_one({"$or": [{"team_id": team_id}, {"slug": team_id}]}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    tid = team.get("team_id", "")
    team["kit_count"] = await db.master_kits.count_documents({"team_id": tid}) if tid else 0
    kits = await db.master_kits.find({"team_id": tid}, {"_id": 0}).sort("season", -1).to_list(500) if tid else []
    team["kits"] = kits
    team["seasons"] = sorted(set(k.get("season", "") for k in kits if k.get("season")), reverse=True)
    return team


@router.post("/teams", response_model=TeamOut)
async def create_team(team: TeamCreate, _user: dict = Depends(get_moderator_user)):
    slug = slugify(team.name)
    if await db.teams.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Team already exists")
    doc = team.model_dump()
    doc["team_id"]    = f"team_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "team", doc["team_id"])
    await db.teams.insert_one(doc)
    result = await db.teams.find_one({"team_id": doc["team_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/teams/pending", response_model=TeamOut)
async def create_team_pending(
    team: TeamCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(team.name)
    existing = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    team_id       = f"team_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = team.model_dump()
    doc["team_id"]       = team_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "team", team_id)
    await db.teams.insert_one(doc)

    # sub_data inclut les champs image après mirroring pour affichage dans la review
    sub_data = {
        "mode":               "create",
        "name":               team.name,
        "entity_id":          team_id,
        "crest_url":          doc.get("crest_url"),
        "stadium_image_url":  doc.get("stadium_image_url"),
    }
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "team",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/teams/{team_id}", response_model=TeamOut)
async def update_team(team_id: str, team: TeamCreate, _user: dict = Depends(get_moderator_user)):
    await assert_not_locked("teams", "team_id", team_id)
    existing = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = {k: v for k, v in team.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(team.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "team", team_id)
    await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"team_id": team_id})
    return result
