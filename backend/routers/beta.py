from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from .database import db

router = APIRouter(prefix="/api/beta", tags=["beta"])


class BetaCodeRequest(BaseModel):
    code: str


@router.post("/verify")
async def verify_beta_code(body: BetaCodeRequest):
    code = body.code.strip().upper()
    doc = await db.beta_codes.find_one({"code": code, "active": True})

    if not doc:
        raise HTTPException(status_code=403, detail="Invalid code")

    # Verifier le quota si max_uses defini
    if doc.get("max_uses") and doc["uses"] >= doc["max_uses"]:
        raise HTTPException(status_code=403, detail="Invalid code")

    # Incrementer le compteur d'utilisation
    await db.beta_codes.update_one(
        {"_id": doc["_id"]},
        {"$inc": {"uses": 1}, "$set": {"last_used_at": datetime.utcnow()}}
    )

    return {"valid": True}
