"""Client async API-Football (api-sports.io) — free tier (100 req/day).

Endpoints utilisés :
  - GET /players/profiles?search={name}  → recherche joueur (DB-first)
  - GET /trophies?player={id}            → palmarès complet
  - GET /transfers?player={id}           → historique de clubs
  - GET /leagues?search={name}           → recherche compétition (DB-first)
  - GET /teams?search={name}             → recherche club (DB-first)

Doc : https://api-sports.io/documentation/football/v3
"""

import httpx
from typing import List
import os

BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.environ.get("API_FOOTBALL_KEY", "92000910b07df3b860baa17aa7f0ef7d")

# ── Poids des compétitions (fallback si pas en DB) ────────────────────────────
HONOUR_WEIGHTS: dict[str, float] = {
    "world cup": 20.0,
    "coupe du monde": 20.0,
    "champions league": 15.0,
    "ligue des champions": 15.0,
    "copa libertadores": 12.0,
    "euro": 10.0,
    "copa america": 10.0,
    "african cup": 10.0,
    "afcon": 10.0,
    "la liga": 7.0,
    "premier league": 7.0,
    "bundesliga": 7.0,
    "serie a": 7.0,
    "ligue 1": 6.0,
    "primeira division": 7.0,
    "fa cup": 4.0,
    "copa del rey": 4.0,
    "dfb pokal": 4.0,
    "coppa italia": 4.0,
    "coupe de france": 3.0,
    "supercoupe": 2.0,
    "supercopa": 2.0,
    "super cup": 2.0,
    "community shield": 2.0,
    "intercontinental": 8.0,
    "nations league": 6.0,
}

# Poids des awards individuels (fallback si pas en DB)
AWARD_WEIGHTS: dict[str, float] = {
    "ballon d'or": 8.0,
    "ballon dor": 8.0,
    "the best": 5.0,
    "fifa best": 5.0,
    "golden boot": 3.0,
    "golden ball": 3.0,
    "golden glove": 2.0,
    "best player": 3.0,
    "player of the year": 3.0,
}

# Multiplicateur selon place
PLACE_MULTIPLIER: dict[str, float] = {
    "winner": 1.0,
    "2nd place": 0.15,
    "runner-up": 0.15,
    "3rd place": 0.05,
}

DEFAULT_HONOUR_WEIGHT = 1.5
SCORE_MESSI_REF = 100.0

# ── Confédérations connues ────────────────────────────────────────────────────
CONFEDERATION_MAP: dict[str, tuple[str, str]] = {
    "UEFA": ("europe", "UEFA"),
    "FIFA": ("world", "FIFA"),
    "CAF": ("africa", "CAF"),
    "CONMEBOL": ("south_america", "CONMEBOL"),
    "AFC": ("asia", "AFC"),
    "CONCACAF": ("north_america", "CONCACAF"),
    "OFC": ("oceania", "OFC"),
}


def _headers() -> dict:
    return {"x-apisports-key": API_KEY}


# ── Sprint 1 — Normalisation league ──────────────────────────────────────────

def normalize_league(api_league: dict) -> dict:
    """Normalise une réponse API-Football /leagues en modèle TopKit."""
    league = api_league.get("league", {})
    country = api_league.get("country", {}) or {}
    name = league.get("name", "")
    upper = name.upper()

    for keyword, (region, organizer) in CONFEDERATION_MAP.items():
        if keyword in upper:
            return {
                "apifootball_league_id": league.get("id"),
                "name": name,
                "type": league.get("type"),
                "entity_type": "confederation" if upper.strip() == keyword else "league",
                "scope": "international",
                "region": region,
                "organizer": organizer,
                "country_name": None,
                "country_code": None,
                "country_flag": None,
                "country_or_region": region,
                "logo_url": league.get("logo", ""),
                "apifootball_logo": league.get("logo", ""),
                "source_payload": api_league,
            }

    country_name = country.get("name") or None
    return {
        "apifootball_league_id": league.get("id"),
        "name": name,
        "type": league.get("type"),
        "entity_type": league.get("type") or "league",
        "scope": "domestic" if country_name else "international",
        "region": "country" if country_name else None,
        "organizer": None,
        "country_name": country_name,
        "country_code": country.get("code") or None,
        "country_flag": country.get("flag") or None,
        "country_or_region": country_name or "",
        "logo_url": league.get("logo", ""),
        "apifootball_logo": league.get("logo", ""),
        "source_payload": api_league,
    }


