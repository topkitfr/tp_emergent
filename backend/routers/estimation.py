from fastapi import APIRouter
from ..models import EstimationRequest
from ..utils import calculate_estimation_for_collection_item
from ..database import db

router = APIRouter(prefix="/api", tags=["estimation"])


async def _get_player_note(player_id: str) -> float:
    """Récupère la note /100 d'un joueur depuis la DB. Retourne 0.0 si non trouvé."""
    if not player_id:
        return 0.0
    player = await db.players.find_one(
        {"player_id": player_id},
        {"_id": 0, "note": 1}
    )
    return float(player.get("note") or 0.0) if player else 0.0


@router.post("/estimate")
async def estimate_price(req: EstimationRequest):
    """
    Calcule le prix estimé d'un maillot.

    mode="basic"    : Modèle + Compétition + État physique
    mode="advanced" : Tous les critères (défaut)

    Option A : si flocking_player_id est fourni, la note du joueur
    est récupérée depuis la DB et remplace flocking_player_profile.
    Barème :
      note 0–39  → "none"           (+0.00)
      note 40–64 → "good_player"    (+0.25)
      note 65–79 → "club_star"      (+0.50)
      note 80–89 → "world_star"     (+0.75)
      note 90–100 → "football_legend" (+1.00)
    """
    player_note = await _get_player_note(req.flocking_player_id or "")
    result = calculate_estimation_for_collection_item(
        model_type=req.model_type,
        competition=req.competition or "",
        condition_origin=req.condition_origin or "",
        physical_state=req.physical_state or "",
        flocking_origin=req.flocking_origin or "",
        flocking_player_note=player_note,
        signed=req.signed or False,
        signed_type=req.signed_type or "",
        signed_other_detail=req.signed_other_detail or "",
        signed_proof=req.signed_proof or "none",
        season_year=req.season_year or 0,
        patch=req.patch or False,
        is_rare=req.is_rare or False,
        rare_reason=req.rare_reason or "",
        mode=req.mode or "advanced",
    )
    # Ajouter la note joueur dans la réponse pour info frontend
    result["flocking_player_note"] = player_note
    return result
