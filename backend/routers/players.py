# backend/routers/players.py
"""Routes CRUD pour les players.

Particularités vs les autres entités :
- Le slug autoincrement (`{slug}-N`) si collision (homonymes fréquents).
- Le get_player enrichit avec les versions de la collection du user
  (lookup collections → versions → master_kits).
- create_player_pending tracke `submitted_by` / `submitter_name` dans
  la submission pour identifier le contributeur (utilisé par le panel mod).
"""
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import PlayerCreate, PlayerOut
from ..auth import get_current_user, get_moderator_user
from ..utils import slugify, safe_regex
from ..image_mirror import mirror_entity_images
from ._entity_helpers import assert_not_locked


router = APIRouter(prefix="/api", tags=["players"])


@router.get("/players")
async def list_players(
    search: Optional[str] = None,
    nationality: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["full_name"] = {"$regex": safe_regex(search), "$options": "i"}
    if nationality:
        query["nationality"] = {"$regex": safe_regex(nationality), "$options": "i"}
    total = await db.players.count_documents(query)
    players = await db.players.find(query, {"_id": 0}).sort("full_name", 1).skip(skip).limit(limit).to_list(limit)
    for p in players:
        pid = p.get("player_id", "")
        p["kit_count"] = await db.versions.count_documents({"main_player_id": pid}) if pid else 0
        if not isinstance(p.get("positions"), list):
            p["positions"] = []
    return {"results": players, "total": total}


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    player = await db.players.find_one({"$or": [{"player_id": player_id}, {"slug": player_id}]}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if not isinstance(player.get("positions"), list):
        player["positions"] = []
    pid = player.get("player_id", "")
    collection_items = await db.collections.find(
        {"flocking_player_id": pid}, {"_id": 0, "version_id": 1}
    ).to_list(2000) if pid else []
    version_ids = list({i["version_id"] for i in collection_items if i.get("version_id")})
    kit_ids_set = set()
    enriched_versions = []
    if version_ids:
        versions = await db.versions.find(
            {"version_id": {"$in": version_ids}}, {"_id": 0}
        ).to_list(len(version_ids))
        for v in versions:
            kit = await db.master_kits.find_one({"kit_id": v.get("kit_id", "")}, {"_id": 0})
            v["master_kit"] = kit
            kit_ids_set.add(v.get("kit_id", ""))
            enriched_versions.append(v)
    player["kit_count"] = len(kit_ids_set)
    player["versions"]  = enriched_versions
    return player


@router.post("/players", response_model=PlayerOut)
async def create_player(player: PlayerCreate, _user: dict = Depends(get_moderator_user)):
    slug = slugify(player.full_name)
    base_slug, counter = slug, 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1
    doc = player.model_dump()
    doc["player_id"]  = f"player_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "player", doc["player_id"])
    await db.players.insert_one(doc)
    result = await db.players.find_one({"player_id": doc["player_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/players/pending", response_model=PlayerOut)
async def create_player_pending(
    player: PlayerCreate,
    request: Request,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(player.full_name)
    base_slug, counter = slug, 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1

    now           = datetime.now(timezone.utc).isoformat()
    player_id     = f"player_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = player.model_dump()
    doc["player_id"]     = player_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "player", player_id)
    await db.players.insert_one(doc)

    # sub_data inclut les champs image après mirroring pour affichage dans la review
    sub_data = {
        "mode":      "create",
        "full_name": player.full_name,
        "entity_id": player_id,
        "photo_url": doc.get("photo_url"),
    }
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    try:
        current_user   = await get_current_user(request)
        submitted_by   = current_user.get("user_id", "")
        submitter_name = current_user.get("name", "")
    except Exception:
        submitted_by   = ""
        submitter_name = ""

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "player",
        "data":            sub_data,
        "submitted_by":    submitted_by,
        "submitter_name":  submitter_name,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/players/{player_id}", response_model=PlayerOut)
async def update_player(player_id: str, player: PlayerCreate, _user: dict = Depends(get_moderator_user)):
    await assert_not_locked("players", "player_id", player_id)
    existing = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Player not found")
    update_data = {k: v for k, v in player.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(player.full_name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "player", player_id)
    await db.players.update_one({"player_id": player_id}, {"$set": update_data})
    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = await db.versions.count_documents({"main_player_id": player_id})
    return result
