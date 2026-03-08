# backend/submission.py
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import SubmissionCreate, VoteCreate, ReportCreate
from auth import get_current_user
from utils import slugify, APPROVAL_THRESHOLD, get_or_create_team_by_name


router = APIRouter(prefix="/api", tags=["submissions"])


ENTITY_COLLECTIONS = {
    "team":   {"collection": "teams",   "id_field": "team_id"},
    "league": {"collection": "leagues", "id_field": "league_id"},
    "brand":  {"collection": "brands",  "id_field": "brand_id"},
    "player": {"collection": "players", "id_field": "player_id"},
}


# ─── Submission Routes ───


@router.post("/submissions")
async def create_submission(sub: SubmissionCreate, request: Request):
    user = await get_current_user(request)
    if sub.submission_type not in ("master_kit", "version", "team", "league", "brand", "player"):
        raise HTTPException(status_code=400, detail="Invalid submission type")
    doc = {
        "submission_id":   f"sub_{uuid.uuid4().hex[:12]}",
        "submission_type": sub.submission_type,
        "data":            sub.data,
        "submitted_by":    user["user_id"],
        "submitter_name":  user.get("name", ""),
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      datetime.now(timezone.utc).isoformat()
    }
    await db.submissions.insert_one(doc)
    result = await db.submissions.find_one({"submission_id": doc["submission_id"]}, {"_id": 0})
    return result


# ─── NEW: Atomic Master Kit Submit ───────────────────────────────────────────
# Crée en une seule requête :
#   1. la submission master_kit
#   2. une submission pending par entité manquante (team / brand / league)
#      avec parent_submission_id → affiché dans RÉFÉRENCES À VALIDER
# Retourne { submission_id, entity_submissions[] }
@router.post("/master-kits/submit")
async def submit_master_kit_atomic(request: Request):
    user = await get_current_user(request)
    body = await request.json()
    now  = datetime.now(timezone.utc).isoformat()

    club      = body.get("club", "").strip()
    brand     = body.get("brand", "").strip()
    league    = body.get("league", "").strip()
    team_id   = body.get("team_id")
    brand_id  = body.get("brand_id")
    league_id = body.get("league_id")

    # 1. Submission master_kit
    kit_sub_id = f"sub_{uuid.uuid4().hex[:12]}"
    kit_sub_doc = {
        "submission_id":   kit_sub_id,
        "submission_type": "master_kit",
        "data": {
            "club":        club,
            "season":      body.get("season", ""),
            "kit_type":    body.get("kit_type", ""),
            "brand":       brand,
            "front_photo": body.get("front_photo", ""),
            "design":      body.get("design", ""),
            "sponsor":     body.get("sponsor", ""),
            "league":      league,
            "gender":      body.get("gender", ""),
            **({"team_id":   team_id}   if team_id   else {}),
            **({"brand_id":  brand_id}  if brand_id  else {}),
            **({"league_id": league_id} if league_id else {}),
        },
        "submitted_by":   user["user_id"],
        "submitter_name": user.get("name", ""),
        "status":         "pending",
        "votes_up":       0,
        "votes_down":     0,
        "voters":         [],
        "created_at":     now,
    }
    await db.submissions.insert_one(kit_sub_doc)

    entity_submissions = []

    async def _create_entity_pending(etype: str, name: str, extra_fields: dict = {}):
        """Insère une entité pending + sa submission liée au master_kit."""
        entity_id_field = f"{etype}_id"
        entity_id       = f"{etype}_{uuid.uuid4().hex[:12]}"
        sub_id          = f"sub_{uuid.uuid4().hex[:12]}"
        collection      = ENTITY_COLLECTIONS[etype]["collection"]

        # Entité pending dans sa collection
        entity_doc = {
            entity_id_field: entity_id,
            "name":          name,
            "slug":          slugify(name),
            "status":        "pending",
            "created_at":    now,
            **extra_fields,
        }
        await db[collection].insert_one(entity_doc)

        # Submission liée
        await db.submissions.insert_one({
            "submission_id":        sub_id,
            "submission_type":      etype,
            "data":                 {"mode": "create", "name": name, "entity_id": entity_id},
            "parent_submission_id": kit_sub_id,
            "submitted_by":         user["user_id"],
            "submitter_name":       user.get("name", ""),
            "status":               "pending",
            "votes_up":             0,
            "votes_down":           0,
            "voters":               [],
            "created_at":           now,
        })
        entity_submissions.append({"type": etype, "submission_id": sub_id, "name": name})
        return entity_id

    # 2a. Team
    if club and not team_id:
        existing = await db.teams.find_one({"name": {"$regex": f"^{club}$", "$options": "i"}}, {"_id": 0})
        if existing:
            # Equipe déjà approuvée → on lie son id dans la submission
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.team_id": existing["team_id"]}}
            )
        else:
            new_team_id = await _create_entity_pending("team", club)
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.team_id": new_team_id}}
            )

    # 2b. Brand
    if brand and not brand_id:
        existing = await db.brands.find_one({"name": {"$regex": f"^{brand}$", "$options": "i"}}, {"_id": 0})
        if existing:
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.brand_id": existing["brand_id"]}}
            )
        else:
            new_brand_id = await _create_entity_pending("brand", brand)
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.brand_id": new_brand_id}}
            )

    # 2c. League
    if league and not league_id:
        existing = await db.leagues.find_one({"name": {"$regex": f"^{league}$", "$options": "i"}}, {"_id": 0})
        if existing:
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.league_id": existing["league_id"]}}
            )
        else:
            new_league_id = await _create_entity_pending("league", league)
            await db.submissions.update_one(
                {"submission_id": kit_sub_id},
                {"$set": {"data.league_id": new_league_id}}
            )

    return {"submission_id": kit_sub_id, "entity_submissions": entity_submissions}
