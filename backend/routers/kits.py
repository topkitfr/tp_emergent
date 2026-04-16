from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import re

from ..database import db, client
from ..models import MasterKitCreate, MasterKitOut, VersionCreate, VersionOut
from ..auth import get_current_user
from .notifications import create_notification

router = APIRouter(prefix="/api", tags=["kits"])

# ─────────────────────────────────────────────────────────────────
# IMAGE URL → Freebox NAS
# Naming convention:
#   master_kit : kits/masters/master_{kit_type}_{uid}.jpg
#   version    : kits/versions/version_{kit_type}_{league_id}_{uid}.jpg
#   autres     : {folder}/{entity_id}_{uid}.jpg
# ─────────────────────────────────────────────────────────────────
MEDIA_BASE_URL = "https://media.topkit.app"

_LEGACY_HOSTS = ("http://82.67.103.45", "https://82.67.103.45",
                 "https://tp-emergent.onrender.com")


def _normalize_url(url: str) -> str:
    """Convertit toute URL legacy vers media.topkit.app."""
    if not url:
        return url
    for host in _LEGACY_HOSTS:
        if url.startswith(host):
            relative = re.sub(r'^https?://[^/]+', '', url)
            return f"{MEDIA_BASE_URL}{relative}"
    return url


def master_kit_image_url(kit_type: str, kit_id: str, stored_photo: str = "") -> str:
    """
    Retourne l'URL d'image pour un master kit.
    - Si stored_photo est renseigné, on normalise et retourne.
    - Sinon, reconstruction selon la convention : kits/masters/master_{kit_type}_{kit_id}.jpg
    """
    if stored_photo:
        return _normalize_url(stored_photo)
    if not kit_id:
        return ""
    return f"{MEDIA_BASE_URL}/kits/masters/master_{kit_type}_{kit_id}.jpg"


def local_image_url(original_url: str) -> str:
    """Normalise toute URL vers media.topkit.app (versions et autres entités)."""
    return _normalize_url(original_url)


# ═══════════════════════════════════════════════════════════════════
# MASTER KITS
# ═══════════════════════════════════════════════════════════════════


@router.get("/master-kits/count")
async def count_master_kits():
    count = await db.master_kits.count_documents({})
    return {"count": count}


@router.get("/master-kits/filters")
async def get_filters():
    # ── Entités depuis les vraies collections DB (approved) ──
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

    # Fallback : si les collections sont vides, on repasse sur distinct()
    if not clubs:
        raw = await db.master_kits.distinct("club")
        clubs = sorted([c for c in raw if c])
    if not brands:
        raw = await db.master_kits.distinct("brand")
        brands = sorted([b for b in raw if b])
    if not leagues:
        raw = await db.master_kits.distinct("league")
        leagues = sorted([l for l in leagues if l])

    # ── Champs sans collection dédiée → distinct() ──
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
        # Toggle Club / National — valeurs fixes, pas besoin de distinct()
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
    # "club"     → équipes dont type != "National"
    # "national" → équipes dont type == "National"
    team_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
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
    if entity_type:
        query["entity_type"] = entity_type
    if search:
        query["$or"] = [
            {"club": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"season": {"$regex": search, "$options": "i"}},
            {"design": {"$regex": search, "$options": "i"}},
            {"sponsor": {"$regex": search, "$options": "i"}},
        ]

    # ── Filtre Club / National via teams.type ────────────────────────────────
    if team_type in ("club", "national"):
        if team_type == "national":
            # Sélections nationales : type contient "National" (insensible à la casse)
            matching_teams = await db.teams.find(
                {"type": {"$regex": "national", "$options": "i"}},
                {"_id": 0, "team_id": 1},
            ).to_list(2000)
        else:
            # Clubs : type ne contient PAS "National" (ou champ absent)
            matching_teams = await db.teams.find(
                {"$or": [
                    {"type": {"$not": {"$regex": "national", "$options": "i"}}},
                    {"type": {"$exists": False}},
                ]},
                {"_id": 0, "team_id": 1},
            ).to_list(2000)

        team_ids = [t["team_id"] for t in matching_teams if t.get("team_id")]
        if team_ids:
            query["team_id"] = {"$in": team_ids}
        else:
            # Aucune équipe de ce type → résultat vide
            return {"results": [], "total": 0, "skip": skip, "limit": min(limit, 100)}

    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    # ── Tri ──────────────────────────────────────────────────────────────────
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

    # ── version_count dynamique ───────────────────────────────────────────────
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
        # version_count calculé dynamiquement (valeur DB en fallback)
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
    versions = await db.versions.find(
        {"kit_id": kit_id_val}, {"_id": 0}
    ).to_list(100)
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
            {"version_id": {"$in": version_ids}},
            {"rating": 1, "_id": 0},
        ).to_list(5000)
        kit["avg_rating"] = (
            round(
                sum(r["rating"] for r in all_reviews) / len(all_reviews),
                1,
            )
            if all_reviews
            else kit.get("avg_rating", 0.0)
        )
        kit["review_count"] = (
            len(all_reviews) if all_reviews else kit.get("review_count", 0)
        )
    else:
        kit["avg_rating"] = kit.get("avg_rating", 0.0)
        kit["review_count"] = kit.get("review_count", 0)
    return kit


