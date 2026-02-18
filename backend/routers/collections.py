from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import CollectionAdd, CollectionUpdate
from auth import get_current_user

router = APIRouter(prefix="/api/collections", tags=["collections"])


@router.get("")
async def get_my_collection(request: Request, category: Optional[str] = None):
    user = await get_current_user(request)
    query = {"user_id": user["user_id"]}
    if category:
        query["category"] = category
    items = await db.collections.find(query, {"_id": 0}).sort("added_at", -1).to_list(500)
    enriched = []
    for item in items:
        version = await db.versions.find_one({"version_id": item["version_id"]}, {"_id": 0})
        if version:
            kit = await db.master_kits.find_one({"kit_id": version["kit_id"]}, {"_id": 0})
            item["version"] = version
            item["master_kit"] = kit
        enriched.append(item)
    return enriched


@router.get("/categories")
async def get_collection_categories(request: Request):
    user = await get_current_user(request)
    cats = await db.collections.distinct("category", {"user_id": user["user_id"]})
    return sorted(cats)


@router.post("")
async def add_to_collection(item: CollectionAdd, request: Request):
    user = await get_current_user(request)
    version = await db.versions.find_one({"version_id": item.version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    existing = await db.collections.find_one(
        {"user_id": user["user_id"], "version_id": item.version_id}, {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already in collection")
    # Use estimated_price as the canonical estimation value
    est_price = item.estimated_price or item.value_estimate or item.price_estimate
    doc = {
        "collection_id": f"col_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "version_id": item.version_id,
        "category": item.category or "General",
        "notes": item.notes or "",
        "flocking_type": item.flocking_type or "",
        "flocking_origin": item.flocking_origin or "",
        "flocking_detail": item.flocking_detail or "",
        "condition_origin": item.condition_origin or "",
        "physical_state": item.physical_state or "",
        "size": item.size or "",
        "purchase_cost": item.purchase_cost,
        "estimated_price": est_price,
        "price_estimate": est_price,
        "value_estimate": est_price,
        "signed": item.signed or False,
        "signed_by": item.signed_by or "",
        "signed_proof": item.signed_proof or False,
        "condition": item.condition or "",
        "printing": item.printing or "",
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    await db.collections.insert_one(doc)
    result = await db.collections.find_one({"collection_id": doc["collection_id"]}, {"_id": 0})
    return result


@router.delete("/{collection_id}")
async def remove_from_collection(collection_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.collections.delete_one({"collection_id": collection_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Removed from collection"}


@router.put("/{collection_id}")
async def update_collection_item(collection_id: str, update: CollectionUpdate, request: Request):
    user = await get_current_user(request)
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Sync all estimation fields when any one is updated
    est_price = update_dict.get("estimated_price") or update_dict.get("value_estimate") or update_dict.get("price_estimate")
    if est_price:
        update_dict["estimated_price"] = est_price
        update_dict["price_estimate"] = est_price
        update_dict["value_estimate"] = est_price
    result = await db.collections.update_one(
        {"collection_id": collection_id, "user_id": user["user_id"]},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = await db.collections.find_one({"collection_id": collection_id}, {"_id": 0})
    return updated


@router.get("/stats")
async def get_collection_stats(request: Request):
    user = await get_current_user(request)
    items = await db.collections.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    total = len(items)
    estimates = [i["value_estimate"] for i in items if i.get("value_estimate") and i["value_estimate"] > 0]
    low = min(estimates) * total if estimates else 0
    avg = sum(estimates) if estimates else 0
    high = max(estimates) * total if estimates else 0
    return {
        "total_jerseys": total,
        "estimated_value": {"low": round(low, 2), "average": round(avg, 2), "high": round(high, 2)},
        "items_with_estimates": len(estimates)
    }


@router.get("/category-stats")
async def get_category_stats(request: Request):
    user = await get_current_user(request)
    items = await db.collections.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    categories = {}
    for item in items:
        cat = item.get("category", "General")
        if cat not in categories:
            categories[cat] = {"count": 0, "estimates": []}
        categories[cat]["count"] += 1
        if item.get("value_estimate") and item["value_estimate"] > 0:
            categories[cat]["estimates"].append(item["value_estimate"])
    result = []
    for cat, data in categories.items():
        est = data["estimates"]
        result.append({
            "category": cat,
            "count": data["count"],
            "estimated_value": {
                "low": round(min(est), 2) if est else 0,
                "average": round(sum(est) / len(est), 2) if est else 0,
                "high": round(max(est), 2) if est else 0,
            }
        })
    return result
