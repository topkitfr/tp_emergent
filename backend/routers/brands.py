# backend/routers/brands.py
"""Routes CRUD pour les brands (équipementiers)."""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import BrandCreate, BrandOut
from ..auth import get_moderator_user
from ..utils import slugify, safe_regex
from ..image_mirror import mirror_entity_images
from ._entity_helpers import assert_not_locked


router = APIRouter(prefix="/api", tags=["brands"])


@router.get("/brands")
async def list_brands(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": safe_regex(search), "$options": "i"}
    if country:
        query["country"] = {"$regex": safe_regex(country), "$options": "i"}
    total = await db.brands.count_documents(query)
    brands = await db.brands.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for b in brands:
        bid = b.get("brand_id", "")
        b["kit_count"] = await db.master_kits.count_documents({"brand_id": bid}) if bid else 0
    return {"results": brands, "total": total}


@router.get("/brands/{brand_id}")
async def get_brand(brand_id: str):
    brand = await db.brands.find_one({"$or": [{"brand_id": brand_id}, {"slug": brand_id}]}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    bid = brand.get("brand_id", "")
    brand["kit_count"] = await db.master_kits.count_documents({"brand_id": bid}) if bid else 0
    kits = await db.master_kits.find({"brand_id": bid}, {"_id": 0}).sort("season", -1).to_list(500) if bid else []
    brand["kits"] = kits
    return brand


@router.post("/brands", response_model=BrandOut)
async def create_brand(brand: BrandCreate, _user: dict = Depends(get_moderator_user)):
    slug = slugify(brand.name)
    if await db.brands.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Brand already exists")
    doc = brand.model_dump()
    doc["brand_id"]   = f"brand_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "brand", doc["brand_id"])
    await db.brands.insert_one(doc)
    result = await db.brands.find_one({"brand_id": doc["brand_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/brands/pending", response_model=BrandOut)
async def create_brand_pending(
    brand: BrandCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(brand.name)
    existing = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    brand_id      = f"brand_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = brand.model_dump()
    doc["brand_id"]      = brand_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "brand", brand_id)
    await db.brands.insert_one(doc)

    # sub_data inclut les champs image après mirroring pour affichage dans la review
    sub_data = {
        "mode":      "create",
        "name":      brand.name,
        "entity_id": brand_id,
        "logo_url":  doc.get("logo_url"),
    }
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "brand",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/brands/{brand_id}", response_model=BrandOut, dependencies=[Depends(get_moderator_user)])
async def update_brand(brand_id: str, brand: BrandCreate):
    await assert_not_locked("brands", "brand_id", brand_id)
    existing = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Brand not found")
    update_data = {k: v for k, v in brand.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(brand.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "brand", brand_id)
    await db.brands.update_one({"brand_id": brand_id}, {"$set": update_data})
    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"brand_id": brand_id})
    return result
