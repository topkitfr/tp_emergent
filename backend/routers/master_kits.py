# backend/routers/master_kits.py
from fastapi import APIRouter, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import MasterKitCreate, MasterKitOut
from ..auth import get_current_user
from ..utils import safe_regex
from .notifications import create_notification
from ._kit_utils import master_kit_image_url, _create_missing_entity_submissions

router = APIRouter(prefix="/api", tags=["master-kits"])


@router.get("/master-kits/count")
async def count_master_kits():
    count = await db.master_kits.count_documents({})
    return {"count": count}


@router.get("/master-kits/filters")
async def get_filters():
    teams_docs = await db.teams.find(
        {"status": "approved"}, {"_id": 0, "name": 1}
    ).to_list(500)
    brands_docs = await db.brands.find(
        {"status": "approved"}, {"_id": 0, "name": 1}
    ).to_list(500)
    leagues_docs = await db.leagues.find(
        {"status": "approved"}, {"_id": 0, "name": 1}
    ).to_list(500)

    clubs = sorted([t["name"] for t in teams_docs if t.get("name")])
    brands = sorted([b["name"] for b in brands_docs if b.get("name")])
    leagues = sorted([l["name"] for l in leagues_docs if l.get("name")])

    if not clubs:
        raw = await db.master_kits.distinct("club")
        clubs = sorted([c for c in raw if c])
    if not brands:
        raw = await db.master_kits.distinct("brand")
        brands = sorted([b for b in raw if b])
    if not leagues:
        raw = await db.master_kits.distinct("league")
        leagues = sorted([l for l in leagues if l])

    seasons = await db.master_kits.distinct("season")
    kit_types = await db.master_kits.distinct("kit_type")
    designs = await db.master_kits.distinct("design")
    sponsors = await db.master_kits.distinct("sponsor")
    genders = await db.master_kits.distinct("gender")
    entity_types = await db.master_kits.distinct("entity_type")

    return {
        "clubs": clubs,
        "brands": brands,
        "seasons": sorted([s for s in seasons if s], reverse=True),
        "kit_types": sorted([t for t in kit_types if t]),
        "designs": sorted([d for d in designs if d]),
        "leagues": leagues,
        "sponsors": sorted([s for s in sponsors if s]),
        "genders": sorted([g for g in genders if g]),
        "entity_types": sorted([e for e in entity_types if e]),
        "team_types": ["club", "national"],
    }


@router.get("/master-kits")
async def list_master_kits(
    club: Optional[str] = None,
    season: Optional[str] = None,
    brand: Optional[str] = None,
    kit_type: Optional[str] = None,
    design: Optional[str] = None,
    league: Optional[str] = None,
    gender: Optional[str] = None,
    entity_type: Optional[str] = None,
    team_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
):
    query = {}
    if club:
        query["club"] = {"$regex": safe_regex(club), "$options": "i"}
    if season:
        query["season"] = {"$regex": safe_regex(season), "$options": "i"}
    if brand:
        query["brand"] = {"$regex": safe_regex(brand), "$options": "i"}
    if kit_type:
        query["kit_type"] = kit_type
    if design:
        query["design"] = design
    if league:
        query["league"] = league
    if gender:
        query["gender"] = gender
    if entity_type:
        query["entity_type"] = entity_type
    if search:
        s = safe_regex(search)
        query["$or"] = [
            {"club": {"$regex": s, "$options": "i"}},
            {"brand": {"$regex": s, "$options": "i"}},
            {"season": {"$regex": s, "$options": "i"}},
            {"design": {"$regex": s, "$options": "i"}},
            {"sponsor": {"$regex": s, "$options": "i"}},
        ]

    if team_type in ("club", "national"):
        if team_type == "national":
            matching_teams = await db.teams.find(
                {"is_national": True},
                {"_id": 0, "team_id": 1},
            ).to_list(2000)
        else:
            matching_teams = await db.teams.find(
                {"$or": [{"is_national": False}, {"is_national": {"$exists": False}}]},
                {"_id": 0, "team_id": 1},
            ).to_list(2000)

        team_ids = [t["team_id"] for t in matching_teams if t.get("team_id")]
        if team_ids:
            query["team_id"] = {"$in": team_ids}
        else:
            return {"results": [], "total": 0, "skip": skip, "limit": min(limit, 100)}

    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    ALLOWED_SORT_FIELDS = {"created_at", "season", "avg_rating", "review_count"}
    sort_field = sort_by if sort_by in ALLOWED_SORT_FIELDS else "season"
    sort_dir = 1 if order == "asc" else -1

    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort(sort_field, sort_dir)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    kit_ids_page = [k.get("kit_id") or k.get("id", "") for k in kits]
    version_counts: dict = {}
    if kit_ids_page:
        pipeline = [
            {"$match": {"kit_id": {"$in": kit_ids_page}}},
            {"$group": {"_id": "$kit_id", "count": {"$sum": 1}}},
        ]
        async for doc in db.versions.aggregate(pipeline):
            version_counts[doc["_id"]] = doc["count"]

    result = []
    for kit in kits:
        kit["kit_id"] = kit.get("kit_id") or kit.get("id", "")
        kit["kit_type"] = kit.get("kit_type") or kit.get("type", "")
        kit["front_photo"] = master_kit_image_url(
            kit["kit_type"], kit["kit_id"], kit.get("front_photo", "")
        )
        kit["version_count"] = version_counts.get(kit["kit_id"], kit.get("version_count", 0))
        kit["avg_rating"] = kit.get("avg_rating", 0.0)
        kit["review_count"] = kit.get("review_count", 0)
        ca = kit.get("created_at")
        if hasattr(ca, "isoformat"):
            kit["created_at"] = ca.isoformat()
        elif not isinstance(ca, str):
            kit["created_at"] = str(ca) if ca else ""
        result.append(kit)

    return {"results": result, "total": total, "skip": skip, "limit": capped_limit}


