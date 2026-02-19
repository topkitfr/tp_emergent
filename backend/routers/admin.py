from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
import uuid
import logging
from database import db
from models import ProfileUpdate
from auth import get_current_user
from utils import slugify, MODERATOR_EMAILS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["admin"])


# ─── Stats ───

@router.get("/stats")
async def get_stats():
    kits = await db.master_kits.count_documents({})
    versions = await db.versions.count_documents({})
    users = await db.users.count_documents({})
    reviews = await db.reviews.count_documents({})
    return {"master_kits": kits, "versions": versions, "users": users, "reviews": reviews}


# ─── User Profile ───

@router.get("/users/by-username/{username}")
async def get_user_by_username(username: str):
    user = await db.users.find_one({"username": username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["user_id"]
    collection_count = await db.collections.count_documents({"user_id": user_id})
    review_count = await db.reviews.count_documents({"user_id": user_id})
    submission_count = await db.submissions.count_documents({"submitted_by": user_id})
    user["collection_count"] = collection_count
    user["review_count"] = review_count
    user["submission_count"] = submission_count
    return user


@router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    collection_count = await db.collections.count_documents({"user_id": user_id})
    review_count = await db.reviews.count_documents({"user_id": user_id})
    submission_count = await db.submissions.count_documents({"submitted_by": user_id})
    user["collection_count"] = collection_count
    user["review_count"] = review_count
    user["submission_count"] = submission_count
    return user


@router.put("/users/profile")
async def update_profile(update: ProfileUpdate, request: Request):
    user = await get_current_user(request)
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "username" in update_dict:
        existing = await db.users.find_one(
            {"username": update_dict["username"], "user_id": {"$ne": user["user_id"]}}, {"_id": 0}
        )
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": update_dict})
    updated = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return updated


# ─── Seed / Import Data ───

@router.post("/seed")
async def seed_data():
    return {"message": "Use POST /api/import-excel to import data from the Excel file"}


@router.post("/import-excel")
async def import_excel():
    import openpyxl

    excel_path = Path("/tmp/Master_Kit_2005_2026.xlsx")
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel file not found at /tmp/Master_Kit_2005_2026.xlsx")

    for col_name in ["master_kits", "versions", "collections", "reviews", "reports", "submissions"]:
        await db[col_name].delete_many({})
    logger.info("Cleared existing data from master_kits, versions, collections, reviews, reports, submissions")

    wb = openpyxl.load_workbook(excel_path, read_only=True)
    imported = 0

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        headers = rows[0]
        col_map = {h: i for i, h in enumerate(headers) if h}

        for idx, row in enumerate(rows[1:]):
            start_year = 2005 + idx
            season = f"{start_year}/{start_year + 1}"

            team = row[col_map.get('Team', 0)] or ''
            if not team or str(team).strip() in ('', 'None'):
                continue
            kit_type = row[col_map['Type']] if 'Type' in col_map else 'Home'
            design = row[col_map['Design']] if 'Design' in col_map and row[col_map['Design']] else ''
            colors = row[col_map['Colors']] if 'Colors' in col_map and row[col_map['Colors']] else ''
            brand = row[col_map['Brand']] if 'Brand' in col_map and row[col_map['Brand']] else ''
            sponsor = row[col_map['Sponsor (primary)']] if 'Sponsor (primary)' in col_map and row[col_map['Sponsor (primary)']] else ''
            league = row[col_map['League']] if 'League' in col_map and row[col_map['League']] else ''
            competition = row[col_map['Competition']] if 'Competition' in col_map and row[col_map['Competition']] else ''
            source_url = row[col_map['URL']] if 'URL' in col_map and row[col_map['URL']] else ''
            front_photo = row[col_map['Image URL']] if 'Image URL' in col_map and row[col_map['Image URL']] else ''

            doc = {
                "kit_id": f"kit_{uuid.uuid4().hex[:12]}",
                "club": str(team).strip(),
                "season": season,
                "kit_type": str(kit_type).strip() if kit_type else "Home",
                "brand": str(brand).strip() if brand else "",
                "front_photo": str(front_photo).strip() if front_photo else "",
                "year": start_year,
                "design": str(design).strip() if design else "",
                "colors": str(colors).strip() if colors else "",
                "sponsor": str(sponsor).strip() if sponsor else "",
                "league": str(league).strip() if league else "",
                "competition": str(competition).strip() if competition else "",
                "source_url": str(source_url).strip() if source_url else "",
                "created_by": "import",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.master_kits.insert_one(doc)
            imported += 1

    wb.close()
    logger.info(f"Imported {imported} master kits from Excel")
    return {"message": f"Successfully imported {imported} master kits", "count": imported}


# ─── Migration Endpoints ───

@router.post("/migrate-schema")
async def migrate_schema():
    remove_fields = {"year", "colors", "competition", "source_url"}
    result = await db.master_kits.update_many(
        {},
        {"$unset": {f: "" for f in remove_fields}}
    )
    updated = result.modified_count
    all_kits = await db.master_kits.find({}, {"_id": 0}).to_list(1000)
    patched = 0
    for kit in all_kits:
        patch = {}
        if not kit.get("league"):
            patch["league"] = ""
        if not kit.get("design"):
            patch["design"] = ""
        if not kit.get("sponsor"):
            patch["sponsor"] = ""
        if not kit.get("gender"):
            patch["gender"] = ""
        if patch:
            await db.master_kits.update_one({"kit_id": kit["kit_id"]}, {"$set": patch})
            patched += 1
    ver_result = await db.versions.update_many({}, {"$unset": {"gender": ""}})
    return {
        "message": "Schema migration complete",
        "master_kits_cleaned": updated,
        "master_kits_patched": patched,
        "versions_cleaned": ver_result.modified_count
    }


@router.post("/migrate-create-default-versions")
async def migrate_create_default_versions():
    all_kits = await db.master_kits.find({}, {"_id": 0, "kit_id": 1, "front_photo": 1}).to_list(2000)
    created_count = 0
    skipped_count = 0
    for kit in all_kits:
        kit_id = kit.get("kit_id")
        if not kit_id:
            continue
        existing_version = await db.versions.find_one({"kit_id": kit_id}, {"_id": 1})
        if existing_version:
            skipped_count += 1
            continue
        default_version = {
            "version_id": f"ver_{uuid.uuid4().hex[:12]}",
            "kit_id": kit_id,
            "competition": "National Championship",
            "model": "Replica",
            "sku_code": "",
            "ean_code": "",
            "front_photo": kit.get("front_photo", ""),
            "back_photo": "",
            "created_by": "system_migration",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.versions.insert_one(default_version)
        created_count += 1
    return {
        "message": "Default versions migration complete",
        "versions_created": created_count,
        "kits_skipped": skipped_count,
        "total_kits_processed": len(all_kits)
    }


@router.post("/set-moderator-role")
async def set_moderator_role():
    updated_count = 0
    for email in MODERATOR_EMAILS:
        result = await db.users.update_one(
            {"email": email},
            {"$set": {"role": "moderator"}}
        )
        if result.modified_count > 0:
            updated_count += 1
    moderators = await db.users.find(
        {"email": {"$in": MODERATOR_EMAILS}},
        {"_id": 0, "email": 1, "role": 1, "name": 1}
    ).to_list(100)
    return {
        "message": "Moderator roles updated",
        "updated_count": updated_count,
        "moderators": moderators
    }


@router.post("/migrate-entities-from-kits")
async def migrate_entities_from_kits():
    all_kits = await db.master_kits.find({}, {"_id": 0}).to_list(5000)
    now = datetime.now(timezone.utc).isoformat()

    teams_created = 0
    leagues_created = 0
    brands_created = 0
    kits_updated = 0

    club_names = set(k.get("club", "").strip() for k in all_kits if k.get("club", "").strip())
    league_names = set(k.get("league", "").strip() for k in all_kits if k.get("league", "").strip())
    brand_names = set(k.get("brand", "").strip() for k in all_kits if k.get("brand", "").strip())

    team_map = {}
    for name in sorted(club_names):
        slug = slugify(name)
        existing = await db.teams.find_one({"slug": slug}, {"_id": 0, "team_id": 1})
        if existing:
            team_map[name] = existing["team_id"]
        else:
            team_id = f"team_{uuid.uuid4().hex[:12]}"
            await db.teams.insert_one({
                "team_id": team_id, "name": name, "slug": slug,
                "country": "", "city": "", "founded": None,
                "primary_color": "", "secondary_color": "",
                "crest_url": "", "aka": [],
                "created_at": now, "updated_at": now
            })
            team_map[name] = team_id
            teams_created += 1

    league_map = {}
    for name in sorted(league_names):
        slug = slugify(name)
        existing = await db.leagues.find_one({"slug": slug}, {"_id": 0, "league_id": 1})
        if existing:
            league_map[name] = existing["league_id"]
        else:
            league_id = f"league_{uuid.uuid4().hex[:12]}"
            await db.leagues.insert_one({
                "league_id": league_id, "name": name, "slug": slug,
                "country_or_region": "", "level": "domestic",
                "organizer": "", "logo_url": "",
                "created_at": now, "updated_at": now
            })
            league_map[name] = league_id
            leagues_created += 1

    brand_map = {}
    for name in sorted(brand_names):
        slug = slugify(name)
        existing = await db.brands.find_one({"slug": slug}, {"_id": 0, "brand_id": 1})
        if existing:
            brand_map[name] = existing["brand_id"]
        else:
            brand_id = f"brand_{uuid.uuid4().hex[:12]}"
            await db.brands.insert_one({
                "brand_id": brand_id, "name": name, "slug": slug,
                "country": "", "founded": None, "logo_url": "",
                "created_at": now, "updated_at": now
            })
            brand_map[name] = brand_id
            brands_created += 1

    for kit in all_kits:
        update = {}
        club = kit.get("club", "").strip()
        league = kit.get("league", "").strip()
        brand = kit.get("brand", "").strip()
        if club and club in team_map:
            update["team_id"] = team_map[club]
        if league and league in league_map:
            update["league_id"] = league_map[league]
        if brand and brand in brand_map:
            update["brand_id"] = brand_map[brand]
        if update:
            await db.master_kits.update_one({"kit_id": kit["kit_id"]}, {"$set": update})
            kits_updated += 1

    logger.info(f"Entity migration: {teams_created} teams, {leagues_created} leagues, {brands_created} brands, {kits_updated} kits updated")
    return {
        "message": "Entity migration complete",
        "teams_created": teams_created,
        "leagues_created": leagues_created,
        "brands_created": brands_created,
        "kits_updated": kits_updated,
        "totals": {"teams": len(team_map), "leagues": len(league_map), "brands": len(brand_map)}
    }
