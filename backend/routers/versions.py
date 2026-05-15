# backend/routers/versions.py
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import VersionCreate, VersionOut
from ..auth import get_current_user
from ..utils import safe_regex
from ._kit_utils import master_kit_image_url, local_image_url

router = APIRouter(prefix="/api", tags=["versions"])


@router.get("/versions", response_model=dict)
async def list_versions(
    kit_id: Optional[str] = None,
    search: Optional[str] = None,
    club: Optional[str] = None,
    brand: Optional[str] = None,
    kit_type: Optional[str] = None,
    season: Optional[str] = None,
    league: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    kit_ids = None
    if club or brand or kit_type or season or league or search:
        kit_query = {}
        if club:
            kit_query["club"] = {"$regex": safe_regex(club), "$options": "i"}
        if brand:
            kit_query["brand"] = {"$regex": safe_regex(brand), "$options": "i"}
        if kit_type:
            kit_query["kit_type"] = kit_type
        if season:
            kit_query["season"] = {"$regex": safe_regex(season), "$options": "i"}
        if league:
            kit_query["league"] = league
        if search:
            s = safe_regex(search)
            kit_query["$or"] = [
                {"club": {"$regex": s, "$options": "i"}},
                {"brand": {"$regex": s, "$options": "i"}},
                {"season": {"$regex": s, "$options": "i"}},
            ]

        matching_kits = await db.master_kits.find(
            kit_query, {"_id": 0, "kit_id": 1, "season": 1}
        ).sort("season", -1).to_list(2000)
        kit_ids = [k["kit_id"] for k in matching_kits]

        if not kit_ids:
            return {"results": [], "total": 0, "skip": skip, "limit": limit}

    version_query = {}
    if kit_id:
        version_query["kit_id"] = kit_id
    elif kit_ids is not None:
        version_query["kit_id"] = {"$in": kit_ids}

    total = await db.versions.count_documents(version_query)
    capped_limit = min(limit, 100)

    versions = (
        await db.versions.find(version_query, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    kid_list = list({v.get("kit_id") for v in versions if v.get("kit_id")})
    kits_map = {}
    if kid_list:
        kits_docs = await db.master_kits.find(
            {"kit_id": {"$in": kid_list}}, {"_id": 0}
        ).to_list(len(kid_list))
        for k in kits_docs:
            k["kit_id"] = k.get("kit_id") or k.get("id", "")
            k["kit_type"] = k.get("kit_type") or k.get("type", "")
            k["front_photo"] = master_kit_image_url(k["kit_type"], k["kit_id"], k.get("front_photo", ""))
            kits_map[k["kit_id"]] = k

    result = []
    for v in versions:
        v["front_photo"] = local_image_url(v.get("front_photo", ""))
        v["back_photo"] = local_image_url(v.get("back_photo", ""))
        v["master_kit"] = kits_map.get(v.get("kit_id"))
        v["avg_rating"] = v.get("avg_rating", 0.0)
        v["review_count"] = v.get("review_count", 0)
        result.append(v)

    return {"results": result, "total": total, "skip": skip, "limit": capped_limit}


@router.get("/versions/{version_id}/estimates")
async def get_version_estimates(version_id: str):
    items = await db.collections.find(
        {"version_id": version_id},
        {"_id": 0, "estimated_price": 1, "value_estimate": 1, "price_estimate": 1},
    ).to_list(1000)
    estimates = []
    for i in items:
        val = (
            i.get("estimated_price") or i.get("value_estimate")
            or i.get("price_estimate") or 0
        )
        if val and val > 0:
            estimates.append(val)
    if not estimates:
        return {"low": 0, "average": 0, "high": 0, "count": 0}
    return {
        "low": round(min(estimates), 2),
        "average": round(sum(estimates) / len(estimates), 2),
        "high": round(max(estimates), 2),
        "count": len(estimates),
        "estimates": sorted(estimates),
    }


@router.get("/versions/{version_id}/worn-by")
async def get_version_worn_by(version_id: str):
    items = await db.collections.find(
        {"version_id": version_id, "flocking_player_id": {"$exists": True, "$ne": ""}},
        {"_id": 0, "flocking_player_id": 1},
    ).to_list(200)
    player_ids = list({i["flocking_player_id"] for i in items if i.get("flocking_player_id")})
    players = []
    for pid in player_ids:
        p = await db.players.find_one(
            {"$or": [{"player_id": pid}, {"_id": pid}]}, {"_id": 0}
        )
        if p:
            players.append({
                "player_id": p.get("player_id") or pid,
                "full_name": p.get("full_name") or p.get("name", ""),
                "slug": p.get("slug", ""),
                "photo_url": p.get("photo_url") or p.get("photo", ""),
            })
    return players


@router.get("/versions/{version_id}/reviews")
async def get_version_reviews(version_id: str):
    reviews = await db.reviews.find(
        {"version_id": version_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)
    return reviews


@router.post("/versions/{version_id}/reviews")
async def post_version_review(version_id: str, request: Request):
    user = await get_current_user(request)
    body = await request.json()
    rating = int(body.get("rating", 0))
    comment = str(body.get("comment", "")).strip()
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")

    existing = await db.reviews.find_one({"version_id": version_id, "user_id": user["user_id"]})
    if existing:
        await db.reviews.update_one(
            {"version_id": version_id, "user_id": user["user_id"]},
            {"$set": {"rating": rating, "comment": comment}},
        )
    else:
        await db.reviews.insert_one({
            "review_id": f"rev_{uuid.uuid4().hex[:12]}",
            "version_id": version_id,
            "user_id": user["user_id"],
            "user_name": user.get("name", "Anonymous"),
            "user_picture": user.get("picture", ""),
            "rating": rating,
            "comment": comment,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    all_reviews = await db.reviews.find(
        {"version_id": version_id}, {"rating": 1, "_id": 0}
    ).to_list(1000)
    avg = (
        round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1)
        if all_reviews else 0.0
    )
    await db.versions.update_one(
        {"version_id": version_id},
        {"$set": {"avg_rating": avg, "review_count": len(all_reviews)}},
    )

    version_doc = await db.versions.find_one({"version_id": version_id}, {"kit_id": 1, "_id": 0})
    if version_doc:
        kit_id = version_doc.get("kit_id")
        sibling_ids = [
            v["version_id"]
            for v in await db.versions.find(
                {"kit_id": kit_id}, {"version_id": 1, "_id": 0}
            ).to_list(500)
        ]
        kit_reviews = await db.reviews.find(
            {"version_id": {"$in": sibling_ids}}, {"rating": 1, "_id": 0}
        ).to_list(5000)
        kit_avg = (
            round(sum(r["rating"] for r in kit_reviews) / len(kit_reviews), 1)
            if kit_reviews else 0.0
        )
        await db.master_kits.update_one(
            {"kit_id": kit_id},
            {"$set": {"avg_rating": kit_avg, "review_count": len(kit_reviews)}},
        )
    return {"ok": True, "avg_rating": avg, "review_count": len(all_reviews)}


@router.get("/versions/{version_id}", response_model=VersionOut)
async def get_version(version_id: str):
    version = await db.versions.find_one({"version_id": version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    version["front_photo"] = local_image_url(version.get("front_photo", ""))
    version["back_photo"] = local_image_url(version.get("back_photo", ""))
    kit = await db.master_kits.find_one({"kit_id": version.get("kit_id")}, {"_id": 0})
    if kit:
        kit["kit_id"] = kit.get("kit_id") or kit.get("id", "")
        kit["kit_type"] = kit.get("kit_type") or kit.get("type", "")
        kit["front_photo"] = master_kit_image_url(kit["kit_type"], kit["kit_id"], kit.get("front_photo", ""))
        version["master_kit"] = kit
    reviews = await db.reviews.find(
        {"version_id": version_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one(
            {"user_id": r.get("user_id")}, {"_id": 0, "name": 1, "picture": 1}
        )
        if u:
            r["user_name"] = u.get("name")
            r["user_picture"] = u.get("picture")
    version["reviews"] = reviews
    version["avg_rating"] = (
        round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        if reviews else version.get("avg_rating", 0.0)
    )
    version["review_count"] = len(reviews) if reviews else version.get("review_count", 0)
    version["collection_count"] = await db.collections.count_documents({"version_id": version_id})
    return version


@router.post("/versions", response_model=VersionOut)
async def create_version(version: VersionCreate, request: Request):
    user = await get_current_user(request)
    kit = await db.master_kits.find_one({"kit_id": version.kit_id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Master Kit not found")
    doc = version.model_dump()
    doc["version_id"] = f"ver_{uuid.uuid4().hex[:12]}"
    doc["created_by"] = user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["avg_rating"] = 0.0
    doc["review_count"] = 0
    if not doc.get("front_photo"):
        doc["front_photo"] = kit.get("front_photo", "")
    await db.versions.insert_one(doc)
    await db.master_kits.update_one({"kit_id": version.kit_id}, {"$inc": {"version_count": 1}})
    result = await db.versions.find_one({"version_id": doc["version_id"]}, {"_id": 0})
    return result
