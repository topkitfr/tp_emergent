from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
from database import db
from models import WishlistAdd
from auth import get_current_user

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])


@router.get("")
async def get_wishlist(request: Request):
    user = await get_current_user(request)
    items = await db.wishlists.find({"user_id": user["user_id"]}, {"_id": 0}).sort("added_at", -1).to_list(500)
    enriched = []
    for item in items:
        version = await db.versions.find_one({"version_id": item["version_id"]}, {"_id": 0})
        if version:
            kit = await db.master_kits.find_one({"kit_id": version["kit_id"]}, {"_id": 0})
            item["version"] = version
            item["master_kit"] = kit
        enriched.append(item)
    return enriched


@router.post("")
async def add_to_wishlist(item: WishlistAdd, request: Request):
    user = await get_current_user(request)
    version = await db.versions.find_one({"version_id": item.version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    existing = await db.wishlists.find_one(
        {"user_id": user["user_id"], "version_id": item.version_id}, {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already in wishlist")
    doc = {
        "wishlist_id": f"wish_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "version_id": item.version_id,
        "notes": item.notes or "",
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    await db.wishlists.insert_one(doc)
    result = await db.wishlists.find_one({"wishlist_id": doc["wishlist_id"]}, {"_id": 0})
    return result


@router.delete("/{wishlist_id}")
async def remove_from_wishlist(wishlist_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.wishlists.delete_one({"wishlist_id": wishlist_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Removed from wishlist"}


@router.get("/check/{version_id}")
async def check_wishlist(version_id: str, request: Request):
    user = await get_current_user(request)
    existing = await db.wishlists.find_one(
        {"user_id": user["user_id"], "version_id": version_id}, {"_id": 0}
    )
    return {
        "in_wishlist": existing is not None,
        "wishlist_id": existing["wishlist_id"] if existing else None
    }
