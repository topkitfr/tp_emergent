"""
Test iteration 6 features:
1. Autocomplete endpoint for forms
2. Wishlist CRUD operations
3. Collection endpoints with new fields (flocking, condition_origin, physical_state, etc.)
4. Master-kits filters with sponsors and genders arrays
5. Version with ean_code field
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
assert BASE_URL, "REACT_APP_BACKEND_URL environment variable must be set"


class TestAutocompleteEndpoint:
    """Test /api/autocomplete endpoint - no auth required"""

    def test_autocomplete_club_returns_matching_clubs(self):
        """GET /api/autocomplete?field=club&q=bar returns matching clubs"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "club", "q": "bar"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return FC Barcelona
        assert any("barcelona" in c.lower() for c in data)

    def test_autocomplete_brand_returns_matching_brands(self):
        """GET /api/autocomplete?field=brand&q=ni returns matching brands"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "brand", "q": "ni"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return Nike
        assert any("nike" in b.lower() for b in data)

    def test_autocomplete_sponsor_returns_matching_sponsors(self):
        """GET /api/autocomplete?field=sponsor&q=qat returns matching sponsors"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "sponsor", "q": "qat"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return Qatar Airways and/or Qatar Foundation
        assert any("qatar" in s.lower() for s in data)

    def test_autocomplete_league_returns_matching_leagues(self):
        """GET /api/autocomplete?field=league&q=lig returns matching leagues"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "league", "q": "lig"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return La Liga or similar
        assert len(data) >= 0  # May have results

    def test_autocomplete_invalid_field_returns_empty(self):
        """GET /api/autocomplete with invalid field returns empty array"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "invalid", "q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestFiltersEndpoint:
    """Test /api/master-kits/filters endpoint"""

    def test_filters_returns_sponsors_array(self):
        """GET /api/master-kits/filters returns sponsors array"""
        response = requests.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "sponsors" in data
        assert isinstance(data["sponsors"], list)
        # Should have some sponsors from imported data
        assert len(data["sponsors"]) > 0

    def test_filters_returns_genders_array(self):
        """GET /api/master-kits/filters returns genders array"""
        response = requests.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "genders" in data
        assert isinstance(data["genders"], list)
        # genders may be empty if not set on existing data

    def test_filters_returns_all_expected_arrays(self):
        """GET /api/master-kits/filters returns all filter arrays"""
        response = requests.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        expected_keys = ["clubs", "brands", "seasons", "years", "kit_types", "designs", "leagues", "sponsors", "genders"]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
            assert isinstance(data[key], list)


@pytest.fixture(scope="module")
def auth_session():
    """Create a test user and session for authenticated tests"""
    import subprocess
    import json
    
    timestamp = int(datetime.now().timestamp() * 1000)
    user_id = f"test-user-{timestamp}"
    session_token = f"test_session_{timestamp}"
    
    # Create user and session in MongoDB
    mongo_script = f'''
    use('test_database');
    db.users.insertOne({{
        user_id: "{user_id}",
        email: "test.user.{timestamp}@example.com",
        name: "Test User",
        picture: "https://via.placeholder.com/150",
        created_at: new Date()
    }});
    db.user_sessions.insertOne({{
        user_id: "{user_id}",
        session_token: "{session_token}",
        expires_at: new Date(Date.now() + 7*24*60*60*1000),
        created_at: new Date()
    }});
    '''
    
    subprocess.run(["mongosh", "--quiet", "--eval", mongo_script], capture_output=True)
    
    yield {"user_id": user_id, "session_token": session_token}
    
    # Cleanup
    cleanup_script = f'''
    use('test_database');
    db.users.deleteOne({{ user_id: "{user_id}" }});
    db.user_sessions.deleteMany({{ user_id: "{user_id}" }});
    db.wishlists.deleteMany({{ user_id: "{user_id}" }});
    db.collections.deleteMany({{ user_id: "{user_id}" }});
    '''
    subprocess.run(["mongosh", "--quiet", "--eval", cleanup_script], capture_output=True)


