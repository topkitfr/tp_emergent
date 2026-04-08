"""
normalizeLeague — Sprint 1

Converti un payload brut API-Football (/leagues) en dict prêt pour LeagueCreate.
Utilisé par :
  - leagues_api.py (upsert depuis API-Football)
  - seed_confederations.py
  - tout futur endpoint qui ingère des compétitions depuis l'API
"""

from typing import Optional

# Mapping pays → code ISO-2 (complété au besoin)
_COUNTRY_TO_CODE: dict[str, str] = {
    "France": "FR", "England": "GB", "Spain": "ES", "Germany": "DE",
    "Italy": "IT", "Portugal": "PT", "Netherlands": "NL", "Belgium": "BE",
    "Brazil": "BR", "Argentina": "AR", "USA": "US", "Japan": "JP",
    "World": "WLD", "Europe": "EUR", "South America": "SAM",
    "Africa": "AFR", "Asia": "ASI", "North America": "NAM", "Oceania": "OCE",
}

# Confédérations connues → entity_type forcé
_CONFEDERATION_NAMES = {
    "UEFA", "FIFA", "CAF", "CONMEBOL", "AFC", "CONCACAF", "OFC",
}

# Mots-clés → entity_type = "cup"
_CUP_KEYWORDS = ("cup", "coupe", "copa", "pokal", "coppa", "fa cup", "league cup")


def _infer_scope(country: str, league_type: str) -> str:
    """Détermine le scope : domestic | international."""
    international_markers = (
        "world", "europe", "south america", "africa", "asia",
        "north america", "oceania", "international", "global",
    )
    if any(m in country.lower() for m in international_markers):
        return "international"
    if league_type and league_type.lower() == "cup":
        # Les coupes nationales restent domestic
        pass
    return "domestic"


def _infer_region(country: str) -> str:
    """Retourne une région normalisée."""
    mapping = {
        "world": "world",
        "europe": "europe",
        "south america": "south_america",
        "africa": "africa",
        "asia": "asia",
        "north america": "north_america",
        "oceania": "oceania",
    }
    lc = country.lower()
    for key, val in mapping.items():
        if key in lc:
            return val
    return "country"


def _infer_entity_type(name: str, league_type: str, country: str) -> str:
    """Détermine entity_type : league | cup | confederation."""
    name_upper = name.strip().upper()
    for conf in _CONFEDERATION_NAMES:
        if conf in name_upper:
            return "confederation"
    name_lower = name.lower()
    if any(kw in name_lower for kw in _CUP_KEYWORDS):
        return "cup"
    if league_type and league_type.lower() == "cup":
        return "cup"
    return "league"


def normalize_league(api_payload: dict) -> dict:
    """
    Prend la réponse brute d'un item /leagues de API-Football :
      {
        "league": { "id": 61, "name": "Ligue 1", "type": "League", "logo": "..." },
        "country": { "name": "France", "code": "FR", "flag": "..." },
        "seasons": [...]
      }
    Retourne un dict compatible avec LeagueCreate / db.leagues.insert.
    """
    league = api_payload.get("league", {})
    country = api_payload.get("country", {})

    name: str = league.get("name", "").strip()
    league_type: str = league.get("type", "").strip()   # "League" | "Cup"
    logo: str = league.get("logo", "") or ""
    apifootball_id: Optional[int] = league.get("id")

    country_name: str = country.get("name", "").strip()
    country_code: str = country.get("code") or _COUNTRY_TO_CODE.get(country_name, "")
    country_flag: str = country.get("flag", "") or ""

    scope = _infer_scope(country_name, league_type)
    region = _infer_region(country_name)
    entity_type = _infer_entity_type(name, league_type, country_name)

    # organizer : confédération détectée dans le nom, sinon vide
    organizer = ""
    for conf in _CONFEDERATION_NAMES:
        if conf in name.upper():
            organizer = conf
            break

    result = {
        "name": name,
        "logo_url": logo,
        "apifootball_league_id": apifootball_id,
        "apifootball_logo": logo,
        "entity_type": entity_type,          # "league" | "cup" | "confederation"
        "scope": scope,                       # "domestic" | "international"
        "region": region,                     # "country" | "europe" | "world" | ...
        "organizer": organizer,
        "country_or_region": country_name,
        "country_name": country_name if scope == "domestic" else None,
        "country_code": country_code or None,
        "country_flag": country_flag or None,
        "source_payload": api_payload,        # conservation payload brut pour re-sync
    }
    return result
