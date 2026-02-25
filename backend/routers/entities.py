from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid
from database import db
from models import (
    TeamCreate, TeamOut, LeagueCreate, LeagueOut,
    BrandCreate, BrandOut, PlayerCreate, PlayerOut,
)
from utils import slugify

router = APIRouter(prefix="/api", tags=["entities"])


# ─── Team Routes ───

@router.get("/teams", response_model=List[TeamOut])
async def list_teams(search: Optional[str] = None, country: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"aka": {"$regex": search, "$options": "i"}},
        ]
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    teams = await db.teams.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for t in teams:
        t["kit_count"] = await db.master_kits.count_documents({"team_id": t["team_id"]})
    return teams


@router.get("/teams/{team_id}")
async def get_team(team_id: str):
    team = await db.teams.find_one({"$or": [{"team_id": team_id}, {"slug": team_id}]}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    kit_count = await db.master_kits.count_documents({"team_id": team["team_id"]})
    team["kit_count"] = kit_count
    kits = await db.master_kits.find({"team_id": team["team_id"]}, {"_id": 0}).sort("season", -1).to_list(500)
    team["kits"] = kits
    seasons = sorted(set(k.get("season", "") for k in kits if k.get("season")), reverse=True)
    team["seasons"] = seasons
    return team


@router.post("/teams", response_model=TeamOut)
async def create_team(team: TeamCreate):
    slug = slugify(team.name)
    existing = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Team already exists")
    doc = team.model_dump()
    doc["team_id"] = f"team_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.teams.insert_one(doc)
    result = await db.teams.find_one({"team_id": doc["team_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result

@router.post("/teams/pending", response_model=TeamOut)
async def create_team_pending(team: TeamCreate):
    slug = slugify(team.name)
    existing = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing
    doc = team.model_dump()
    doc["team_id"] = f"team_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["status"] = "for_review"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.teams.insert_one(doc)
    result = await db.teams.find_one({"team_id": doc["team_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/teams/{team_id}", response_model=TeamOut)
async def update_team(team_id: str, team: TeamCreate):
    existing = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = {k: v for k, v in team.model_dump().items() if v is not None}
    update_data["slug"] = slugify(team.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.teams.update_one({"team_id": team_id}, {"$set": update_data})
    result = await db.teams.find_one({"team_id": team_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"team_id": team_id})
    return result


# ─── League Routes ───

@router.get("/leagues", response_model=List[LeagueOut])
async def list_leagues(search: Optional[str] = None, country_or_region: Optional[str] = None, level: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country_or_region:
        query["country_or_region"] = {"$regex": country_or_region, "$options": "i"}
    if level:
        query["level"] = level
    leagues = await db.leagues.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for l in leagues:
        l["kit_count"] = await db.master_kits.count_documents({"league_id": l["league_id"]})
    return leagues


@router.get("/leagues/{league_id}")
async def get_league(league_id: str):
    league = await db.leagues.find_one({"$or": [{"league_id": league_id}, {"slug": league_id}]}, {"_id": 0})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    kit_count = await db.master_kits.count_documents({"league_id": league["league_id"]})
    league["kit_count"] = kit_count
    kits = await db.master_kits.find({"league_id": league["league_id"]}, {"_id": 0}).sort("season", -1).to_list(500)
    league["kits"] = kits
    return league


@router.post("/leagues", response_model=LeagueOut)
async def create_league(league: LeagueCreate):
    slug = slugify(league.name)
    existing = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="League already exists")
    doc = league.model_dump()
    doc["league_id"] = f"league_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.leagues.insert_one(doc)
    result = await db.leagues.find_one({"league_id": doc["league_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result

@router.post("/leagues/pending", response_model=LeagueOut)
async def create_league_pending(league: LeagueCreate):
    slug = slugify(league.name)
    existing = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing
    doc = league.model_dump()
    doc["league_id"] = f"league_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["status"] = "for_review"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.leagues.insert_one(doc)
    result = await db.leagues.find_one({"league_id": doc["league_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result



@router.put("/leagues/{league_id}", response_model=LeagueOut)
async def update_league(league_id: str, league: LeagueCreate):
    existing = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="League not found")
    update_data = {k: v for k, v in league.model_dump().items() if v is not None}
    update_data["slug"] = slugify(league.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.leagues.update_one({"league_id": league_id}, {"$set": update_data})
    result = await db.leagues.find_one({"league_id": league_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"league_id": league_id})
    return result


# ─── Brand Routes ───

@router.get("/brands", response_model=List[BrandOut])
async def list_brands(search: Optional[str] = None, country: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    brands = await db.brands.find(query, {"_id": 0}).sort("name", 1).skip(skip).limit(limit).to_list(limit)
    for b in brands:
        b["kit_count"] = await db.master_kits.count_documents({"brand_id": b["brand_id"]})
    return brands


@router.get("/brands/{brand_id}")
async def get_brand(brand_id: str):
    brand = await db.brands.find_one({"$or": [{"brand_id": brand_id}, {"slug": brand_id}]}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    kit_count = await db.master_kits.count_documents({"brand_id": brand["brand_id"]})
    brand["kit_count"] = kit_count
    kits = await db.master_kits.find({"brand_id": brand["brand_id"]}, {"_id": 0}).sort("season", -1).to_list(500)
    brand["kits"] = kits
    return brand


@router.post("/brands", response_model=BrandOut)
async def create_brand(brand: BrandCreate):
    slug = slugify(brand.name)
    existing = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Brand already exists")
    doc = brand.model_dump()
    doc["brand_id"] = f"brand_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.brands.insert_one(doc)
    result = await db.brands.find_one({"brand_id": doc["brand_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result

@router.post("/brands/pending", response_model=BrandOut)
async def create_brand_pending(brand: BrandCreate):
    slug = slugify(brand.name)
    existing = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if existing:
        return existing
    doc = brand.model_dump()
    doc["brand_id"] = f"brand_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["status"] = "for_review"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.brands.insert_one(doc)
    result = await db.brands.find_one({"brand_id": doc["brand_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result



@router.put("/brands/{brand_id}", response_model=BrandOut)
async def update_brand(brand_id: str, brand: BrandCreate):
    existing = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Brand not found")
    update_data = {k: v for k, v in brand.model_dump().items() if v is not None}
    update_data["slug"] = slugify(brand.name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.brands.update_one({"brand_id": brand_id}, {"$set": update_data})
    result = await db.brands.find_one({"brand_id": brand_id}, {"_id": 0})
    result["kit_count"] = await db.master_kits.count_documents({"brand_id": brand_id})
    return result


# ─── Player Routes ───

@router.get("/players", response_model=List[PlayerOut])
async def list_players(search: Optional[str] = None, nationality: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = {}
    if search:
        query["full_name"] = {"$regex": search, "$options": "i"}
    if nationality:
        query["nationality"] = {"$regex": nationality, "$options": "i"}
    players = await db.players.find(query, {"_id": 0}).sort("full_name", 1).skip(skip).limit(limit).to_list(limit)
    for p in players:
        p["kit_count"] = await db.versions.count_documents({"main_player_id": p["player_id"]})
    return players


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    player = await db.players.find_one({"$or": [{"player_id": player_id}, {"slug": player_id}]}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    player["kit_count"] = await db.versions.count_documents({"main_player_id": player["player_id"]})
    versions = await db.versions.find({"main_player_id": player["player_id"]}, {"_id": 0}).to_list(500)
    enriched_versions = []
    for v in versions:
        kit = await db.master_kits.find_one({"kit_id": v["kit_id"]}, {"_id": 0})
        v["master_kit"] = kit
        enriched_versions.append(v)
    player["versions"] = enriched_versions
    return player


@router.post("/players", response_model=PlayerOut)
async def create_player(player: PlayerCreate):
    slug = slugify(player.full_name)
    base_slug = slug
    counter = 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1
    doc = player.model_dump()
    doc["player_id"] = f"player_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.players.insert_one(doc)
    result = await db.players.find_one({"player_id": doc["player_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result

@router.post("/players/pending", response_model=PlayerOut)
async def create_player_pending(player: PlayerCreate):
    slug = slugify(player.full_name)
    base_slug = slug
    counter = 1
    while await db.players.find_one({"slug": slug}, {"_id": 1}):
        slug = f"{base_slug}-{counter}"
        counter += 1
    doc = player.model_dump()
    doc["player_id"] = f"player_{uuid.uuid4().hex[:12]}"
    doc["slug"] = slug
    doc["status"] = "for_review"
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = doc["created_at"]
    await db.players.insert_one(doc)
    result = await db.players.find_one({"player_id": doc["player_id"]}, {"_id": 0})
    result["kit_count"] = 0
    return result


@router.put("/players/{player_id}", response_model=PlayerOut)
async def update_player(player_id: str, player: PlayerCreate):
    existing = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Player not found")
    update_data = {k: v for k, v in player.model_dump().items() if v is not None}
    update_data["slug"] = slugify(player.full_name)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.players.update_one({"player_id": player_id}, {"$set": update_data})
    result = await db.players.find_one({"player_id": player_id}, {"_id": 0})
    result["kit_count"] = await db.versions.count_documents({"main_player_id": player_id})
    return result


# ─── Pending Approval Routes ───

ENTITY_CONFIG = {
    "team":   {"collection": "teams",   "id_field": "team_id"},
    "league": {"collection": "leagues", "id_field": "league_id"},
    "brand":  {"collection": "brands",  "id_field": "brand_id"},
    "player": {"collection": "players", "id_field": "player_id"},
}

@router.get("/pending")
async def get_all_pending():
    results = {}
    for entity_type, config in ENTITY_CONFIG.items():
        docs = await db[config["collection"]].find(
            {"status": "for_review"}, {"_id": 0}
        ).to_list(100)
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


# ─── Autocomplete Route ───

@router.get("/autocomplete")
async def autocomplete(field: Optional[str] = None, type: Optional[str] = None, q: str = "", query: str = ""):
    search_q = q or query

    if type:
        entity_config = {
            "team": {"collection": "teams", "search_field": "name", "id_field": "team_id", "label_field": "name", "extra_field": "country"},
            "league": {"collection": "leagues", "search_field": "name", "id_field": "league_id", "label_field": "name", "extra_field": "country_or_region"},
            "brand": {"collection": "brands", "search_field": "name", "id_field": "brand_id", "label_field": "name", "extra_field": "country"},
            "player": {"collection": "players", "search_field": "full_name", "id_field": "player_id", "label_field": "full_name", "extra_field": "nationality"},
        }
        config = entity_config.get(type)
        if not config:
            return []
        filter_q = {}
        if search_q:
            filter_q[config["search_field"]] = {"$regex": search_q, "$options": "i"}
        docs = await db[config["collection"]].find(filter_q, {"_id": 0}).limit(20).to_list(20)
        return [{"id": d[config["id_field"]], "label": d[config["label_field"]], "extra": d.get(config["extra_field"], "")} for d in docs]

    if field:
        field_map = {
            "club": "master_kits",
            "brand": "master_kits",
            "league": "master_kits",
            "sponsor": "master_kits",
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

