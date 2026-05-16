from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import db
from ..auth import get_current_user
from .notifications import create_notification

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(name: str, user_id: str) -> dict:
    return {"event": name, "at": _now(), "by": user_id}


async def create_transaction(listing: dict, offer: dict) -> dict:
    """Internal helper called by marketplace router on offer acceptance."""
    is_trade = offer.get("offer_type") in ("trade", "buy_and_trade")
    txn_id = f"txn_{uuid.uuid4().hex[:12]}"
    doc = {
        "transaction_id": txn_id,
        "transaction_type": "trade" if is_trade else "sale",
        "listing_id": listing["listing_id"],
        "offer_id": offer["offer_id"],
        "seller_id": listing["user_id"],
        "buyer_id": offer["offerer_id"],
        "seller_collection_id": listing["collection_id"],
        "buyer_collection_id": offer.get("offered_collection_id"),
        "agreed_price": offer.get("offered_price"),
        "status": "awaiting_shipment",
        "seller_shipped": False,
        "seller_tracking": None,
        "buyer_shipped": False,
        "buyer_received": False,
        "seller_received": False,
        "buyer_approved": False,
        "seller_approved": False,
        "dispute_opened_by": None,
        "dispute_reason": None,
        "timeline": [{"event": "created", "at": _now(), "by": "system"}],
        "created_at": _now(),
        "updated_at": _now(),
        "completed_at": None,
    }
    await db.transactions.insert_one(doc)
    # Lock collection items so they can't be re-listed during escrow
    await db.collections.update_one(
        {"collection_id": listing["collection_id"]},
        {"$set": {"locked": True, "locked_by_transaction": txn_id}}
    )
    if offer.get("offered_collection_id"):
        await db.collections.update_one(
            {"collection_id": offer["offered_collection_id"]},
            {"$set": {"locked": True, "locked_by_transaction": txn_id}}
        )
    return doc


