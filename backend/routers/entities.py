# backend/routers/entities.py
from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from ..database import db, client
from ..models import (
    TeamCreate, TeamOut,
    LeagueCreate, LeagueOut,
    BrandCreate, BrandOut,
    PlayerCreate, PlayerOut,
)
from ..auth import get_current_user
from ..utils import slugify
from ..utils.image_mirror import mirror_entity_images

router = APIRouter(prefix="/api", tags=["entities"])


# ───────────────────────────────────────────────
# Helper — verrou sur entités en attente d'approbation
# ───────────────────────────────────────────────
LOCKED_STATUSES = ("for_review", "pending")


async def _assert_not_locked(collection: str, id_field: str, entity_id: str):
    doc = await db[collection].find_one({id_field: entity_id}, {"_id": 0, "status": 1})
    if doc and doc.get("status") in LOCKED_STATUSES:
        raise HTTPException(
            status_code=423,
            detail=(
                "This entity is currently pending community approval and cannot be modified. "
                "It will be unlocked once the linked kit submission is approved or rejected."
            )
        )


# ───────────────────────────────────────────────
# Team Routes
# ───────────────────────────────────────────────

@router.get("/teams")
async def list_teams(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"aka":  {"$regex": search, "$options": "i"}},
        ]
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    total = await db.teams.count_documents(query)
    teams = await db.teams.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for t in teams:
        tid = t.get("team_id", "")
        t["kit_count"] = await db.master_kits.count_documents({"team_id": tid}) if tid else 0
    return {"results": teams, "total": total}


