# backend/routers/entities.py
from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import (
    TeamCreate, TeamOut,
    LeagueCreate, LeagueOut,
    BrandCreate, BrandOut,
    PlayerCreate, PlayerOut,
    SponsorOut  # Ajout du modèle SponsorOut
)
from utils import slugify

router = APIRouter(prefix="/api", tags=["entities"])

# ─────────────────────────────────────────────
# Helper — verrou sur entités en attente d'approbation
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# Team Routes
# ─────────────────────────────────────────────

@router.get("/teams", response_model=List[TeamOut])
async def list_teams(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search:
        query["$or"] = [
            {"name":    {"$regex": search, "$options": "i"}},
            {"aka":     {"$regex": search, "$options": "i"}},
        ]
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    teams = await db.teams.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for t in teams:
        tid = t.get("team_id", "")
        t["kit_count"] = await db.master_kits.count_documents({"team_id": tid}) if tid else 0
    return teams


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
    await db.teams.insert_one(doc)
    result = await db.teams.find_one({"team_id": doc["team_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/teams/pending", response_model=TeamOut)
async def create_team_pending(
    team: TeamCreate,
    parent_submission_id: Optional[str] = Query(default=None)
):
    """
    Crée une équipe en statut for_review + une submission liée.
    parent_submission_id : submission_id du master_kit parent (pour liaison CASCADE).
    Si l'équipe existe déjà (même slug) on la retourne sans créer de doublon.
    """
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
    # ── VERROU CRITIQUE ──
    await _assert_not_locked("teams", "team_id", team_id)

    existing = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = {k: v for k, v in team.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(team.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"team_id": team_id})
    return result


# ─────────────────────────────────────────────
# League Routes
# ─────────────────────────────────────────────

@router.get("/leagues", response_model=List[LeagueOut])
async def list_leagues(
    search: Optional[str] = None,
    country_or_region: Optional[str] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country_or_region:
        query["country_or_region"] = {"$regex": country_or_region, "$options": "i"}
    if level:
        query["level"] = level
    leagues = await db.leagues.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for l in leagues:
        lid = l.get("league_id", "")
        l["kit_count"] = await db.master_kits.count_documents({"league_id": lid}) if lid else 0
    return leagues


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
    # ── VERROU CRITIQUE ──
    await _assert_not_locked("leagues", "league_id", league_id)

    existing = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="League not found")

    update_data = {k: v for k, v in league.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(league.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.leagues.update_one({"league_id": league_id}, {"$set": update_data})
    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"league_id": league_id})
    return result


# ─────────────────────────────────────────────
# Brand Routes
# ─────────────────────────────────────────────

@router.get("/brands", response_model=List[BrandOut])
async def list_brands(
    search: Optional[str] = None,
    country: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    brands = await db.brands.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for b in brands:
        bid = b.get("brand_id", "")
        b["kit_count"] = await db.master_kits.count_documents({"brand_id": bid}) if bid else 0
    return brands


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
    # ── VERROU CRITIQUE ──
    await _assert_not_locked("brands", "brand_id", brand_id)

    existing = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Brand not found")

    update_data = {k: v for k, v in brand.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(brand.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.brands.update_one({"brand_id": brand_id}, {"$set": update_data})
    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"brand_id": brand_id})
    return result


# ─────────────────────────────────────────────
# Player Routes
# ─────────────────────────────────────────────

@router.get("/players", response_model=List[PlayerOut])
async def list_players(
    search: Optional[str] = None,
    nationality: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search:
        query["full_name"] = {"$regex": search, "$options": "i"}
    if nationality:
        query["nationality"] = {"$regex": nationality, "$options": "i"}
    players = await db.players.find(query, {"_id": 0}).sort("full_name", 1).skip(skip).limit(limit).to_list(limit)
    for p in players:
        pid = p.get("player_id", "")
        p["kit_count"] = await db.versions.count_documents({"main_player_id": pid}) if pid else 0
    return players


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    player = await db.players.find_one({"$or": [{"player_id": player_id}, {"slug": player_id}]}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    pid = player.get("player_id", "")
    player["kit_count"] = await db.versions.count_documents({"main_player_id": pid}) if pid else 0
    versions = await db.versions.find({"main_player_id": pid}, {"_id": 0}).to_list(500) if pid else []
    enriched = []
    for v in versions:
        kit = await db.master_kits.find_one({"kit_id": v.get("kit_id", "")}, {"_id": 0})
        v["master_kit"] = kit
        enriched.append(v)
    player["versions"] = enriched
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
    await db.players.insert_one(doc)
    result = await db.players.find_one({"player_id": doc["player_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.post("/players/pending", response_model=PlayerOut)
async def create_player_pending(
    player: PlayerCreate,
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
    await db.players.insert_one(doc)

    sub_data = {"mode": "create", "full_name": player.full_name, "entity_id": player_id}
    if parent_submission_id:
        sub_data["parent_submission_id"] = parent_submission_id

    await db.submissions.insert_one({
        "submission_id":   submission_id,
        "submission_type": "player",
        "data":            sub_data,
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
    # ── VERROU CRITIQUE ──
    await _assert_not_locked("players", "player_id", player_id)

    existing = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Player not found")

    update_data = {k: v for k, v in player.model_dump().items() if v is not None}
    update_data["slug"]       = slugify(player.full_name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.players.update_one({"player_id": player_id}, {"$set": update_data})
    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = await db.versions.count_documents({"main_player_id": player_id})
    return result

# ─────────────────────────────────────────────
# Sponsors Routes
# ─────────────────────────────────────────────
router.get("/sponsors", response_model=List[SponsorOut])
async def list_sponsors(
    search: Optional[str] = None,
    country: Optional[str] = None,
    status: Optional[str] = "approved",
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    if status:
        query["status"] = status

    sponsors = await db.sponsors.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)

    for s in sponsors:
        s["kit_count"] = await db.master_kits.count_documents({"sponsor": s["name"]})

    return sponsors

@router.get("/sponsors/{sponsor_id}", response_model=SponsorOut)
async def get_sponsor(sponsor_id: str):
    sponsor = await db.sponsors.find_one({"$or": [{"sponsor_id": sponsor_id}, {"slug": sponsor_id}]}, {"_id": 0})
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sponsor["kit_count"] = await db.master_kits.count_documents({"sponsor": sponsor["name"]})
    return sponsor

@router.patch("/sponsors/{sponsor_id}/approve")
async def approve_sponsor(sponsor_id: str):
    result = await db.sponsors.update_one(
        {"sponsor_id": sponsor_id},
        {"$set": {"status": "approved", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    return {"message": "Sponsor approved"}

@router.patch("/sponsors/{sponsor_id}/reject")
async def reject_sponsor(sponsor_id: str):
    result = await db.sponsors.update_one(
        {"sponsor_id": sponsor_id},
        {"$set": {"status": "rejected", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    return {"message": "Sponsor rejected"}

# ─────────────────────────────────────────────
# Pending Approval Routes
# ─────────────────────────────────────────────

ENTITY_CONFIG = {
    "team":    {"collection": "teams",    "id_field": "team_id"},
    "league":  {"collection": "leagues",  "id_field": "league_id"},
    "brand":   {"collection": "brands",   "id_field": "brand_id"},
    "player":  {"collection": "players",  "id_field": "player_id"},
    "sponsor": {"collection": "sponsors", "id_field": "sponsor_id"},  # ← AJOUT
}


@router.get("/pending")
async def get_all_pending(master_kit_submission_id: Optional[str] = Query(default=None)):
    """
    Retourne les entités en attente (for_review).
    Si master_kit_submission_id est fourni → filtre sur la liaison parent.
    Chaque doc inclut submission_id, name (ou full_name pour players).
    """
    results = {}
    for entity_type, config in ENTITY_CONFIG.items():
        query: dict = {"status": "for_review"}

        if master_kit_submission_id:
            # On cherche les submissions liées pour récupérer les entity_ids correspondants
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

        # Normalise le champ "display_name" pour le frontend
        for d in docs:
            d["display_name"] = d.get("full_name") or d.get("name") or "—"

        results[entity_type] = docs
    return results


@router.patch("/{entity_type}/{entity_id}/approve")
async def approve_entity(entity_type: str, entity_id: str):
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown entity type")
    result = await db[config["collection"]].update_one(
        {config["id_field"]: entity_id},
        {"$set": {"status": "approved", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": f"{entity_type} approved"}


@router.patch("/{entity_type}/{entity_id}/reject")
async def reject_entity(entity_type: str, entity_id: str):
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown entity type")
    result = await db[config["collection"]].update_one(
        {config["id_field"]: entity_id},
        {"$set": {"status": "rejected", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": f"{entity_type} rejected"}


# ─────────────────────────────────────────────
# Autocomplete Route
# ─────────────────────────────────────────────

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
            "team":   {"collection": "teams",   "search_field": "name",      "id_field": "team_id",   "label_field": "name",      "extra_field": "country"},
            "league": {"collection": "leagues", "search_field": "name",      "id_field": "league_id", "label_field": "name",      "extra_field": "country_or_region"},
            "brand":  {"collection": "brands",  "search_field": "name",      "id_field": "brand_id",  "label_field": "name",      "extra_field": "country"},
            "player": {"collection": "players", "search_field": "full_name", "id_field": "player_id", "label_field": "full_name", "extra_field": "nationality"},
        }
        config = entity_config.get(type)
        if not config:
            return []

        filter_q: dict = {}
        if search_q:
            filter_q[config["search_field"]] = {"$regex": search_q, "$options": "i"}

        docs = await db[config["collection"]].find(filter_q, {"_id": 0}).limit(20).to_list(20)
        return [
            {
                "id":     d.get(config["id_field"], ""),
                "label":  d.get(config["label_field"], ""),
                "extra":  d.get(config["extra_field"], ""),
                # Expose le statut pour que le frontend puisse afficher un badge "en attente"
                "status": d.get("status", "approved"),
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
