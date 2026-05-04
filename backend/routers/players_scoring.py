"""Router players_scoring — enrichissement automatique via API-Football.

Routes :
  GET  /api/scoring/players/search?name=...        → recherche DB-first + API-Football
  POST /api/scoring/players/enrich                 → enrichit palmarès
  GET  /api/scoring/players/{player_id}/full       → fiche complète (identité + carrière + palmarès + maillots)
  GET  /api/scoring/players/{player_id}/career     → carrière clubs + maillots Topkit liés
  GET  /api/scoring/players/{player_id}            → score actuel
  PATCH /api/scoring/players/{player_id}/aura      → mise à jour aura

IMPORTANT: les routes statiques (/search, /enrich) sont déclarées AVANT les routes
dynamiques (/{player_id}) pour éviter que FastAPI matche "search" ou "enrich"
comme un player_id et renvoie une Pydantic validation error à la place d'un 404.
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


async def _count_all_player_kits(player_id: str) -> int:
    """Compte le nombre d'items TopKit floqués au nom du joueur."""
    count = await db["collections"].count_documents({"flocking_player_id": player_id})
    return count


# ── routes STATIQUES (doivent être déclarées AVANT /{player_id}) ─────────────

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
    score_palmares = compute_score_palmares(honours_raw)

    # Récupère et persiste la carrière depuis API-Football
    try:
        transfers = await lookup_career(body.apifootball_id)
        sorted_transfers = sorted(transfers, key=lambda x: x["date"] or "")
        career_clean = []
        for i, t in enumerate(sorted_transfers):
            date_end = sorted_transfers[i + 1]["date"] if i + 1 < len(sorted_transfers) else None
            career_clean.append({
                "club": t["club"],
                "team_logo": t["team_logo"],
                "from_club": t["from_club"],
                "date_start": t["date"],
                "date_end": date_end,
                "year_start": _extract_year(t["date"]),
                "year_end": _extract_year(date_end),
                "transfer_type": t.get("transfer_type", ""),
            })
        career_clean.reverse()
    except Exception:
        career_clean = player.get("career", [])

    # Calcul du nombre de maillots TopKit via la carrière fraîche
    topkit_kits_count = await _count_all_player_kits(body.player_id)

    # Lire aura_avg depuis la DB (ne jamais écraser avec body.aura)
    aura_db = player.get("aura", 0.0)
    note, note_breakdown = compute_note(
        score_palmares=score_palmares,
        aura=aura_db,
        individual_awards=individual_awards,
        topkit_kits_count=topkit_kits_count,
    )
    now = datetime.now(timezone.utc).isoformat()

    await coll.update_one(
        {"player_id": body.player_id},
        {"$set": {
            "apifootball_id": body.apifootball_id,
            "honours": honours_clean,
            "career": career_clean,
            "score_palmares": score_palmares,

            "note": note,
            "note_breakdown": note_breakdown,
            "updated_at": now,
        }},
    )

    return PlayerScoringOut(
        player_id=body.player_id,
        full_name=player.get("full_name", ""),
        apifootball_id=body.apifootball_id,
        honours_count=len(honours_clean),
        score_palmares=score_palmares,
        aura=aura_db,
        note=note,
        note_breakdown=note_breakdown,
        updated_at=now,
    )


# ── routes DYNAMIQUES /{player_id}/... ───────────────────────────────────────

@router.get("/{player_id}/full")
async def get_player_full(player_id: str):
    """Fiche complète d'un joueur :
      - identité (DB + API-Football si apifootball_id)
      - carrière clubs (API-Football si dispo, sinon DB)
      - maillots Topkit (5 max + total)
      - trophées individuels
      - palmarès collectif (Winner / 2nd Place)
      - score + note sur 100 + breakdown
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    apifootball_id = player.get("apifootball_id") or player.get("tsdb_id")

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

    # Carrière : API-Football en priorité, sinon fallback sur la DB (entrées manuelles)
    career = []
    if apifootball_id:
        try:
            transfers = await lookup_career(apifootball_id)
            if transfers:
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
                        "transfer_type": t.get("transfer_type", ""),
                        "source": "api",
                    })
                career.reverse()
        except Exception:
            pass

    # Fallback DB si l'API n'a rien retourné (pas d'apifootball_id ou API vide)
    if not career:
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
        "has_apifootball_id": bool(apifootball_id),
    }


@router.get("/{player_id}/career")
async def get_player_career(player_id: str):
    """Retourne la carrière clubs d'un joueur avec les maillots Topkit liés.
    Fallback sur la carrière DB si pas d'apifootball_id ou API vide.
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    apifootball_id = player.get("apifootball_id") or player.get("tsdb_id")

    # Tente l'API si on a un ID
    transfers = []
    if apifootball_id:
        try:
            transfers = await lookup_career(apifootball_id)
        except Exception:
            transfers = []

    # Fallback DB si l'API est vide
    if not transfers:
        db_career = player.get("career", [])
        if not db_career:
            return {"player_id": player_id, "has_apifootball_id": bool(apifootball_id), "career": [], "source": "none"}

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
        return {"player_id": player_id, "has_apifootball_id": bool(apifootball_id), "career": career, "source": "manual"}

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
            "source": "api",
        })
    career.reverse()
    return {"player_id": player_id, "has_apifootball_id": True, "career": career, "source": "api"}


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
        note_breakdown=player.get("note_breakdown"),
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
    score_palmares = compute_score_palmares(honours)

    # Compte les maillots TopKit via la carrière stockée en DB
    career_raw = player.get("career", [])
    topkit_kits_count = await _count_all_player_kits(player_id)

    # Lire aura_avg depuis la DB (ne jamais écraser avec body.aura)
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