@router.get("/teams/{team_id}")
async def get_team(team_id: str):
    team = await db.teams.find_one({"$or": [{"team_id": team_id}, {"slug": team_id}]}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    tid = team.get("team_id", "")
    team["kit_count"] = await db.master_kits.count_documents({"team_id": tid}) if tid else 0
    kits = await db.master_kits.find({"team_id": tid}, {"_id": 0}).sort("season", -1).to_list(500) if tid else []
    team["kits"] = kits
    team["seasons"] = sorted(set(k.get("season", "") for k in kits if k.get("season")), reverse=True)
    return team


@router.post("/teams", response_model=TeamOut)
async def create_team(team: TeamCreate):
    slug = slugify(team.name)
    if await db.teams.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Team already exists")
    doc = team.model_dump()
    doc["team_id"]    = f"team_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "team", doc["team_id"])
    await db.teams.insert_one(doc)
    result = await db.teams.find_one({"team_id": doc["team_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/teams/pending", response_model=TeamOut)
async def create_team_pending(
    team: TeamCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(team.name)
    existing = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    team_id       = f"team_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = team.model_dump()
    doc["team_id"]       = team_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "team", team_id)
    await db.teams.insert_one(doc)

    sub_data = {"mode": "create", "name": team.name, "entity_id": team_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "team",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/teams/{team_id}", response_model=TeamOut)
async def update_team(team_id: str, team: TeamCreate):
    await _assert_not_locked("teams", "team_id", team_id)
    existing = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = {k: v for k, v in team.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(team.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "team", team_id)
    await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"team_id": team_id})
    return result


# ───────────────────────────────────────────────
# League Routes
# ───────────────────────────────────────────────

@router.get("/leagues")
async def list_leagues(
    search: Optional[str] = None,
    country_or_region: Optional[str] = None,
    level: Optional[str] = None,
    entity_type: Optional[str] = None,   # "league" | "cup" | "confederation"
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country_or_region:
        query["country_or_region"] = {"$regex": country_or_region, "$options": "i"}
    if level:
        query["level"] = level
    if entity_type:
        query["entity_type"] = entity_type
    total = await db.leagues.count_documents(query)
    leagues = await db.leagues.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for l in leagues:
        lid = l.get("league_id", "")
        l["kit_count"] = await db.master_kits.count_documents({"league_id": lid}) if lid else 0
    return {"results": leagues, "total": total}


@router.get("/leagues/{league_id}")
async def get_league(league_id: str):
    league = await db.leagues.find_one({"$or": [{"league_id": league_id}, {"slug": league_id}]}, {"_id": 0})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    lid = league.get("league_id", "")
    league["kit_count"] = await db.master_kits.count_documents({"league_id": lid}) if lid else 0
    kits = await db.master_kits.find({"league_id": lid}, {"_id": 0}).sort("season", -1).to_list(500) if lid else []
    league["kits"] = kits
    return league


@router.post("/leagues", response_model=LeagueOut)
async def create_league(league: LeagueCreate):
    slug = slugify(league.name)
    if await db.leagues.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="League already exists")
    doc = league.model_dump()
    doc["league_id"]  = f"league_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "league", doc["league_id"])
    await db.leagues.insert_one(doc)
    result = await db.leagues.find_one({"league_id": doc["league_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/leagues/pending", response_model=LeagueOut)
async def create_league_pending(
    league: LeagueCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(league.name)
    existing = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    league_id     = f"league_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = league.model_dump()
    doc["league_id"]     = league_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "league", league_id)
    await db.leagues.insert_one(doc)

    sub_data = {"mode": "create", "name": league.name, "entity_id": league_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "league",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/leagues/{league_id}", response_model=LeagueOut)
async def update_league(league_id: str, league: LeagueCreate):
    await _assert_not_locked("leagues", "league_id", league_id)
    existing = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="League not found")
    update_data = {k: v for k, v in league.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(league.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "league", league_id)
    await db.leagues.update_one({"league_id": league_id}, {"$set": update_data})
    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"league_id": league_id})
    return result


# ───────────────────────────────────────────────
# Brand Routes
# ───────────────────────────────────────────────

@router.get("/brands")
async def list_brands(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    total = await db.brands.count_documents(query)
    brands = await db.brands.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for b in brands:
        bid = b.get("brand_id", "")
        b["kit_count"] = await db.master_kits.count_documents({"brand_id": bid}) if bid else 0
    return {"results": brands, "total": total}


@router.get("/brands/{brand_id}")
async def get_brand(brand_id: str):
    brand = await db.brands.find_one({"$or": [{"brand_id": brand_id}, {"slug": brand_id}]}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    bid = brand.get("brand_id", "")
    brand["kit_count"] = await db.master_kits.count_documents({"brand_id": bid}) if bid else 0
    kits = await db.master_kits.find({"brand_id": bid}, {"_id": 0}).sort("season", -1).to_list(500) if bid else []
    brand["kits"] = kits
    return brand


@router.post("/brands", response_model=BrandOut)
async def create_brand(brand: BrandCreate):
    slug = slugify(brand.name)
    if await db.brands.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Brand already exists")
    doc = brand.model_dump()
    doc["brand_id"]   = f"brand_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "brand", doc["brand_id"])
    await db.brands.insert_one(doc)
    result = await db.brands.find_one({"brand_id": doc["brand_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/brands/pending", response_model=BrandOut)
async def create_brand_pending(
    brand: BrandCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(brand.name)
    existing = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    brand_id      = f"brand_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = brand.model_dump()
    doc["brand_id"]      = brand_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "brand", brand_id)
    await db.brands.insert_one(doc)

    sub_data = {"mode": "create", "name": brand.name, "entity_id": brand_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "brand",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/brands/{brand_id}", response_model=BrandOut)
async def update_brand(brand_id: str, brand: BrandCreate):
    await _assert_not_locked("brands", "brand_id", brand_id)
    existing = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Brand not found")
    update_data = {k: v for k, v in brand.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(brand.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "brand", brand_id)
    await db.brands.update_one({"brand_id": brand_id}, {"$set": update_data})
    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"brand_id": brand_id})
    return result


# ── SPONSORS ────────────────────────────────────────────────────────────────────────

@router.get("/sponsors")
async def list_sponsors(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query: dict = {"status": {"$ne": "rejected"}}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    total = await db.sponsors.count_documents(query)
    sponsors = await db.sponsors.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for s in sponsors:
        sid  = s.get("sponsor_id", "")
        name = s.get("name", "")
        count_by_id = await db.master_kits.count_documents({"sponsor_id": sid}) if sid else 0
        if count_by_id == 0 and name:
            count_by_name = await db.master_kits.count_documents(
                {"sponsor": {"$regex": f"^{name}$", "$options": "i"}}
            )
        else:
            count_by_name = 0
        s["kit_count"] = count_by_id or count_by_name
    return {"results": sponsors, "total": total}


@router.get("/sponsors/{sponsor_id}")
async def get_sponsor(sponsor_id: str):
    sponsor = await db.sponsors.find_one(
        {"$or": [{"sponsor_id": sponsor_id}, {"slug": sponsor_id}]},
        {"_id": 0}
    )
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sid  = sponsor.get("sponsor_id", "")
    name = sponsor.get("name", "")
    kits = await db.master_kits.find({"sponsor_id": sid}, {"_id": 0}).sort("season", -1).to_list(200) if sid else []
    if not kits and name:
        kits = await db.master_kits.find(
            {"sponsor": {"$regex": f"^{name}$", "$options": "i"}},
            {"_id": 0}
        ).sort("season", -1).to_list(200)
    sponsor["kits"]      = kits
    sponsor["kit_count"] = len(kits)
    return sponsor


@router.post("/sponsors")
async def create_sponsor(sponsor: dict):
    slug = slugify(sponsor.get("name", ""))
    if await db.sponsors.find_one({"slug": slug}, {"_id": 0}):
        raise HTTPException(status_code=400, detail="Sponsor already exists")
    doc = {**sponsor}
    doc["sponsor_id"]  = f"sponsor_{uuid.uuid4().hex[:12]}"
    doc["slug"]        = slug
    doc["status"]      = "approved"
    doc["created_at"]  = datetime.now(timezone.utc).isoformat()
    doc["updated_at"]  = doc["created_at"]
    doc = await mirror_entity_images(doc, "sponsor", doc["sponsor_id"])
    await db.sponsors.insert_one(doc)
    return await db.sponsors.find_one({"sponsor_id": doc["sponsor_id"]}, {"_id": 0})


@router.post("/sponsors/pending")
async def create_sponsor_pending(
    sponsor: dict,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(sponsor.get("name", ""))
    existing = await db.sponsors.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing

    now           = datetime.now(timezone.utc).isoformat()
    sponsor_id    = f"sponsor_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = {**sponsor}
    doc["sponsor_id"]    = sponsor_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "sponsor", sponsor_id)
    await db.sponsors.insert_one(doc)

    sub_data = {"mode": "create", "name": sponsor.get("name"), "entity_id": sponsor_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "sponsor",
        "data":            sub_data,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })
    return await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})


@router.put("/sponsors/{sponsor_id}")
async def update_sponsor(sponsor_id: str, sponsor: dict):
    await _assert_not_locked("sponsors", "sponsor_id", sponsor_id)
    existing = await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    update_data = {k: v for k, v in sponsor.items() if v is not None}
    update_data["slug"]       = slugify(sponsor.get("name", ""))
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "sponsor", sponsor_id)
    await db.sponsors.update_one({"sponsor_id": sponsor_id}, {"$set": update_data})
    return await db.sponsors.find_one({"sponsor_id": sponsor_id}, {"_id": 0})


# ───────────────────────────────────────────────
# Player Routes
# ───────────────────────────────────────────────

@router.get("/players")
async def list_players(
    search: Optional[str] = None,
    nationality: Optional[str] = None,
    skip: int = 0,
    limit: int = 48
):
    query = {"status": {"$ne": "rejected"}}
    if search:
        query["full_name"] = {"$regex": search, "$options": "i"}
    if nationality:
        query["nationality"] = {"$regex": nationality, "$options": "i"}
    total = await db.players.count_documents(query)
    players = await db.players.find(query, {"_id": 0}).sort("full_name", 1).skip(skip).limit(limit).to_list(limit)
    for p in players:
        pid = p.get("player_id", "")
        p["kit_count"] = await db.versions.count_documents({"main_player_id": pid}) if pid else 0
        if not isinstance(p.get("positions"), list):
            p["positions"] = []
    return {"results": players, "total": total}


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    player = await db.players.find_one({"$or": [{"player_id": player_id}, {"slug": player_id}]}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    if not isinstance(player.get("positions"), list):
        player["positions"] = []
    pid = player.get("player_id", "")
    collection_items = await db.collections.find(
        {"flocking_player_id": pid}, {"_id": 0, "version_id": 1}
    ).to_list(2000) if pid else []
    version_ids = list({i["version_id"] for i in collection_items if i.get("version_id")})
    kit_ids_set = set()
    enriched_versions = []
    if version_ids:
        versions = await db.versions.find(
            {"version_id": {"$in": version_ids}}, {"_id": 0}
        ).to_list(len(version_ids))
        for v in versions:
            kit = await db.master_kits.find_one({"kit_id": v.get("kit_id", "")}, {"_id": 0})
            v["master_kit"] = kit
            kit_ids_set.add(v.get("kit_id", ""))
            enriched_versions.append(v)
    player["kit_count"] = len(kit_ids_set)
    player["versions"]  = enriched_versions
    return player


@router.post("/players", response_model=PlayerOut)
async def create_player(player: PlayerCreate):
    slug = slugify(player.full_name)
    base_slug, counter = slug, 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1
    doc = player.model_dump()
    doc["player_id"]  = f"player_{uuid.uuid4().hex[:12]}"
    doc["slug"]       = slug
    doc["status"]     = "approved"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    doc = await mirror_entity_images(doc, "player", doc["player_id"])
    await db.players.insert_one(doc)
    result = await db.players.find_one({"player_id": doc["player_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/players/pending", response_model=PlayerOut)
async def create_player_pending(
    player: PlayerCreate,
    request: Request,
    parent_submission_id: Optional[str] = Query(default=None)
):
    slug = slugify(player.full_name)
    base_slug, counter = slug, 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1

    now           = datetime.now(timezone.utc).isoformat()
    player_id     = f"player_{uuid.uuid4().hex[:12]}"
    submission_id = f"sub_{uuid.uuid4().hex[:12]}"

    doc = player.model_dump()
    doc["player_id"]     = player_id
    doc["slug"]          = slug
    doc["status"]        = "for_review"
    doc["submission_id"] = submission_id
    doc["created_at"]    = now
    doc["updated_at"]    = now
    doc = await mirror_entity_images(doc, "player", player_id)
    await db.players.insert_one(doc)

    sub_data = {"mode": "create", "full_name": player.full_name, "entity_id": player_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    try:
        current_user   = await get_current_user(request)
        submitted_by   = current_user.get("user_id", "")
        submitter_name = current_user.get("name", "")
    except Exception:
        submitted_by   = ""
        submitter_name = ""

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "player",
        "data":            sub_data,
        "submitted_by":    submitted_by,
        "submitter_name":  submitter_name,
        "status":          "pending",
        "votes_up":        0,
        "votes_down":      0,
        "voters":          [],
        "created_at":      now,
    })

    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/players/{player_id}", response_model=PlayerOut)
async def update_player(player_id: str, player: PlayerCreate):
    await _assert_not_locked("players", "player_id", player_id)
    existing = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Player not found")
    update_data = {k: v for k, v in player.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(player.full_name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data = await mirror_entity_images(update_data, "player", player_id)
    await db.players.update_one({"player_id": player_id}, {"$set": update_data})
    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = await db.versions.count_documents({"main_player_id": player_id})
    return result


# ───────────────────────────────────────────────
# Pending Approval Routes
# ───────────────────────────────────────────────

ENTITY_CONFIG = {
    "team":    {"collection": "teams",    "id_field": "team_id"},
    "league":  {"collection": "leagues",  "id_field": "league_id"},
    "brand":   {"collection": "brands",   "id_field": "brand_id"},
    "player":  {"collection": "players",  "id_field": "player_id"},
    "sponsor": {"collection": "sponsors", "id_field": "sponsor_id"},
}


@router.get("/pending")
async def get_all_pending(master_kit_submission_id: Optional[str] = Query(default=None)):
    results = {}
    for entity_type, config in ENTITY_CONFIG.items():
        query: dict = {"status": "for_review"}
        if master_kit_submission_id:
            linked_subs = await db.submissions.find(
                {
                    "submission_type": entity_type,
                    "status": "pending",
                    "data.parent_submission_id": master_kit_submission_id,
                },
                {"_id": 0, "data.entity_id": 1}
            ).to_list(50)
            linked_ids = [s["data"]["entity_id"] for s in linked_subs if s.get("data", {}).get("entity_id")]
            if not linked_ids:
                results[entity_type] = []
                continue
            query[config["id_field"]] = {"$in": linked_ids}

        docs = await db[config["collection"]].find(query, {"_id": 0}).to_list(100)
        for d in docs:
            d["display_name"] = d.get("full_name") or d.get("name") or "—"
        results[entity_type] = docs
    return results


@router.patch("/{entity_type}/{entity_id}/approve")
async def approve_entity(entity_type: str, entity_id: str):
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown entity type")
    now = datetime.now(timezone.utc).isoformat()
    result = await db[config["collection"]].update_one(
        {config["id_field"]: entity_id},
        {"$set": {"status": "approved", "updated_at": now}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")
    await db.submissions.update_one(
        {
            "submission_type": entity_type,
            "data.entity_id": entity_id,
            "status": {"$in": ["pending", "for_review"]},
        },
        {"$set": {"status": "approved", "updated_at": now}}
    )
    return {"message": f"{entity_type} approved"}


@router.patch("/{entity_type}/{entity_id}/reject")
async def reject_entity(entity_type: str, entity_id: str):
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown entity type")
    now = datetime.now(timezone.utc).isoformat()
    result = await db[config["collection"]].update_one(
        {config["id_field"]: entity_id},
        {"$set": {"status": "rejected", "updated_at": now}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")
    await db.submissions.update_one(
        {
            "submission_type": entity_type,
            "data.entity_id": entity_id,
            "status": {"$in": ["pending", "for_review"]},
        },
        {"$set": {"status": "rejected", "updated_at": now}}
    )
    return {"message": f"{entity_type} rejected"}


# ───────────────────────────────────────────────
# Autocomplete Route
# ───────────────────────────────────────────────

# Mapping par entité : quels champs logo inclure dans la réponse autocomplete
_LOGO_FIELDS = {
    "team":    ["crest_url", "logo_url"],
    "league":  ["logo_url", "crest_url"],
    "brand":   ["logo_url"],
    "player":  ["photo_url"],
    "sponsor": ["logo_url"],
}


@router.get("/autocomplete")
async def autocomplete(
    field: Optional[str] = None,
    type: Optional[str] = None,
    q: str = "",
    query: str = ""
):
    search_q = q or query

    if type:
        entity_config = {
            "team":    {"collection": "teams",    "search_fields": ["name", "aka"], "id_field": "team_id",    "label_field": "name",      "extra_field": "country"},
            "league":  {"collection": "leagues",  "search_fields": ["name"],         "id_field": "league_id",  "label_field": "name",      "extra_field": "country_or_region"},
            "brand":   {"collection": "brands",   "search_fields": ["name"],         "id_field": "brand_id",   "label_field": "name",      "extra_field": "country"},
            "player":  {"collection": "players",  "search_fields": ["full_name"],    "id_field": "player_id",  "label_field": "full_name", "extra_field": "nationality"},
            "sponsor": {"collection": "sponsors", "search_fields": ["name"],         "id_field": "sponsor_id", "label_field": "name",      "extra_field": "country"},
        }
        config = entity_config.get(type)
        if not config:
            return []

        # Filtre de recherche : OR sur tous les search_fields
        filter_q: dict = {"status": {"$ne": "rejected"}}
        if search_q:
            if len(config["search_fields"]) == 1:
                filter_q[config["search_fields"][0]] = {"$regex": search_q, "$options": "i"}
            else:
                filter_q["$or"] = [
                    {f: {"$regex": search_q, "$options": "i"}}
                    for f in config["search_fields"]
                ]

        docs = await db[config["collection"]].find(filter_q, {"_id": 0}).limit(20).to_list(20)

        logo_fields = _LOGO_FIELDS.get(type, [])

        return [
            {
                "id":      d.get(config["id_field"], ""),
                "label":   d.get(config["label_field"], ""),
                "extra":   d.get(config["extra_field"], ""),
                "status":  d.get("status", "approved"),
                # Inclure le premier champ logo trouvé dans logo_url pour le frontend
                "logo_url": next(
                    (d[f] for f in logo_fields if d.get(f)),
                    None
                ),
            }
            for d in docs
        ]

    if field:
        field_map = {
            "club":        "master_kits",
            "brand":       "master_kits",
            "league":      "master_kits",
            "sponsor":     "master_kits",
            "competition": "versions",
        }
        if field not in field_map:
            return []
        collection_name = field_map[field]
        values = await db[collection_name].distinct(field)
        if search_q:
            q_lower = search_q.lower()
            values = [v for v in values if v and q_lower in str(v).lower()]
        return sorted([v for v in values if v])[:20]

    return []
