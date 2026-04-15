# backend/routers/apifootball_search.py
# Endpoint proxy vers API-Football pour la recherche de clubs, ligues et joueurs.
# Route  : GET /api/apifootball/search/{entity_type}?q=...
# entity_type : 'team' | 'league' | 'player'

import os
import httpx
from fastapi import APIRouter, Query, HTTPException
from typing import Literal

router = APIRouter(prefix="/api/apifootball", tags=["apifootball"])

API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
# Fallback identique à thesportsdb.py pour garantir la clé même sans variable d'env
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "92000910b07df3b860baa17aa7f0ef7d")

HEADERS = {
    "x-apisports-key": API_FOOTBALL_KEY,
}

# ─── Mapping entité → endpoint + clé de réponse ───────────────────────────────
ENTITY_CONFIG = {
    "team": {
        "endpoint": "/teams",
        "param": "search",
        "min_chars": 3,
        "timeout": 10.0,
    },
    "league": {
        "endpoint": "/leagues",
        "param": "search",
        "min_chars": 3,
        "timeout": 10.0,
    },
    "player": {
        # /players/profiles accepte search= sans league ni season obligatoire.
        # Contrairement à /players qui exige league ou team en plus du search.
        "endpoint": "/players/profiles",
        "param": "search",
        "min_chars": 4,
        "timeout": 15.0,
    },
}


@router.get("/search/{entity_type}")
async def search_apifootball(
    entity_type: Literal["team", "league", "player"],
    q: str = Query(..., min_length=2, description="Terme de recherche"),
):
    """
    Proxy de recherche vers API-Football.
    Retourne une liste de résultats bruts selon l'entity_type.
    """
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail=f"entity_type inconnu : {entity_type}")

    if len(q.strip()) < config["min_chars"]:
        return {"results": []}

    url = f"{API_FOOTBALL_BASE}{config['endpoint']}"
    params = {config["param"]: q.strip()}
    if "extra_params" in config:
        params.update(config["extra_params"])

    timeout = config.get("timeout", 10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.get(url, headers=HEADERS, params=params)
            resp.raise_for_status()
        except httpx.TimeoutException:
            return {"results": [], "error": "timeout", "total": 0}
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API-Football error: {e.response.text[:200]}",
            )

    data = resp.json()

    # Erreurs métier (ex: quota dépassé)
    errors = data.get("errors", {})
    if errors:
        first_error = next(iter(errors.values()), "Erreur API-Football")
        raise HTTPException(
            status_code=429 if "limit" in str(first_error).lower() else 502,
            detail=str(first_error),
        )

    results = data.get("response", [])

    return {"results": results, "total": len(results)}
