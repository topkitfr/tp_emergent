# backend/routers/submissions.py
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
from ..database import db, client
from ..models import SubmissionCreate, VoteCreate, ReportCreate
from ..auth import get_current_user
from ..utils import slugify, APPROVAL_THRESHOLD, get_or_create_team_by_name, check_user_quota, normalize_season
from .notifications import create_notification
from ..email_service import send_submission_result, send_report_result

router = APIRouter(prefix="/api", tags=["submissions"])

ENTITY_COLLECTIONS = {
    "team":    {"collection": "teams",    "id_field": "team_id",    "name_field": "name"},
    "league":  {"collection": "leagues",  "id_field": "league_id",  "name_field": "name"},
    "brand":   {"collection": "brands",   "id_field": "brand_id",   "name_field": "name"},
    "player":  {"collection": "players",  "id_field": "player_id",  "name_field": "full_name"},
    "sponsor": {"collection": "sponsors", "id_field": "sponsor_id", "name_field": "name"},
}

KIT_ID_FIELDS = {
    "team":    "team_id",
    "brand":   "brand_id",
    "league":  "league_id",
    "sponsor": "sponsor_id",
}

IMAGE_FIELDS = {"logo_url", "crest_url", "photo_url", "stadium_image_url"}

SUBMISSION_TYPE_LABELS = {
    "master_kit": "maillot",
    "version":    "version de maillot",
    "team":       "équipe",
    "league":     "championnat",
    "brand":      "marque",
    "player":     "joueur",
    "sponsor":    "sponsor",
}


def _submission_name(sub: dict) -> str:
    data = sub.get("data", {})
    return (
        data.get("club")
        or data.get("name")
        or data.get("full_name")
        or sub.get("submission_id", "")
    )


async def _get_user_email_and_name(user_id: str) -> tuple[str, str]:
    doc = await db.users.find_one(
        {"user_id": user_id},
        {"_id": 0, "email": 1, "name": 1}
    )
    if doc:
        return doc.get("email", ""), doc.get("name", "")
    return "", ""


# ─────────────────────────────────────────────
# Submission Routes
# ─────────────────────────────────────────────

