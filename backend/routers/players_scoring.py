"""Router players_scoring — enrichissement automatique via API-Football.

Routes :
  GET  /api/scoring/players/search?name=...        → recherche DB-first + API-Football
  POST /api/scoring/players/enrich                 → enrichit palmarès
  GET  /api/scoring/players/{player_id}/full       → fiche complète (identité + carrière + palmarès + maillots)
  GET  /api/scoring/players/{player_id}/career     → carrière clubs + maillots Topkit liés
  GET  /api/scoring/players/{player_id}            → score actuel
  PATCH /api/scoring/players/{player_id}/aura      → mise à jour aura
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
import re

from ..database import db
from ..models import PlayerScoringEnrichRequest, PlayerScoringOut
from ..services.thesportsdb import (
    search_players_db_first,
    lookup_honours,
    lookup_career,
    lookup_player_profile,
    compute_score_palmares,
    compute_note,
    _dedup_honours,
)

router = APIRouter(prefix="/api/scoring/players", tags=["players-scoring"])

KITS_PREVIEW_LIMIT = 5


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


# ── routes ───────────────────────────────────────────────────────────────────

@router.get("/search")
async def search_players(name: str = Query(..., min_length=2)):
    """Recherche DB-first puis API-Football."""
    try:
        results = await search_players_db_first(name, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search error: {str(e)}")
    return results


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

    # Dédupliquer et nettoyer
    honours_deduped = _dedup_honours(honours_raw)
    honours_clean = [
        {
            "honour": h.get("strHonour", ""),
            "season": h.get("strSeason", ""),
            "team": h.get("strTeam", ""),
            "place": h.get("place", ""),
            "league": h.get("league", ""),
        }
        for h in honours_deduped
    ]

    individual_awards = player.get("individual_awards", [])
    score_palmares = compute_score_palmares(honours_raw, individual_awards)
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


@router.get("/{player_id}/full")
async def get_player_full(player_id: str):
    """Fiche complète d'un joueur :
      - identité (DB + API-Football si apifootball_id)
      - carrière clubs + montant transfert
      - maillots Topkit (5 max + total)
      - trophées individuels
      - palmarès collectif (Winner / 2nd Place)
      - score + note sur 100
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    apifootball_id = player.get("apifootball_id") or player.get("tsdb_id")

    # 1. Identité API-Football (si dispo)
    api_identity = None
    if apifootball_id:
        try:
            api_identity = await lookup_player_profile(apifootball_id)
        except Exception:
            pass

    identity = {
        "player_id": player_id,
        "full_name": player.get("full_name", ""),
        "slug": player.get("slug", ""),
        "nationality": api_identity["nationality"] if api_identity else player.get("nationality", ""),
        "birth_date": api_identity["birth_date"] if api_identity else player.get("birth_date", ""),
        "birth_place": api_identity.get("birth_place", "") if api_identity else "",
        "birth_country": api_identity.get("birth_country", "") if api_identity else "",
        "age": api_identity.get("age") if api_identity else None,
        "height": api_identity.get("height", "") if api_identity else "",
        "weight": api_identity.get("weight", "") if api_identity else "",
        "position": api_identity.get("position", "") if api_identity else (player.get("positions") or [""])[0],
        "photo": api_identity.get("photo", "") if api_identity else player.get("photo_url", ""),
        "bio": player.get("bio", ""),
        "apifootball_id": apifootball_id or "",
    }

    # 2. Carrière clubs + montant transfert
    career = []
    if apifootball_id:
        try:
            transfers = await lookup_career(apifootball_id)
            sorted_transfers = sorted(transfers, key=lambda x: x["date"] or "")
            for i, t in enumerate(sorted_transfers):
                date_end = sorted_transfers[i + 1]["date"] if i + 1 < len(sorted_transfers) else None
                career.append({
                    "club": t["club"],
                    "team_logo": t["team_logo"],
                    "from_club": t["from_club"],
                    "from_club_logo": t.get("from_club_logo", ""),
                    "date_start": t["date"],
                    "date_end": date_end,
                    "year_start": _extract_year(t["date"]),
                    "year_end": _extract_year(date_end),
                    "transfer_type": t.get("transfer_type", ""),  # "Free", "Loan", "€ 180M"…
                })
            career.reverse()  # plus récent en premier
        except Exception:
            pass

    # 3. Maillots Topkit (5 max, tous clubs confondus)
    all_topkit_kits = []
    for entry in career:
        kits, _ = await _match_kits(
            entry["club"],
            entry.get("year_start"),
            entry.get("year_end"),
            limit=None,
        )
        all_topkit_kits.extend(kits)

    topkit_kits_total = len(all_topkit_kits)
    topkit_kits_preview = all_topkit_kits[:KITS_PREVIEW_LIMIT]

    # 4. Trophées individuels
    individual_awards = player.get("individual_awards", [])

    # 5. Palmarès collectif (dédupliqué, groupé Winner / 2nd Place)
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

    # 6. Score
    score_palmares = player.get("score_palmares", 0.0)
    aura = player.get("aura", 0.0)
    note = player.get("note", 0.0)

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
        "note": note,  # sur 100
        "has_apifootball_id": bool(apifootball_id),
    }


@router.get("/{player_id}/career")
async def get_player_career(player_id: str):
    """Retourne la carrière clubs d'un joueur avec les maillots Topkit liés."""
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

    sorted_transfers = sorted(transfers, key=lambda x: x["date"] or "")
    career = []
    for i, t in enumerate(sorted_transfers):
        date_end = sorted_transfers[i + 1]["date"] if i + 1 < len(sorted_transfers) else None
        year_start = _extract_year(t["date"])
        year_end = _extract_year(date_end)
        kits, total = await _match_kits(t["club"], year_start, year_end)
        career.append({
            "club": t["club"],
            "team_logo": t["team_logo"],
            "from_club": t["from_club"],
            "from_club_logo": t.get("from_club_logo", ""),
            "date_start": t["date"],
            "date_end": date_end,
            "year_start": year_start,
            "year_end": year_end,
            "transfer_type": t.get("transfer_type", ""),
            "topkit_kits": kits,
            "topkit_kits_total": total,
        })
    career.reverse()
    return {"player_id": player_id, "has_apifootball_id": True, "career": career}


@router.get("/{player_id}", response_model=PlayerScoringOut)
async def get_player_scoring(player_id: str):
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
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")
    score_palmares = player.get("score_palmares", 0.0)
    individual_awards = player.get("individual_awards", [])
    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours, individual_awards)
    note = compute_note(score_palmares, aura)
    now = datetime.now(timezone.utc).isoformat()
    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {"aura": aura, "score_palmares": score_palmares, "note": note, "updated_at": now}},
    )
    return {"player_id": player_id, "aura": aura, "note": note, "updated_at": now}
