"""
Fixtures partagées pour la suite de tests Topkit.

Stratégie :
  - On remplace le client Mongo réel (Motor / Atlas) par une instance
    `mongomock-motor` en mémoire — tests instantanés, zéro infra.
  - On instancie l'app FastAPI avec `asgi-lifespan` pour exécuter le
    `@app.on_event("startup")` sans bloquer (création des indexes).
  - On expose un `httpx.AsyncClient` configuré sur l'app via ASGITransport.

Convention : chaque test reçoit une DB vierge (fixture function-scoped).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ─── Variables d'env requises AVANT import des modules backend ──────────────
# Le backend lève une RuntimeError au boot si ces vars sont absentes/mauvaises.
# On configure des valeurs valides pour le contexte test.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("MONGO_URL", "mongodb://test/")
os.environ.setdefault("DB_NAME", "topkit_test")
os.environ.setdefault("RECEIVER_SECRET", "test-secret-not-changeme")
os.environ.pop("DEV_LOGIN", None)  # pas de bypass auth en test

# Permet `from backend.xxx import ...` quand on lance pytest depuis la racine
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport


# ─── DB mock — réinitialisée pour chaque test ───────────────────────────────
@pytest_asyncio.fixture
async def mock_db(monkeypatch):
    """
    Remplace `backend.database.db` (et `client`) par une instance mongomock.
    On patche AVANT que les routers ne soient importés pour s'assurer que
    tous les imports `from ..database import db` voient la version mockée.
    """
    fake_client = AsyncMongoMockClient()
    fake_db = fake_client["topkit_test"]

    # On patche dans tous les modules qui ont déjà importé `db`/`client`.
    # `monkeypatch.setattr` accepte le module objet OU son chemin string.
    import backend.database as db_module
    monkeypatch.setattr(db_module, "client", fake_client)
    monkeypatch.setattr(db_module, "db", fake_db)

    # Les routers font `from ..database import db` (référence directe).
    # Donc on doit aussi patcher la référence locale dans chaque router déjà importé.
    for mod_name in list(sys.modules):
        if mod_name.startswith("backend.routers.") or mod_name in (
            "backend.auth", "backend.utils", "backend.middleware",
            "backend.image_mirror",
        ):
            mod = sys.modules[mod_name]
            if hasattr(mod, "db"):
                monkeypatch.setattr(mod, "db", fake_db, raising=False)
            if hasattr(mod, "client"):
                monkeypatch.setattr(mod, "client", fake_client, raising=False)

    yield fake_db


# ─── Reset rate-limit store entre tests ─────────────────────────────────────
@pytest.fixture(autouse=True)
def _reset_rate_limit():
    """
    Le rate-limiter de `backend.server` stocke ses compteurs dans un dict
    en mémoire process. Sans reset, les tests qui spamment /api/auth/* finissent
    par toucher le seuil et reçoivent 429 au lieu du code attendu.
    """
    try:
        from backend.server import _rate_limit_store
        _rate_limit_store.clear()
    except Exception:
        pass
    yield


# ─── App FastAPI lifecyclée ─────────────────────────────────────────────────
@pytest_asyncio.fixture
async def app(mock_db):
    """
    Importe l'app après le mock DB et déroule son lifespan (startup/shutdown).
    """
    # Import différé pour bénéficier des env vars + mock_db
    from backend.server import app as fastapi_app

    # Re-patche db dans server.py au cas où il a importé après mock_db
    import backend.server as server_mod
    if hasattr(server_mod, "db"):
        server_mod.db = mock_db

    async with LifespanManager(fastapi_app):
        yield fastapi_app


# ─── Client HTTP async ──────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─── Helpers d'authentification ─────────────────────────────────────────────
@pytest_asyncio.fixture
async def make_user(mock_db):
    """
    Factory : crée un user en DB et retourne (user_id, session_token, cookies dict).
    Usage :
        async def test_x(make_user, client):
            user_id, token, cookies = await make_user(role="user")
            r = await client.get("/api/auth/me", cookies=cookies)
    """
    from datetime import datetime, timezone, timedelta
    import uuid

    async def _factory(
        role: str = "user",
        email: str | None = None,
        is_banned: bool = False,
    ):
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        token = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        await mock_db.users.insert_one({
            "user_id": user_id,
            "email": email or f"{user_id}@example.com",
            "name": f"Test {user_id[-6:]}",
            "role": role,
            "password_hash": "$2b$12$placeholder",  # bcrypt-shaped, jamais matché
            "created_at": now.isoformat(),
            "is_banned": is_banned,
        })
        await mock_db.user_sessions.insert_one({
            "user_id": user_id,
            "session_token": token,
            "expires_at": (now + timedelta(days=7)).isoformat(),
            "created_at": now.isoformat(),
        })
        cookies = {"session_token": token}
        return user_id, token, cookies

    return _factory