@router.post("/submissions")
async def create_submission(sub: SubmissionCreate, request: Request):
    user = await get_current_user(request)
    if sub.submission_type not in ("master_kit", "version", "team", "league", "brand", "player", "sponsor"):
        raise HTTPException(status_code=400, detail="Invalid submission type")

    # Quota par user (admins et modérateurs exemptés)
    if user.get("role", "user") == "user":
        await check_user_quota(db, user["user_id"], sub.submission_type)

    # Normalisation de la saison à la soumission
    data = sub.data
    if isinstance(data, dict) and data.get("season"):
        data["season"] = normalize_season(data["season"])

    doc = {
        "submission_id": f"sub_{uuid.uuid4().hex[:12]}",
        "submission_type": sub.submission_type,
        "data": data,
        "submitted_by": user["user_id"],
        "submitter_name": user.get("name", ""),
        "submitter_username": user.get("username", ""),
        "status": "pending",
        "votes_up": 0,
        "votes_down": 0,
        "voters": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.submissions.insert_one(doc)
    result = await db.submissions.find_one({"submission_id": doc["submission_id"]}, {"_id": 0})
    return result


@router.get("/pending/refs")
async def get_pending_refs(master_kit_submission_id: str):
    refs = {}
    for etype, cfg in ENTITY_COLLECTIONS.items():
        subs = await db.submissions.find(
            {
                "submission_type": etype,
                "status": "pending",
                "data.parent_submission_id": master_kit_submission_id
            },
            {"_id": 0}
        ).to_list(50)

        items = []
        for s in subs:
            name = (
                s.get("data", {}).get("name")
                or s.get("data", {}).get("full_name")
                or "—"
            )
            items.append({
                "submission_id": s["submission_id"],
                "name": name,
                "status": s["status"],
                "entity_type": etype,
            })
        if items:
            refs[etype] = items

    return refs


@router.get("/pending/submission-id")
async def get_submission_for_entity(entity_type: str, entity_id: str):
    doc = await db["submissions"].find_one({
        "submission_type": entity_type,
        "data.entity_id": entity_id
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"submission_id": doc["submission_id"]}


@router.get("/submissions")
async def list_submissions(status: Optional[str] = "pending", skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    subs = await db.submissions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    # Enrichir submitter_username si absent (anciennes soumissions)
    for s in subs:
        if not s.get("submitter_username") and s.get("submitted_by"):
            u = await db.users.find_one({"user_id": s["submitted_by"]}, {"_id": 0, "username": 1})
            if u:
                s["submitter_username"] = u.get("username", "")
    return subs


@router.get("/submissions/{submission_id}")
async def get_submission(submission_id: str):
    sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@router.post("/submissions/{submission_id}/vote")
async def vote_on_submission(submission_id: str, vote: VoteCreate, request: Request):
    user = await get_current_user(request)
    user_role = user.get("role", "user")
    is_moderator = user_role in ("moderator", "admin")

    if not is_moderator:
        col_count = await db.collections.count_documents({"user_id": user["user_id"]})
        if col_count == 0:
            raise HTTPException(status_code=403, detail="You must have at least 1 jersey in your collection to vote")

    sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")

    if sub["submission_type"] in ("team", "league", "brand", "player", "sponsor"):
        if sub["data"].get("mode", "create") == "create" and sub["data"].get("parent_submission_id"):
            raise HTTPException(
                status_code=400,
                detail="Entity reference submissions are approved automatically when their parent kit is approved."
            )

    if sub["status"] != "pending":
        raise HTTPException(status_code=400, detail="Submission is no longer pending")
    if user["user_id"] in sub.get("voters", []):
        raise HTTPException(status_code=400, detail="Already voted")
    if vote.vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Vote must be 'up' or 'down'")

    if is_moderator and vote.vote == "up":
        vote_weight = APPROVAL_THRESHOLD
    elif user_role == "admin" and vote.vote == "down":
        vote_weight = APPROVAL_THRESHOLD
    else:
        vote_weight = 1

    inc_field = "votes_up" if vote.vote == "up" else "votes_down"

    await db.submissions.update_one(
        {"submission_id": submission_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )

    updated_sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    submitter_id = updated_sub.get("submitted_by", "")
    sub_name = _submission_name(updated_sub)
    sub_type_label = SUBMISSION_TYPE_LABELS.get(updated_sub["submission_type"], updated_sub["submission_type"])

    # ─── APPROBATION ─────────────────────────────────────────────────────────
    if updated_sub["votes_up"] >= APPROVAL_THRESHOLD:
        try:
            data = updated_sub["data"]
            kit_submission_id = updated_sub["submission_id"]

            if updated_sub["submission_type"] == "master_kit":
                kit_id = f"kit_{uuid.uuid4().hex[:12]}"
                # Normalisation saison à l'approbation (filet de sécurité)
                season = normalize_season(data.get("season", ""))
                kit_doc = {
                    "kit_id":      kit_id,
                    "club":        data.get("club", ""),
                    "season":      season,
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
                    "created_at":  datetime.now(timezone.utc).isoformat(),
                }
                await db.master_kits.insert_one(kit_doc)
                await db.versions.insert_one({
                    "version_id":  f"ver_{uuid.uuid4().hex[:12]}",
                    "kit_id":      kit_id,
                    "competition": "National Championship",
                    "model":       "Replica",
                    "sku_code":    "",
                    "ean_code":    "",
                    "front_photo": data.get("front_photo", ""),
                    "back_photo":  "",
                    "created_by":  updated_sub["submitted_by"],
                    "created_at":  datetime.now(timezone.utc).isoformat()
                })

                now_iso = datetime.now(timezone.utc).isoformat()
                linked_entity_subs = await db.submissions.find(
                    {
                        "submission_type": {"$in": ["team", "league", "brand", "player", "sponsor"]},
                        "status": "pending",
                        "data.parent_submission_id": kit_submission_id
                    },
                    {"_id": 0}
                ).to_list(50)

                kit_patch = {}
                for entity_sub in linked_entity_subs:
                    new_entity_id = await _apply_entity_submission(entity_sub)
                    await db.submissions.update_one(
                        {"submission_id": entity_sub["submission_id"]},
                        {"$set": {"status": "approved", "updated_at": now_iso}}
                    )
                    etype = entity_sub["submission_type"]
                    if etype in KIT_ID_FIELDS and new_entity_id:
                        kit_patch[KIT_ID_FIELDS[etype]] = new_entity_id

                if kit_patch:
                    await db.master_kits.update_one({"kit_id": kit_id}, {"$set": kit_patch})

                for cfg in ENTITY_COLLECTIONS.values():
                    await db[cfg["collection"]].update_many(
                        {"submission_id": kit_submission_id, "status": "pending"},
                        {"$set": {"status": "approved", "updated_at": now_iso}}
                    )

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
                    "created_at":  datetime.now(timezone.utc).isoformat()
                })

            elif updated_sub["submission_type"] in ("team", "league", "brand", "player", "sponsor"):
                if not data.get("parent_submission_id"):
                    await _apply_entity_submission(updated_sub)

            await db.submissions.update_one(
                {"submission_id": submission_id},
                {"$set": {"status": "approved"}}
            )

            if submitter_id:
                await create_notification(
                    user_id=submitter_id,
                    notif_type="submission_approved",
                    title="Soumission approuvée ✅",
                    message=f"Votre {sub_type_label} « {sub_name} » a été approuvé(e) par la communauté.",
                    target_type=updated_sub["submission_type"],
                    target_id=updated_sub.get("data", {}).get("kit_id", ""),
                    submission_id=submission_id,
                )
                email, name = await _get_user_email_and_name(submitter_id)
                if email:
                    await send_submission_result(email, name, sub_name, approved=True)

        except Exception as e:
            print(f"[CASCADE ERROR] {e}")

    # ─── REJET ───────────────────────────────────────────────────────────────
    elif updated_sub["votes_down"] >= APPROVAL_THRESHOLD:
        now_iso = datetime.now(timezone.utc).isoformat()
        kit_submission_id = updated_sub["submission_id"]

        if updated_sub["submission_type"] == "master_kit":
            await db.submissions.update_many(
                {
                    "submission_type": {"$in": ["team", "league", "brand", "player", "sponsor"]},
                    "status": "pending",
                    "data.parent_submission_id": kit_submission_id
                },
                {"$set": {"status": "rejected", "updated_at": now_iso}}
            )
            for cfg in ENTITY_COLLECTIONS.values():
                await db[cfg["collection"]].update_many(
                    {"submission_id": kit_submission_id, "status": "pending"},
                    {"$set": {"status": "rejected", "updated_at": now_iso}}
                )

        await db.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": {"status": "rejected"}}
        )

        if submitter_id:
            await create_notification(
                user_id=submitter_id,
                notif_type="submission_rejected",
                title="Soumission rejetée ❌",
                message=f"Votre {sub_type_label} « {sub_name} » a été rejeté(e) par la communauté.",
                target_type=updated_sub["submission_type"],
                submission_id=submission_id,
            )
            email, name = await _get_user_email_and_name(submitter_id)
            if email:
                await send_report_result(email, name, sub_type_label, sub_name, approved=False, report_type="error")

    return await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})


