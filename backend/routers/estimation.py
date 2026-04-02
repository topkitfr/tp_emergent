from fastapi import APIRouter
from ..models import EstimationRequest
from ..utils import calculate_estimation_for_collection_item

router = APIRouter(prefix="/api", tags=["estimation"])


@router.post("/estimate")
async def estimate_price(req: EstimationRequest):
    """
    Calcule le prix estimé d'un maillot.

    mode="basic"    : Modèle + Compétition + État physique
    mode="advanced" : Tous les critères (défaut)
    """
    result = calculate_estimation_for_collection_item(
        model_type=req.model_type,
        competition=req.competition or "",
        condition_origin=req.condition_origin or "",
        physical_state=req.physical_state or "",
        flocking_origin=req.flocking_origin or "",
        flocking_player_profile=req.flocking_player_profile or "none",
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
    return result
