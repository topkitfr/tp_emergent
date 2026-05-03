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

    # Filtre les anciens documents malformés puis ajoute/remplace l'entrée
    existing_awards = _clean_awards(player.get("individual_awards", []))
    updated_awards = [a for a in existing_awards
                      if not (a.get("award_id") == entry["award_id"] and a.get("year") == entry["year"])]
    updated_awards.append(entry)

    # Recalcul score — compute_note retourne (note, breakdown)
    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours)
    aura = player.get("aura", 0.0)
    topkit_kits_count = player.get("topkit_kits_count", 0)
    note, note_breakdown = compute_note(
        score_palmares, aura, updated_awards, topkit_kits_count
    )
    now = datetime.now(timezone.utc).isoformat()

    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {
            "individual_awards": updated_awards,
            "score_palmares": score_palmares,
            "note": note,
            "note_breakdown": note_breakdown,
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

    # Recalcul score — compute_note retourne (note, breakdown)
    honours = player.get("honours", [])
    score_palmares = compute_score_palmares(honours)
    aura = player.get("aura", 0.0)
    topkit_kits_count = player.get("topkit_kits_count", 0)
    note, note_breakdown = compute_note(
        score_palmares, aura, updated_awards, topkit_kits_count
    )
    now = datetime.now(timezone.utc).isoformat()

    await db["players"].update_one(
        {"player_id": player_id},
        {"$set": {
            "individual_awards": updated_awards,
            "score_palmares": score_palmares,
            "note": note,
            "note_breakdown": note_breakdown,
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
