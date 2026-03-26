# backend/routers/admin_panel.py
"""
Routes réservées aux admins :
  GET  /api/admin/stats
  GET  /api/admin/users
  POST /api/admin/users/{user_id}/ban
  POST /api/admin/users/{user_id}/unban
  POST /api/admin/users/{user_id}/promote
  POST /api/admin/users/{user_id}/demote
  POST /api/admin/submissions/{submission_id}/approve
  POST /api/admin/submissions/{submission_id}/reject
  POST /api/admin/maintenance          (toggle)
  GET  /api/admin/maintenance
"""
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone, timedelta
from typing import Optional
from ..database import db
from ..auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin-panel"])


def _require_admin(user: dict):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Rôle admin requis.")


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/stats")
async def admin_stats(request: Request):
    user = await get_current_user(request)
    _require_admin(user)

    since_24h = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    since_7d  = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    kits              = await db.master_kits.count_documents({})
    versions          = await db.versions.count_documents({})
    total_users       = await db.users.count_documents({})
    banned_users      = await db.users.count_documents({"is_banned": True})
    moderators        = await db.users.count_documents({"role": "moderator"})
    admins            = await db.users.count_documents({"role": "admin"})
    pending_subs      = await db.submissions.count_documents({"status": "pending"})
    pending_reports   = await db.reports.count_documents({"status": "pending"})
    subs_today        = await db.submissions.count_documents({"created_at": {"$gte": since_24h}})
    subs_7d           = await db.submissions.count_documents({"created_at": {"$gte": since_7d}})
    new_users_7d      = await db.users.count_documents({"created_at": {"$gte": since_7d}})

    return {
        "kits":            kits,
        "versions":        versions,
        "users": {
            "total":    total_users,
            "banned":   banned_users,
            "moderators": moderators,
            "admins":   admins,
            "new_7d":   new_users_7d,
        },
        "submissions": {
            "pending":  pending_subs,
            "today":    subs_today,
            "last_7d":  subs_7d,
        },
        "reports": {
            "pending":  pending_reports,
        }
    }


# ─── Gestion Users ────────────────────────────────────────────────────────────

@router.get("/users")
async def list_users(
    request: Request,
    page: int = 1,
    per_page: int = 30,
    search: Optional[str] = None,
    role: Optional[str] = None,
    banned: Optional[bool] = None,
):
    user = await get_current_user(request)
    _require_admin(user)

    query: dict = {}
    if search:
        query["$or"] = [
            {"name":     {"$regex": search, "$options": "i"}},
            {"email":    {"$regex": search, "$options": "i"}},
            {"username": {"$regex": search, "$options": "i"}},
        ]
    if role:
        query["role"] = role
    if banned is not None:
        query["is_banned"] = banned

    skip = (page - 1) * per_page
    total = await db.users.count_documents(query)
    users = await db.users.find(
        query,
        {"_id": 0, "password_hash": 0}
    ).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)

    return {"total": total, "page": page, "per_page": per_page, "users": users}


@router.post("/users/{user_id}/ban")
async def ban_user(user_id: str, request: Request):
    admin = await get_current_user(request)
    _require_admin(admin)

    target = await db.users.find_one({"user_id": user_id}, {"_id": 0, "role": 1})
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    if target.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Impossible de bannir un admin.")

    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": True, "banned_at": now, "banned_by": admin["user_id"]}}
    )
    # Invalider toutes les sessions de l'utilisateur
    await db.user_sessions.delete_many({"user_id": user_id})
    return {"message": "Utilisateur banni.", "user_id": user_id}


@router.post("/users/{user_id}/unban")
async def unban_user(user_id: str, request: Request):
    admin = await get_current_user(request)
    _require_admin(admin)

    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": False}, "$unset": {"banned_at": "", "banned_by": ""}}
    )
    return {"message": "Utilisateur débanni.", "user_id": user_id}


@router.post("/users/{user_id}/promote")
async def promote_user(user_id: str, request: Request):
    """Passe un user en modérateur."""
    admin = await get_current_user(request)
    _require_admin(admin)

    target = await db.users.find_one({"user_id": user_id}, {"_id": 0, "role": 1})
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    if target.get("role") == "admin":
        raise HTTPException(status_code=400, detail="L'utilisateur est déjà admin.")

    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": "moderator"}}
    )
    return {"message": "Utilisateur promu modérateur.", "user_id": user_id}


@router.post("/users/{user_id}/demote")
async def demote_user(user_id: str, request: Request):
    """Repasse un modérateur en user."""
    admin = await get_current_user(request)
    _require_admin(admin)

    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": "user"}}
    )
    return {"message": "Modérateur rétrogradé en user.", "user_id": user_id}


# ─── Approve / Reject direct (bypass vote) ───────────────────────────────────

