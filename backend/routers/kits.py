from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import MasterKitCreate, MasterKitOut, VersionCreate, VersionOut
from auth import get_current_user

router = APIRouter(prefix="/api", tags=["kits"])

# ─── Master Kit Routes ───

@router.get("/master-kits", response_model=List[MasterKitOut])
async def list_master_kits(
    club: Optional[str] = None,
    season: Optional[str] = None,
    brand: Optional[str] = None,
    kit_type: Optional[str] = None,
    design: Optional[str] = None,
    league: Optional[str] = None,
    gender: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 200
):
    query = {}
    if club:
        query["club"] = {"$regex": club, "$options": "i"}
    if season:
        query["season"] = {"$regex": season, "$options": "i"}
    if brand:
        query["brand"] = {"$regex": brand, "$options": "i"}
    if kit_type:
        query["kit_type"] = kit_type
    if design:
        query["design"] = design
    if league:
        query["league"] = league
    if gender:
        query["gender"] = gender
    if search:
        query["$or"] = [
            {"club": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"season": {"$regex": search, "$options": "i"}},
            {"design": {"$regex": search, "$options": "i"}},
            {"sponsor": {"$regex": search, "$options": "i"}},
        ]
    kits = await db.master_kits.find(query, {"_id": 0}).sort("season", -1).skip(skip).limit(limit).to_list(limit)
    result = []
    for kit in kits:
        # Normalisation des champs CSV → schéma backend
        kit["kit_id"]      = kit.get("kit_id") or kit.get("id", "")
        kit["kit_type"]    = kit.get("kit_type") or kit.get("type", "")
        kit["front_photo"] = kit.get("front_photo") or kit.get("img_url", "")
        kit["club"]        = kit.get("club") or kit.get("team_id", "")
        kit["brand"]       = kit.get("brand") or kit.get("brand_id", "")
        kit["league"]      = kit.get("league") or kit.get("league_id", "")
        # created_at → toujours une string
        ca = kit.get("created_at", "")
        if hasattr(ca, "isoformat"):
            kit["created_at"] = ca.isoformat()
        elif not isinstance(ca, str):
            kit["created_at"] = str(ca)

        kit_id = kit["kit_id"]
        version_count = await db.versions.count_documents({"kit_id": kit_id}) if kit_id else 0
        kit["version_count"] = version_count
        reviews = await db.reviews.find({"kit_id": kit_id}, {"_id": 0, "rating": 1}).to_list(1000) if kit_id else []
        kit["avg_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else kit.get("avg_rating", 0.0)
        result.append(kit)
    return result

@router.get("/master-kits/count")
async def count_master_kits():
    count = await db.master_kits.count_documents({})
    return {"count": count}

@router.get("/master-kits/filters")
async def get_filters():
    clubs   = await db.master_kits.distinct("club")
    brands  = await db.master_kits.distinct("brand")
    seasons = await db.master_kits.distinct("season")
    kit_types = await db.master_kits.distinct("kit_type")
    designs = await db.master_kits.distinct("design")
    leagues = await db.master_kits.distinct("league")
    sponsors = await db.master_kits.distinct("sponsor")
    genders = await db.master_kits.distinct("gender")
    return {
        "clubs":     sorted([c for c in clubs if c]),
        "brands":    sorted([b for b in brands if b]),
        "seasons":   sorted([s for s in seasons if s], reverse=True),
        "kit_types": sorted([t for t in kit_types if t]),
        "designs":   sorted([d for d in designs if d]),
        "leagues":   sorted([lg for lg in leagues if lg]),
        "sponsors":  sorted([s for s in sponsors if s]),
        "genders":   sorted([g for g in genders if g]),
    }

@router.get("/master-kits/{kit_id}")
async def get_master_kit(kit_id: str):
    kit = await db.master_kits.find_one(
    {"$or": [{"kit_id": kit_id}, {"id": kit_id}]}, {"_id": 0}
)

    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    # Normalisation
    kit["kit_id"]      = kit.get("kit_id") or kit.get("id", "")
    kit["kit_type"]    = kit.get("kit_type") or kit.get("type", "")
    kit["front_photo"] = kit.get("front_photo") or kit.get("img_url", "")
    ca = kit.get("created_at", "")
    if hasattr(ca, "isoformat"):
        kit["created_at"] = ca.isoformat()
    elif not isinstance(ca, str):
        kit["created_at"] = str(ca)

    versions = await db.versions.find({"kit_id": kit_id}, {"_id": 0}).to_list(100)
    for v in versions:
        reviews = await db.reviews.find({"version_id": v.get("version_id", "")}, {"_id": 0, "rating": 1}).to_list(1000)
        v["avg_rating"]   = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
        v["review_count"] = len(reviews)
    kit["versions"]      = versions
    kit["version_count"] = len(versions)
    all_reviews = await db.reviews.find({"kit_id": kit_id}, {"_id": 0, "rating": 1}).to_list(1000)
    kit["avg_rating"] = round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1) if all_reviews else 0.0
    return kit

