# backend/routers/marketplace.py
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import ListingCreate, ListingOut, OfferCreate, OfferOut
from ..auth import get_current_user
from .notifications import create_notification

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

MAX_ACTIVE_LISTINGS = 10
VALID_LISTING_TYPES = {"sale", "trade", "both"}
VALID_OFFER_TYPES = {"buy", "trade", "buy_and_trade"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Browse ─────────────────────────────────────────────────────────────────

@router.get("")
async def list_listings(
    listing_type: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    version_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(48, ge=1, le=100),
):
    query: dict = {"status": "active"}
    if listing_type and listing_type in VALID_LISTING_TYPES:
        query["listing_type"] = listing_type
    if version_id:
        query["version_id"] = version_id
    if min_price is not None or max_price is not None:
        price_filter: dict = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        query["asking_price"] = price_filter

    total = await db.listings.count_documents(query)
    docs = await db.listings.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    # Enrichit chaque listing avec les infos du maillot
    for doc in docs:
        col = await db.collections.find_one({"collection_id": doc["collection_id"]}, {"_id": 0})
        if col:
            version = await db.versions.find_one({"version_id": col["version_id"]}, {"_id": 0})
            doc["kit_snapshot"] = version or {}
        seller = await db.users.find_one({"user_id": doc["user_id"]}, {"_id": 0, "username": 1, "name": 1, "picture": 1})
        doc["seller"] = seller or {}

    return {"results": docs, "total": total, "skip": skip, "limit": limit}


@router.get("/my-listings")
async def my_listings(request: Request):
    user = await get_current_user(request)
    docs = await db.listings.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)

    for doc in docs:
        doc["offer_count"] = await db.offers.count_documents(
            {"listing_id": doc["listing_id"], "status": "pending"}
        )
    return docs


