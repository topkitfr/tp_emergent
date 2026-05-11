# backend/routers/_entity_helpers.py
"""
Helpers partagés entre les routers per-type (teams/leagues/brands/sponsors/players)
et le router transversal entity_workflow (pending/approve/reject/autocomplete).

Centraliser ces 3 constantes + 1 fonction évite la duplication qui a longtemps
existé quand tout vivait dans entities.py (cf. Vague 4 — split du router).
"""
from __future__ import annotations

from fastapi import HTTPException

from ..database import db


# ─── Verrou sur entités en attente d'approbation ────────────────────────────
LOCKED_STATUSES: tuple[str, ...] = ("for_review", "pending")


async def assert_not_locked(collection: str, id_field: str, entity_id: str) -> None:
    """Lève 423 si l'entité est en attente d'approbation communautaire.

    Utilisé par les PUT (modif) pour empêcher un modérateur de modifier
    une entité qu'un user est en train de soumettre — le master_kit lié
    doit être approuvé/rejeté d'abord pour libérer l'entité.
    """
    doc = await db[collection].find_one({id_field: entity_id}, {"_id": 0, "status": 1})
    if doc and doc.get("status") in LOCKED_STATUSES:
        raise HTTPException(
            status_code=423,
            detail=(
                "This entity is currently pending community approval and cannot be modified. "
                "It will be unlocked once the linked kit submission is approved or rejected."
            ),
        )


# ─── Mapping entity_type → collection / champ id ────────────────────────────
# Utilisé par /pending, /approve, /reject et /autocomplete.
ENTITY_CONFIG: dict[str, dict[str, str]] = {
    "team":    {"collection": "teams",    "id_field": "team_id"},
    "league":  {"collection": "leagues",  "id_field": "league_id"},
    "brand":   {"collection": "brands",   "id_field": "brand_id"},
    "player":  {"collection": "players",  "id_field": "player_id"},
    "sponsor": {"collection": "sponsors", "id_field": "sponsor_id"},
}


# ─── Champs image par type pour la réponse autocomplete ─────────────────────
LOGO_FIELDS: dict[str, list[str]] = {
    "team":    ["crest_url", "logo_url"],
    "league":  ["logo_url", "crest_url"],
    "brand":   ["logo_url"],
    "player":  ["photo_url"],
    "sponsor": ["logo_url"],
}