async def _complete_transaction(txn: dict):
    """Transfers item ownership and finalises the transaction."""
    txn_id = txn["transaction_id"]
    is_trade = txn["transaction_type"] == "trade"

    # Seller's item: remove from seller, add to buyer
    seller_item = await db.collections.find_one(
        {"collection_id": txn["seller_collection_id"]}, {"_id": 0}
    )
    if seller_item:
        new_col_id = f"col_{uuid.uuid4().hex[:12]}"
        buyer_copy = {**seller_item, "collection_id": new_col_id,
                      "user_id": txn["buyer_id"], "locked": False,
                      "locked_by_transaction": None,
                      "added_at": _now()}
        await db.collections.insert_one(buyer_copy)
        await db.collections.delete_one({"collection_id": txn["seller_collection_id"]})

    if is_trade and txn.get("buyer_collection_id"):
        buyer_item = await db.collections.find_one(
            {"collection_id": txn["buyer_collection_id"]}, {"_id": 0}
        )
        if buyer_item:
            new_col_id2 = f"col_{uuid.uuid4().hex[:12]}"
            seller_copy = {**buyer_item, "collection_id": new_col_id2,
                           "user_id": txn["seller_id"], "locked": False,
                           "locked_by_transaction": None,
                           "added_at": _now()}
            await db.collections.insert_one(seller_copy)
            await db.collections.delete_one({"collection_id": txn["buyer_collection_id"]})

    # Finalise listing and transaction
    await db.listings.update_one(
        {"listing_id": txn["listing_id"]},
        {"$set": {"status": "completed", "updated_at": _now()}}
    )
    now = _now()
    await db.transactions.update_one(
        {"transaction_id": txn_id},
        {"$set": {"status": "completed", "completed_at": now, "updated_at": now},
         "$push": {"timeline": _event("completed", "system")}}
    )
    # Notify both parties
    await create_notification(
        user_id=txn["buyer_id"], notif_type="transaction_completed",
        title="Transaction finalisée !",
        message="Le maillot a été ajouté à votre collection.",
        target_type="transaction", target_id=txn_id,
    )
    await create_notification(
        user_id=txn["seller_id"], notif_type="transaction_completed",
        title="Transaction finalisée !",
        message="La vente est terminée. Le maillot a quitté votre collection.",
        target_type="transaction", target_id=txn_id,
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("")
async def list_transactions(request: Request, role: Optional[str] = None):
    user = await get_current_user(request)
    uid = user["user_id"]
    if role == "buyer":
        query = {"buyer_id": uid}
    elif role == "seller":
        query = {"seller_id": uid}
    else:
        query = {"$or": [{"seller_id": uid}, {"buyer_id": uid}]}
    txns = await db.transactions.find(query, {"_id": 0}).sort("created_at", -1).to_list(200)

    # Enrich with kit snapshot
    for t in txns:
        col = await db.collections.find_one({"collection_id": t["seller_collection_id"]}, {"_id": 0})
        if col:
            version = await db.versions.find_one({"version_id": col.get("version_id", "")}, {"_id": 0})
            kit = await db.master_kits.find_one({"kit_id": (version or {}).get("kit_id", "")}, {"_id": 0}) if version else None
            t["kit_snapshot"] = {**(version or {}), **(kit or {})}
        seller = await db.users.find_one({"user_id": t["seller_id"]}, {"_id": 0, "username": 1, "name": 1, "picture": 1})
        buyer  = await db.users.find_one({"user_id": t["buyer_id"]},  {"_id": 0, "username": 1, "name": 1, "picture": 1})
        t["seller"] = seller or {}
        t["buyer"]  = buyer or {}
    return txns


@router.get("/pending-action")
async def pending_action_count(request: Request):
    """Returns count of transactions where the caller has a pending action."""
    user = await get_current_user(request)
    uid = user["user_id"]
    txns = await db.transactions.find(
        {"$or": [{"seller_id": uid}, {"buyer_id": uid}],
         "status": {"$nin": ["completed", "disputed"]}},
        {"_id": 0}
    ).to_list(200)
    count = 0
    for t in txns:
        is_seller = t["seller_id"] == uid
        is_trade  = t["transaction_type"] == "trade"
        s = t["status"]
        if is_seller and s == "awaiting_shipment" and not t["seller_shipped"]:
            count += 1
        elif not is_seller and s == "shipped" and not t["buyer_received"]:
            count += 1
        elif not is_seller and s == "delivered" and not t["buyer_approved"]:
            count += 1
        elif is_trade and is_seller and s == "delivered" and not t["seller_approved"]:
            count += 1
        elif is_trade and not is_seller and s == "awaiting_shipment" and not t["buyer_shipped"]:
            count += 1
    return {"count": count}


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    txn  = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != uid and txn["buyer_id"] != uid:
        raise HTTPException(status_code=403, detail="Not your transaction")
    col = await db.collections.find_one({"collection_id": txn["seller_collection_id"]}, {"_id": 0})
    if col:
        version = await db.versions.find_one({"version_id": col.get("version_id", "")}, {"_id": 0})
        kit = await db.master_kits.find_one({"kit_id": (version or {}).get("kit_id", "")}, {"_id": 0}) if version else None
        txn["kit_snapshot"] = {**(version or {}), **(kit or {})}
    seller = await db.users.find_one({"user_id": txn["seller_id"]}, {"_id": 0, "username": 1, "name": 1, "picture": 1})
    buyer  = await db.users.find_one({"user_id": txn["buyer_id"]},  {"_id": 0, "username": 1, "name": 1, "picture": 1})
    txn["seller"] = seller or {}
    txn["buyer"]  = buyer or {}
    return txn


@router.post("/{transaction_id}/ship")
async def mark_shipped(transaction_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    body = await request.json()
    tracking = body.get("tracking", "")

    txn = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != uid and txn["buyer_id"] != uid:
        raise HTTPException(status_code=403, detail="Not your transaction")
    if txn["status"] not in ("awaiting_shipment",):
        raise HTTPException(status_code=400, detail="Cannot mark as shipped in current status")

    is_seller = txn["seller_id"] == uid
    is_trade  = txn["transaction_type"] == "trade"

    update: dict = {"updated_at": _now()}
    event_name = "seller_shipped" if is_seller else "buyer_shipped"

    if is_seller:
        if txn["seller_shipped"]:
            raise HTTPException(status_code=400, detail="Already marked as shipped")
        update["seller_shipped"] = True
        if tracking:
            update["seller_tracking"] = tracking
    else:
        if not is_trade:
            raise HTTPException(status_code=403, detail="Only seller ships in a sale")
        if txn["buyer_shipped"]:
            raise HTTPException(status_code=400, detail="Already marked as shipped")
        update["buyer_shipped"] = True
        if tracking:
            update["buyer_tracking"] = tracking

    # Transition to "shipped" when all required parties have shipped
    after_seller = update.get("seller_shipped", txn["seller_shipped"])
    after_buyer  = update.get("buyer_shipped",  txn["buyer_shipped"])
    if after_seller and (not is_trade or after_buyer):
        update["status"] = "shipped"

    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": update, "$push": {"timeline": _event(event_name, uid)}}
    )

    # Notify counterpart
    counterpart_id = txn["buyer_id"] if is_seller else txn["seller_id"]
    await create_notification(
        user_id=counterpart_id, notif_type="transaction_shipped",
        title="Envoi confirmé",
        message="L'expéditeur a confirmé l'envoi de son maillot.",
        target_type="transaction", target_id=transaction_id,
    )
    return {"ok": True}


@router.post("/{transaction_id}/confirm-receipt")
async def confirm_receipt(transaction_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]

    txn = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != uid and txn["buyer_id"] != uid:
        raise HTTPException(status_code=403, detail="Not your transaction")
    if txn["status"] != "shipped":
        raise HTTPException(status_code=400, detail="Cannot confirm receipt in current status")

    is_seller = txn["seller_id"] == uid
    is_trade  = txn["transaction_type"] == "trade"

    update: dict = {"updated_at": _now()}
    event_name = "seller_received" if is_seller else "buyer_received"

    if is_seller:
        if not is_trade:
            raise HTTPException(status_code=403, detail="Only buyer confirms receipt in a sale")
        if txn["seller_received"]:
            raise HTTPException(status_code=400, detail="Already confirmed")
        update["seller_received"] = True
    else:
        if txn["buyer_received"]:
            raise HTTPException(status_code=400, detail="Already confirmed")
        update["buyer_received"] = True

    after_buyer_recv  = update.get("buyer_received",  txn["buyer_received"])
    after_seller_recv = update.get("seller_received", txn["seller_received"])
    if after_buyer_recv and (not is_trade or after_seller_recv):
        update["status"] = "delivered"

    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": update, "$push": {"timeline": _event(event_name, uid)}}
    )

    counterpart_id = txn["buyer_id"] if is_seller else txn["seller_id"]
    await create_notification(
        user_id=counterpart_id, notif_type="transaction_received",
        title="Réception confirmée",
        message="L'autre partie a confirmé avoir reçu le maillot.",
        target_type="transaction", target_id=transaction_id,
    )
    return {"ok": True}