# ── Normalisation team ────────────────────────────────────────────────────────

def normalize_team(api_item: dict) -> dict:
    """Normalise une réponse API-Football /teams en modèle TopKit.

    Structure API : { "team": {...}, "venue": {...} }
    """
    team = api_item.get("team", {})
    venue = api_item.get("venue", {}) or {}
    return {
        "source": "api",
        "apifootball_team_id": team.get("id"),
        "name": team.get("name", ""),
        "code": team.get("code", ""),
        "country": team.get("country", ""),
        "founded": team.get("founded"),
        "is_national": team.get("national", False),
        "logo": team.get("logo", ""),
        "city": venue.get("city", ""),
        "stadium_name": venue.get("name", ""),
        "stadium_capacity": venue.get("capacity"),
        "stadium_surface": venue.get("surface", ""),
        "stadium_image_url": venue.get("image", ""),
    }


# ── Helpers couleurs ──────────────────────────────────────────────────────────

def parse_colors(raw: str) -> list[str]:
    """Parse une chaîne CSV de couleurs en liste normalisée.

    Exemple : parse_colors("Red, White, red, BLUE ") → ["red", "white", "blue"]
    """
    return list(dict.fromkeys(
        c.strip().lower()
        for c in raw.split(",")
        if c.strip()
    ))


# ── Fonctions existantes ──────────────────────────────────────────────────────

def _dedup_honours(honours: List[dict]) -> List[dict]:
    """Supprime les doublons sans saison quand le même titre existe avec une saison."""
    has_season: set[tuple] = set()
    for h in honours:
        season = (h.get("strSeason") or h.get("season") or "").strip()
        league = (h.get("strHonour") or h.get("league") or "").strip()
        place = (h.get("place") or "").strip()
        if season:
            has_season.add((league.lower(), place.lower()))

    result = []
    for h in honours:
        season = (h.get("strSeason") or h.get("season") or "").strip()
        league = (h.get("strHonour") or h.get("league") or "").strip()
        place = (h.get("place") or "").strip()
        if not season and (league.lower(), place.lower()) in has_season:
            continue
        result.append(h)
    return result


def compute_score_palmares(honours: List[dict], individual_awards: List[dict] | None = None) -> float:
    """Calcule le score palmarès pondéré."""
    clean_honours = _dedup_honours(honours)

    total = 0.0
    for h in clean_honours:
        place = (h.get("place") or "").lower().strip()
        multiplier = PLACE_MULTIPLIER.get(place, 0.0)
        if multiplier == 0.0:
            continue
        honour_name = (h.get("strHonour") or h.get("league") or "").lower()
        weight = h.get("scoring_weight") or DEFAULT_HONOUR_WEIGHT
        for keyword, w in HONOUR_WEIGHTS.items():
            if keyword in honour_name:
                weight = w
                break
        total += weight * multiplier

    for award in (individual_awards or []):
        award_name = (award.get("award_name") or "").lower()
        weight = award.get("scoring_weight") or DEFAULT_HONOUR_WEIGHT
        for keyword, w in AWARD_WEIGHTS.items():
            if keyword in award_name:
                weight = w
                break
        count = award.get("count") or 1
        total += weight * count

    return round(total, 2)


def compute_note(score_palmares: float, aura: float) -> float:
    """Note finale sur 100 : 50% palmarès + 50% aura."""
    palmares_part = min(score_palmares / SCORE_MESSI_REF, 1.0) * 50.0
    aura_part = min(aura / 100.0, 1.0) * 50.0
    return round(palmares_part + aura_part, 1)


# ── Recherche joueur (DB-first) ───────────────────────────────────────────────

