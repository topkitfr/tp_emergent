"""Client async TheSportsDB — free tier (api key = 1).

Endpoints utilisés :
  - searchplayers.php?p={name}    → auto-complétion joueur
  - lookuphonours.php?id={tsdb_id} → palmarès complet
"""

import httpx
from typing import List, Optional

BASE_URL = "https://www.thesportsdb.com/api/v1/json/1"

# Poids par type de trophée pour le calcul score_palmares.
# Clé = sous-chaîne (insensible à la casse) présente dans strHonour.
# Score Messi de référence : ~40 titres majeurs → score_palmares ≈ 100.
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

DEFAULT_HONOUR_WEIGHT = 1.5  # Tout titre non reconnu vaut 1.5 pt

# Score de référence Messi (pour calibration à 97.5)
# Calculé empiriquement sur ses ~40 titres majeurs
SCORE_MESSI_REF = 100.0


def compute_score_palmares(honours: List[dict]) -> float:
    """Calcule le score palmarès pondéré à partir de la liste honours TheSportsDB."""
    total = 0.0
    for h in honours:
        honour_name = (h.get("strHonour") or "").lower()
        weight = DEFAULT_HONOUR_WEIGHT
        for keyword, w in HONOUR_WEIGHTS.items():
            if keyword in honour_name:
                weight = w
                break
        total += weight
    return round(total, 2)


def compute_note(score_palmares: float, aura: float) -> float:
    """Formule validée : note = (score_palmares / SCORE_MESSI_REF) * 50 + (aura / 100) * 50."""
    palmares_part = min(score_palmares / SCORE_MESSI_REF, 1.0) * 50.0
    aura_part = min(aura / 100.0, 1.0) * 50.0
    return round(palmares_part + aura_part, 1)


async def search_players_by_name(name: str) -> List[dict]:
    """Recherche des joueurs TheSportsDB par nom (pour auto-complétion)."""
    url = f"{BASE_URL}/searchplayers.php"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params={"p": name})
        r.raise_for_status()
        data = r.json()
        players = data.get("player") or []
        return [
            {
                "tsdb_id": p.get("idPlayer", ""),
                "name": p.get("strPlayer", ""),
                "team": p.get("strTeam", ""),
                "nationality": p.get("strNationality", ""),
                "thumb": p.get("strThumb", "") or p.get("strCutout", ""),
                "sport": p.get("strSport", ""),
            }
            for p in players
            if p.get("strSport", "").lower() in ("soccer", "football", "")
        ]


async def lookup_honours(tsdb_id: str) -> List[dict]:
    """Récupère le palmarès complet d'un joueur via TheSportsDB."""
    url = f"{BASE_URL}/lookuphonours.php"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params={"id": tsdb_id})
        r.raise_for_status()
        data = r.json()
        return data.get("honours") or []
