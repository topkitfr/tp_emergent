from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
import uuid
import logging

from ..database import db
from ..auth import get_current_user
from ..models import TransactionReviewCreate
from .. import email_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["transaction-reviews"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── POST /api/transactions/{transaction_id}/review ──────────────────────────

@router.post("/api/transactions/{transaction_id}/review")
async def submit_transaction_review(
    transaction_id: str,
    review: TransactionReviewCreate,
    request: Request,
):
    user = await get_current_user(request)
    uid = user["user_id"]

    # Validate score
    if review.score < 1 or review.score > 5:
        raise HTTPException(status_code=422, detail="score must be between 1 and 5")

    # Validate comment length
    comment = (review.comment or "").strip()
    if len(comment) > 500:
        raise HTTPException(status_code=422, detail="comment must be 500 characters or fewer")

    # Fetch transaction
    txn = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Must be completed
    if txn["status"] != "completed":
        raise HTTPException(status_code=400, detail="Transaction must be completed before leaving a review")

    # Must be a party
    is_seller = txn["seller_id"] == uid
    is_buyer = txn["buyer_id"] == uid
    if not is_seller and not is_buyer:
        raise HTTPException(status_code=403, detail="Not your transaction")

    # Check for duplicate review
    existing = await db.transaction_reviews.find_one(
        {"transaction_id": transaction_id, "reviewer_id": uid}, {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this transaction")

    # Determine role and reviewee
    role = "seller" if is_seller else "buyer"
    reviewee_id = txn["buyer_id"] if is_seller else txn["seller_id"]

    # Get reviewer username
    reviewer_user = await db.users.find_one({"user_id": uid}, {"_id": 0, "username": 1, "name": 1})
    reviewer_username = reviewer_user.get("username") or reviewer_user.get("name") or uid

    # Insert review
    review_id = f"txrev_{uuid.uuid4().hex[:12]}"
    now = _now()
    doc = {
        "review_id": review_id,
        "transaction_id": transaction_id,
        "reviewer_id": uid,
        "reviewer_username": reviewer_username,
        "reviewee_id": reviewee_id,
        "role": role,
        "score": review.score,
        "comment": comment,
        "created_at": now,
    }
    await db.transaction_reviews.insert_one(doc)

    # Send email notification to reviewee
    reviewee_user = await db.users.find_one({"user_id": reviewee_id}, {"_id": 0, "email": 1})
    if reviewee_user and reviewee_user.get("email"):
        try:
            await email_service.send_review_notification_email(
                to_email=reviewee_user["email"],
                reviewer_username=reviewer_username,
                score=review.score,
                comment=comment,
                frontend_url=email_service.FRONTEND_URL,
            )
        except Exception as e:
            logger.error(f"[transaction_reviews] email error: {e}")

    doc.pop("_id", None)
    return doc


# ─── GET /api/users/{user_id}/reviews ────────────────────────────────────────

@router.get("/api/users/{user_id}/reviews")
async def get_user_reviews(user_id: str):
    """Public endpoint — returns reviews received by user_id, newest first."""
    reviews = await db.transaction_reviews.find(
        {"reviewee_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    return reviews


# ─── GET /api/users/{user_id}/reviews/summary ────────────────────────────────

@router.get("/api/users/{user_id}/reviews/summary")
async def get_user_reviews_summary(user_id: str):
    """Public endpoint — returns avg_score (1 decimal) and count."""
    reviews = await db.transaction_reviews.find(
        {"reviewee_id": user_id},
        {"_id": 0, "score": 1}
    ).to_list(10000)
    count = len(reviews)
    if count == 0:
        return {"avg_score": 0.0, "count": 0}
    avg = round(sum(r["score"] for r in reviews) / count, 1)
    return {"avg_score": avg, "count": count}


# ─── GET /api/transactions/reviewed-by-me ────────────────────────────────────

@router.get("/api/transactions/reviewed-by-me")
async def get_my_reviewed_transactions(request: Request):
    """Auth required — returns transaction_ids the caller has already reviewed."""
    user = await get_current_user(request)
    uid = user["user_id"]
    docs = await db.transaction_reviews.find(
        {"reviewer_id": uid},
        {"_id": 0, "transaction_id": 1}
    ).to_list(1000)
    return {"transaction_ids": [d["transaction_id"] for d in docs]}
