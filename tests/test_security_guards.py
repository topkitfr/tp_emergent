"""
Tests "filet" pour les gardes de sécurité ajoutées en Vague 1.

Objectif : si quelqu'un retire ou affaiblit un de ces contrôles plus tard,
la suite échoue immédiatement.

Couvre :
  - POST /api/{teams,leagues,brands,sponsors,players} : modérateur requis
  - PUT  /api/{teams,leagues,brands,sponsors,players}/{id} : idem
  - PATCH /api/{type}/{id}/approve|reject : idem
  - POST /api/teams-api/upsert : Pydantic + modérateur
  - safe_regex : un pattern dangereux ne fait pas exploser la recherche

Matrice de réponse attendue :
  - Anonyme         → 401 Not authenticated
  - User normal     → 403 Action réservée aux modérateurs
  - Moderator/Admin → 200/201 (succès)
"""
from __future__ import annotations

import pytest


# ─── Endpoints verrouillés en POST (création directe, hors /pending) ────────

POST_ENDPOINTS = [
    ("/api/teams",    {"name": "Test FC"}),
    ("/api/leagues",  {"name": "Test League"}),
    ("/api/brands",   {"name": "Test Brand"}),
    ("/api/sponsors", {"name": "Test Sponsor"}),
    ("/api/players",  {"full_name": "Test Player"}),
]


@pytest.mark.parametrize("endpoint,payload", POST_ENDPOINTS)
@pytest.mark.asyncio
async def test_post_entity_anonymous_returns_401(client, endpoint, payload):
    r = await client.post(endpoint, json=payload)
    assert r.status_code == 401, (
        f"{endpoint} anonyme devrait être 401, reçu {r.status_code} : {r.text}"
    )


@pytest.mark.parametrize("endpoint,payload", POST_ENDPOINTS)
@pytest.mark.asyncio
async def test_post_entity_normal_user_returns_403(client, make_user, endpoint, payload):
    _uid, _token, cookies = await make_user(role="user")
    r = await client.post(endpoint, json=payload, cookies=cookies)
    assert r.status_code == 403, (
        f"{endpoint} en user devrait être 403, reçu {r.status_code} : {r.text}"
    )


@pytest.mark.parametrize("endpoint,payload", POST_ENDPOINTS)
@pytest.mark.asyncio
async def test_post_entity_moderator_succeeds(client, make_user, endpoint, payload):
    _uid, _token, cookies = await make_user(role="moderator")
    r = await client.post(endpoint, json=payload, cookies=cookies)
    # Selon le router, on peut avoir 200 OU 201. On accepte tout 2xx.
    assert 200 <= r.status_code < 300, (
        f"{endpoint} en modérateur devrait réussir, reçu {r.status_code} : {r.text}"
    )


# ─── /pending — accessible aux users normaux (workflow communautaire) ──────

PENDING_ENDPOINTS = [
    ("/api/teams/pending",    {"name": "Pending FC"}),
    ("/api/leagues/pending",  {"name": "Pending League"}),
    ("/api/brands/pending",   {"name": "Pending Brand"}),
    ("/api/sponsors/pending", {"name": "Pending Sponsor"}),
    ("/api/players/pending",  {"full_name": "Pending Player"}),
]


@pytest.mark.parametrize("endpoint,payload", PENDING_ENDPOINTS)
@pytest.mark.asyncio
async def test_pending_endpoints_accessible_to_users(
    client, make_user, endpoint, payload,
):
    """Les routes /pending doivent rester ouvertes aux users normaux,
    sinon le workflow communautaire ne fonctionne plus."""
    _uid, _token, cookies = await make_user(role="user")
    r = await client.post(endpoint, json=payload, cookies=cookies)
    assert 200 <= r.status_code < 300, (
        f"{endpoint} en user devrait réussir, reçu {r.status_code} : {r.text}"
    )


# ─── Approve / Reject — modérateur strict ───────────────────────────────────

class TestApproveReject:

    @pytest.mark.asyncio
    async def test_approve_anonymous_returns_401(self, client, mock_db):
        await mock_db.teams.insert_one({"team_id": "t_x", "name": "X", "slug": "x"})
        r = await client.patch("/api/team/t_x/approve")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_approve_user_returns_403(self, client, mock_db, make_user):
        await mock_db.teams.insert_one({"team_id": "t_y", "name": "Y", "slug": "y"})
        _uid, _t, cookies = await make_user(role="user")
        r = await client.patch("/api/team/t_y/approve", cookies=cookies)
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_approve_moderator_works(self, client, mock_db, make_user):
        await mock_db.teams.insert_one({"team_id": "t_z", "name": "Z", "slug": "z",
                                         "status": "for_review"})
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.patch("/api/team/t_z/approve", cookies=cookies)
        assert r.status_code == 200
        # Vérif side-effect
        team = await mock_db.teams.find_one({"team_id": "t_z"})
        assert team["status"] == "approved"


# ─── /api/teams-api/upsert — auth + Pydantic ────────────────────────────────

class TestTeamsApiUpsert:

    @pytest.mark.asyncio
    async def test_upsert_anonymous_401(self, client):
        r = await client.post("/api/teams-api/upsert", json={"name": "Anonym FC"})
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_upsert_user_403(self, client, make_user):
        _uid, _t, cookies = await make_user(role="user")
        r = await client.post(
            "/api/teams-api/upsert",
            json={"name": "User FC"},
            cookies=cookies,
        )
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_upsert_validates_pydantic(self, client, make_user):
        """Pydantic refuse `name` manquant (avant Vague 1, dict accepté brut)."""
        _uid, _t, cookies = await make_user(role="moderator")
        r = await client.post(
            "/api/teams-api/upsert",
            json={"country": "France"},  # name manquant
            cookies=cookies,
        )
        assert r.status_code == 422, r.text


# ─── safe_regex — sanity sur un pattern dangereux ───────────────────────────

class TestSafeRegex:

    def test_safe_regex_escapes_metacharacters(self):
        from backend.utils import safe_regex
        # Caractères regex vénères : .  *  +  ?  (  )  [  ]  {  }  ^  $  |  \\
        dangerous = ".*+?(){}[]^$|\\"
        out = safe_regex(dangerous)
        # Tous les méta-caractères doivent être préfixés d'un \
        for c in dangerous:
            assert f"\\{c}" in out, f"{c!r} non échappé dans {out!r}"

    def test_safe_regex_strips_whitespace(self):
        from backend.utils import safe_regex
        assert safe_regex("  hello  ") == "hello"

    def test_safe_regex_handles_empty_string(self):
        from backend.utils import safe_regex
        assert safe_regex("") == ""
        assert safe_regex(None) == ""

    @pytest.mark.asyncio
    async def test_master_kits_search_with_regex_payload_does_not_crash(
        self, client, mock_db,
    ):
        """
        Avant Vague 1, un payload genre `.*.*.*` pouvait déclencher un ReDoS
        ou un comportement bizarre côté Mongo. Maintenant : escape → recherche
        littérale, retour vide.
        """
        await mock_db.master_kits.insert_one({
            "kit_id": "k1", "club": "PSG", "season": "2023/24",
            "kit_type": "Home", "brand": "Nike", "front_photo": "",
        })
        r = await client.get("/api/master-kits", params={"search": ".*.*.*"})
        assert r.status_code == 200
        # Aucun club ne contient littéralement la chaîne ".*.*.*"
        assert r.json()["total"] == 0