@router.post("/{transaction_id}/approve")
async def approve_transaction(transaction_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]

    txn = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != uid and txn["buyer_id"] != uid:
        raise HTTPException(status_code=403, detail="Not your transaction")
    if txn["status"] != "delivered":
        raise HTTPException(status_code=400, detail="Cannot approve in current status")

    is_seller = txn["seller_id"] == uid
    is_trade  = txn["transaction_type"] == "trade"
    update: dict = {"updated_at": _now()}

    if is_seller:
        if not is_trade:
            raise HTTPException(status_code=403, detail="Only buyer approves in a sale")
        if txn["seller_approved"]:
            raise HTTPException(status_code=400, detail="Already approved")
        update["seller_approved"] = True
    else:
        if txn["buyer_approved"]:
            raise HTTPException(status_code=400, detail="Already approved")
        update["buyer_approved"] = True

    after_buyer_appr  = update.get("buyer_approved",  txn["buyer_approved"])
    after_seller_appr = update.get("seller_approved", txn["seller_approved"])
    both_approved = after_buyer_appr and (not is_trade or after_seller_appr)

    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": update, "$push": {"timeline": _event("approved", uid)}}
    )

    if both_approved:
        refreshed = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
        await _complete_transaction({**txn, **update} if refreshed is None else refreshed)
    else:
        counterpart_id = txn["buyer_id"] if is_seller else txn["seller_id"]
        await create_notification(
            user_id=counterpart_id, notif_type="transaction_approved",
            title="Maillot approuvé",
            message="L'autre partie a approuvé le maillot reçu. En attente de votre validation.",
            target_type="transaction", target_id=transaction_id,
        )
    return {"ok": True}


@router.post("/{transaction_id}/dispute")
async def open_dispute(transaction_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    body = await request.json()
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="Reason is required")

    txn = await db.transactions.find_one({"transaction_id": transaction_id}, {"_id": 0})
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn["seller_id"] != uid and txn["buyer_id"] != uid:
        raise HTTPException(status_code=403, detail="Not your transaction")
    if txn["status"] in ("completed", "disputed"):
        raise HTTPException(status_code=400, detail="Cannot dispute in current status")

    role = "seller" if txn["seller_id"] == uid else "buyer"
    await db.transactions.update_one(
        {"transaction_id": transaction_id},
        {"$set": {
            "status": "disputed",
            "dispute_opened_by": role,
            "dispute_reason": reason,
            "updated_at": _now(),
        },
         "$push": {"timeline": _event("dispute_opened", uid)}}
    )
    # Notify counterpart and moderators
    counterpart_id = txn["buyer_id"] if role == "seller" else txn["seller_id"]
    await create_notification(
        user_id=counterpart_id, notif_type="transaction_disputed",
        title="Litige ouvert",
        message=f"Un litige a été ouvert sur cette transaction : {reason[:80]}",
        target_type="transaction", target_id=transaction_id,
    )
    moderators = await db.users.find({"role": "moderator"}, {"_id": 0, "user_id": 1}).to_list(50)
    for mod in moderators:
        await create_notification(
            user_id=mod["user_id"], notif_type="transaction_disputed",
            title="Nouveau litige à traiter",
            message=f"Transaction {transaction_id} : {reason[:80]}",
            target_type="transaction", target_id=transaction_id,
        )
    return {"ok": True}