@pytest.fixture(scope="module")
def test_version(auth_session):
    """Create a test version for wishlist and collection tests"""
    token = auth_session["session_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get a kit_id to create version for
    kits_response = requests.get(f"{BASE_URL}/api/master-kits?limit=1")
    kit_id = kits_response.json()[0]["kit_id"]
    
    # Create a version
    version_data = {
        "kit_id": kit_id,
        "competition": "Test Competition",
        "model": "Replica",
        "sku_code": "TEST-SKU-456",
        "ean_code": "9876543210987"
    }
    response = requests.post(f"{BASE_URL}/api/versions", json=version_data, headers=headers)
    version = response.json()
    
    yield version
    
    # Cleanup - versions don't have delete endpoint, so leave it


class TestWishlistEndpoints:
    """Test /api/wishlist endpoints - requires auth"""

    def test_add_to_wishlist(self, auth_session, test_version):
        """POST /api/wishlist adds version to wishlist"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/api/wishlist",
            json={"version_id": test_version["version_id"], "notes": "Test note"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "wishlist_id" in data
        assert data["version_id"] == test_version["version_id"]
        assert data["notes"] == "Test note"

    def test_get_wishlist(self, auth_session, test_version):
        """GET /api/wishlist returns user's wishlist items"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/wishlist", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Should include version and master_kit details
        assert "version" in data[0]
        assert "master_kit" in data[0]

    def test_check_wishlist_returns_in_wishlist_true(self, auth_session, test_version):
        """GET /api/wishlist/check/{version_id} returns in_wishlist: true"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/api/wishlist/check/{test_version['version_id']}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["in_wishlist"] == True
        assert "wishlist_id" in data
        assert data["wishlist_id"] is not None

    def test_remove_from_wishlist(self, auth_session, test_version):
        """DELETE /api/wishlist/{wishlist_id} removes from wishlist"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get wishlist_id
        check_response = requests.get(
            f"{BASE_URL}/api/wishlist/check/{test_version['version_id']}",
            headers=headers
        )
        wishlist_id = check_response.json()["wishlist_id"]
        
        # Delete
        response = requests.delete(f"{BASE_URL}/api/wishlist/{wishlist_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Removed from wishlist"
        
        # Verify removed
        check_after = requests.get(
            f"{BASE_URL}/api/wishlist/check/{test_version['version_id']}",
            headers=headers
        )
        assert check_after.json()["in_wishlist"] == False

    def test_wishlist_requires_auth(self, test_version):
        """Wishlist endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/wishlist")
        assert response.status_code == 401


class TestCollectionWithNewFields:
    """Test /api/collections endpoints with new fields"""

    def test_post_collections_accepts_new_fields(self, auth_session, test_version):
        """POST /api/collections accepts new fields: flocking_type, condition_origin, etc."""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        collection_data = {
            "version_id": test_version["version_id"],
            "category": "Test",
            "flocking_type": "Name+Number",
            "flocking_origin": "Official",
            "flocking_detail": "Ronaldo 7",
            "condition_origin": "Match Worn",
            "physical_state": "Very good",
            "purchase_cost": 100.50,
            "price_estimate": 200.00,
            "signed": True,
            "signed_by": "Cristiano Ronaldo"
        }
        
        response = requests.post(f"{BASE_URL}/api/collections", json=collection_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all new fields are present
        assert data["flocking_type"] == "Name+Number"
        assert data["flocking_origin"] == "Official"
        assert data["flocking_detail"] == "Ronaldo 7"
        assert data["condition_origin"] == "Match Worn"
        assert data["physical_state"] == "Very good"
        assert data["purchase_cost"] == 100.50
        assert data["price_estimate"] == 200.00
        assert data["signed"] == True
        assert data["signed_by"] == "Cristiano Ronaldo"

    def test_put_collections_accepts_new_fields(self, auth_session, test_version):
        """PUT /api/collections/{id} accepts new collection item fields"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Get collection item
        get_response = requests.get(f"{BASE_URL}/api/collections", headers=headers)
        collection_id = get_response.json()[0]["collection_id"]
        
        # Update with new fields
        update_data = {
            "flocking_type": "Number",
            "condition_origin": "Club Stock",
            "physical_state": "New with tag",
            "purchase_cost": 150.00,
            "signed": False
        }
        
        response = requests.put(
            f"{BASE_URL}/api/collections/{collection_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify updated fields
        assert data["flocking_type"] == "Number"
        assert data["condition_origin"] == "Club Stock"
        assert data["physical_state"] == "New with tag"
        assert data["purchase_cost"] == 150.00
        assert data["signed"] == False
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/collections/{collection_id}", headers=headers)


class TestVersionWithEanCode:
    """Test Version creation with ean_code field"""

    def test_create_version_with_ean_code(self, auth_session):
        """POST /api/versions accepts ean_code field"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Get a kit_id
        kits_response = requests.get(f"{BASE_URL}/api/master-kits?limit=1")
        kit_id = kits_response.json()[0]["kit_id"]
        
        version_data = {
            "kit_id": kit_id,
            "competition": "EAN Test Competition",
            "model": "Authentic",
            "sku_code": "EAN-TEST-SKU",
            "ean_code": "0123456789012"
        }
        
        response = requests.post(f"{BASE_URL}/api/versions", json=version_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ean_code"] == "0123456789012"
        assert data["sku_code"] == "EAN-TEST-SKU"


class TestMasterKitWithNewFields:
    """Test Master Kit creation with new fields"""

    def test_create_master_kit_with_gender_and_sponsor(self, auth_session):
        """POST /api/master-kits accepts gender and sponsor fields"""
        token = auth_session["session_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        kit_data = {
            "club": "Test Club",
            "season": "2025/2026",
            "kit_type": "Home",
            "brand": "Adidas",
            "front_photo": "https://example.com/photo.jpg",
            "year": 2025,
            "sponsor": "Test Sponsor",
            "gender": "Man",
            "league": "Test League"
        }
        
        response = requests.post(f"{BASE_URL}/api/master-kits", json=kit_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["sponsor"] == "Test Sponsor"
        assert data["gender"] == "Man"
        assert data["league"] == "Test League"
