"""
Tests "filet" pour le router entities, à exécuter avant le split en
fichiers par type (teams.py / leagues.py / brands.py / sponsors.py /
players.py + entity_workflow.py).

Cible le comportement fonctionnel qui doit rester inchangé après split :
  - GET list / detail
  - POST /pending (workflow communautaire)
  - PATCH approve / reject + side-effect sur la submission liée
  - GET /pending (vue modérateur)
  - GET /autocomplete (utilisé par UnifiedEntitySearch côté front)
  - Verrou for_review (les PUT renvoient 423 quand l'entité est pending)

La couverture sécurité (auth/modérateur sur POST/PUT/PATCH) est déjà
dans test_security_guards.py, pas dupliquée ici.
"""
from __future__ import annotations

import pytest


# ─── GET list / detail ──────────────────────────────────────────────────────

class TestListAndDetail:

    @pytest.mark.asyncio
    async def test_list_teams_empty_returns_zero(self, client):
        r = await client.get("/api/teams")
        assert r.status_code == 200
        body = r.json()
        assert body == {"results": [], "total": 0}

    @pytest.mark.asyncio
    async def test_list_teams_returns_inserted_docs(self, client, mock_db):
        await mock_db.teams.insert_many([
            {"team_id": "t1", "name": "PSG",       "slug": "psg",       "country": "France"},
            {"team_id": "t2", "name": "Liverpool", "slug": "liverpool", "country": "England"},
        ])
        r = await client.get("/api/teams")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 2
        names = {t["name"] for t in body["results"]}
        assert names == {"PSG", "Liverpool"}
        # Chaque team doit exposer kit_count (calculé à la volée)
        assert all("kit_count" in t for t in body["results"])

    @pytest.mark.asyncio
    async def test_list_teams_search_filters_by_name(self, client, mock_db):
        await mock_db.teams.insert_many([
            {"team_id": "t1", "name": "PSG",       "slug": "psg"},
            {"team_id": "t2", "name": "Liverpool", "slug": "liverpool"},
        ])
        r = await client.get("/api/teams", params={"search": "liver"})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["results"][0]["name"] == "Liverpool"

    @pytest.mark.asyncio
    async def test_get_team_by_id(self, client, mock_db):
        await mock_db.teams.insert_one({"team_id": "t1", "name": "PSG", "slug": "psg"})
        r = await client.get("/api/teams/t1")
        assert r.status_code == 200
        assert r.json()["name"] == "PSG"

    @pytest.mark.asyncio
    async def test_get_team_by_slug(self, client, mock_db):
        await mock_db.teams.insert_one({"team_id": "t1", "name": "PSG", "slug": "psg"})
        r = await client.get("/api/teams/psg")
        assert r.status_code == 200
        assert r.json()["team_id"] == "t1"

    @pytest.mark.asyncio
    async def test_get_team_unknown_returns_404(self, client):
        r = await client.get("/api/teams/does-not-exist")
        assert r.status_code == 404


# ─── Workflow pending (création communautaire) ──────────────────────────────

