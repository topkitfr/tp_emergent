"""
normalizeLeague(api_league) — Sprint 1

Transforme la réponse brute API-Football (endpoint /leagues)
en un dict prêt à insérer dans la collection `leagues` de TopKit.

Structure d'entrée attendue (réponse API-Football) :
{
    "league": { "id": 61, "name": "Ligue 1", "type": "League", "logo": "..." },
    "country": { "name": "France", "code": "FR", "flag": "..." },
    "seasons": [...]
}
"""
from typing import Optional

# ── Mapping type API → entity_type TopKit ─────────────────────────────────────
ENTITY_TYPE_MAP = {
    "League": "league",
    "Cup": "cup",
    "league": "league",
    "cup": "cup",
}

# ── Mapping pays connus → region ──────────────────────────────────────────────
EUROPEAN_COUNTRIES = {
    "France", "England", "Spain", "Germany", "Italy", "Portugal", "Netherlands",
    "Belgium", "Scotland", "Turkey", "Greece", "Russia", "Poland", "Ukraine",
    "Switzerland", "Austria", "Denmark", "Sweden", "Norway", "Czech Republic",
    "Croatia", "Romania", "Serbia", "Hungary",
}
SOUTH_AMERICAN_COUNTRIES = {
    "Brazil", "Argentina", "Colombia", "Chile", "Uruguay", "Peru", "Ecuador",
    "Paraguay", "Bolivia", "Venezuela",
}
AFRICAN_COUNTRIES = {
    "Morocco", "Egypt", "Tunisia", "Algeria", "South Africa", "Nigeria",
    "Ghana", "Senegal", "Ivory Coast", "Cameroon", "Kenya",
}

# Pays internationaux connus (ligues mondiales/continentales)
INTERNATIONAL_NAMES = {"World", "Europe", "South America", "Africa", "Asia", "Oceania"}


def _infer_scope(country_name: Optional[str]) -> str:
    """Retourne 'domestic' ou 'international' selon le pays."""
    if not country_name or country_name in INTERNATIONAL_NAMES:
        return "international"
    return "domestic"


def _infer_region(country_name: Optional[str]) -> str:
    """Retourne une région normalisée."""
    if not country_name:
        return "world"
    if country_name in EUROPEAN_COUNTRIES:
        return "europe"
    if country_name in SOUTH_AMERICAN_COUNTRIES:
        return "south_america"
    if country_name in AFRICAN_COUNTRIES:
        return "africa"
    if country_name == "World":
        return "world"
    if country_name == "Europe":
        return "europe"
    if country_name == "South America":
        return "south_america"
    if country_name == "Africa":
        return "africa"
    if country_name == "Asia":
        return "asia"
    if country_name == "Oceania":
        return "oceania"
    # Par défaut : domestic mais région générique
    return "other"


def _slugify(name: str) -> str:
    """Slug basique : lowercase, espaces → tirets, suppression caractères spéciaux."""
    import re
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug)
    return slug.strip("-")


def normalize_league(api_response: dict) -> dict:
    """
    Normalise une entrée API-Football /leagues en dict TopKit.

    Paramètre :
        api_response : une entrée du tableau `response[]` retourné par API-Football
                       (contient les clés "league", "country", "seasons")

    Retourne :
        dict prêt à être inséré/mis à jour dans la collection `leagues`
    """
    league_data = api_response.get("league", {})
    country_data = api_response.get("country", {})

    apifootball_id = league_data.get("id")
    name = league_data.get("name", "")
    api_type = league_data.get("type", "League")  # "League" | "Cup"
    logo = league_data.get("logo", "")

    country_name = country_data.get("name", "")
    country_code = country_data.get("code", "")
    country_flag = country_data.get("flag", "")

    entity_type = ENTITY_TYPE_MAP.get(api_type, "league")
    scope = _infer_scope(country_name)
    region = _infer_region(country_name)

    # Organizer : FIFA pour scope world, sinon on laisse vide (à enrichir manuellement)
    organizer = ""
    if scope == "international" and region == "world":
        organizer = "FIFA"
    elif scope == "international" and region == "europe":
        organizer = "UEFA"
    elif scope == "international" and region == "south_america":
        organizer = "CONMEBOL"
    elif scope == "international" and region == "africa":
        organizer = "CAF"
    elif scope == "international" and region == "asia":
        organizer = "AFC"
    elif scope == "international" and region == "north_central_america":
        organizer = "CONCACAF"
    elif scope == "international" and region == "oceania":
        organizer = "OFC"

    slug = _slugify(f"{name}-{country_name}" if country_name else name)

    return {
        "name": name,
        "slug": slug,
        "entity_type": entity_type,
        "scope": scope,
        "region": region,
        "organizer": organizer,
        "country_or_region": country_name or "",
        "country_name": country_name or "",
        "country_code": country_code or "",
        "country_flag": country_flag or "",
        "logo_url": logo or "",
        "apifootball_logo": logo or "",
        "apifootball_league_id": apifootball_id,
        "level": "domestic" if scope == "domestic" else "continental",
        "source_payload": api_response,  # réponse brute pour re-sync future
        "kit_count": 0,
        "status": "approved",
    }
