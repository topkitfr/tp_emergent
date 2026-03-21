# backend/routers/notifications.py
from fastapi import APIRouter, Request
from datetime import datetime, timezone
import uuid
from .database import db, client
from auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


# ─────────────────────────────────────────────
# Helpers — appelés depuis submissions.py / reports.py
# ─────────────────────────────────────────────

async def create_notification(
    user_id: str,
    notif_type: str,   # "submission_approved" | "submission_rejected" | "report_approved" | "report_rejected"
    title: str,
    message: str,
    target_type: str = "",   # "master_kit" | "version" | "team" | "league" | "brand" | "player"
    target_id: str = "",
    submission_id: str = "",
):
    """Crée une notification en base pour un utilisateur donné."""
    doc = {
        "notification_id": f"notif_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "type": notif_type,
        "title": title,
        "message": message,
        "target_type": target_type,
        "target_id": target_id,
        "submission_id": submission_id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.notifications.insert_one(doc)
    return doc


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@router.get("")
async def get_notifications(request: Request):
    """Récupère les notifications de l'utilisateur connecté (les 50 dernières)."""
    user = await get_current_user(request)
    notifs = (
        await db.notifications.find(
            {"user_id": user["user_id"]}, {"_id": 0}
        )
        .sort("created_at", -1)
        .limit(50)
        .to_list(50)
    )
    unread_count = await db.notifications.count_documents(
        {"user_id": user["user_id"], "read": False}
    )
    return {"notifications": notifs, "unread_count": unread_count}


@router.patch("/{notification_id}/read")
async def mark_as_read(notification_id: str, request: Request):
    """Marque une notification comme lue."""
    user = await get_current_user(request)
    await db.notifications.update_one(
        {"notification_id": notification_id, "user_id": user["user_id"]},
        {"$set": {"read": True}},
    )
    return {"ok": True}


@router.patch("/read-all")
async def mark_all_read(request: Request):
    """Marque toutes les notifications de l'utilisateur comme lues."""
    user = await get_current_user(request)
    await db.notifications.update_many(
        {"user_id": user["user_id"], "read": False},
        {"$set": {"read": True}},
    )
    return {"ok": True}


@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, request: Request):
    """Supprime une notification."""
    user = await get_current_user(request)
    await db.notifications.delete_one(
        {"notification_id": notification_id, "user_id": user["user_id"]}
    )
    return {"ok": True}
