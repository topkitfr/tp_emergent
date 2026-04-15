"""Router players_chart — données de carrière pour le graphique transferts.

Routes :
  GET /api/players-chart/{player_id}/transfers
    → série {season, amount, amount_label, from, to, type} prête pour un chart
       abscisse = saison, ordonnée = montant du transfert

Cache mémoire 7 jours (les transferts changent rarement).
"""

import time as _time
import re

from fastapi import APIRouter, HTTPException

from ..database import db
from ..services.thesportsdb import lookup_career

router = APIRouter(prefix="/api/players-chart", tags=["players-chart"])

# ── Cache mémoire 7 jours ────────────────────────────────────────────────
CACHE_TTL: int = 7 * 24 * 3600
_chart_cache: dict[str, tuple[float, dict]] = {}


def _cache_get(key: str):
    entry = _chart_cache.get(key)
    if entry is None:
        return None
    ts, data = entry
    if _time.monotonic() - ts > CACHE_TTL:
        del _chart_cache[key]
        return None
    return data


def _cache_set(key: str, data: dict) -> None:
    _chart_cache[key] = (_time.monotonic(), data)


# ── Normalisation montant ────────────────────────────────────────────────

def _parse_amount(raw: str | None) -> float | None:
    """Convertit un montant texte en valeur numérique (euros).

    Exemples :
      "€ 180M"   → 180_000_000.0
      "€ 45M"    → 45_000_000.0
      "€ 500K"   → 500_000.0
      "Free"     → 0.0
      "Loan"     → None  (pas un vrai montant, on exclut du graphique)
      "N/A"      → None
      None       → None
    """
    if not raw:
        return None

    cleaned = raw.strip()

    low = cleaned.lower()
    if low in ("free", "gratuit", "free transfer"):
        return 0.0
    if low in ("loan", "prêt", "pret", "n/a", "-", ""):
        return None

    # Extraire valeur numérique + unité (M / K)
    m = re.search(r"([\d.,]+)\s*([MK]?)", cleaned.upper())
    if not m:
        return None

    try:
        value = float(m.group(1).replace(",", "."))
    except ValueError:
        return None

    unit = m.group(2)
    if unit == "M":
        return value * 1_000_000
    if unit == "K":
        return value * 1_000
    return value


def _date_to_season(date_str: str | None) -> str | None:
    """Convertit une date ISO (YYYY-MM-DD) en saison "YYYY/YYYY+1"."""
    if not date_str:
        return None
    try:
        year = int(date_str[:4])
        month = int(date_str[5:7]) if len(date_str) >= 7 else 1
        # Transferts de juillet → décembre = début de saison YEAR/YEAR+1
        # Transferts de janvier → juin = fin de saison YEAR-1/YEAR
        if month >= 7:
            return f"{year}/{year + 1}"
        else:
            return f"{year - 1}/{year}"
    except (ValueError, IndexError):
        return None


# ── Route ────────────────────────────────────────────────────────────────

@router.get("/{player_id}/transfers")
async def get_player_transfer_chart(player_id: str):
    """Retourne la série de transferts d'un joueur pour le graphique carrière.

    Chaque point :
      - season      : "2017/2018"  (abscisse)
      - amount      : 180000000.0  (ordonnée, null si Loan/N/A)
      - amount_label: "€180M"      (tooltip)
      - from        : "Monaco"
      - to          : "Paris Saint Germain"
      - type        : "Loan" | "Free" | "€180M" | …
      - date        : "2017-08-31"
    """
    cached = _cache_get(player_id)
    if cached is not None:
        return cached

    # Récupérer le joueur en base pour avoir son apifootball_id
    player = await db.players.find_one({"player_id": player_id})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    api_id = player.get("apifootball_id")
    if not api_id:
        payload = {"player_id": player_id, "apifootball_id": None, "points": []}
        _cache_set(player_id, payload)
        return payload

    # Appel API-Football via le service existant
    raw_entries = await lookup_career(str(api_id))

    points = []
    for entry in raw_entries:
        raw_type = entry.get("transfer_type") or ""
        amount = _parse_amount(raw_type)
        date_str = entry.get("date")
        season = _date_to_season(date_str)

        # Label lisible
        if amount is None:
            amount_label = raw_type or "N/A"
        elif amount == 0.0:
            amount_label = "Free"
        else:
            m = amount / 1_000_000
            if m >= 1:
                amount_label = f"€{m:g}M"
            else:
                amount_label = f"€{amount / 1_000:g}K"

        points.append({
            "date": date_str,
            "season": season,
            "amount": amount,
            "amount_label": amount_label,
            "from": entry.get("from_club"),
            "from_logo": entry.get("from_club_logo"),
            "to": entry.get("club"),
            "to_logo": entry.get("team_logo"),
            "type": raw_type,
        })

    # Tri chronologique (le plus ancien en premier → lecture naturelle du chart)
    points.sort(key=lambda x: x.get("date") or "")

    payload = {
        "player_id": player_id,
        "apifootball_id": api_id,
        "points": points,
    }
    _cache_set(player_id, payload)
    return payload
