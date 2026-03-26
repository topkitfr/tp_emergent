# backend/routers/reports.py
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from ..database import db
from ..auth import get_current_user
import uuid

router = APIRouter(prefix="/api/reports", tags=["reports"])

ADMIN_ROLES = {"admin", "moderator"}

REASONS = [
    "Image incorrecte",
    "Informations erronées",
    "Doublon",
    "Contenu inapproprié",
    "Autre",
]


class ReportCreate(BaseModel):
    target_type: str   # "kit" | "version" | "submission"
    target_id: str
    reason: str
    comment: Optional[str] = None


# ─── Créer un signalement (user connecté) ────────────────────────────────────

@router.post("", status_code=201)
async def create_report(body: ReportCreate, request: Request):
    user = await get_current_user(request)

    if body.reason not in REASONS:
        raise HTTPException(status_code=400, detail=f"Raison invalide. Valeurs : {REASONS}")
    if body.target_type not in ("kit", "version", "submission"):
        raise HTTPException(status_code=400, detail="target_type invalide.")

    # Anti-doublon : un user ne peut pas signaler le même objet deux fois
    existing = await db.reports.find_one({
        "reported_by": user["user_id"],
        "target_id":   body.target_id,
        "status":      "pending",
    })
    if existing:
        raise HTTPException(status_code=409, detail="Vous avez déjà signalé cet élément.")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "report_id":   f"rep_{uuid.uuid4().hex[:12]}",
        "target_type": body.target_type,
        "target_id":   body.target_id,
        "reason":      body.reason,
        "comment":     body.comment or "",
        "reported_by": user["user_id"],
        "status":      "pending",
        "created_at":  now,
        "updated_at":  now,
    }
    await db.reports.insert_one(doc)
    return {"message": "Signalement envoyé.", "report_id": doc["report_id"]}


# ─── Lister les signalements (admin/mod) ─────────────────────────────────────

@router.get("/admin")
async def list_reports(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = "pending",
    target_type: Optional[str] = None,
):
    user = await get_current_user(request)
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Accès refusé.")

    query: dict = {}
    if status:      query["status"]      = status
    if target_type: query["target_type"] = target_type

    skip  = (page - 1) * per_page
    total = await db.reports.count_documents(query)
    docs  = await db.reports.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(per_page).to_list(per_page)

    return {"total": total, "page": page, "per_page": per_page, "reports": docs}


# ─── Résoudre (action prise) ─────────────────────────────────────────────────

@router.post("/admin/{report_id}/resolve")
async def resolve_report(report_id: str, request: Request):
    user = await get_current_user(request)
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Accès refusé.")

    rep = await db.reports.find_one({"report_id": report_id})
    if not rep:
        raise HTTPException(status_code=404, detail="Signalement introuvable.")

    now = datetime.now(timezone.utc).isoformat()
    await db.reports.update_one(
        {"report_id": report_id},
        {"$set": {"status": "resolved", "handled_by": user["user_id"], "updated_at": now}}
    )
    return {"message": "Signalement résolu.", "report_id": report_id}


# ─── Ignorer ─────────────────────────────────────────────────────────────────

@router.post("/admin/{report_id}/dismiss")
async def dismiss_report(report_id: str, request: Request):
    user = await get_current_user(request)
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Accès refusé.")

    rep = await db.reports.find_one({"report_id": report_id})
    if not rep:
        raise HTTPException(status_code=404, detail="Signalement introuvable.")

    now = datetime.now(timezone.utc).isoformat()
    await db.reports.update_one(
        {"report_id": report_id},
        {"$set": {"status": "dismissed", "handled_by": user["user_id"], "updated_at": now}}
    )
    return {"message": "Signalement ignoré.", "report_id": report_id}


# ─── Raisons disponibles (pour le front) ─────────────────────────────────────

@router.get("/reasons")
async def get_reasons():
    return {"reasons": REASONS}
