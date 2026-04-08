"""
Router API-Football — endpoints proxy pour le frontend.

Préfixe : /api/apifootball

Routes :
  GET /teams/search?q=...           → recherche clubs
  GET /leagues/search?q=...         → recherche compétitions
  GET /players/search?q=...         → recherche joueurs
  GET /players/{id}                 → détail joueur
  GET /players/{id}/transfers       → transferts joueur
  GET /players/{id}/career          → carrière joueur
  GET /players/{id}/trophies        → palmarès joueur
"""

from fastapi import APIRouter, HTTPException, Query
from ..services.apifootball import (
    search_teams,
    search_leagues,
    search_players,
    get_player,
    get_player_transfers,
    get_player_career,
    get_player_trophies,
)

router = APIRouter(prefix="/api/apifootball", tags=["apifootball"])


@router.get("/teams/search")
async def api_search_teams(q: str = Query(..., min_length=2)):
    """Recherche clubs via API-Football."""
    try:
        return await search_teams(q)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/leagues/search")
async def api_search_leagues(q: str = Query(..., min_length=2)):
    """Recherche compétitions via API-Football."""
    try:
        return await search_leagues(q)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/players/search")
async def api_search_players(q: str = Query(..., min_length=2)):
    """Recherche joueurs via API-Football."""
    try:
        return await search_players(q)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/players/{apifootball_id}")
async def api_get_player(apifootball_id: int, season: int = 2024):
    """Détail d'un joueur par son ID API-Football."""
    try:
        result = await get_player(apifootball_id, season)
        if not result:
            raise HTTPException(status_code=404, detail="Joueur introuvable")
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/players/{apifootball_id}/transfers")
async def api_get_player_transfers(apifootball_id: int):
    """Historique des transferts d'un joueur."""
    try:
        return await get_player_transfers(apifootball_id)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/players/{apifootball_id}/career")
async def api_get_player_career(apifootball_id: int):
    """Carrière (clubs + saisons) d'un joueur."""
    try:
        return await get_player_career(apifootball_id)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")


@router.get("/players/{apifootball_id}/trophies")
async def api_get_player_trophies(apifootball_id: int):
    """Palmarès d'un joueur."""
    try:
        return await get_player_trophies(apifootball_id)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API-Football error: {str(e)}")