async def search_players_db_first(name: str, db) -> dict:
    """Recherche un joueur : DB en premier, API-Football en fallback."""
    import unicodedata

    def norm(s: str) -> str:
        s = s.lower().strip()
        s = unicodedata.normalize("NFD", s)
        return "".join(c for c in s if unicodedata.category(c) != "Mn")

    name_norm = norm(name)

    cursor = db["players"].find(
        {"full_name": {"$regex": name, "$options": "i"}},
        {"player_id": 1, "full_name": 1, "nationality": 1,
         "birth_date": 1, "photo_url": 1, "apifootball_id": 1, "note": 1}
    ).limit(10)
    db_players = await cursor.to_list(length=10)

    db_results = [
        {
            "source": "db",
            "player_id": p["player_id"],
            "apifootball_id": p.get("apifootball_id", ""),
            "name": p["full_name"],
            "nationality": p.get("nationality", ""),
            "birth_date": p.get("birth_date", ""),
            "photo": p.get("photo_url", ""),
            "note": p.get("note", 0.0),
        }
        for p in db_players
    ]

    api_results = await search_players_by_name(name)
    return {"db_results": db_results, "api_results": api_results}


async def search_players_by_name(name: str) -> List[dict]:
    """Recherche des joueurs via /players/profiles."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/players/profiles",
            params={"search": name},
            headers=_headers(),
        )
        if r.status_code == 404:
            return []
        r.raise_for_status()
        players = r.json().get("response") or []
        results = []
        for p in players:
            player = p.get("player")
            if not player:
                continue
            raw_dob = player.get("birth", {}).get("date", "") if isinstance(player.get("birth"), dict) else ""
            birth_date_formatted = ""
            if raw_dob:
                try:
                    parts = raw_dob.split("-")
                    birth_date_formatted = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except Exception:
                    birth_date_formatted = raw_dob
            results.append({
                "source": "api",
                "apifootball_id": str(player["id"]),
                "name": player.get("name", ""),
                "firstname": player.get("firstname", ""),
                "lastname": player.get("lastname", ""),
                "nationality": player.get("nationality", ""),
                "birth_date": birth_date_formatted,
                "birth_place": player.get("birth", {}).get("place", "") if isinstance(player.get("birth"), dict) else "",
                "photo": player.get("photo", ""),
                "height": player.get("height", ""),
                "weight": player.get("weight", ""),
                "position": player.get("position", ""),
            })
        return results


# ── Recherche league (DB-first) ───────────────────────────────────────────────

async def search_leagues_db_first(name: str, db) -> dict:
    """Recherche une compétition : DB en premier, API-Football en fallback."""
    cursor = db["leagues"].find(
        {"name": {"$regex": name, "$options": "i"}},
        {"league_id": 1, "name": 1, "country_or_region": 1, "country_name": 1,
         "scope": 1, "region": 1, "organizer": 1, "entity_type": 1,
         "logo_url": 1, "apifootball_league_id": 1, "apifootball_logo": 1, "scoring_weight": 1}
    ).limit(10)
    db_leagues = await cursor.to_list(length=10)

    db_results = [
        {
            "source": "db",
            "league_id": l["league_id"],
            "apifootball_league_id": l.get("apifootball_league_id"),
            "name": l["name"],
            "country": l.get("country_name") or l.get("country_or_region", ""),
            "scope": l.get("scope"),
            "region": l.get("region"),
            "organizer": l.get("organizer"),
            "entity_type": l.get("entity_type", "league"),
            "logo": l.get("apifootball_logo") or l.get("logo_url", ""),
            "scoring_weight": l.get("scoring_weight"),
        }
        for l in db_leagues
    ]

    api_results = await search_leagues_by_name(name)
    return {"db_results": db_results, "api_results": api_results}


async def search_leagues_by_name(name: str) -> List[dict]:
    """Recherche des compétitions via /leagues avec normalisation."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/leagues",
            params={"search": name},
            headers=_headers(),
        )
        if r.status_code == 404:
            return []
        r.raise_for_status()
        leagues = r.json().get("response") or []
        results = []
        for item in leagues:
            normalized = normalize_league(item)
            normalized["source"] = "api"
            results.append(normalized)
        return results[:10]