async def _create_missing_entity_submissions(
    data: dict,
    user_id: str,
    parent_submission_id: str,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    fk_patch = {}

    ENTITY_MAP = [
        {
            "id_field": "team_id",
            "name_field": "club",
            "collection": "teams",
            "sub_type": "team",
            "name_key": "name",
        },
        {
            "id_field": "league_id",
            "name_field": "league",
            "collection": "leagues",
            "sub_type": "league",
            "name_key": "name",
        },
        {
            "id_field": "brand_id",
            "name_field": "brand",
            "collection": "brands",
            "sub_type": "brand",
            "name_key": "name",
        },
        {
            "id_field": "sponsor_id",
            "name_field": "sponsor",
            "collection": "sponsors",
            "sub_type": "sponsor",
            "name_key": "name",
        },
    ]

    for cfg in ENTITY_MAP:
        entity_id = data.get(cfg["id_field"], "")
        name = data.get(cfg["name_field"], "")

        if not name:
            continue

        if entity_id:
            exists = await db[cfg["collection"]].find_one(
                {cfg["id_field"]: entity_id}, {"_id": 0, cfg["id_field"]: 1}
            )
            if exists:
                continue

        from ..utils import slugify

        slug = slugify(name)
        existing = await db[cfg["collection"]].find_one(
            {"slug": slug}, {"_id": 0}
        )
        if existing:
            fk_patch[cfg["id_field"]] = existing[cfg["id_field"]]
            continue

        new_entity_id = f"{cfg['sub_type']}_{uuid.uuid4().hex[:12]}"
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"

        entity_doc = {
            cfg["id_field"]: new_entity_id,
            "name": name,
            "slug": slug,
            "status": "for_review",
            "submission_id": submission_id,
            "created_at": now,
            "updated_at": now,
        }
        await db[cfg["collection"]].insert_one(entity_doc)

        sub_data = {
            "mode": "create",
            cfg["name_key"]: name,
            "entity_id": new_entity_id,
            "parent_submission_id": parent_submission_id,
        }
        await db.submissions.insert_one(
            {
                "submission_id": submission_id,
                "submission_type": cfg["sub_type"],
                "data": sub_data,
                "submitted_by": user_id,
                "status": "pending",
                "votes_up": 0,
                "votes_down": 0,
                "voters": [],
                "created_at": now,
            }
        )

        fk_patch[cfg["id_field"]] = new_entity_id

    return fk_patch


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
        data=doc,
        user_id=user["user_id"],
        parent_submission_id=doc["kit_id"],
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
    result = await db.master_kits.find_one(
        {"kit_id": doc["kit_id"]}, {"_id": 0}
    )
    return result


@router.post("/master-kits/submit", response_model=dict)
async def submit_master_kit(kit: MasterKitCreate, request: Request):
    user = await get_current_user(request)
    now = datetime.now(timezone.utc).isoformat()
    data = kit.model_dump()

    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    fk_patch = await _create_missing_entity_submissions(
        data=data,
        user_id=user["user_id"],
        parent_submission_id=submission_id,
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
    result = await db.submissions.find_one(
        {"submission_id": submission_id}, {"_id": 0}
    )
    return result


# ═══════════════════════════════════════════════════════════════════
# VERSIONS
# ═══════════════════════════════════════════════════════════════════


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
            kit_query["club"] = {"$regex": club, "$options": "i"}
        if brand:
            kit_query["brand"] = {"$regex": brand, "$options": "i"}
        if kit_type:
            kit_query["kit_type"] = kit_type
        if season:
            kit_query["season"] = {"$regex": season, "$options": "i"}
        if league:
            kit_query["league"] = league
        if search:
            kit_query["$or"] = [
                {"club": {"$regex": search, "$options": "i"}},
                {"brand": {"$regex": search, "$options": "i"}},
                {"season": {"$regex": search, "$options": "i"}},
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
            k["front_photo"] = master_kit_image_url(
                k["kit_type"], k["kit_id"], k.get("front_photo", "")
            )
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
            i.get("estimated_price")
            or i.get("value_estimate")
            or i.get("price_estimate")
            or 0
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
    player_ids = list(
        {i["flocking_player_id"] for i in items if i.get("flocking_player_id")}
    )
    players = []
    for pid in player_ids:
        p = await db.players.find_one(
            {"$or": [{"player_id": pid}, {"_id": pid}]},
            {"_id": 0},
        )
        if p:
            players.append(
                {
                    "player_id": p.get("player_id") or pid,
                    "full_name": p.get("full_name") or p.get("name", ""),
                    "slug": p.get("slug", ""),
                    "photo_url": p.get("photo_url") or p.get("photo", ""),
                }
            )
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
        raise HTTPException(
            status_code=422, detail="Rating must be between 1 and 5"
        )

    existing = await db.reviews.find_one(
        {"version_id": version_id, "user_id": user["user_id"]}
    )
    if existing:
        await db.reviews.update_one(
            {"version_id": version_id, "user_id": user["user_id"]},
            {"$set": {"rating": rating, "comment": comment}},
        )
    else:
        await db.reviews.insert_one(
            {
                "review_id": f"rev_{uuid.uuid4().hex[:12]}",
                "version_id": version_id,
                "user_id": user["user_id"],
                "user_name": user.get("name", "Anonymous"),
                "user_picture": user.get("picture", ""),
                "rating": rating,
                "comment": comment,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    all_reviews = await db.reviews.find(
        {"version_id": version_id}, {"rating": 1, "_id": 0}
    ).to_list(1000)
    avg = (
        round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1)
        if all_reviews
        else 0.0
    )
    await db.versions.update_one(
        {"version_id": version_id},
        {"$set": {"avg_rating": avg, "review_count": len(all_reviews)}},
    )

    version_doc = await db.versions.find_one(
        {"version_id": version_id}, {"kit_id": 1, "_id": 0}
    )
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
            round(
                sum(r["rating"] for r in kit_reviews) / len(kit_reviews),
                1,
            )
            if kit_reviews
            else 0.0
        )
        await db.master_kits.update_one(
            {"kit_id": kit_id},
            {"$set": {"avg_rating": kit_avg, "review_count": len(kit_reviews)}},
        )
    return {"ok": True, "avg_rating": avg, "review_count": len(all_reviews)}


@router.get("/versions/{version_id}", response_model=VersionOut)
async def get_version(version_id: str):
    version = await db.versions.find_one(
        {"version_id": version_id}, {"_id": 0}
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    version["front_photo"] = local_image_url(version.get("front_photo", ""))
    version["back_photo"] = local_image_url(version.get("back_photo", ""))
    kit = await db.master_kits.find_one(
        {"kit_id": version.get("kit_id")}, {"_id": 0}
    )
    if kit:
        kit["kit_id"] = kit.get("kit_id") or kit.get("id", "")
        kit["kit_type"] = kit.get("kit_type") or kit.get("type", "")
        kit["front_photo"] = master_kit_image_url(
            kit["kit_type"], kit["kit_id"], kit.get("front_photo", "")
        )
        version["master_kit"] = kit
    reviews = await db.reviews.find(
        {"version_id": version_id}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one(
            {"user_id": r.get("user_id")},
            {"_id": 0, "name": 1, "picture": 1},
        )
        if u:
            r["user_name"] = u.get("name")
            r["user_picture"] = u.get("picture")
    version["reviews"] = reviews
    version["avg_rating"] = (
        round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        if reviews
        else version.get("avg_rating", 0.0)
    )
    version["review_count"] = (
        len(reviews) if reviews else version.get("review_count", 0)
    )
    version["collection_count"] = await db.collections.count_documents(
        {"version_id": version_id}
    )
    return version


@router.post("/versions", response_model=VersionOut)
async def create_version(version: VersionCreate, request: Request):
    user = await get_current_user(request)
    kit = await db.master_kits.find_one(
        {"kit_id": version.kit_id}, {"_id": 0}
    )
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
    await db.master_kits.update_one(
        {"kit_id": version.kit_id}, {"$inc": {"version_count": 1}}
    )
    result = await db.versions.find_one(
        {"version_id": doc["version_id"]}, {"_id": 0}
    )
    return result


# ═══════════════════════════════════════════════════════════════════
# PLAYERS PAR KIT
# ═══════════════════════════════════════════════════════════════════


@router.get("/kits/{kit_id}/players")
async def get_kit_players(kit_id: str):
    players = await db.players.find({"kit_id": kit_id}).limit(6).to_list(6)
    return [
        {
            "id": str(p.get("player_id", p.get("_id", ""))),
            "name": p.get("full_name", ""),
            "photo": p.get("photo_url", ""),
        }
        for p in players
    ]


# ═══════════════════════════════════════════════════════════════════
# ENTITÉS → KITS
# ═══════════════════════════════════════════════════════════════════


async def _normalize_kit(doc: dict) -> dict:
    if not doc:
        return {}
    doc["kit_id"] = doc.get("kit_id") or doc.get("id", "")
    doc["kit_type"] = doc.get("kit_type") or doc.get("type", "")
    doc["front_photo"] = master_kit_image_url(
        doc["kit_type"], doc["kit_id"], doc.get("front_photo", "")
    )
    doc["avg_rating"] = doc.get("avg_rating", 0.0)
    doc["review_count"] = doc.get("review_count", 0)
    doc["version_count"] = doc.get("version_count", 0)
    return doc


@router.get("/leagues/{slug}/kits")
async def get_league_kits(slug: str, skip: int = 0, limit: int = 50):
    league = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    league_id = league.get("league_id") or league.get("id")
    if not league_id:
        raise HTTPException(
            status_code=500, detail="League has no league_id"
        )

    query = {"league_id": league_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    return {
        "results": [await _normalize_kit(k) for k in kits],
        "total": total,
        "skip": skip,
        "limit": capped_limit,
    }


@router.get("/brands/{slug}/kits")
async def get_brand_kits(slug: str, skip: int = 0, limit: int = 50):
    brand = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand_id = brand.get("brand_id") or brand.get("id")
    if not brand_id:
        raise HTTPException(
            status_code=500, detail="Brand has no brand_id"
        )

    query = {"brand_id": brand_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    return {
        "results": [await _normalize_kit(k) for k in kits],
        "total": total,
        "skip": skip,
        "limit": capped_limit,
    }


@router.get("/teams/{slug}/kits")
async def get_team_kits(slug: str, skip: int = 0, limit: int = 50):
    team = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_id = team.get("team_id") or team.get("id")
    if not team_id:
        raise HTTPException(
            status_code=500, detail="Team has no team_id"
        )

    query = {"team_id": team_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    return {
        "results": [await _normalize_kit(k) for k in kits],
        "total": total,
        "skip": skip,
        "limit": capped_limit,
    }


@router.get("/players/{slug}/kits")
async def get_player_kits(slug: str, skip: int = 0, limit: int = 50):
    player = await db.players.find_one({"slug": slug}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    player_id = player.get("player_id") or player.get("id")
    if not player_id:
        raise HTTPException(
            status_code=500, detail="Player has no player_id"
        )

    items = await db.collections.find(
        {"flocking_player_id": player_id}, {"_id": 0, "version_id": 1}
    ).to_list(2000)
    version_ids = list(
        {i["version_id"] for i in items if i.get("version_id")}
    )
    if not version_ids:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    versions = await db.versions.find(
        {"version_id": {"$in": version_ids}}, {"_id": 0, "kit_id": 1}
    ).to_list(len(version_ids))
    kit_ids = list({v["kit_id"] for v in versions if v.get("kit_id")})
    if not kit_ids:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    query = {"kit_id": {"$in": kit_ids}}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    return {
        "results": [await _normalize_kit(k) for k in kits],
        "total": total,
        "skip": skip,
        "limit": capped_limit,
    }


@router.get("/sponsors/{slug}/kits")
async def get_sponsor_kits(slug: str, skip: int = 0, limit: int = 50):
    sponsor = await db.sponsors.find_one({"slug": slug}, {"_id": 0})
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sponsor_id = sponsor.get("sponsor_id") or sponsor.get("id")
    name = sponsor.get("name", "")

    query = {}
    if sponsor_id:
        query = {"sponsor_id": sponsor_id}
    elif name:
        query = {"sponsor": {"$regex": f"^{name}$", "$options": "i"}}
    else:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)

    kits_by_id = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1)
        .skip(skip)
        .limit(capped_limit)
        .to_list(capped_limit)
    )

    return {
        "results": [await _normalize_kit(k) for k in kits_by_id],
        "total": total,
        "skip": skip,
        "limit": capped_limit,
    }