@router.get("/my-offers")
async def my_offers(request: Request):
    user = await get_current_user(request)
    docs = await db.offers.find(
        {"offerer_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)

    for doc in docs:
        listing = await db.listings.find_one({"listing_id": doc["listing_id"]}, {"_id": 0})
        doc["listing"] = listing or {}
    return docs


@router.get("/user/{user_id}")
async def user_listings(user_id: str):
    docs = await db.listings.find(
        {"user_id": user_id, "status": "active"}, {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    for doc in docs:
        col = await db.collections.find_one({"collection_id": doc["collection_id"]}, {"_id": 0})
        if col:
            version = await db.versions.find_one({"version_id": col.get("version_id", "")}, {"_id": 0})
            doc["kit_snapshot"] = version or {}
    return docs


@router.get("/{listing_id}")
async def get_listing(listing_id: str, request: Request):
    listing = await db.listings.find_one({"listing_id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    col = await db.collections.find_one({"collection_id": listing["collection_id"]}, {"_id": 0})
    listing["collection_item"] = col or {}

    if col:
        version = await db.versions.find_one({"version_id": col.get("version_id", "")}, {"_id": 0})
        listing["version"] = version or {}

    seller = await db.users.find_one(
        {"user_id": listing["user_id"]},
        {"_id": 0, "username": 1, "name": 1, "picture": 1}
    )
    listing["seller"] = seller or {}

    # Offres visibles uniquement au vendeur
    try:
        user = await get_current_user(request)
        if user["user_id"] == listing["user_id"]:
            offers = await db.offers.find(
                {"listing_id": listing_id}, {"_id": 0}
            ).sort("created_at", -1).to_list(100)
            for o in offers:
                offerer = await db.users.find_one(
                    {"user_id": o["offerer_id"]},
                    {"_id": 0, "username": 1, "name": 1, "picture": 1}
                )
                o["offerer"] = offerer or {}
                if o.get("offered_collection_id"):
                    offered_col = await db.collections.find_one(
                        {"collection_id": o["offered_collection_id"]}, {"_id": 0}
                    )
                    o["offered_item"] = offered_col or {}
            listing["offers"] = offers
    except Exception:
        pass

    return listing


# ─── Créer / modifier / annuler un listing ──────────────────────────────────

@router.post("", response_model=ListingOut)
async def create_listing(body: ListingCreate, request: Request):
    user = await get_current_user(request)

    if body.listing_type not in VALID_LISTING_TYPES:
        raise HTTPException(status_code=422, detail=f"listing_type must be one of {VALID_LISTING_TYPES}")
    if body.listing_type in ("sale", "both") and not body.asking_price:
        raise HTTPException(status_code=422, detail="asking_price required for sale or both")
    if body.listing_type in ("trade", "both") and not body.trade_for:
        raise HTTPException(status_code=422, detail="trade_for required for trade or both")

    col = await db.collections.find_one(
        {"collection_id": body.collection_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not col:
        raise HTTPException(status_code=404, detail="Collection item not found or not yours")

    # Vérifie qu'il n'y a pas déjà un listing actif pour ce maillot
    existing = await db.listings.find_one(
        {"collection_id": body.collection_id, "status": "active"}
    )
    if existing:
        raise HTTPException(status_code=400, detail="This item is already listed")

    # Quota anti-spam
    active_count = await db.listings.count_documents(
        {"user_id": user["user_id"], "status": "active"}
    )
    if active_count >= MAX_ACTIVE_LISTINGS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_ACTIVE_LISTINGS} active listings reached")

    now = _now()
    doc = {
        "listing_id": f"lst_{uuid.uuid4().hex[:12]}",
        "collection_id": body.collection_id,
        "user_id": user["user_id"],
        "version_id": col.get("version_id", ""),
        "listing_type": body.listing_type,
        "asking_price": body.asking_price,
        "trade_for": body.trade_for,
        "condition_summary": col.get("physical_state") or col.get("condition", ""),
        "estimated_price": col.get("estimated_price") or col.get("value_estimate"),
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    await db.listings.insert_one(doc)
    result = await db.listings.find_one({"listing_id": doc["listing_id"]}, {"_id": 0})
    return result


@router.put("/{listing_id}")
async def update_listing(listing_id: str, body: dict, request: Request):
    user = await get_current_user(request)
    listing = await db.listings.find_one({"listing_id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your listing")
    if listing["status"] not in ("active", "reserved"):
        raise HTTPException(status_code=400, detail="Cannot edit a completed or cancelled listing")

    allowed = {"asking_price", "trade_for", "listing_type"}
    patch = {k: v for k, v in body.items() if k in allowed}
    patch["updated_at"] = _now()
    await db.listings.update_one({"listing_id": listing_id}, {"$set": patch})
    return await db.listings.find_one({"listing_id": listing_id}, {"_id": 0})


@router.delete("/{listing_id}")
async def cancel_listing(listing_id: str, request: Request):
    user = await get_current_user(request)
    listing = await db.listings.find_one({"listing_id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your listing")
    if listing["status"] in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Listing already closed")

    await db.listings.update_one(
        {"listing_id": listing_id},
        {"$set": {"status": "cancelled", "updated_at": _now()}}
    )
    # Retire les offres pending
    await db.offers.update_many(
        {"listing_id": listing_id, "status": "pending"},
        {"$set": {"status": "withdrawn"}}
    )
    return {"ok": True}


# ─── Offres ─────────────────────────────────────────────────────────────────

@router.post("/{listing_id}/offers", response_model=OfferOut)
async def create_offer(listing_id: str, body: OfferCreate, request: Request):
    user = await get_current_user(request)

    listing = await db.listings.find_one({"listing_id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["status"] != "active":
        raise HTTPException(status_code=400, detail="Listing is not active")
    if listing["user_id"] == user["user_id"]:
        raise HTTPException(status_code=403, detail="Cannot offer on your own listing")

    if body.offer_type not in VALID_OFFER_TYPES:
        raise HTTPException(status_code=422, detail=f"offer_type must be one of {VALID_OFFER_TYPES}")
    if body.offer_type in ("buy", "buy_and_trade") and not body.offered_price:
        raise HTTPException(status_code=422, detail="offered_price required for buy offer")
    if body.offer_type in ("trade", "buy_and_trade") and not body.offered_collection_id:
        raise HTTPException(status_code=422, detail="offered_collection_id required for trade offer")

    # Vérifie que le maillot proposé en échange appartient bien à l'offrant
    if body.offered_collection_id:
        offered_col = await db.collections.find_one(
            {"collection_id": body.offered_collection_id, "user_id": user["user_id"]},
            {"_id": 0}
        )
        if not offered_col:
            raise HTTPException(status_code=404, detail="Offered collection item not found or not yours")

    # Une seule offre pending par user par listing
    existing = await db.offers.find_one({
        "listing_id": listing_id,
        "offerer_id": user["user_id"],
        "status": "pending",
    })
    if existing:
        raise HTTPException(status_code=400, detail="You already have a pending offer on this listing")

    now = _now()
    doc = {
        "offer_id": f"off_{uuid.uuid4().hex[:12]}",
        "listing_id": listing_id,
        "offerer_id": user["user_id"],
        "offer_type": body.offer_type,
        "offered_price": body.offered_price,
        "offered_collection_id": body.offered_collection_id,
        "message": body.message,
        "status": "pending",
        "created_at": now,
    }
    await db.offers.insert_one(doc)

    # Notifie le vendeur
    await create_notification(
        user_id=listing["user_id"],
        notif_type="marketplace_offer",
        title="Nouvelle offre reçue",
        message=f"Quelqu'un a fait une offre sur votre annonce.",
        target_type="listing",
        target_id=listing_id,
    )

    result = await db.offers.find_one({"offer_id": doc["offer_id"]}, {"_id": 0})
    return result


@router.put("/offers/{offer_id}")
async def update_offer(offer_id: str, body: dict, request: Request):
    user = await get_current_user(request)
    offer = await db.offers.find_one({"offer_id": offer_id}, {"_id": 0})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    listing = await db.listings.find_one({"listing_id": offer["listing_id"]}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    new_status = body.get("status")

    # Retrait par l'offrant
    if new_status == "withdrawn":
        if offer["offerer_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Not your offer")
        if offer["status"] != "pending":
            raise HTTPException(status_code=400, detail="Offer is not pending")
        await db.offers.update_one({"offer_id": offer_id}, {"$set": {"status": "withdrawn"}})
        return {"ok": True}

    # Acceptation / refus par le vendeur
    if new_status in ("accepted", "refused"):
        if listing["user_id"] != user["user_id"]:
            raise HTTPException(status_code=403, detail="Not your listing")
        if offer["status"] != "pending":
            raise HTTPException(status_code=400, detail="Offer is not pending")

        await db.offers.update_one({"offer_id": offer_id}, {"$set": {"status": new_status}})

        if new_status == "accepted":
            # Clôture le listing
            await db.listings.update_one(
                {"listing_id": offer["listing_id"]},
                {"$set": {"status": "completed", "updated_at": _now()}}
            )
            # Refuse toutes les autres offres pending
            await db.offers.update_many(
                {"listing_id": offer["listing_id"], "status": "pending", "offer_id": {"$ne": offer_id}},
                {"$set": {"status": "refused"}}
            )
            # Retire le maillot de la collection du vendeur
            await db.collections.delete_one({"collection_id": listing["collection_id"]})

            # Notifie l'acheteur
            await create_notification(
                user_id=offer["offerer_id"],
                notif_type="marketplace_offer_accepted",
                title="Offre acceptée !",
                message="Votre offre a été acceptée. Contactez le vendeur pour finaliser la transaction.",
                target_type="listing",
                target_id=offer["listing_id"],
            )
        else:
            await create_notification(
                user_id=offer["offerer_id"],
                notif_type="marketplace_offer_refused",
                title="Offre refusée",
                message="Votre offre n'a pas été retenue.",
                target_type="listing",
                target_id=offer["listing_id"],
            )
        return {"ok": True}

    raise HTTPException(status_code=422, detail="status must be accepted, refused or withdrawn")
