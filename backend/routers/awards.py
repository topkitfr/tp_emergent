"""Router awards — CRUD des trophées individuels (Ballon d'Or, Golden Boot…).

Routes :
  GET    /api/awards            → liste tous les awards
  POST   /api/awards            → créer un award
  PATCH  /api/awards/{award_id} → mettre à jour
  DELETE /api/awards/{award_id} → supprimer

  POST   /api/awards/player/{player_id}         → ajouter un award à un joueur
  DELETE /api/awards/player/{player_id}/{award_id} → retirer un award d'un joueur
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid

from ..database import db
from ..models import AwardCreate, AwardOut
from ..services.thesportsdb import compute_score_palmares, compute_note

router = APIRouter(prefix="/api/awards", tags=["awards"])


# ── Helpers ────────────────────────────────────────────────────────────

def _clean_awards(awards: list) -> list:
    """Filtre les entrées malformées (sans award_id) dans individual_awards."""
    return [a for a in awards if a.get("award_id")]


async def _get_player_aura_and_kits(player: dict) -> tuple[float, int]:
    """Retourne (aura_sur_100, topkit_kits_count) pour un joueur.

    - aura : aura_avg (0-10) * 10 → 0-100. Fallback sur champ 'aura' si absent.
    - topkit_kits_count : nb de collection items où le joueur est flocqué ou signataire.
      Champs concernés : flocking_player_id, signed_by_player_id.
    """
    aura_avg = player.get("aura_avg")
    if aura_avg is not None:
        aura = float(aura_avg) * 10.0
    else:
        aura = float(player.get("aura") or 0.0)

    pid = player["player_id"]
    topkit_kits_count = await db["collections"].count_documents({
        "$or": [
            {"flocking_player_id": pid},
            {"signed_by_player_id": pid},
        ]
    })

    return aura, topkit_kits_count


# ── Référentiel awards ────────────────────────────────────────────────────────

@router.get("", response_model=list[AwardOut])
async def list_awards():
    """Liste tous les awards disponibles."""
    awards = await db["awards"].find().sort("name", 1).to_list(length=200)
    return [AwardOut(**a) for a in awards]


@router.post("", response_model=AwardOut)
async def create_award(body: AwardCreate):
    """Crée un nouveau type d'award."""
    now = datetime.now(timezone.utc).isoformat()
    award_id = str(uuid.uuid4())
    doc = {
        "award_id": award_id,
        "name": body.name,
        "category": body.category or "individual",
        "scoring_weight": body.scoring_weight or 5.0,
        "logo_url": body.logo_url or "",
        "description": body.description or "",
        "created_at": now,
        "updated_at": now,
    }
    await db["awards"].insert_one(doc)
    return AwardOut(**doc)


@router.patch("/{award_id}")
async def update_award(award_id: str, body: dict):
    """Met à jour un award (nom, poids, logo…)."""
    award = await db["awards"].find_one({"award_id": award_id})
    if not award:
        raise HTTPException(status_code=404, detail="Award introuvable")

    allowed = {"name", "category", "scoring_weight", "logo_url", "description"}
    update = {k: v for k, v in body.items() if k in allowed}
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db["awards"].update_one({"award_id": award_id}, {"$set": update})
    return {"award_id": award_id, **update}


@router.delete("/{award_id}")
async def delete_award(award_id: str):
    result = await db["awards"].delete_one({"award_id": award_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Award introuvable")
    return {"deleted": True, "award_id": award_id}


# ── Awards d'un joueur ────────────────────────────────────────────────────────

@router.post("/player/{player_id}")
async def add_player_award(player_id: str, body: dict):
    """Ajoute un award individuel à un joueur et recalcule son score.

    Body:
      {
        award_id: str,
        year: str,      (ex: "2023")
        count: int      (ex: 1)
      }
    """
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    award = await db["awards"].find_one({"award_id": body.get("award_id")})
    if not award:
        raise HTTPException(status_code=404, detail="Award introuvable")

    entry = {
        "award_id": award["award_id"],
        "award_name": award["name"],
        "scoring_weight": award["scoring_weight"],
        "year": body.get("year", ""),
        "count": int(body.get("count", 1)),
    }

    existing_awards = _clean_awards(player.get("individual_awards", []))
    updated_awards = [a for a in existing_awards
                      if not (a.get("award_id") == entry["award_id"] and a.get("year") == entry["year"])]
    updated_awards.append(entry)

    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours)
    aura, topkit_kits_count = await _get_player_aura_and_kits(player)
    note, note_breakdown = compute_note(score_palmares, aura, updated_awards, topkit_kits_count)
    now = datetime.now(timezone.utc).isoformat()

    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {
            "individual_awards": updated_awards,
            "score_palmares": score_palmares,
            "note": note,
            "note_breakdown": note_breakdown,
            "topkit_kits_count": topkit_kits_count,
            "updated_at": now,
        }}
    )

    return {
        "player_id": player_id,
        "individual_awards": updated_awards,
        "score_palmares": score_palmares,
        "note": note,
        "note_breakdown": note_breakdown,
    }


@router.delete("/player/{player_id}/{award_id}")
async def remove_player_award(player_id: str, award_id: str, year: str = ""):
    """Retire un award d'un joueur et recalcule son score."""
    player = await db["players"].find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    existing_awards = _clean_awards(player.get("individual_awards", []))
    if year:
        updated_awards = [a for a in existing_awards
                          if not (a.get("award_id") == award_id and a.get("year") == year)]
    else:
        updated_awards = [a for a in existing_awards if a.get("award_id") != award_id]

    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours)
    aura, topkit_kits_count = await _get_player_aura_and_kits(player)
    note, note_breakdown = compute_note(score_palmares, aura, updated_awards, topkit_kits_count)
    now = datetime.now(timezone.utc).isoformat()

    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {
            "individual_awards": updated_awards,
            "score_palmares": score_palmares,
            "note": note,
            "note_breakdown": note_breakdown,
            "topkit_kits_count": topkit_kits_count,
            "updated_at": now,
        }}
    )

    return {
        "player_id": player_id,
        "individual_awards": updated_awards,
        "score_palmares": score_palmares,
        "note": note,
        "note_breakdown": note_breakdown,
    }
