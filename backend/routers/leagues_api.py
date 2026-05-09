# backend/routers/leagues_api.py
# Recherche leagues en DB.
# GET /api/leagues?search=...&limit=N&skip=N

from fastapi import APIRouter, Query
from typing import Optional
import re

from ..database import db

router = APIRouter(prefix="/api/leagues", tags=["leagues"])


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("")
async def search_leagues(
    search: Optional[str] = Query(None, min_length=2),
    limit: int = Query(8, ge=1, le=50),
    skip: int = Query(0, ge=0),
):
    query = {}
    if search:
        query["name"] = {"$regex": re.escape(search.strip()), "$options": "i"}

    cursor = db.leagues.find(query).skip(skip).limit(limit).sort("name", 1)
    leagues = [_serialize(doc) async for doc in cursor]
    total = await db.leagues.count_documents(query)

    return {"leagues": leagues, "total": total}
