"""Router players_scoring — fiche joueur + score, 100 % DB.

Routes :
  GET   /api/scoring/players/{player_id}/full       → fiche complète (identité + carrière + maillots + palmarès + note)
  GET   /api/scoring/players/{player_id}/career     → carrière clubs + maillots Topkit liés
  GET   /api/scoring/players/{player_id}            → score actuel
  PATCH /api/scoring/players/{player_id}/aura       → mise à jour aura

IMPORTANT: les routes statiques sont déclarées AVANT les dynamiques
(/{player_id}) pour éviter qu'un mot-clé soit interprété comme un player_id.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import re

from ..database import db
from ..models import PlayerScoringOut
from ..services.scoring import (
    compute_score_palmares,
    compute_note,
    _dedup_honours,
)

router = APIRouter(prefix="/api/scoring/players", tags=["players-scoring"])


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_year(date_str: str) -> str | None:
    if not date_str:
        return None
    m = re.match(r"(\d{4})", date_str)
    return m.group(1) if m else None


def _normalize(s: str) -> str:
    import unicodedata
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


async def _match_kits(club: str, year_start: str | None, year_end: str | None, limit: int | None = None):
    if not club:
        return [], 0
    club_norm = _normalize(club)
    pipeline = [
        {"$match": {"status": "approved"}},
        {"$project": {"kit_id": 1, "club": 1, "season": 1,
                      "kit_type": 1, "brand": 1, "front_photo": 1}},
    ]
    all_kits = await db["master_kits"].aggregate(pipeline).to_list(length=2000)
    matched = []
    for kit in all_kits:
        kit_club = _normalize(kit.get("club") or "")
        if not kit_club:
            continue
        if club_norm not in kit_club and kit_club not in club_norm:
            continue
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
    total = len(matched)
    if limit:
        matched = matched[:limit]
    return matched, total


async def _count_all_player_kits(player_id: str) -> int:
    """Compte le nombre d'items TopKit floqués au nom du joueur."""
    return await db["collections"].count_documents({"flocking_player_id": player_id})


# ── routes DYNAMIQUES /{player_id}/... ───────────────────────────────────────

@router.get("/{player_id}/full")
async def get_player_full(player_id: str):
    """Fiche complète d'un joueur (DB-only) :
      - identité
      - carrière clubs (entrées manuelles en DB)
      - maillots Topkit liés (5 max + total)
      - trophées individuels
      - palmarès collectif (Winner / 2nd Place)
      - score + note sur 100 + breakdown
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    identity = {
        "player_id": player_id,
        "full_name": player.get("full_name", ""),
        "slug": player.get("slug", ""),
        "nationality": player.get("nationality", ""),
        "birth_date": player.get("birth_date", ""),
        "birth_place": player.get("birth_place", ""),
        "birth_country": player.get("birth_country", ""),
        "age": None,
        "height": player.get("height", ""),
        "weight": player.get("weight", ""),
        "position": (player.get("positions") or [""])[0],
        "photo": player.get("photo_url", ""),
        "bio": player.get("bio", ""),
    }

    career = [
        {**entry, "source": "manual"}
        for entry in player.get("career", [])
    ]

    topkit_kits_total = await _count_all_player_kits(player_id)
    topkit_kits_preview = []

    individual_awards = player.get("individual_awards", [])

    honours_raw = player.get("honours", [])
    honours_deduped = _dedup_honours(honours_raw)
    honours_winner = [
        h for h in honours_deduped
        if (h.get("place") or "").lower() == "winner"
    ]
    honours_runner_up = [
        h for h in honours_deduped
        if (h.get("place") or "").lower() in ("2nd place", "runner-up")
    ]

    score_palmares = player.get("score_palmares", 0.0)
    aura = player.get("aura", 0.0)

    note, note_breakdown = compute_note(
        score_palmares=score_palmares,
        aura=aura,
        individual_awards=individual_awards,
        topkit_kits_count=topkit_kits_total,
    )

    return {
        "identity": identity,
        "career": career,
        "topkit_kits": topkit_kits_preview,
        "topkit_kits_total": topkit_kits_total,
        "individual_awards": individual_awards,
        "honours_winner": honours_winner,
        "honours_runner_up": honours_runner_up,
        "score_palmares": score_palmares,
        "aura": aura,
        "note": note,
        "note_breakdown": note_breakdown,
    }


@router.get("/{player_id}/career")
async def get_player_career(player_id: str):
    """Retourne la carrière clubs d'un joueur (entrées manuelles DB) avec les
    maillots Topkit liés.
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    db_career = player.get("career", [])
    if not db_career:
        return {"player_id": player_id, "career": [], "source": "none"}

    career = []
    for entry in db_career:
        year_start = entry.get("year_start") or _extract_year(entry.get("date_start", ""))
        year_end = entry.get("year_end") or _extract_year(entry.get("date_end", ""))
        club = entry.get("club", "")
        kits, total = await _match_kits(club, year_start, year_end)
        career.append({
            **entry,
            "topkit_kits": kits,
            "topkit_kits_total": total,
            "source": "manual",
        })
    return {"player_id": player_id, "career": career, "source": "manual"}


@router.get("/{player_id}", response_model=PlayerScoringOut)
async def get_player_scoring(player_id: str):
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")
    return PlayerScoringOut(
        player_id=player_id,
        full_name=player.get("full_name", ""),
        honours_count=len(player.get("honours", [])),
        score_palmares=player.get("score_palmares", 0.0),
        aura=player.get("aura", 0.0),
        note=player.get("note", 0.0),
        note_breakdown=player.get("note_breakdown"),
        updated_at=player.get("updated_at"),
    )


@router.patch("/{player_id}/aura")
async def update_player_aura(player_id: str, aura: float = Query(..., ge=0, le=100)):
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    individual_awards = player.get("individual_awards", [])
    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours)

    topkit_kits_count = await _count_all_player_kits(player_id)

    note, note_breakdown = compute_note(
        score_palmares=score_palmares,
        aura=aura,
        individual_awards=individual_awards,
        topkit_kits_count=topkit_kits_count,
    )
    now = datetime.now(timezone.utc).isoformat()
    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {
            "aura": aura,
            "score_palmares": score_palmares,
            "note": note,
            "note_breakdown": note_breakdown,
            "updated_at": now,
        }},
    )
    return {
        "player_id": player_id,
        "aura": aura,
        "note": note,
        "note_breakdown": note_breakdown,
        "updated_at": now,
    }