# ─────────────────────────────────────────────
# Helper interne
# ─────────────────────────────────────────────

async def _apply_entity_submission(updated_sub: dict) -> Optional[str]:
    entity_type = updated_sub["submission_type"]
    data = updated_sub["data"]
    mode = data.get("mode", "create")
    now = datetime.now(timezone.utc).isoformat()
    config = ENTITY_COLLECTIONS.get(entity_type)
    if not config:
        return None

    sub_id = updated_sub.get("submission_id")

    if mode == "create":
        entity_id = data.get("entity_id")
        if entity_id:
            update_doc = {k: v for k, v in data.items() if k not in ("mode", "parent_submission_id", "entity_id", "entity_type")}
            update_doc["status"] = "approved"
            update_doc["updated_at"] = now
            await db[config["collection"]].update_one(
                {config["id_field"]: entity_id},
                {"$set": update_doc}
            )
            return entity_id
        else:
            name = data.get("name") or data.get("full_name", "")
            slug = slugify(name)
            new_id = f"{entity_type}_{uuid.uuid4().hex[:12]}"
            doc = {k: v for k, v in data.items() if k not in ("mode", "parent_submission_id")}
            doc[config["id_field"]] = new_id
            doc["slug"]       = slug
            doc["status"]     = "approved"
            doc["created_at"] = now
            doc["updated_at"] = now
            if sub_id:
                doc["submission_id"] = sub_id
            await db[config["collection"]].insert_one(doc)
            return new_id

    elif mode == "edit":
        entity_id = data.get("entity_id", "")
        update_fields = {}
        for k, v in data.items():
            if k in ("mode", "entity_id", "entity_type", "parent_submission_id"):
                continue
            if k in IMAGE_FIELDS:
                if v is not None:
                    update_fields[k] = v
            else:
                if v is not None and v != [] and (v != "" or k in IMAGE_FIELDS):
                    update_fields[k] = v

        update_fields["updated_at"] = now
        update_fields["status"]     = "approved"

        name_key = "full_name" if entity_type == "player" else "name"
        if name_key in update_fields:
            update_fields["slug"] = slugify(update_fields[name_key])

        if entity_id:
            await db[config["collection"]].update_one(
                {config["id_field"]: entity_id},
                {"$set": update_fields}
            )
        return entity_id

    elif mode == "removal":
        entity_id = data.get("entity_id", "")
        if entity_id:
            await db[config["collection"]].delete_one(
                {config["id_field"]: entity_id}
            )
        return None

    return None


