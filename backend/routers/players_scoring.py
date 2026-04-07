"""Router players_scoring — enrichissement automatique via API-Football.

Routes :
  GET  /api/scoring/players/api-search?name=...  → recherche joueur
  POST /api/scoring/players/enrich               → enrichit palmarès
  GET  /api/scoring/players/{player_id}/career   → carrière clubs + maillots Topkit liés
  GET  /api/scoring/players/{player_id}          → score actuel
  PATCH /api/scoring/players/{player_id}/aura    → mise à jour aura
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import re

from ..database import db
from ..models import PlayerScoringEnrichRequest, PlayerScoringOut
from ..services.thesportsdb import (
    search_players_by_name,
    lookup_honours,
    lookup_career,
    compute_score_palmares,
    compute_note,
)

router = APIRouter(prefix="/api/scoring/players", tags=["players-scoring"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_year(date_str: str) -> str | None:
    """Extrait l'année depuis 'YYYY-MM-DD' ou 'YYYY'."""
    if not date_str:
        return None
    m = re.match(r"(\d{4})", date_str)
    return m.group(1) if m else None


def _normalize(s: str) -> str:
    """Normalise une chaîne pour comparaison floue (lowercase, sans accents)."""
    import unicodedata
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


async def _match_kits(club: str, year_start: str | None, year_end: str | None):
    """Cherche les MasterKits Topkit qui correspondent à un club et une période.

    Logique :
      - club normalisé contenu dans master_kit.club normalisé (ou inversement)
      - season contient year_start ou year_end  (ex: '2005-2006' contient '2005')
    """
    if not club:
        return []

    club_norm = _normalize(club)
    pipeline = [
        {"$match": {"status": "approved"}},
        {"$project": {
            "kit_id": 1, "club": 1, "season": 1,
            "kit_type": 1, "brand": 1, "front_photo": 1,
        }},
    ]
    all_kits = await db["master_kits"].aggregate(pipeline).to_list(length=2000)

    matched = []
    for kit in all_kits:
        kit_club = _normalize(kit.get("club") or "")
        if not kit_club:
            continue
        # Match de club
        if club_norm not in kit_club and kit_club not in club_norm:
            continue
        # Match de saison si on a une année
        season = kit.get("season") or ""
        if year_start or year_end:
            years = [y for y in [year_start, year_end] if y]
            if not any(y in season for y in years):
                continue
        matched.append({
            "kit_id": kit["kit_id"],
            "club": kit.get("club", ""),
            "season": season,
            "kit_type": kit.get("kit_type", ""),
            "brand": kit.get("brand", ""),
            "front_photo": kit.get("front_photo", ""),
        })
    return matched


# ── routes ───────────────────────────────────────────────────────────────────

@router.get("/api-search")
async def api_search_players(name: str = Query(..., min_length=2)):
    """Recherche un joueur sur API-Football pour auto-complétion."""
    try:
        results = await search_players_by_name(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")
    return {"players": results}


@router.post("/enrich", response_model=PlayerScoringOut)
async def enrich_player_scoring(body: PlayerScoringEnrichRequest):
    """Enrichit un joueur Topkit avec son palmarès API-Football."""
    coll = db["players"]
    player = await coll.find_one({"player_id": body.player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    try:
        honours_raw = await lookup_honours(body.apifootball_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")

    honours_clean = [
        {
            "honour": h.get("strHonour", ""),
            "season": h.get("strSeason", ""),
            "team": h.get("strTeam", ""),
            "place": h.get("place", ""),
            "league": h.get("league", ""),
        }
        for h in honours_raw
    ]

    score_palmares = compute_score_palmares(honours_raw)
    note = compute_note(score_palmares, body.aura)
    now = datetime.now(timezone.utc).isoformat()

    await coll.update_one(
        {"player_id": body.player_id},
        {"$set": {
            "apifootball_id": body.apifootball_id,
            "honours": honours_clean,
            "score_palmares": score_palmares,
            "aura": body.aura,
            "note": note,
            "updated_at": now,
        }},
    )

    return PlayerScoringOut(
        player_id=body.player_id,
        full_name=player.get("full_name", ""),
        apifootball_id=body.apifootball_id,
        honours_count=len(honours_clean),
        score_palmares=score_palmares,
        aura=body.aura,
        note=note,
        updated_at=now,
    )


@router.get("/{player_id}/career")
async def get_player_career(player_id: str):
    """Retourne la carrière clubs d'un joueur avec les maillots Topkit liés.

    Pour chaque entrée de transfert (arrivée dans un club) :
      - infos club (nom, logo, date)
      - liste des maillots Topkit matchant ce club + cette période
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    apifootball_id = player.get("apifootball_id") or player.get("tsdb_id")
    if not apifootball_id:
        return {"career": [], "has_apifootball_id": False}

    try:
        transfers = await lookup_career(apifootball_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")

    # Reconstituer les périodes : date d'arrivée = date_start, date d'arrivée suivante = date_end
    # On trie par date croissante pour calculer les fins de période
    sorted_transfers = sorted(transfers, key=lambda x: x["date"] or "")

    career = []
    for i, t in enumerate(sorted_transfers):
        date_start = t["date"]
        # La date de fin est la date du transfert suivant (si dispo)
        date_end = sorted_transfers[i + 1]["date"] if i + 1 < len(sorted_transfers) else None

        year_start = _extract_year(date_start)
        year_end = _extract_year(date_end)

        # Chercher les maillots Topkit correspondants
        kits = await _match_kits(t["club"], year_start, year_end)

        career.append({
            "club": t["club"],
            "team_logo": t["team_logo"],
            "from_club": t["from_club"],
            "date_start": date_start,
            "date_end": date_end,
            "year_start": year_start,
            "year_end": year_end,
            "topkit_kits": kits,
        })

    # Retourner du plus récent au plus ancien
    career.reverse()

    return {
        "player_id": player_id,
        "has_apifootball_id": True,
        "career": career,
    }


@router.get("/{player_id}", response_model=PlayerScoringOut)
async def get_player_scoring(player_id: str):
    """Retourne le score actuel d'un joueur."""
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    return PlayerScoringOut(
        player_id=player_id,
        full_name=player.get("full_name", ""),
        apifootball_id=player.get("apifootball_id", player.get("tsdb_id", "")),
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