@router.post("/submissions/{submission_id}/approve")
async def admin_approve_submission(submission_id: str, request: Request):
    admin = await get_current_user(request)
    _require_admin(admin)

    sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Soumission introuvable.")
    if sub["status"] != "pending":
        raise HTTPException(status_code=400, detail="La soumission n'est plus en attente.")

    # On force le threshold pour déclencher l'approbation via le vote handler
    from ..utils import APPROVAL_THRESHOLD
    now = datetime.now(timezone.utc).isoformat()
    await db.submissions.update_one(
        {"submission_id": submission_id},
        {
            "$set":  {"votes_up": APPROVAL_THRESHOLD, "admin_approved_by": admin["user_id"], "admin_approved_at": now},
            "$push": {"voters": admin["user_id"]},
        }
    )
    # Réutilise la logique d'approbation existante
    from .submissions import vote_on_submission
    from ..models import VoteCreate

    class FakeRequest:
        cookies = {}
        headers = {}

    fake_vote = VoteCreate(vote="up")
    # Direct DB path : on appelle _apply depuis submissions
    from .submissions import _apply_entity_submission
    import uuid

    updated_sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    data = updated_sub["data"]

    if updated_sub["submission_type"] == "master_kit":
        kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        kit_doc = {
            "kit_id":      kit_id,
            "club":        data.get("club", ""),
            "season":      data.get("season", ""),
            "kit_type":    data.get("kit_type", ""),
            "brand":       data.get("brand", ""),
            "front_photo": data.get("front_photo", ""),
            "league":      data.get("league", ""),
            "design":      data.get("design", ""),
            "sponsor":     data.get("sponsor", ""),
            "gender":      data.get("gender", ""),
            "team_id":     data.get("team_id", ""),
            "league_id":   data.get("league_id", ""),
            "brand_id":    data.get("brand_id", ""),
            "created_by":  updated_sub["submitted_by"],
            "created_at":  now,
        }
        await db.master_kits.insert_one(kit_doc)
        await db.versions.insert_one({
            "version_id":  f"ver_{uuid.uuid4().hex[:12]}",
            "kit_id":      kit_id,
            "competition": "National Championship",
            "model":       "Replica",
            "sku_code":    "", "ean_code": "",
            "front_photo": data.get("front_photo", ""),
            "back_photo":  "",
            "created_by":  updated_sub["submitted_by"],
            "created_at":  now,
        })
        linked = await db.submissions.find(
            {"submission_type": {"$in": ["team","league","brand","player","sponsor"]},
             "status": "pending", "data.parent_submission_id": submission_id},
            {"_id": 0}
        ).to_list(50)
        kit_patch = {}
        KIT_ID_FIELDS = {"team": "team_id", "brand": "brand_id", "league": "league_id", "sponsor": "sponsor_id"}
        for entity_sub in linked:
            new_eid = await _apply_entity_submission(entity_sub)
            await db.submissions.update_one(
                {"submission_id": entity_sub["submission_id"]},
                {"$set": {"status": "approved", "updated_at": now}}
            )
            etype = entity_sub["submission_type"]
            if etype in KIT_ID_FIELDS and new_eid:
                kit_patch[KIT_ID_FIELDS[etype]] = new_eid
        if kit_patch:
            await db.master_kits.update_one({"kit_id": kit_id}, {"$set": kit_patch})

    elif updated_sub["submission_type"] == "version":
        await db.versions.insert_one({
            "version_id":  f"ver_{uuid.uuid4().hex[:12]}",
            "kit_id":      data.get("kit_id", ""),
            "competition": data.get("competition", ""),
            "model":       data.get("model", ""),
            "sku_code":    data.get("sku_code", ""),
            "ean_code":    data.get("ean_code", ""),
            "front_photo": data.get("front_photo", ""),
            "back_photo":  data.get("back_photo", ""),
            "created_by":  updated_sub["submitted_by"],
            "created_at":  now,
        })
    elif updated_sub["submission_type"] in ("team","league","brand","player","sponsor"):
        if not data.get("parent_submission_id"):
            await _apply_entity_submission(updated_sub)

    await db.submissions.update_one(
        {"submission_id": submission_id},
        {"$set": {"status": "approved"}}
    )
    return {"message": "Soumission approuvée.", "submission_id": submission_id}


@router.post("/submissions/{submission_id}/reject")
async def admin_reject_submission(submission_id: str, request: Request):
    admin = await get_current_user(request)
    _require_admin(admin)

    sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Soumission introuvable.")
    if sub["status"] != "pending":
        raise HTTPException(status_code=400, detail="La soumission n'est plus en attente.")

    now = datetime.now(timezone.utc).isoformat()
    if sub["submission_type"] == "master_kit":
        await db.submissions.update_many(
            {"submission_type": {"$in": ["team","league","brand","player","sponsor"]},
             "status": "pending", "data.parent_submission_id": submission_id},
            {"$set": {"status": "rejected", "updated_at": now}}
        )
    await db.submissions.update_one(
        {"submission_id": submission_id},
        {"$set": {"status": "rejected", "admin_rejected_by": admin["user_id"], "updated_at": now}}
    )
    return {"message": "Soumission rejetée.", "submission_id": submission_id}


# ─── Maintenance ─────────────────────────────────────────────────────────────

@router.get("/maintenance")
async def get_maintenance(request: Request):
    # Route publique pour que le front sache si on est en maintenance
    flag = await db.config.find_one({"key": "maintenance_mode"}, {"_id": 0})
    return {"maintenance": flag.get("value", False) if flag else False}


@router.post("/maintenance")
async def toggle_maintenance(request: Request):
    admin = await get_current_user(request)
    _require_admin(admin)

    flag = await db.config.find_one({"key": "maintenance_mode"}, {"_id": 0})
    current = flag.get("value", False) if flag else False
    new_val = not current

    await db.config.update_one(
        {"key": "maintenance_mode"},
        {"$set": {"value": new_val, "updated_at": datetime.now(timezone.utc).isoformat(),
                  "updated_by": admin["user_id"]}},
        upsert=True,
    )
    return {"maintenance": new_val, "message": "Mode maintenance activé." if new_val else "Mode maintenance désactivé."}
