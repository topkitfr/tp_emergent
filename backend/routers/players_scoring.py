"""Router players_scoring — enrichissement automatique via TheSportsDB.

Routes :
  GET  /api/scoring/players/tsdb-search?name=...  → auto-complétion (TheSportsDB)
  POST /api/scoring/players/enrich                → enrichit un joueur Topkit avec son palmarès
  GET  /api/scoring/players/{player_id}           → score actuel d'un joueur
  PATCH /api/scoring/players/{player_id}/aura     → mise à jour de l'aura (vote communautaire)
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone

from ..database import db
from ..models import PlayerScoringEnrichRequest, PlayerScoringOut
from ..services.thesportsdb import (
    search_players_by_name,
    lookup_honours,
    compute_score_palmares,
    compute_note,
)

router = APIRouter(prefix="/api/scoring/players", tags=["players-scoring"])


@router.get("/tsdb-search")
async def tsdb_search_players(name: str = Query(..., min_length=2)):
    """Auto-complétion joueur via TheSportsDB (non authentifié)."""
    try:
        results = await search_players_by_name(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TheSportsDB error: {str(e)}")
    return {"players": results}


@router.post("/enrich", response_model=PlayerScoringOut)
async def enrich_player_scoring(body: PlayerScoringEnrichRequest):
    """Enrichit un joueur Topkit avec son palmarès TheSportsDB et recalcule son score."""
    coll = db["players"]

    player = await coll.find_one({"player_id": body.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    try:
        honours_raw = await lookup_honours(body.tsdb_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TheSportsDB error: {str(e)}")

    honours_clean = [
        {
            "honour": h.get("strHonour", ""),
            "season": h.get("strSeason", ""),
            "team": h.get("strTeam", ""),
        }
        for h in honours_raw
    ]

    score_palmares = compute_score_palmares(honours_raw)
    note = compute_note(score_palmares, body.aura)
    now = datetime.now(timezone.utc).isoformat()

    update_fields = {
        "tsdb_id": body.tsdb_id,
        "honours": honours_clean,
        "score_palmares": score_palmares,
        "aura": body.aura,
        "note": note,
        "updated_at": now,
    }

    await coll.update_one(
        {"player_id": body.player_id},
        {"$set": update_fields},
    )

    return PlayerScoringOut(
        player_id=body.player_id,
        full_name=player.get("full_name", ""),
        tsdb_id=body.tsdb_id,
        honours_count=len(honours_clean),
        score_palmares=score_palmares,
        aura=body.aura,
        note=note,
        updated_at=now,
    )


@router.get("/{player_id}", response_model=PlayerScoringOut)
async def get_player_scoring(player_id: str):
    """Retourne le score actuel d'un joueur."""
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    return PlayerScoringOut(
        player_id=player_id,
        full_name=player.get("full_name", ""),
        tsdb_id=player.get("tsdb_id", ""),
        honours_count=len(player.get("honours", [])),
        score_palmares=player.get("score_palmares", 0.0),
        aura=player.get("aura", 0.0),
        note=player.get("note", 0.0),
        updated_at=player.get("updated_at"),
    )


@router.patch("/{player_id}/aura")
async def update_player_aura(player_id: str, aura: float = Query(..., ge=0, le=100)):
    """Met à jour l'aura d'un joueur et recalcule sa note."""
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    score_palmares = player.get("score_palmares", 0.0)
    note = compute_note(score_palmares, aura)
    now = datetime.now(timezone.utc).isoformat()

    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {"aura": aura, "note": note, "updated_at": now}},
    )

    return {"player_id": player_id, "aura": aura, "note": note, "updated_at": now}