# ── Recherche team (DB-first) ─────────────────────────────────────────────────

async def search_teams_db_first(name: str, db) -> dict:
    """Recherche un club : DB en premier, API-Football en fallback."""
    cursor = db["teams"].find(
        {"name": {"$regex": name, "$options": "i"}},
        {"team_id": 1, "name": 1, "country": 1, "founded": 1,
         "is_national": 1, "crest_url": 1, "city": 1,
         "stadium_name": 1, "stadium_capacity": 1,
         "apifootball_team_id": 1}
    ).limit(10)
    db_teams = await cursor.to_list(length=10)

    db_results = [
        {
            "source": "db",
            "team_id": t["team_id"],
            "apifootball_team_id": t.get("apifootball_team_id"),
            "name": t["name"],
            "country": t.get("country", ""),
            "founded": t.get("founded"),
            "is_national": t.get("is_national", False),
            "logo": t.get("crest_url", ""),
            "city": t.get("city", ""),
            "stadium_name": t.get("stadium_name", ""),
            "stadium_capacity": t.get("stadium_capacity"),
        }
        for t in db_teams
    ]

    api_results = await search_teams_by_name(name)
    return {"db_results": db_results, "api_results": api_results}


async def search_teams_by_name(name: str) -> List[dict]:
    """Recherche des clubs via /teams avec normalisation."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/teams",
            params={"search": name},
            headers=_headers(),
        )
        if r.status_code == 404:
            return []
        r.raise_for_status()
        teams = r.json().get("response") or []
        results = [normalize_team(item) for item in teams]
        return results[:10]


# ── Lookup trophées / carrière / profil ───────────────────────────────────────

async def lookup_honours(player_id: str) -> List[dict]:
    """Récupère le palmarès complet d'un joueur via /trophies."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/trophies",
            params={"player": player_id},
            headers=_headers(),
        )
        if r.status_code == 404:
            return []
        r.raise_for_status()
        trophies = r.json().get("response") or []
        return [
            {
                "strHonour": t.get("league", ""),
                "strSeason": t.get("season", ""),
                "strTeam": t.get("team", ""),
                "place": t.get("place", ""),
                "league": t.get("league", ""),
            }
            for t in trophies
        ]


async def lookup_career(player_id: str) -> List[dict]:
    """Récupère l'historique de clubs d'un joueur via /transfers."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/transfers",
            params={"player": player_id},
            headers=_headers(),
        )
        if r.status_code == 404:
            return []
        r.raise_for_status()
        data = r.json().get("response") or []

    entries = []
    for item in data:
        transfers = item.get("transfers") or []
        for t in transfers:
            team_in = t.get("teams", {}).get("in", {})
            team_out = t.get("teams", {}).get("out", {})
            date = t.get("date", "")
            transfer_type = t.get("type", "")
            entries.append({
                "club": team_in.get("name", ""),
                "team_id": team_in.get("id"),
                "team_logo": team_in.get("logo", ""),
                "from_club": team_out.get("name", ""),
                "from_club_logo": team_out.get("logo", ""),
                "date": date,
                "transfer_type": transfer_type,
            })

    entries.sort(key=lambda x: x["date"] or "", reverse=True)
    return entries


async def lookup_player_profile(player_id: str) -> dict | None:
    """Récupère les infos identité d'un joueur via /players/profiles."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/players/profiles",
            params={"player": player_id},
            headers=_headers(),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        response = r.json().get("response") or []
        if not response:
            return None
        p = response[0].get("player", {})
        birth = p.get("birth") or {}
        return {
            "apifootball_id": str(p.get("id", "")),
            "name": p.get("name", ""),
            "firstname": p.get("firstname", ""),
            "lastname": p.get("lastname", ""),
            "age": p.get("age"),
            "birth_date": birth.get("date", ""),
            "birth_place": birth.get("place", ""),
            "birth_country": birth.get("country", ""),
            "nationality": p.get("nationality", ""),
            "height": p.get("height", ""),
            "weight": p.get("weight", ""),
            "position": p.get("position", ""),
            "photo": p.get("photo", ""),
            "number": p.get("number"),
        }