@router.post("/master-kits", response_model=MasterKitOut)
async def create_master_kit(kit: MasterKitCreate, request: Request):
    user = await get_current_user(request)
    doc = kit.model_dump()
    doc["kit_id"]     = f"kit_{uuid.uuid4().hex[:12]}"
    doc["created_by"] = user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.master_kits.insert_one(doc)
    default_version = {
        "version_id":  f"ver_{uuid.uuid4().hex[:12]}",
        "kit_id":      doc["kit_id"],
        "competition": "National Championship",
        "model":       "Replica",
        "sku_code":    "",
        "ean_code":    "",
        "front_photo": doc.get("front_photo", ""),
        "back_photo":  "",
        "created_by":  user["user_id"],
        "created_at":  datetime.now(timezone.utc).isoformat()
    }
    await db.versions.insert_one(default_version)
    result = await db.master_kits.find_one({"kit_id": doc["kit_id"]}, {"_id": 0})
    result["version_count"] = 1
    result["avg_rating"]    = 0.0
    return result

# ─── Version Routes ───

@router.get("/versions/{version_id}")
async def get_version(version_id: str):
    version = await db.versions.find_one({"version_id": version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    kit = await db.master_kits.find_one({"kit_id": version.get("kit_id", "")}, {"_id": 0})
    version["master_kit"] = kit
    reviews = await db.reviews.find({"version_id": version_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one({"user_id": r["user_id"]}, {"_id": 0, "name": 1, "picture": 1})
        if u:
            r["user_name"]    = u.get("name", "")
            r["user_picture"] = u.get("picture", "")
    version["reviews"]      = reviews
    version["avg_rating"]   = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
    version["review_count"] = len(reviews)
    collection_count = await db.collections.count_documents({"version_id": version_id})
    version["collection_count"] = collection_count
    return version

@router.get("/versions/{version_id}/estimates")
async def get_version_estimates(version_id: str):
    items = await db.collections.find(
        {"version_id": version_id},
        {"_id": 0, "estimated_price": 1, "value_estimate": 1, "price_estimate": 1}
    ).to_list(1000)
    estimates = []
    for i in items:
        val = i.get("estimated_price") or i.get("value_estimate") or i.get("price_estimate") or 0
        if val and val > 0:
            estimates.append(val)
    if not estimates:
        return {"low": 0, "average": 0, "high": 0, "count": 0, "estimates": []}
    return {
        "low":       round(min(estimates), 2),
        "average":   round(sum(estimates) / len(estimates), 2),
        "high":      round(max(estimates), 2),
        "count":     len(estimates),
        "estimates": sorted(estimates)
    }

@router.post("/versions", response_model=VersionOut)
async def create_version(version: VersionCreate, request: Request):
    user = await get_current_user(request)
    kit = await db.master_kits.find_one({"kit_id": version.kit_id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Master Kit not found")
    doc = version.model_dump()
    doc["version_id"]  = f"ver_{uuid.uuid4().hex[:12]}"
    doc["created_by"]  = user["user_id"]
    doc["created_at"]  = datetime.now(timezone.utc).isoformat()
    if not doc["front_photo"]:
        doc["front_photo"] = kit.get("front_photo", "")
    await db.versions.insert_one(doc)
    result = await db.versions.find_one({"version_id": doc["version_id"]}, {"_id": 0})
    result["avg_rating"]    = 0.0
    result["review_count"]  = 0
    return result

@router.get("/versions", response_model=List[VersionOut])
async def list_versions(kit_id: Optional[str] = None, skip: int = 0, limit: int = 50):
    query = {}
    if kit_id:
        query["kit_id"] = kit_id
    versions = await db.versions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for v in versions:
        reviews = await db.reviews.find({"version_id": v.get("version_id", "")}, {"_id": 0, "rating": 1}).to_list(1000)
        v["avg_rating"]   = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
        v["review_count"] = len(reviews)
    return versions
