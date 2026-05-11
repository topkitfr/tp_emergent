# backend/routers/entity_workflow.py
"""
Routes transversales aux 5 types d'entités (team/league/brand/player/sponsor) :

- GET   /api/pending                       → vue agrégée modérateur
- PATCH /api/{entity_type}/{id}/approve    → validation modérateur
- PATCH /api/{entity_type}/{id}/reject     → rejet modérateur
- GET   /api/autocomplete                  → recherche unifiée (front)

Extrait de entities.py en Vague 4 pour casser le monolithe 857 l.
Les routes CRUD per-type sont dans teams.py / leagues.py / brands.py /
sponsors.py / players.py.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_moderator_user
from ..database import db
from ..utils import safe_regex
from ._entity_helpers import ENTITY_CONFIG, LOGO_FIELDS


router = APIRouter(prefix="/api", tags=["entity-workflow"])


# ─── Pending listing (modérateur) ───────────────────────────────────────────

@router.get("/pending")
async def get_all_pending(master_kit_submission_id: Optional[str] = Query(default=None)):
    """Retourne toutes les entités `for_review`, groupées par type.

    Si `master_kit_submission_id` est passé, on filtre sur les entités
    rattachées à ce master_kit (via `data.parent_submission_id` côté submissions).
    """
    results: dict[str, list[dict]] = {}
    for entity_type, config in ENTITY_CONFIG.items():
        query: dict = {"status": "for_review"}
        if master_kit_submission_id:
            linked_subs = await db.submissions.find(
                {
                    "submission_type":             entity_type,
                    "status":                      "pending",
                    "data.parent_submission_id":   master_kit_submission_id,
                },
                {"_id": 0, "data.entity_id": 1},
            ).to_list(50)
            linked_ids = [
                s["data"]["entity_id"]
                for s in linked_subs
                if s.get("data", {}).get("entity_id")
            ]
            if not linked_ids:
                results[entity_type] = []
                continue
            query[config["id_field"]] = {"$in": linked_ids}

        docs = await db[config["collection"]].find(query, {"_id": 0}).to_list(100)
        for d in docs:
            d["display_name"] = d.get("full_name") or d.get("name") or "—"
        results[entity_type] = docs
    return results


# ─── Approve / Reject ───────────────────────────────────────────────────────

async def _set_status(entity_type: str, entity_id: str, new_status: str) -> dict:
    """Logique partagée approve/reject : update entité + submission liée."""
    config = ENTITY_CONFIG.get(entity_type)
    if not config:
        raise HTTPException(status_code=400, detail="Unknown entity type")

    now = datetime.now(timezone.utc).isoformat()
    result = await db[config["collection"]].update_one(
        {config["id_field"]: entity_id},
        {"$set": {"status": new_status, "updated_at": now}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entity not found")

    await db.submissions.update_one(
        {
            "submission_type": entity_type,
            "data.entity_id":  entity_id,
            "status":          {"$in": ["pending", "for_review"]},
        },
        {"$set": {"status": new_status, "updated_at": now}},
    )
    return {"message": f"{entity_type} {new_status}"}


@router.patch("/{entity_type}/{entity_id}/approve", dependencies=[Depends(get_moderator_user)])
async def approve_entity(entity_type: str, entity_id: str):
    return await _set_status(entity_type, entity_id, "approved")


@router.patch("/{entity_type}/{entity_id}/reject", dependencies=[Depends(get_moderator_user)])
async def reject_entity(entity_type: str, entity_id: str):
    return await _set_status(entity_type, entity_id, "rejected")


# ─── Autocomplete unifié (consommé par UnifiedEntitySearch.js) ──────────────

# Config locale, car spécifique à l'autocomplete (mapping search_fields /
# label / extra). Pas dans _entity_helpers car non partagé.
_AUTOCOMPLETE_CONFIG: dict[str, dict] = {
    "team":    {"collection": "teams",    "search_fields": ["name", "aka"], "id_field": "team_id",    "label_field": "name",      "extra_field": "country"},
    "league":  {"collection": "leagues",  "search_fields": ["name"],         "id_field": "league_id",  "label_field": "name",      "extra_field": "country_or_region"},
    "brand":   {"collection": "brands",   "search_fields": ["name"],         "id_field": "brand_id",   "label_field": "name",      "extra_field": "country"},
    "player":  {"collection": "players",  "search_fields": ["full_name"],    "id_field": "player_id",  "label_field": "full_name", "extra_field": "nationality"},
    "sponsor": {"collection": "sponsors", "search_fields": ["name"],         "id_field": "sponsor_id", "label_field": "name",      "extra_field": "country"},
}


@router.get("/autocomplete")
async def autocomplete(
    field: Optional[str] = None,
    type: Optional[str] = None,
    q: str = "",
    query: str = "",
):
    """Deux modes :

    - `type=<entity>&q=<term>` → recherche dans les collections d'entités,
      retourne `[{id, label, extra, status, logo_url}, ...]`.
    - `field=<field>&q=<term>` → recherche les valeurs distinctes d'un champ
      dans master_kits ou versions (pour les filtres de la page Contributions).
    """
    search_q = q or query

    # Mode 1 : recherche entité
    if type:
        config = _AUTOCOMPLETE_CONFIG.get(type)
        if not config:
            return []

        filter_q: dict = {"status": {"$ne": "rejected"}}
        if search_q:
            sq = safe_regex(search_q)
            if len(config["search_fields"]) == 1:
                filter_q[config["search_fields"][0]] = {"$regex": sq, "$options": "i"}
            else:
                filter_q["$or"] = [
                    {f: {"$regex": sq, "$options": "i"}}
                    for f in config["search_fields"]
                ]

        docs = await db[config["collection"]].find(filter_q, {"_id": 0}).limit(20).to_list(20)
        logo_fields = LOGO_FIELDS.get(type, [])

        return [
            {
                "id":       d.get(config["id_field"], ""),
                "label":    d.get(config["label_field"], ""),
                "extra":    d.get(config["extra_field"], ""),
                "status":   d.get("status", "approved"),
                "logo_url": next((d[f] for f in logo_fields if d.get(f)), None),
            }
            for d in docs
        ]

    # Mode 2 : recherche valeurs distinctes d'un champ
    if field:
        field_map = {
            "club":        "master_kits",
            "brand":       "master_kits",
            "league":      "master_kits",
            "sponsor":     "master_kits",
            "competition": "versions",
        }
        if field not in field_map:
            return []
        values = await db[field_map[field]].distinct(field)
        if search_q:
            q_lower = search_q.lower()
            values = [v for v in values if v and q_lower in str(v).lower()]
        return sorted([v for v in values if v])[:20]

    return []
