"""
Tests du router /api/marketplace.

Couvre :
  - Créer un listing (sale / trade / both)
  - Quota max 10 listings actifs
  - Impossible de lister un item qui n'est pas dans sa collection
  - Browse listings (GET /api/marketplace)
  - Détail listing (GET /api/marketplace/{id})
  - Faire une offre (buy / trade)
  - Refus de faire une offre sur son propre listing
  - Accepter / refuser une offre
  - Annuler un listing
"""
from __future__ import annotations

import uuid
import pytest
import pytest_asyncio


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _collection_id() -> str:
    return f"col_{uuid.uuid4().hex[:12]}"

def _version_id() -> str:
    return f"ver_{uuid.uuid4().hex[:12]}"

def _kit_id() -> str:
    return f"kit_{uuid.uuid4().hex[:12]}"


async def _seed_collection_item(mock_db, user_id: str, collection_id: str | None = None, version_id: str | None = None) -> dict:
    """Insère un item de collection pour user_id et retourne le doc."""
    col_id = collection_id or _collection_id()
    ver_id = version_id or _version_id()
    doc = {
        "collection_id": col_id,
        "user_id": user_id,
        "version_id": ver_id,
        "physical_state": "Good",
        "estimated_price": 80.0,
        "condition_summary": "Good",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    await mock_db.collections.insert_one(doc)
    return doc


# ─── Créer un listing ─────────────────────────────────────────────────────────

class TestCreateListing:
    @pytest.mark.asyncio
    async def test_create_sale_listing(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        r = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 75.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["listing_type"] == "sale"
        assert data["asking_price"] == 75.0
        assert data["status"] == "active"
        assert data["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_create_trade_listing(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        r = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "trade",
            "trade_for": "PSG 2012 home L",
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["listing_type"] == "trade"
        assert data["asking_price"] is None

    @pytest.mark.asyncio
    async def test_create_listing_requires_auth(self, client, mock_db, make_user):
        user_id, _, _ = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        r = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 50.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_cannot_list_someone_elses_item(self, client, mock_db, make_user):
        owner_id, _, _ = await make_user()
        thief_id, _, thief_cookies = await make_user()
        col = await _seed_collection_item(mock_db, owner_id)

        r = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 50.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=thief_cookies)
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_quota_max_10_active_listings(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()

        # Crée 10 listings actifs directement en DB
        for _ in range(10):
            col = await _seed_collection_item(mock_db, user_id)
            await mock_db.listings.insert_one({
                "listing_id": f"lst_{uuid.uuid4().hex[:12]}",
                "collection_id": col["collection_id"],
                "user_id": user_id,
                "listing_type": "sale",
                "status": "active",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            })

        # Le 11e doit être refusé
        col11 = await _seed_collection_item(mock_db, user_id)
        r = await client.post("/api/marketplace", json={
            "collection_id": col11["collection_id"],
            "listing_type": "sale",
            "asking_price": 50.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        assert r.status_code == 400
        assert "quota" in r.json()["detail"].lower() or "max" in r.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_cannot_list_already_listed_item(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        r1 = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 50.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        assert r1.status_code == 200

        r2 = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 60.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        assert r2.status_code == 400
        assert "already listed" in r2.json()["detail"].lower()


# ─── Browse ───────────────────────────────────────────────────────────────────

class TestBrowseListings:
    @pytest.mark.asyncio
    async def test_browse_returns_active_listings(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 90.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)

        r = await client.get("/api/marketplace")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert len(data["results"]) >= 1

    @pytest.mark.asyncio
    async def test_browse_filter_by_type(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col1 = await _seed_collection_item(mock_db, user_id)
        col2 = await _seed_collection_item(mock_db, user_id)

        await client.post("/api/marketplace", json={
            "collection_id": col1["collection_id"],
            "listing_type": "sale",
            "asking_price": 50.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        await client.post("/api/marketplace", json={
            "collection_id": col2["collection_id"],
            "listing_type": "trade",
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)

        r = await client.get("/api/marketplace?listing_type=trade")
        assert r.status_code == 200
        results = r.json()["results"]
        assert all(l["listing_type"] == "trade" for l in results)


# ─── Offres ───────────────────────────────────────────────────────────────────

class TestOffers:
    @pytest_asyncio.fixture
    async def listing(self, client, mock_db, make_user):
        """Crée un listing actif et retourne (listing_id, seller_cookies, buyer_cookies)."""
        seller_id, _, seller_cookies = await make_user()
        buyer_id, _, buyer_cookies = await make_user()
        col = await _seed_collection_item(mock_db, seller_id)

        r = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "both",
            "asking_price": 100.0,
            "trade_for": "n'importe quel maillot",
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=seller_cookies)
        assert r.status_code == 200
        listing_id = r.json()["listing_id"]
        return listing_id, seller_cookies, buyer_cookies, seller_id, buyer_id

    @pytest.mark.asyncio
    async def test_buyer_can_make_buy_offer(self, client, mock_db, make_user, listing):
        listing_id, seller_cookies, buyer_cookies, *_ = listing

        r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 85.0,
            "message": "Je prends !",
        }, cookies=buyer_cookies)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["offer_type"] == "buy"
        assert data["offered_price"] == 85.0
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_seller_cannot_offer_on_own_listing(self, client, mock_db, make_user, listing):
        listing_id, seller_cookies, *_ = listing

        r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 90.0,
        }, cookies=seller_cookies)
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_offer_requires_auth(self, client, mock_db, make_user, listing):
        listing_id, *_ = listing

        r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 90.0,
        })
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_seller_can_accept_offer(self, client, mock_db, make_user, listing):
        listing_id, seller_cookies, buyer_cookies, *_ = listing

        offer_r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 85.0,
        }, cookies=buyer_cookies)
        offer_id = offer_r.json()["offer_id"]

        r = await client.put(f"/api/marketplace/offers/{offer_id}", json={
            "status": "accepted",
        }, cookies=seller_cookies)
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_seller_can_refuse_offer(self, client, mock_db, make_user, listing):
        listing_id, seller_cookies, buyer_cookies, *_ = listing

        offer_r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 50.0,
        }, cookies=buyer_cookies)
        offer_id = offer_r.json()["offer_id"]

        r = await client.put(f"/api/marketplace/offers/{offer_id}", json={
            "status": "refused",
        }, cookies=seller_cookies)
        assert r.status_code == 200
        assert r.json()["status"] == "refused"

    @pytest.mark.asyncio
    async def test_buyer_cannot_accept_own_offer(self, client, mock_db, make_user, listing):
        listing_id, _, buyer_cookies, *_ = listing

        offer_r = await client.post(f"/api/marketplace/{listing_id}/offers", json={
            "offer_type": "buy",
            "offered_price": 85.0,
        }, cookies=buyer_cookies)
        offer_id = offer_r.json()["offer_id"]

        r = await client.put(f"/api/marketplace/offers/{offer_id}", json={
            "status": "accepted",
        }, cookies=buyer_cookies)
        assert r.status_code == 403


