"""Router players_api — recherche joueurs avec DB-first + API-Football fallback.

Routes :
  GET  /api/players-api/search?name=...  → recherche DB + API-Football
  GET  /api/players-api/get/{id}         → profil complet par apifootball_id

⚠️  Cache mémoire 24 h sur /search pour économiser le quota API-Football (100 req/j).
    Entrée = query lowercasée, TTL = CACHE_TTL secondes.
    Le cache est purgé au redémarrage du conteneur.
"""

import time as _time

from fastapi import APIRouter, HTTPException, Query

from ..database import db
from ..services.thesportsdb import search_players_db_first, lookup_player_profile

router = APIRouter(prefix="/api/players-api", tags=["players-api"])

# ── Cache mémoire 24 h ───────────────────────────────────────────────────
CACHE_TTL: int = 86_400  # 24 heures
_search_cache: dict[str, tuple[float, dict]] = {}


def _cache_get(key: str):
    """Retourne la valeur cachée ou None si absente/expirée."""
    entry = _search_cache.get(key)
    if entry is None:
        return None
    ts, data = entry
    if _time.monotonic() - ts > CACHE_TTL:
        del _search_cache[key]
        return None
    return data


def _cache_set(key: str, data: dict) -> None:
    _search_cache[key] = (_time.monotonic(), data)


# ── Routes ───────────────────────────────────────────────────────────────

@router.get("/search")
async def search_players(name: str = Query(..., min_length=2)):
    """Recherche DB-first puis API-Football (avec cache 24 h).

    Retourne :
      {
        db_results:  [ { source, player_id, apifootball_id, name, nationality,
                         birth_date, photo, note } ],
        api_results: [ { source, apifootball_id, name, firstname, lastname,
                         nationality, birth_date, birth_place, photo,
                         height, weight, position } ]
      }
    """
    cache_key = name.strip().lower()
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        results = await search_players_db_first(name, db)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Search error: {str(e)}")

    _cache_set(cache_key, results)
    return results


@router.get("/get/{apifootball_id}")
async def get_player_profile(apifootball_id: str):
    """Récupère le profil complet d'un joueur depuis API-Football par son ID.

    Utilisé pour le préfill du formulaire joueur après sélection dans
    ApiFootballSearch.

    Retourne les champs mappés au modèle TopKit :
      apifootball_id, name, firstname, lastname, birth_date, birth_place,
      birth_country, nationality, height, weight, position, photo, number
    """
    try:
        profile = await lookup_player_profile(apifootball_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"API error: {str(e)}")
    if not profile:
        raise HTTPException(status_code=404, detail="Joueur non trouvé")
    return profile
