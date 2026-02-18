from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
from database import db
from models import ReviewCreate
from auth import get_current_user

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("")
async def create_review(review: ReviewCreate, request: Request):
    user = await get_current_user(request)
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    version = await db.versions.find_one({"version_id": review.version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    existing = await db.reviews.find_one(
        {"user_id": user["user_id"], "version_id": review.version_id}, {"_id": 0}
    )
    if existing:
        await db.reviews.update_one(
            {"review_id": existing["review_id"]},
            {"$set": {"rating": review.rating, "comment": review.comment, "created_at": datetime.now(timezone.utc).isoformat()}}
        )
        updated = await db.reviews.find_one({"review_id": existing["review_id"]}, {"_id": 0})
        return updated
    doc = {
        "review_id": f"rev_{uuid.uuid4().hex[:12]}",
        "version_id": review.version_id,
        "kit_id": version["kit_id"],
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "user_picture": user.get("picture", ""),
        "rating": review.rating,
        "comment": review.comment or "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.reviews.insert_one(doc)
    result = await db.reviews.find_one({"review_id": doc["review_id"]}, {"_id": 0})
    return result


@router.get("")
async def get_reviews(version_id: str):
    reviews = await db.reviews.find({"version_id": version_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one({"user_id": r["user_id"]}, {"_id": 0, "name": 1, "picture": 1})
        if u:
            r["user_name"] = u.get("name", "")
            r["user_picture"] = u.get("picture", "")
    return reviews