# ─────────────────────────────────────────────
# Report Routes
# ─────────────────────────────────────────────

@router.post("/reports")
async def create_report(report: ReportCreate, request: Request):
    user = await get_current_user(request)
    if report.target_type == "master_kit":
        target = await db.master_kits.find_one({"kit_id": report.target_id}, {"_id": 0})
    elif report.target_type == "version":
        target = await db.versions.find_one({"version_id": report.target_id}, {"_id": 0})
    else:
        raise HTTPException(status_code=400, detail="Invalid target type")
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    report_type = report.report_type or "error"
    if report_type not in ("error", "removal"):
        raise HTTPException(status_code=400, detail="report_type must be 'error' or 'removal'")

    doc = {
        "report_id":       f"rep_{uuid.uuid4().hex[:12]}",
        "target_type":     report.target_type,
        "target_id":       report.target_id,
        "report_type":     report_type,
        "original_data":   target,
        "corrections":     report.corrections if report_type == "error" else {},
        "notes":           report.notes or "",
        "reported_by":     user["user_id"],
        "reporter_name":   user.get("name", ""),
        "reporter_username": user.get("username", ""),
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      datetime.now(timezone.utc).isoformat()
    }
    await db.reports.insert_one(doc)
    result = await db.reports.find_one({"report_id": doc["report_id"]}, {"_id": 0})
    return result


