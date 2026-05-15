# backend/routers/_kit_utils.py
# Helpers partagés entre master_kits.py, versions.py et kits_by_entity.py
import re
import uuid
from datetime import datetime, timezone

from ..database import db

MEDIA_BASE_URL = "https://media.topkit.app"

_LEGACY_HOSTS = ("http://82.67.103.45", "https://82.67.103.45",
                 "https://tp-emergent.onrender.com")


def _normalize_url(url: str) -> str:
    if not url:
        return url
    for host in _LEGACY_HOSTS:
        if url.startswith(host):
            relative = re.sub(r'^https?://[^/]+', '', url)
            return f"{MEDIA_BASE_URL}{relative}"
    return url


def master_kit_image_url(kit_type: str, kit_id: str, stored_photo: str = "") -> str:
    if stored_photo:
        return _normalize_url(stored_photo)
    if not kit_id:
        return ""
    return f"{MEDIA_BASE_URL}/kits/masters/master_{kit_type}_{kit_id}.jpg"


def local_image_url(original_url: str) -> str:
    return _normalize_url(original_url)


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


async def _create_missing_entity_submissions(
    data: dict,
    user_id: str,
    parent_submission_id: str,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    fk_patch = {}

    ENTITY_MAP = [
        {"id_field": "team_id",    "name_field": "club",    "collection": "teams",    "sub_type": "team",    "name_key": "name"},
        {"id_field": "league_id",  "name_field": "league",  "collection": "leagues",  "sub_type": "league",  "name_key": "name"},
        {"id_field": "brand_id",   "name_field": "brand",   "collection": "brands",   "sub_type": "brand",   "name_key": "name"},
        {"id_field": "sponsor_id", "name_field": "sponsor", "collection": "sponsors", "sub_type": "sponsor", "name_key": "name"},
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
        existing = await db[cfg["collection"]].find_one({"slug": slug}, {"_id": 0})
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

        await db.submissions.insert_one({
            "submission_id": submission_id,
            "submission_type": cfg["sub_type"],
            "data": {"mode": "create", cfg["name_key"]: name, "entity_id": new_entity_id, "parent_submission_id": parent_submission_id},
            "submitted_by": user_id,
            "status": "pending",
            "votes_up": 0,
            "votes_down": 0,
            "voters": [],
            "created_at": now,
        })

        fk_patch[cfg["id_field"]] = new_entity_id

    return fk_patch