class TestCreatePending:

    @pytest.mark.asyncio
    async def test_create_team_pending_creates_for_review_entity(self, client, make_user, mock_db):
        _uid, _t, cookies = await make_user(role="user")
        r = await client.post("/api/teams/pending", json={"name": "Pending FC"}, cookies=cookies)
        assert r.status_code == 200
        team = await mock_db.teams.find_one({"name": "Pending FC"})
        assert team is not None
        assert team["status"] == "for_review"
        assert team["submission_id"].startswith("sub_")

    @pytest.mark.asyncio
    async def test_create_team_pending_creates_linked_submission(self, client, make_user, mock_db):
        _uid, _t, cookies = await make_user(role="user")
        r = await client.post("/api/teams/pending", json={"name": "Linked FC"}, cookies=cookies)
        assert r.status_code == 200
        team = await mock_db.teams.find_one({"name": "Linked FC"})
        sub = await mock_db.submissions.find_one({"submission_id": team["submission_id"]})
        assert sub is not None
        assert sub["submission_type"] == "team"
        assert sub["status"] == "pending"
        assert sub["data"]["entity_id"] == team["team_id"]
        assert sub["votes_up"] == 0
        assert sub["voters"] == []

    @pytest.mark.asyncio
    async def test_create_team_pending_dedup_returns_existing(self, client, make_user, mock_db):
        """Si une team existe déjà avec le même slug, on ne recrée pas."""
        await mock_db.teams.insert_one({
            "team_id": "t_existing", "name": "Dedup FC", "slug": "dedup-fc", "status": "approved",
        })
        _uid, _t, cookies = await make_user(role="user")
        r = await client.post("/api/teams/pending", json={"name": "Dedup FC"}, cookies=cookies)
        assert r.status_code == 200
        # Une seule team en base, pas de doublon
        count = await mock_db.teams.count_documents({"slug": "dedup-fc"})
        assert count == 1

    @pytest.mark.asyncio
    async def test_create_player_pending_records_submitter(self, client, make_user, mock_db):
        """Spécificité player : tracking submitted_by / submitter_name."""
        uid, _t, cookies = await make_user(role="user", email="contrib@x.com")
        r = await client.post("/api/players/pending", json={"full_name": "Z. Ibrahimović"}, cookies=cookies)
        assert r.status_code == 200
        player = await mock_db.players.find_one({"full_name": "Z. Ibrahimović"})
        sub = await mock_db.submissions.find_one({"submission_id": player["submission_id"]})
        assert sub["submitted_by"] == uid


# ─── Approve / Reject ──────────────────────────────────────────────────────

ENTITY_FIXTURES = [
    # (entity_type_singulier, collection, id_field, payload)
    ("team",    "teams",    "team_id",    {"team_id":    "t_a", "name": "A", "slug": "a"}),
    ("league",  "leagues",  "league_id",  {"league_id":  "l_a", "name": "A", "slug": "a"}),
    ("brand",   "brands",   "brand_id",   {"brand_id":   "b_a", "name": "A", "slug": "a"}),
    ("sponsor", "sponsors", "sponsor_id", {"sponsor_id": "s_a", "name": "A", "slug": "a"}),
    ("player",  "players",  "player_id",  {"player_id":  "p_a", "full_name": "A", "slug": "a"}),
]


