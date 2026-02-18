from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import SubmissionCreate, VoteCreate, ReportCreate
from auth import get_current_user
from utils import slugify, APPROVAL_THRESHOLD

router = APIRouter(prefix="/api", tags=["submissions"])


# ─── Submission Routes ───

@router.post("/submissions")
async def create_submission(sub: SubmissionCreate, request: Request):
    user = await get_current_user(request)
    if sub.submission_type not in ("master_kit", "version", "team", "league", "brand", "player"):
        raise HTTPException(status_code=400, detail="Invalid submission type")
    doc = {
        "submission_id": f"sub_{uuid.uuid4().hex[:12]}",
        "submission_type": sub.submission_type,
        "data": sub.data,
        "submitted_by": user["user_id"],
        "submitter_name": user.get("name", ""),
        "status": "pending",
        "votes_up": 0,
        "votes_down": 0,
        "voters": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.submissions.insert_one(doc)
    result = await db.submissions.find_one({"submission_id": doc["submission_id"]}, {"_id": 0})
    return result


@router.get("/submissions")
async def list_submissions(status: Optional[str] = "pending", skip: int = 0, limit: int = 50):
    query = {}
    if status:
        query["status"] = status
    subs = await db.submissions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
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
    if sub["status"] != "pending":
        raise HTTPException(status_code=400, detail="Submission is no longer pending")
    if user["user_id"] in sub.get("voters", []):
        raise HTTPException(status_code=400, detail="Already voted")
    if vote.vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Vote must be 'up' or 'down'")

    vote_weight = APPROVAL_THRESHOLD if is_moderator and vote.vote == "up" else 1
    inc_field = "votes_up" if vote.vote == "up" else "votes_down"
    await db.submissions.update_one(
        {"submission_id": submission_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )
    updated_sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})
    if updated_sub["votes_up"] >= APPROVAL_THRESHOLD:
        data = updated_sub["data"]
        if updated_sub["submission_type"] == "master_kit":
            kit_id = f"kit_{uuid.uuid4().hex[:12]}"
            kit_doc = {
                "kit_id": kit_id,
                "club": data.get("club", ""),
                "season": data.get("season", ""),
                "kit_type": data.get("kit_type", ""),
                "brand": data.get("brand", ""),
                "front_photo": data.get("front_photo", ""),
                "league": data.get("league", ""),
                "design": data.get("design", ""),
                "sponsor": data.get("sponsor", ""),
                "gender": data.get("gender", ""),
                "created_by": updated_sub["submitted_by"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.master_kits.insert_one(kit_doc)
            default_version = {
                "version_id": f"ver_{uuid.uuid4().hex[:12]}",
                "kit_id": kit_id,
                "competition": "National Championship",
                "model": "Replica",
                "sku_code": "",
                "ean_code": "",
                "front_photo": data.get("front_photo", ""),
                "back_photo": "",
                "created_by": updated_sub["submitted_by"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.versions.insert_one(default_version)
        elif updated_sub["submission_type"] == "version":
            ver_doc = {
                "version_id": f"ver_{uuid.uuid4().hex[:12]}",
                "kit_id": data.get("kit_id", ""),
                "competition": data.get("competition", ""),
                "model": data.get("model", ""),
                "sku_code": data.get("sku_code", ""),
                "ean_code": data.get("ean_code", ""),
                "front_photo": data.get("front_photo", ""),
                "back_photo": data.get("back_photo", ""),
                "created_by": updated_sub["submitted_by"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.versions.insert_one(ver_doc)
        elif updated_sub["submission_type"] in ("team", "league", "brand", "player"):
            await _apply_entity_submission(updated_sub)
        await db.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": {"status": "approved"}}
        )
    return await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})


async def _apply_entity_submission(updated_sub: dict):
    """Apply an approved entity submission (create or edit)."""
    entity_type = updated_sub["submission_type"]
    data = updated_sub["data"]
    mode = data.get("mode", "create")
    now = datetime.now(timezone.utc).isoformat()
    if mode == "create":
        if entity_type == "team":
            slug = slugify(data.get("name", ""))
            if not await db.teams.find_one({"slug": slug}, {"_id": 1}):
                await db.teams.insert_one({
                    "team_id": f"team_{uuid.uuid4().hex[:12]}",
                    "name": data.get("name", ""), "slug": slug,
                    "country": data.get("country", ""), "city": data.get("city", ""),
                    "founded": data.get("founded"), "primary_color": data.get("primary_color", ""),
                    "secondary_color": data.get("secondary_color", ""),
                    "crest_url": data.get("crest_url", ""), "aka": data.get("aka", []),
                    "created_at": now, "updated_at": now
                })
        elif entity_type == "league":
            slug = slugify(data.get("name", ""))
            if not await db.leagues.find_one({"slug": slug}, {"_id": 1}):
                await db.leagues.insert_one({
                    "league_id": f"league_{uuid.uuid4().hex[:12]}",
                    "name": data.get("name", ""), "slug": slug,
                    "country_or_region": data.get("country_or_region", ""),
                    "level": data.get("level", "domestic"),
                    "organizer": data.get("organizer", ""),
                    "logo_url": data.get("logo_url", ""),
                    "created_at": now, "updated_at": now
                })
        elif entity_type == "brand":
            slug = slugify(data.get("name", ""))
            if not await db.brands.find_one({"slug": slug}, {"_id": 1}):
                await db.brands.insert_one({
                    "brand_id": f"brand_{uuid.uuid4().hex[:12]}",
                    "name": data.get("name", ""), "slug": slug,
                    "country": data.get("country", ""),
                    "founded": data.get("founded"),
                    "logo_url": data.get("logo_url", ""),
                    "created_at": now, "updated_at": now
                })
        elif entity_type == "player":
            slug = slugify(data.get("full_name", ""))
            base_slug = slug
            counter = 1
            while await db.players.find_one({"slug": slug}, {"_id": 1}):
                slug = f"{base_slug}-{counter}"
                counter += 1
            await db.players.insert_one({
                "player_id": f"player_{uuid.uuid4().hex[:12]}",
                "full_name": data.get("full_name", ""), "slug": slug,
                "nationality": data.get("nationality", ""),
                "birth_year": data.get("birth_year"),
                "positions": data.get("positions", []),
                "preferred_number": data.get("preferred_number"),
                "photo_url": data.get("photo_url", ""),
                "created_at": now, "updated_at": now
            })
    elif mode == "edit":
        entity_id = data.get("entity_id", "")
        update_fields = {k: v for k, v in data.items() if k not in ("mode", "entity_id", "entity_type") and v is not None}
        update_fields["updated_at"] = now
        if entity_type == "team" and entity_id:
            if "name" in update_fields:
                update_fields["slug"] = slugify(update_fields["name"])
            await db.teams.update_one({"team_id": entity_id}, {"$set": update_fields})
        elif entity_type == "league" and entity_id:
            if "name" in update_fields:
                update_fields["slug"] = slugify(update_fields["name"])
            await db.leagues.update_one({"league_id": entity_id}, {"$set": update_fields})
        elif entity_type == "brand" and entity_id:
            if "name" in update_fields:
                update_fields["slug"] = slugify(update_fields["name"])
            await db.brands.update_one({"brand_id": entity_id}, {"$set": update_fields})
        elif entity_type == "player" and entity_id:
            if "full_name" in update_fields:
                update_fields["slug"] = slugify(update_fields["full_name"])
            await db.players.update_one({"player_id": entity_id}, {"$set": update_fields})


# ─── Report Routes ───

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
    doc = {
        "report_id": f"rep_{uuid.uuid4().hex[:12]}",
        "target_type": report.target_type,
        "target_id": report.target_id,
        "original_data": target,
        "corrections": report.corrections,
        "notes": report.notes or "",
        "reported_by": user["user_id"],
        "reporter_name": user.get("name", ""),
        "status": "pending",
        "votes_up": 0,
        "votes_down": 0,
        "voters": [],
        "created_at": datetime.now(timezone.utc).isoformat()
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

    vote_weight = APPROVAL_THRESHOLD if is_moderator and vote.vote == "up" else 1
    inc_field = "votes_up" if vote.vote == "up" else "votes_down"
    await db.reports.update_one(
        {"report_id": report_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )
    updated = await db.reports.find_one({"report_id": report_id}, {"_id": 0})
    if updated["votes_up"] >= APPROVAL_THRESHOLD:
        corrections = updated["corrections"]
        if updated["target_type"] == "master_kit":
            update_fields = {k: v for k, v in corrections.items() if k not in ("kit_id", "_id")}
            if update_fields:
                await db.master_kits.update_one({"kit_id": updated["target_id"]}, {"$set": update_fields})
        elif updated["target_type"] == "version":
            update_fields = {k: v for k, v in corrections.items() if k not in ("version_id", "_id")}
            if update_fields:
                await db.versions.update_one({"version_id": updated["target_id"]}, {"$set": update_fields})
        await db.reports.update_one({"report_id": report_id}, {"$set": {"status": "approved"}})
    return await db.reports.find_one({"report_id": report_id}, {"_id": 0})
