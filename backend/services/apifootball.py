"""
Service API-Football v3 — wrapper async httpx.

Variables d'environnement :
  APIFOOTBALL_KEY  → clé API (header x-apisports-key)

Endpoints couverts :
  search_teams(name)          → /teams?search=name
  search_leagues(name)        → /leagues?search=name
  search_players(name)        → /players/profiles?search=name
  get_player(apifootball_id)  → /players?id=id&season=2024
  get_player_transfers(id)    → /transfers?player=id
  get_player_career(id)       → /players/teams?player=id
  get_player_trophies(id)     → /trophies?player=id
"""

import os
import httpx
from typing import Optional

BASE_URL = "https://v3.football.api-sports.io"
API_KEY  = os.environ.get("APIFOOTBALL_KEY", "")


def _headers() -> dict:
    return {"x-apisports-key": API_KEY}


async def _get(path: str, params: dict) -> dict:
    """GET générique avec gestion d'erreurs."""
    if not API_KEY:
        raise ValueError("APIFOOTBALL_KEY non configurée")
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE_URL}{path}", headers=_headers(), params=params)
        resp.raise_for_status()
        return resp.json()


# ─── Teams ────────────────────────────────────────────────────────────────────

async def search_teams(name: str) -> list[dict]:
    """Recherche clubs par nom.
    Retourne une liste normalisée TopKit-ready.
    """
    data = await _get("/teams", {"search": name})
    results = []
    for item in data.get("response", []):
        team    = item.get("team", {})
        venue   = item.get("venue", {})
        results.append({
            "apifootball_id":      team.get("id"),
            "name":                team.get("name", ""),
            "code":                team.get("code", ""),
            "country":             team.get("country", ""),
            "founded":             team.get("founded"),
            "is_national":         team.get("national", False),
            "crest_url":           team.get("logo", ""),
            "stadium_name":        venue.get("name", ""),
            "city":                venue.get("city", ""),
            "stadium_capacity":    venue.get("capacity"),
            "stadium_surface":     venue.get("surface", ""),
            "stadium_image_url":   venue.get("image", ""),
        })
    return results


# ─── Leagues ──────────────────────────────────────────────────────────────────

async def search_leagues(name: str) -> list[dict]:
    """Recherche compétitions/ligues par nom.
    Retourne une liste normalisée TopKit-ready.
    """
    data = await _get("/leagues", {"search": name})
    results = []
    for item in data.get("response", []):
        league  = item.get("league", {})
        country = item.get("country", {})
        seasons = item.get("seasons", [])
        results.append({
            "apifootball_league_id": league.get("id"),
            "name":                  league.get("name", ""),
            "type":                  league.get("type", ""),     # "League" | "Cup"
            "logo":                  league.get("logo", ""),
            "country_name":          country.get("name", ""),
            "country_code":          country.get("code", ""),
            "country_flag":          country.get("flag", ""),
            "seasons_available":     [s.get("year") for s in seasons],
        })
    return results


# ─── Players ──────────────────────────────────────────────────────────────────

async def search_players(name: str) -> list[dict]:
    """Recherche joueurs par nom via /players/profiles.
    Retourne une liste normalisée TopKit-ready.
    """
    data = await _get("/players/profiles", {"search": name})
    results = []
    for item in data.get("response", []):
        p = item.get("player", {})
        results.append(_normalize_player(p))
    return results


async def get_player(apifootball_id: int, season: int = 2024) -> Optional[dict]:
    """Récupère un joueur par son ID API-Football."""
    data = await _get("/players", {"id": apifootball_id, "season": season})
    resp = data.get("response", [])
    if not resp:
        return None
    p    = resp[0].get("player", {})
    stats = resp[0].get("statistics", [{}])
    result = _normalize_player(p)
    if stats:
        s = stats[0]
        result["position"]         = s.get("games", {}).get("position", "")
        result["preferred_number"] = s.get("games", {}).get("number")
        result["current_team"]     = s.get("team", {}).get("name", "")
        result["current_team_logo"]= s.get("team", {}).get("logo", "")
    return result


async def get_player_transfers(apifootball_id: int) -> list[dict]:
    """Historique des transferts d'un joueur."""
    data = await _get("/transfers", {"player": apifootball_id})
    results = []
    for item in data.get("response", []):
        for transfer in item.get("transfers", []):
            results.append({
                "date":         transfer.get("date", ""),
                "type":         transfer.get("type", ""),
                "fee_currency": transfer.get("fees", {}).get("currency", "€"),
                "fee_value":    transfer.get("fees", {}).get("value"),
                "teams_in":     transfer.get("teams", {}).get("in", {}).get("name", ""),
                "teams_in_logo":transfer.get("teams", {}).get("in", {}).get("logo", ""),
                "teams_out":    transfer.get("teams", {}).get("out", {}).get("name", ""),
                "teams_out_logo":transfer.get("teams", {}).get("out", {}).get("logo", ""),
            })
    return results


async def get_player_career(apifootball_id: int) -> list[dict]:
    """Carrière (clubs + saisons) d'un joueur."""
    data = await _get("/players/teams", {"player": apifootball_id})
    results = []
    for item in data.get("response", []):
        team    = item.get("team", {})
        seasons = item.get("seasons", [])
        for season in seasons:
            results.append({
                "team_id":   team.get("id"),
                "team_name": team.get("name", ""),
                "team_logo": team.get("logo", ""),
                "season":    season,
            })
    # Trier par saison croissante
    results.sort(key=lambda x: x["season"])
    return results


async def get_player_trophies(apifootball_id: int) -> list[dict]:
    """Palmarès (trophées) d'un joueur."""
    data = await _get("/trophies", {"player": apifootball_id})
    return [
        {
            "league":    t.get("league", ""),
            "country":   t.get("country", ""),
            "season":    t.get("season", ""),
            "place":     t.get("place", ""),
        }
        for t in data.get("response", [])
    ]


# ─── Helper ───────────────────────────────────────────────────────────────────

def _normalize_player(p: dict) -> dict:
    """Normalise un objet player API-Football vers le format TopKit."""
    birth = p.get("birth", {})
    birth_date = birth.get("date", "")
    birth_year = None
    if birth_date and len(birth_date) >= 4:
        try:
            birth_year = int(birth_date[:4])
        except ValueError:
            pass
    return {
        "apifootball_id":  str(p.get("id", "")),
        "full_name":       p.get("name", ""),
        "firstname":       p.get("firstname", ""),
        "lastname":        p.get("lastname", ""),
        "birth_date":      birth_date,
        "birth_year":      birth_year,
        "birth_place":     birth.get("place", ""),
        "birth_country":   birth.get("country", ""),
        "nationality":     p.get("nationality", ""),
        "height":          p.get("height", ""),
        "weight":          p.get("weight", ""),
        "photo_url":       p.get("photo", ""),
    }