class TestApproveReject:

    @pytest.mark.parametrize("etype,collection,id_field,doc", ENTITY_FIXTURES)
    @pytest.mark.asyncio
    async def test_approve_updates_entity_and_submission(
        self, client, make_user, mock_db, etype, collection, id_field, doc,
    ):
        # Setup : entité for_review + submission pending liée
        entity_id = doc[id_field]
        doc_full = {**doc, "status": "for_review", "submission_id": "sub_x"}
        await mock_db[collection].insert_one(doc_full)
        await mock_db.submissions.insert_one({
            "submission_id":   "sub_x",
            "submission_type": etype,
            "data":            {"entity_id": entity_id},
            "status":          "pending",
        })

        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.patch(f"/api/{etype}/{entity_id}/approve", cookies=cookies)
        assert r.status_code == 200, r.text

        # Side-effects
        entity = await mock_db[collection].find_one({id_field: entity_id})
        assert entity["status"] == "approved"
        sub = await mock_db.submissions.find_one({"submission_id": "sub_x"})
        assert sub["status"] == "approved"

    @pytest.mark.parametrize("etype,collection,id_field,doc", ENTITY_FIXTURES)
    @pytest.mark.asyncio
    async def test_reject_updates_entity_and_submission(
        self, client, make_user, mock_db, etype, collection, id_field, doc,
    ):
        entity_id = doc[id_field]
        doc_full = {**doc, "status": "for_review", "submission_id": "sub_y"}
        await mock_db[collection].insert_one(doc_full)
        await mock_db.submissions.insert_one({
            "submission_id":   "sub_y",
            "submission_type": etype,
            "data":            {"entity_id": entity_id},
            "status":          "pending",
        })

        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.patch(f"/api/{etype}/{entity_id}/reject", cookies=cookies)
        assert r.status_code == 200, r.text

        entity = await mock_db[collection].find_one({id_field: entity_id})
        assert entity["status"] == "rejected"
        sub = await mock_db.submissions.find_one({"submission_id": "sub_y"})
        assert sub["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_approve_unknown_entity_type_returns_400(self, client, make_user):
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.patch("/api/foobar/x/approve", cookies=cookies)
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_approve_unknown_id_returns_404(self, client, make_user):
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.patch("/api/team/does-not-exist/approve", cookies=cookies)
        assert r.status_code == 404


# ─── Verrou for_review sur PUT ──────────────────────────────────────────────

class TestForReviewLock:

    @pytest.mark.asyncio
    async def test_put_team_locked_when_for_review(self, client, make_user, mock_db):
        await mock_db.teams.insert_one({
            "team_id": "t_locked", "name": "L", "slug": "l", "status": "for_review",
        })
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.put("/api/teams/t_locked", json={"name": "L2"}, cookies=cookies)
        assert r.status_code == 423, r.text

    @pytest.mark.asyncio
    async def test_put_team_works_when_approved(self, client, make_user, mock_db):
        await mock_db.teams.insert_one({
            "team_id": "t_ok", "name": "OK", "slug": "ok", "status": "approved",
        })
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.put("/api/teams/t_ok", json={"name": "OK2"}, cookies=cookies)
        assert r.status_code == 200, r.text


# ─── GET /pending (vue agrégée modérateur) ──────────────────────────────────

class TestPendingListing:

    @pytest.mark.asyncio
    async def test_pending_returns_dict_with_all_types(self, client, mock_db):
        await mock_db.teams.insert_one({"team_id": "t1", "name": "T", "slug": "t", "status": "for_review"})
        await mock_db.players.insert_one({"player_id": "p1", "full_name": "P", "slug": "p", "status": "for_review"})
        r = await client.get("/api/pending")
        assert r.status_code == 200
        body = r.json()
        # Toutes les clés des 5 types doivent être présentes (vides ou pas)
        assert set(body.keys()) == {"team", "league", "brand", "player", "sponsor"}
        assert len(body["team"]) == 1
        assert len(body["player"]) == 1
        assert body["team"][0]["display_name"] == "T"
        assert body["player"][0]["display_name"] == "P"


# ─── GET /autocomplete (consommé par UnifiedEntitySearch.js) ────────────────

class TestAutocomplete:

    @pytest.mark.asyncio
    async def test_autocomplete_by_type_team_matches_name(self, client, mock_db):
        await mock_db.teams.insert_many([
            {"team_id": "t1", "name": "PSG",       "slug": "psg",       "country": "France"},
            {"team_id": "t2", "name": "Liverpool", "slug": "liverpool", "country": "England"},
        ])
        r = await client.get("/api/autocomplete", params={"type": "team", "q": "liver"})
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1
        assert items[0]["id"]    == "t2"
        assert items[0]["label"] == "Liverpool"
        assert items[0]["extra"] == "England"

    @pytest.mark.asyncio
    async def test_autocomplete_by_type_player_uses_full_name(self, client, mock_db):
        await mock_db.players.insert_one({
            "player_id": "p1", "full_name": "Lionel Messi", "slug": "lionel-messi",
            "nationality": "Argentina",
        })
        r = await client.get("/api/autocomplete", params={"type": "player", "q": "messi"})
        assert r.status_code == 200
        items = r.json()
        assert len(items) == 1
        assert items[0]["label"] == "Lionel Messi"
        assert items[0]["extra"] == "Argentina"

    @pytest.mark.asyncio
    async def test_autocomplete_unknown_type_returns_empty(self, client):
        r = await client.get("/api/autocomplete", params={"type": "unknown", "q": "x"})
        assert r.status_code == 200
        assert r.json() == []

    @pytest.mark.asyncio
    async def test_autocomplete_no_args_returns_empty(self, client):
        r = await client.get("/api/autocomplete")
        assert r.status_code == 200
        assert r.json() == []
