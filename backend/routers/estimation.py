from fastapi import APIRouter
from models import EstimationRequest
from utils import calculate_estimation

router = APIRouter(prefix="/api", tags=["estimation"])


@router.post("/estimate")
async def estimate_price(req: EstimationRequest):
    result = calculate_estimation(
        model_type=req.model_type,
        competition=req.competition or "",
        condition_origin=req.condition_origin or "",
        physical_state=req.physical_state or "",
        flocking_origin=req.flocking_origin or "",
        signed=req.signed or False,
        signed_proof=req.signed_proof or False,
        season_year=req.season_year or 0
    )
    return result
