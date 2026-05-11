# backend/routers/sponsors.py
"""Routes CRUD pour les sponsors.

Particularités vs les autres entités :
- Pas de Pydantic model dédié — payload accepté en dict.
- Le kit_count fait un fallback name-based (regex insensitive) si l'ID
  n'a pas encore été rattaché aux master_kits par un modérateur.
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..auth import get_moderator_user
from ..utils import slugify, safe_regex
from ..image_mirror import mirror_entity_images
from ._entity_helpers import assert_not_locked


router = APIRouter(prefix="/api", tags=["sponsors"])


@router.get("/sponsors")
async def list_sponsors(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query: dict = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": safe_regex(search), "$options": "i"}
    if country:
        query["country"] = {"$regex": safe_regex(country), "$options": "i"}
    total = await db.sponsors.count_documents(query)
    sponsors = await db.sponsors.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for s in sponsors:
        sid  = s.get("sponsor_id", "")
        name = s.get("name", "")
        count_by_id = await db.master_kits.count_documents({"sponsor_id": sid}) if sid else 0
        if count_by_id == 0 and name:
            count_by_name = await db.master_kits.count_documents(
                {"sponsor": {"$regex": f"^{safe_regex(name)}$", "$options": "i"}}
            )
        else:
            count_by_name = 0
        s["kit_count"] = count_by_id or count_by_name
    return {"results": sponsors, "total": total}


@router.get("/sponsors/{sponsor_id}")
async def get_sponsor(sponsor_id: str):
    sponsor = await db.sponsors.find_one(
        {"$or": [{"sponsor_id": sponsor_id}, {"slug": sponsor_id}]},
        {"_id": 0}
    )
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sid  = sponsor.get("sponsor_id", "")
    name = sponsor.get("name", "")
    kits = await db.master_kits.find({"sponsor_id": sid}, {"_id": 0}).sort("season", -1).to_list(200) if sid else []
    if not kits and name:
        kits = await db.master_kits.find(
            {"sponsor": {"$regex": f"^{safe_regex(name)}$", "$options": "i"}},
            {"_id": 0}
        ).sort("season", -1).to_list(200)
    sponsor["kits"]      = kits
    sponsor["kit_count"] = len(kits)
    return sponsor


@router.post("/sponsors", dependencies=[Depends(get_moderator_user)])
async def create_sponsor(sponsor: dict):
    slug = slugify(sponsor.get("name", ""))
    if await db.sponsors.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Sponsor already exists")
    doc = {**sponsor}
    doc["sponsor_id"]  = f"sponsor_{uuid.uuid4().hex[:12]}"
    doc["slug"]        = slug
    doc["status"]      = "approved"
    doc["created_at"]  = datetime.now(timezone.utc).isoformat()
    doc["updated_at"]  = doc["created_at"]
    doc = await mirror_entity_images(doc, "sponsor", doc["sponsor_id"])
    await db.sponsors.insert_one(doc)
    return await db.sponsors.find_one({"sponsor_id": doc["sponsor_id"]}, {"_id": 0})


@router.post("/sponsors/pending")
async def create_sponsor_pending(
    sponsor: dict,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(sponsor.get("name", ""))
    existing = await db.sponsors.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    sponsor_id    = f"sponsor_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = {**sponsor}
    doc["sponsor_id"]    = sponsor_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "sponsor", sponsor_id)
    await db.sponsors.insert_one(doc)

    # sub_data inclut les champs image après mirroring pour affichage dans la review
    sub_data = {
        "mode":      "create",
        "name":      sponsor.get("name"),
        "entity_id": sponsor_id,
        "logo_url":  doc.get("logo_url"),
    }
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "sponsor",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })
    return await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})


@router.put("/sponsors/{sponsor_id}", dependencies=[Depends(get_moderator_user)])
async def update_sponsor(sponsor_id: str, sponsor: dict):
    await assert_not_locked("sponsors", "sponsor_id", sponsor_id)
    existing = await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    update_data = {k: v for k, v in sponsor.items() if v is not None}
    update_data["slug"]       = slugify(sponsor.get("name", ""))
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "sponsor", sponsor_id)
    await db.sponsors.update_one({"sponsor_id": sponsor_id}, {"$set": update_data})
    return await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})