# ─────────────────────────────────────────────────────────────────────────────


@router.get("/pending/submission-id")
async def get_submission_for_entity(entity_type: str, entity_id: str):
    doc = await db["submissions"].find_one({
        "submission_type": entity_type,
        "data.entity_id":  entity_id
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"submission_id": doc["submission_id"]}


# ─── NEW: Linked Refs for a master_kit submission ────────────────────────────
# Utilisé par fetchLinkedRefs() côté frontend après submit_master_kit_atomic
@router.get("/pending/refs")
async def get_pending_refs_for_submission(master_kit_submission_id: str):
    """Retourne les submissions d'entités liées à un master_kit submission."""
    subs = await db.submissions.find(
        {
            "parent_submission_id": master_kit_submission_id,
            "status": "pending",
        },
        {"_id": 0}
    ).to_list(100)

    result = {"team": [], "league": [], "brand": [], "player": []}
    for sub in subs:
        etype = sub.get("submission_type")
        if etype not in result:
            continue
        entity_id = sub["data"].get("entity_id")
        name      = sub["data"].get("name") or sub["data"].get("full_name", "")
        item = {
            "submission_id": sub["submission_id"],
            "name":          name,
            f"{etype}_id":   entity_id,
        }
        result[etype].append(item)

    return result
# ─────────────────────────────────────────────────────────────────────────────


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
    user         = await get_current_user(request)
    user_role    = user.get("role", "user")
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
    inc_field   = "votes_up" if vote.vote == "up" else "votes_down"

    await db.submissions.update_one(
        {"submission_id": submission_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )

    updated_sub = await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})

    # ── APPROBATION ──
    if updated_sub["votes_up"] >= APPROVAL_THRESHOLD:
        data = updated_sub["data"]

        if updated_sub["submission_type"] == "master_kit":
            kit_id  = f"kit_{uuid.uuid4().hex[:12]}"
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
                "created_by":  updated_sub["submitted_by"],
                "created_at":  datetime.now(timezone.utc).isoformat()
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

        elif updated_sub["submission_type"] in ("team", "league", "brand", "player"):
            await _apply_entity_submission(updated_sub)

        await db.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": {"status": "approved"}}
        )

    # ── REJET ──
    elif updated_sub["votes_down"] >= APPROVAL_THRESHOLD:
        entity_type = updated_sub["submission_type"]
        if entity_type in ENTITY_COLLECTIONS:
            entity_id = updated_sub["data"].get("entity_id")
            config    = ENTITY_COLLECTIONS[entity_type]
            if entity_id:
                await db[config["collection"]].update_one(
                    {config["id_field"]: entity_id},
                    {"$set": {
                        "status":     "rejected",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        await db.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": {"status": "rejected"}}
        )

    return await db.submissions.find_one({"submission_id": submission_id}, {"_id": 0})


async def _apply_entity_submission(updated_sub: dict):
    entity_type = updated_sub["submission_type"]
    data        = updated_sub["data"]
    mode        = data.get("mode", "create")
    now         = datetime.now(timezone.utc).isoformat()
    config      = ENTITY_COLLECTIONS.get(entity_type)
    if not config:
        return

    if mode == "create":
        entity_id = data.get("entity_id")
        if entity_id:
            await db[config["collection"]].update_one(
                {config["id_field"]: entity_id},
                {"$set": {"status": "approved", "updated_at": now}}
            )
        else:
            name   = data.get("name") or data.get("full_name", "")
            slug   = slugify(name)
            new_id = f"{entity_type}_{uuid.uuid4().hex[:12]}"
            doc    = {k: v for k, v in data.items() if k != "mode"}
            doc[config["id_field"]] = new_id
            doc["slug"]             = slug
            doc["status"]           = "approved"
            doc["created_at"]       = now
            doc["updated_at"]       = now
            await db[config["collection"]].insert_one(doc)

    elif mode == "edit":
        entity_id     = data.get("entity_id", "")
        update_fields = {
            k: v for k, v in data.items()
            if k not in ("mode", "entity_id", "entity_type") and v is not None
        }
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

    elif mode == "removal":
        entity_id = data.get("entity_id", "")
        if entity_type == "team" and entity_id:
            await db.teams.delete_one({"team_id": entity_id})
        elif entity_type == "league" and entity_id:
            await db.leagues.delete_one({"league_id": entity_id})
        elif entity_type == "brand" and entity_id:
            await db.brands.delete_one({"brand_id": entity_id})
        elif entity_type == "player" and entity_id:
            await db.players.delete_one({"player_id": entity_id})


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
    report_type = report.report_type or "error"
    if report_type not in ("error", "removal"):
        raise HTTPException(status_code=400, detail="report_type must be 'error' or 'removal'")
    doc = {
        "report_id":     f"rep_{uuid.uuid4().hex[:12]}",
        "target_type":   report.target_type,
        "target_id":     report.target_id,
        "report_type":   report_type,
        "original_data": target,
        "corrections":   report.corrections if report_type == "error" else {},
        "notes":         report.notes or "",
        "reported_by":   user["user_id"],
        "reporter_name": user.get("name", ""),
        "status":        "pending",
        "votes_up":      0,
        "votes_down":    0,
        "voters":        [],
        "created_at":    datetime.now(timezone.utc).isoformat()
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
    user         = await get_current_user(request)
    user_role    = user.get("role", "user")
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
    inc_field   = "votes_up" if vote.vote == "up" else "votes_down"

    await db.reports.update_one(
        {"report_id": report_id},
        {"$inc": {inc_field: vote_weight}, "$push": {"voters": user["user_id"]}}
    )
    updated = await db.reports.find_one({"report_id": report_id}, {"_id": 0})

    if updated["votes_up"] >= APPROVAL_THRESHOLD:
        report_type = updated.get("report_type", "error")
        if report_type == "removal":
            if updated["target_type"] == "master_kit":
                await db.versions.delete_many({"kit_id": updated["target_id"]})
                await db.master_kits.delete_one({"kit_id": updated["target_id"]})
            elif updated["target_type"] == "version":
                await db.versions.delete_one({"version_id": updated["target_id"]})
        else:
            corrections = updated["corrections"]
            if updated["target_type"] == "master_kit":
                update_fields = {
                    k: v for k, v in corrections.items()
                    if k not in ("kit_id", "_id")
                }

                new_club = corrections.get("club")
                if new_club:
                    team_id = await get_or_create_team_by_name(new_club)
                    update_fields["club"] = new_club
                    update_fields["team_id"] = team_id

                if update_fields:
                    await db.master_kits.update_one(
                        {"kit_id": updated["target_id"]},
                        {"$set": update_fields}
                    )

            elif updated["target_type"] == "version":
                update_fields = {
                    k: v for k, v in corrections.items()
                    if k not in ("version_id", "_id")
                }
                if update_fields:
                    await db.versions.update_one(
                        {"version_id": updated["target_id"]},
                        {"$set": update_fields}
                    )

        await db.reports.update_one({"report_id": report_id}, {"$set": {"status": "approved"}})

    elif updated["votes_down"] >= APPROVAL_THRESHOLD:
        await db.reports.update_one({"report_id": report_id}, {"$set": {"status": "rejected"}})

    return await db.reports.find_one({"report_id": report_id}, {"_id": 0})