# ─── Annuler un listing ───────────────────────────────────────────────────────

class TestCancelListing:
    @pytest.mark.asyncio
    async def test_owner_can_cancel_listing(self, client, mock_db, make_user):
        user_id, _, cookies = await make_user()
        col = await _seed_collection_item(mock_db, user_id)

        r_create = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 60.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=cookies)
        listing_id = r_create.json()["listing_id"]

        r = await client.delete(f"/api/marketplace/{listing_id}", cookies=cookies)
        assert r.status_code == 200

        listing = await mock_db.listings.find_one({"listing_id": listing_id})
        assert listing["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_other_user_cannot_cancel_listing(self, client, mock_db, make_user):
        owner_id, _, owner_cookies = await make_user()
        other_id, _, other_cookies = await make_user()
        col = await _seed_collection_item(mock_db, owner_id)

        r_create = await client.post("/api/marketplace", json={
            "collection_id": col["collection_id"],
            "listing_type": "sale",
            "asking_price": 60.0,
            "listing_photos": ["https://example.com/front.jpg", "https://example.com/back.jpg"],
        }, cookies=owner_cookies)
        listing_id = r_create.json()["listing_id"]

        r = await client.delete(f"/api/marketplace/{listing_id}", cookies=other_cookies)
        assert r.status_code == 403