@router.get("/master-kits/{kit_id}")
async def get_master_kit(kit_id: str):
    from fastapi import HTTPException
    from ._kit_utils import local_image_url
    kit = await db.master_kits.find_one(
        {"$or": [{"kit_id": kit_id}, {"id": kit_id}]},
        {"_id": 0},
    )
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    kit["kit_id"] = kit.get("kit_id") or kit.get("id", "")
    kit["kit_type"] = kit.get("kit_type") or kit.get("type", "")
    kit["front_photo"] = master_kit_image_url(
        kit["kit_type"], kit["kit_id"], kit.get("front_photo", "")
    )
    ca = kit.get("created_at")
    if hasattr(ca, "isoformat"):
        kit["created_at"] = ca.isoformat()
    elif not isinstance(ca, str):
        kit["created_at"] = str(ca) if ca else ""

    kit_id_val = kit["kit_id"]
    versions = await db.versions.find({"kit_id": kit_id_val}, {"_id": 0}).to_list(100)
    for v in versions:
        v["avg_rating"] = v.get("avg_rating", 0.0)
        v["review_count"] = v.get("review_count", 0)
        v["front_photo"] = local_image_url(v.get("front_photo", ""))
        v["back_photo"] = local_image_url(v.get("back_photo", ""))
    kit["versions"] = versions
    kit["version_count"] = len(versions)

    version_ids = [v.get("version_id") for v in versions if v.get("version_id")]
    if version_ids:
        all_reviews = await db.reviews.find(
            {"version_id": {"$in": version_ids}}, {"rating": 1, "_id": 0}
        ).to_list(5000)
        kit["avg_rating"] = (
            round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1)
            if all_reviews else kit.get("avg_rating", 0.0)
        )
        kit["review_count"] = len(all_reviews) if all_reviews else kit.get("review_count", 0)
    else:
        kit["avg_rating"] = kit.get("avg_rating", 0.0)
        kit["review_count"] = kit.get("review_count", 0)
    return kit


@router.post("/master-kits", response_model=MasterKitOut)
async def create_master_kit(kit: MasterKitCreate, request: Request):
    user = await get_current_user(request)
    doc = kit.model_dump()
    doc["kit_id"] = f"kit_{uuid.uuid4().hex[:12]}"
    doc["created_by"] = user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["avg_rating"] = 0.0
    doc["review_count"] = 0
    doc["version_count"] = 1

    fk_patch = await _create_missing_entity_submissions(
        data=doc, user_id=user["user_id"], parent_submission_id=doc["kit_id"],
    )
    doc.update(fk_patch)
    await db.master_kits.insert_one(doc)

    team_id = doc.get("team_id", "")
    if team_id:
        followers = await db.follows.find(
            {"target_type": "team", "target_id": team_id},
            {"_id": 0, "user_id": 1},
        ).to_list(1000)
        for f in followers:
            await create_notification(
                user_id=f["user_id"],
                notif_type="new_kit",
                title=f"New kit — {doc.get('club', '')}",
                message=f"{doc.get('club', '')} {doc.get('season', '')} {doc.get('kit_type', '')} just added to the catalog.",
                target_type="master_kit",
                target_id=doc["kit_id"],
            )

    default_version = {
        "version_id": f"ver_{uuid.uuid4().hex[:12]}",
        "kit_id": doc["kit_id"],
        "competition": "National Championship",
        "model": "Replica",
        "sku_code": "",
        "ean_code": "",
        "front_photo": doc.get("front_photo", ""),
        "back_photo": "",
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "avg_rating": 0.0,
        "review_count": 0,
    }
    await db.versions.insert_one(default_version)
    result = await db.master_kits.find_one({"kit_id": doc["kit_id"]}, {"_id": 0})
    return result


@router.post("/master-kits/submit", response_model=dict)
async def submit_master_kit(kit: MasterKitCreate, request: Request):
    user = await get_current_user(request)
    now = datetime.now(timezone.utc).isoformat()
    data = kit.model_dump()

    submission_id = f"sub_{uuid.uuid4().hex[:12]}"
    fk_patch = await _create_missing_entity_submissions(
        data=data, user_id=user["user_id"], parent_submission_id=submission_id,
    )
    data.update(fk_patch)

    sub_doc = {
        "submission_id": submission_id,
        "submission_type": "master_kit",
        "data": data,
        "submitted_by": user["user_id"],
        "submitter_name": user.get("name", ""),
        "status": "pending",
        "votes_up": 0,
        "votes_down": 0,
        "voters": [],
        "created_at": now,
    }
    await db.submissions.insert_one(sub_doc)
    result = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    return result
