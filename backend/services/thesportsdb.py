"""Client async API-Football (api-sports.io) — free tier (100 req/day).

Endpoints utilisés :
  - GET /players/profiles?search={name}  → recherche joueur
  - GET /trophies?player={id}            → palmarès complet
  - GET /transfers?player={id}           → historique de clubs

Doc : https://api-sports.io/documentation/football/v3
"""

import httpx
from typing import List
import os

BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.environ.get("API_FOOTBALL_KEY", "92000910b07df3b860baa17aa7f0ef7d")

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
    "primera division": 7.0,
    "fa cup": 4.0,
    "copa del rey": 4.0,
    "dfb pokal": 4.0,
    "coppa italia": 4.0,
    "coupe de france": 3.0,
    "supercoupe": 2.0,
    "supercopa": 2.0,
    "super cup": 2.0,
    "community shield": 2.0,
    "ballon d'or": 8.0,
    "ballon dor": 8.0,
    "fifa best": 5.0,
    "golden boot": 3.0,
    "golden ball": 3.0,
}

DEFAULT_HONOUR_WEIGHT = 1.5
SCORE_MESSI_REF = 100.0


def _headers() -> dict:
    return {"x-apisports-key": API_KEY}


def compute_score_palmares(honours: List[dict]) -> float:
    """Calcule le score palmarès pondéré (uniquement les victoires)."""
    total = 0.0
    for h in honours:
        if (h.get("place") or "").lower() != "winner":
            continue
        honour_name = (h.get("strHonour") or h.get("league") or "").lower()
        weight = DEFAULT_HONOUR_WEIGHT
        for keyword, w in HONOUR_WEIGHTS.items():
            if keyword in honour_name:
                weight = w
                break
        total += weight
    return round(total, 2)


def compute_note(score_palmares: float, aura: float) -> float:
    palmares_part = min(score_palmares / SCORE_MESSI_REF, 1.0) * 50.0
    aura_part = min(aura / 100.0, 1.0) * 50.0
    return round(palmares_part + aura_part, 1)


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
            })
        return results


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
    """Récupère l'historique de clubs d'un joueur via /transfers.

    Retourne une liste ordonnée (du plus récent au plus ancien) :
      club, team_id, date_start, date_end, type ("IN"/"OUT")
    On ne garde que les transferts IN pour reconstituer la carrière.
    """
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
            date = t.get("date", "")  # YYYY-MM-DD or YYYY
            entries.append({
                "club": team_in.get("name", ""),
                "team_id": team_in.get("id"),
                "team_logo": team_in.get("logo", ""),
                "from_club": team_out.get("name", ""),
                "date": date,
                "type": t.get("type", ""),
            })

    # Trier par date décroissante, filtrer les arrivées uniquement
    entries.sort(key=lambda x: x["date"] or "", reverse=True)
    return entries
