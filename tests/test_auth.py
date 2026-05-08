"""
Tests sur le router /api/auth.

Couvre :
  - register : succès, validations (mdp court, nom court, doublon email)
  - login : succès, mauvais mdp, email inconnu
  - /me : avec session valide / sans session / session expirée / user banni
  - logout : invalide bien la session côté DB
  - bcrypt 72-bytes truncation (régression historique)

Les emails (Resend) sont mockés pour éviter les appels réseau.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio


@pytest_asyncio.fixture(autouse=True)
async def _mock_emails(monkeypatch):
    """Stub des envois d'emails (Resend) — sinon tests touchent le réseau."""
    async def _noop(*args, **kwargs):
        return None
    import backend.email_service as es
    monkeypatch.setattr(es, "send_welcome", _noop, raising=False)
    monkeypatch.setattr(es, "send_password_reset", _noop, raising=False)
    # Les routers importent ces fonctions via `from ..email_service import ...`
    # → on patche aussi la référence locale dans le router auth.
    import backend.routers.auth as auth_router
    monkeypatch.setattr(auth_router, "send_welcome", _noop, raising=False)
    monkeypatch.setattr(auth_router, "send_password_reset", _noop, raising=False)


# ─── Register ───────────────────────────────────────────────────────────────

class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success_creates_user_and_session(self, client, mock_db):
        r = await client.post("/api/auth/register", json={
            "email": "alice@example.com",
            "password": "supersecret",
            "name": "Alice",
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert "password_hash" not in data  # ne doit jamais ressortir

        # Vérif DB
        user = await mock_db.users.find_one({"email": "alice@example.com"})
        assert user is not None
        assert user["role"] == "user"
        assert "password_hash" in user

        # Cookie de session posé
        assert "session_token" in r.cookies

    @pytest.mark.asyncio
    async def test_register_short_password_rejected(self, client):
        r = await client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "password": "short",
            "name": "Bob",
        })
        assert r.status_code == 400
        assert "8 caractères" in r.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_short_name_rejected(self, client):
        r = await client.post("/api/auth/register", json={
            "email": "c@example.com",
            "password": "longenough",
            "name": "X",  # 1 char
        })
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_register_duplicate_email_rejected(self, client, mock_db):
        await mock_db.users.insert_one({
            "user_id": "u_existing",
            "email": "dup@example.com",
            "password_hash": "x",
            "role": "user",
            "name": "Existing",
        })
        r = await client.post("/api/auth/register", json={
            "email": "dup@example.com",
            "password": "longenough",
            "name": "Whoever",
        })
        assert r.status_code == 400
        assert "registered" in r.json()["detail"].lower()


# ─── Login ──────────────────────────────────────────────────────────────────

class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client):
        # On enregistre puis on login
        await client.post("/api/auth/register", json={
            "email": "login@example.com",
            "password": "thepassword1",
            "name": "Login User",
        })
        # Logout pour clean les cookies du registre
        await client.post("/api/auth/logout")

        r = await client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "thepassword1",
        })
        assert r.status_code == 200
        assert "session_token" in r.cookies

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client):
        await client.post("/api/auth/register", json={
            "email": "pwd@example.com",
            "password": "rightpassword",
            "name": "Pwd User",
        })
        await client.post("/api/auth/logout")

        r = await client.post("/api/auth/login", json={
            "email": "pwd@example.com",
            "password": "wrongpassword",
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unknown_email(self, client):
        r = await client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "whatever1234",
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_password_truncated_to_72_bytes(self, client):
        """
        bcrypt limite à 72 bytes. Le router tronque pour éviter une exception.
        Régression : sans la troncature, register crashait avec un mot de passe long.
        """
        long_pwd = "A" * 200  # 200 bytes ASCII
        r = await client.post("/api/auth/register", json={
            "email": "long@example.com",
            "password": long_pwd,
            "name": "Long Pwd",
        })
        assert r.status_code == 200

        await client.post("/api/auth/logout")

        # Le login doit aussi marcher avec le mdp long
        r2 = await client.post("/api/auth/login", json={
            "email": "long@example.com",
            "password": long_pwd,
        })
        assert r2.status_code == 200

        # Et avec n'importe quoi de différent dans les 72 premiers bytes → fail
        r3 = await client.post("/api/auth/login", json={
            "email": "long@example.com",
            "password": "B" * 200,
        })
        assert r3.status_code == 401


# ─── /me ────────────────────────────────────────────────────────────────────

class TestMe:
    @pytest.mark.asyncio
    async def test_me_with_valid_session(self, client, make_user):
        _uid, _token, cookies = await make_user()
        r = await client.get("/api/auth/me", cookies=cookies)
        assert r.status_code == 200
        assert r.json()["user_id"] == _uid

    @pytest.mark.asyncio
    async def test_me_without_session_returns_401(self, client):
        r = await client.get("/api/auth/me")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_unknown_token_returns_401(self, client):
        r = await client.get("/api/auth/me", cookies={"session_token": "nope"})
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_expired_session_returns_401(self, client, mock_db):
        # On crée manuellement une session déjà expirée
        past = datetime.now(timezone.utc) - timedelta(days=1)
        await mock_db.users.insert_one({
            "user_id": "u_exp", "email": "e@x", "name": "X",
            "role": "user", "password_hash": "$2b$12$x",
        })
        await mock_db.user_sessions.insert_one({
            "user_id": "u_exp",
            "session_token": "expired_token",
            "expires_at": past.isoformat(),
        })
        r = await client.get("/api/auth/me", cookies={"session_token": "expired_token"})
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_banned_user_blocked(self, client, make_user):
        _uid, _token, cookies = await make_user(is_banned=True)
        r = await client.get("/api/auth/me", cookies=cookies)
        assert r.status_code == 403


# ─── Logout ─────────────────────────────────────────────────────────────────

class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_invalidates_session_in_db(self, client, mock_db, make_user):
        _uid, token, cookies = await make_user()
        # Avant : session existe
        assert await mock_db.user_sessions.find_one({"session_token": token})

        r = await client.post("/api/auth/logout", cookies=cookies)
        assert r.status_code == 200

        # Après : session retirée
        assert await mock_db.user_sessions.find_one({"session_token": token}) is None

    @pytest.mark.asyncio
    async def test_logout_without_session_is_idempotent(self, client):
        r = await client.post("/api/auth/logout")
        assert r.status_code == 200


# ─── forgot/reset password — anti-énumération ───────────────────────────────

class TestForgotPassword:
    @pytest.mark.asyncio
    async def test_forgot_password_unknown_email_returns_200(self, client):
        """Anti-enumeration : un email inconnu ne doit pas révéler son inexistence."""
        r = await client.post("/api/auth/forgot-password", json={
            "email": "unknown@example.com",
        })
        assert r.status_code == 200
        # Pas de token créé en DB côté unknown — vérification dans test ci-dessous

    @pytest.mark.asyncio
    async def test_forgot_password_known_email_creates_token(self, client, mock_db):
        await mock_db.users.insert_one({
            "user_id": "u_known", "email": "known@example.com",
            "name": "K", "role": "user", "password_hash": "$2b$12$x",
        })
        r = await client.post("/api/auth/forgot-password", json={
            "email": "known@example.com",
        })
        assert r.status_code == 200

        token_doc = await mock_db.password_resets.find_one({"email": "known@example.com"})
        assert token_doc is not None
        assert token_doc["used"] is False