@router.get("/reports")
async def list_reports(status: Optional[str] = "pending", skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    reports = await db.reports.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    # Enrichir reporter_username si absent (anciens reports)
    for rep in reports:
        if not rep.get("reporter_username") and rep.get("reported_by"):
            u = await db.users.find_one({"user_id": rep["reported_by"]}, {"_id": 0, "username": 1})
            if u:
                rep["reporter_username"] = u.get("username", "")
    return reports


@router.post("/reports/{report_id}/vote")
async def vote_on_report(report_id: str, vote: VoteCreate, request: Request):
    user = await get_current_user(request)
    user_role = user.get("role", "user")
    is_moderator = user_role in ("moderator", "admin")

    if not is_moderator:
        col_count = await db.collections.count_documents({"user_id": user["user_id"]})
        if col_count == 0:
            raise HTTPException(status_code=403, detail="You must have at least 1 jersey in your collection to vote")

    report = await db.reports.find_one({"report_id": report_id}, {"_id": 0})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report["status"] != "pending":
        raise HTTPException(status_code=400, detail="Report is no longer pending")
    if user["user_id"] in report.get("voters", []):
        raise HTTPException(status_code=400, detail="Already voted")
    if vote.vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Vote must be 'up' or 'down'")

    if is_moderator and vote.vote == "up":
        vote_weight = APPROVAL_THRESHOLD
    elif user_role == "admin" and vote.vote == "down":
        vote_weight = APPROVAL_THRESHOLD
    else:
        vote_weight = 1

    inc_field = "votes_up" if vote.vote == "up" else "votes_down"

    await db.reports.update_one(
        {"report_id": report_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )
    updated = await db.reports.find_one({"report_id": report_id}, {"_id": 0})
    reporter_id = updated.get("reported_by", "")

    target_label = "maillot" if updated["target_type"] == "master_kit" else "version"
    target_name = updated.get("original_data", {}).get("club", updated["target_id"])
    report_type  = updated.get("report_type", "error")

    if updated["votes_up"] >= APPROVAL_THRESHOLD:
        if report_type == "removal":
            if updated["target_type"] == "master_kit":
                await db.versions.delete_many({"kit_id": updated["target_id"]})
                await db.master_kits.delete_one({"kit_id": updated["target_id"]})
            elif updated["target_type"] == "version":
                await db.versions.delete_one({"version_id": updated["target_id"]})
        else:
            corrections = updated["corrections"]
            # Normaliser la saison si elle est corrigée
            if "season" in corrections:
                corrections["season"] = normalize_season(corrections["season"])
            if updated["target_type"] == "master_kit":
                update_fields = {k: v for k, v in corrections.items() if k not in ("kit_id", "_id")}
                new_club = corrections.get("club")
                if new_club:
                    team_id = await get_or_create_team_by_name(new_club)
                    update_fields["club"]    = new_club
                    update_fields["team_id"] = team_id
                if update_fields:
                    await db.master_kits.update_one({"kit_id": updated["target_id"]}, {"$set": update_fields})
            elif updated["target_type"] == "version":
                update_fields = {k: v for k, v in corrections.items() if k not in ("version_id", "_id")}
                if update_fields:
                    await db.versions.update_one({"version_id": updated["target_id"]}, {"$set": update_fields})
        await db.reports.update_one({"report_id": report_id}, {"$set": {"status": "approved"}})

        if reporter_id:
            msg = (
                f"Votre demande de correction sur le {target_label} « {target_name} » a été approuvée."
                if report_type == "error"
                else f"Votre demande de suppression du {target_label} « {target_name} » a été approuvée."
            )
            await create_notification(
                user_id=reporter_id, notif_type="report_approved",
                title="Signalement approuvé ✅", message=msg,
                target_type=updated["target_type"], target_id=updated["target_id"],
            )
            email, name = await _get_user_email_and_name(reporter_id)
            if email:
                await send_report_result(email, name, target_label, target_name, approved=True, report_type=report_type)

    elif updated["votes_down"] >= APPROVAL_THRESHOLD:
        await db.reports.update_one({"report_id": report_id}, {"$set": {"status": "rejected"}})
        if reporter_id:
            await create_notification(
                user_id=reporter_id, notif_type="report_rejected",
                title="Signalement rejeté ❌",
                message=f"Votre signalement sur le {target_label} « {target_name} » a été rejeté par la communauté.",
                target_type=updated["target_type"], target_id=updated["target_id"],
            )
            email, name = await _get_user_email_and_name(reporter_id)
            if email:
                await send_report_result(email, name, target_label, target_name, approved=False, report_type=report_type)

    return await db.reports.find_one({"report_id": report_id}, {"_id": 0})
