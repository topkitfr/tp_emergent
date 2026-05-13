# backend/routers/kits_by_entity.py
from fastapi import APIRouter, HTTPException
from typing import Optional

from ..database import db
from ..utils import safe_regex
from ._kit_utils import _normalize_kit

router = APIRouter(prefix="/api", tags=["kits-by-entity"])


@router.get("/kits/{kit_id}/players")
async def get_kit_players(kit_id: str):
    players = await db.players.find({"kit_id": kit_id}).limit(6).to_list(6)
    return [
        {
            "id": str(p.get("player_id", p.get("_id", ""))),
            "name": p.get("full_name", ""),
            "photo": p.get("photo_url", ""),
        }
        for p in players
    ]


@router.get("/leagues/{slug}/kits")
async def get_league_kits(slug: str, skip: int = 0, limit: int = 50):
    league = await db.leagues.find_one({"slug": slug}, {"_id": 0})
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    league_id = league.get("league_id") or league.get("id")
    if not league_id:
        raise HTTPException(status_code=500, detail="League has no league_id")

    query = {"league_id": league_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)
    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1).skip(skip).limit(capped_limit).to_list(capped_limit)
    )
    return {"results": [await _normalize_kit(k) for k in kits], "total": total, "skip": skip, "limit": capped_limit}


@router.get("/brands/{slug}/kits")
async def get_brand_kits(slug: str, skip: int = 0, limit: int = 50):
    brand = await db.brands.find_one({"slug": slug}, {"_id": 0})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand_id = brand.get("brand_id") or brand.get("id")
    if not brand_id:
        raise HTTPException(status_code=500, detail="Brand has no brand_id")

    query = {"brand_id": brand_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)
    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1).skip(skip).limit(capped_limit).to_list(capped_limit)
    )
    return {"results": [await _normalize_kit(k) for k in kits], "total": total, "skip": skip, "limit": capped_limit}


@router.get("/teams/{slug}/kits")
async def get_team_kits(slug: str, skip: int = 0, limit: int = 50):
    team = await db.teams.find_one({"slug": slug}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_id = team.get("team_id") or team.get("id")
    if not team_id:
        raise HTTPException(status_code=500, detail="Team has no team_id")

    query = {"team_id": team_id}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)
    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1).skip(skip).limit(capped_limit).to_list(capped_limit)
    )
    return {"results": [await _normalize_kit(k) for k in kits], "total": total, "skip": skip, "limit": capped_limit}


@router.get("/players/{slug}/kits")
async def get_player_kits(slug: str, skip: int = 0, limit: int = 50):
    player = await db.players.find_one({"slug": slug}, {"_id": 0})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    player_id = player.get("player_id") or player.get("id")
    if not player_id:
        raise HTTPException(status_code=500, detail="Player has no player_id")

    items = await db.collections.find(
        {"flocking_player_id": player_id}, {"_id": 0, "version_id": 1}
    ).to_list(2000)
    version_ids = list({i["version_id"] for i in items if i.get("version_id")})
    if not version_ids:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    versions = await db.versions.find(
        {"version_id": {"$in": version_ids}}, {"_id": 0, "kit_id": 1}
    ).to_list(len(version_ids))
    kit_ids = list({v["kit_id"] for v in versions if v.get("kit_id")})
    if not kit_ids:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    query = {"kit_id": {"$in": kit_ids}}
    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)
    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1).skip(skip).limit(capped_limit).to_list(capped_limit)
    )
    return {"results": [await _normalize_kit(k) for k in kits], "total": total, "skip": skip, "limit": capped_limit}


@router.get("/sponsors/{slug}/kits")
async def get_sponsor_kits(slug: str, skip: int = 0, limit: int = 50):
    sponsor = await db.sponsors.find_one({"slug": slug}, {"_id": 0})
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    sponsor_id = sponsor.get("sponsor_id") or sponsor.get("id")
    name = sponsor.get("name", "")

    if sponsor_id:
        query = {"sponsor_id": sponsor_id}
    elif name:
        query = {"sponsor": {"$regex": f"^{safe_regex(name)}$", "$options": "i"}}
    else:
        return {"results": [], "total": 0, "skip": skip, "limit": limit}

    total = await db.master_kits.count_documents(query)
    capped_limit = min(limit, 100)
    kits = (
        await db.master_kits.find(query, {"_id": 0})
        .sort("season", -1).skip(skip).limit(capped_limit).to_list(capped_limit)
    )
    return {"results": [await _normalize_kit(k) for k in kits], "total": total, "skip": skip, "limit": capped_limit}
