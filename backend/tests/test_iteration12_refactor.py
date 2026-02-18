"""
Iteration 12: Backend Regression Tests after Server.py Refactoring
Tests all API routes to ensure they remain functional after splitting 1907-line server.py into modular routers.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestStats:
    """Admin Stats Endpoint - /api/stats"""
    
    def test_stats_returns_counts(self):
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "master_kits" in data, "Missing master_kits in stats"
        assert "versions" in data, "Missing versions in stats"
        assert "users" in data, "Missing users in stats"
        assert "reviews" in data, "Missing reviews in stats"
        assert isinstance(data["master_kits"], int), "master_kits should be int"
        assert isinstance(data["versions"], int), "versions should be int"
        print(f"✓ Stats: {data['master_kits']} kits, {data['versions']} versions, {data['users']} users, {data['reviews']} reviews")


class TestMasterKits:
    """Master Kits CRUD - /api/master-kits routes"""
    
    def test_list_master_kits(self):
        response = requests.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Should return list"
        if data:
            kit = data[0]
            assert "kit_id" in kit, "Missing kit_id"
            assert "club" in kit, "Missing club"
            assert "season" in kit, "Missing season"
            assert "version_count" in kit, "Missing version_count"
        print(f"✓ List master-kits returned {len(data)} kits")

    def test_master_kits_with_club_filter(self):
        response = requests.get(f"{BASE_URL}/api/master-kits?club=Barcelona&limit=5")
        assert response.status_code == 200
        data = response.json()
        for kit in data:
            assert "barcelona" in kit.get("club", "").lower(), f"Filter failed: {kit.get('club')}"
        print(f"✓ Club filter (Barcelona): {len(data)} kits")

    def test_master_kits_with_search(self):
        response = requests.get(f"{BASE_URL}/api/master-kits?search=Paris&limit=5")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Search (Paris): {len(data)} kits found")

    def test_master_kits_count(self):
        response = requests.get(f"{BASE_URL}/api/master-kits/count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data, "Missing count"
        assert isinstance(data["count"], int)
        print(f"✓ Master kits count: {data['count']}")

    def test_master_kits_filters(self):
        response = requests.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "clubs" in data, "Missing clubs filter"
        assert "brands" in data, "Missing brands filter"
        assert "seasons" in data, "Missing seasons filter"
        assert "kit_types" in data, "Missing kit_types filter"
        print(f"✓ Filters: {len(data.get('clubs', []))} clubs, {len(data.get('brands', []))} brands")

    def test_get_master_kit_by_id(self):
        # First get a kit ID
        list_resp = requests.get(f"{BASE_URL}/api/master-kits?limit=1")
        assert list_resp.status_code == 200
        kits = list_resp.json()
        if not kits:
            pytest.skip("No kits available")
        kit_id = kits[0]["kit_id"]
        
        # Get by ID
        response = requests.get(f"{BASE_URL}/api/master-kits/{kit_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["kit_id"] == kit_id
        assert "versions" in data, "Missing versions in kit detail"
        print(f"✓ Get kit {kit_id}: {data.get('club')} {data.get('season')}")


class TestVersions:
    """Versions Routes - /api/versions"""
    
    def test_list_versions(self):
        response = requests.get(f"{BASE_URL}/api/versions?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            v = data[0]
            assert "version_id" in v
            assert "kit_id" in v
            assert "competition" in v
        print(f"✓ List versions: {len(data)} versions")

    def test_versions_by_kit_id(self):
        # Get a kit first
        kits_resp = requests.get(f"{BASE_URL}/api/master-kits?limit=1")
        kits = kits_resp.json()
        if not kits:
            pytest.skip("No kits available")
        kit_id = kits[0]["kit_id"]
        
        response = requests.get(f"{BASE_URL}/api/versions?kit_id={kit_id}")
        assert response.status_code == 200
        data = response.json()
        for v in data:
            assert v["kit_id"] == kit_id, "Versions filtered by wrong kit_id"
        print(f"✓ Versions for kit {kit_id}: {len(data)}")

    def test_get_version_by_id(self):
        # Get a version ID
        list_resp = requests.get(f"{BASE_URL}/api/versions?limit=1")
        versions = list_resp.json()
        if not versions:
            pytest.skip("No versions available")
        version_id = versions[0]["version_id"]
        
        response = requests.get(f"{BASE_URL}/api/versions/{version_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["version_id"] == version_id
        assert "master_kit" in data, "Missing master_kit in version detail"
        assert "reviews" in data, "Missing reviews in version detail"
        print(f"✓ Get version {version_id}: {data.get('competition')}, {data.get('model')}")


class TestTeams:
    """Teams Entity Routes - /api/teams"""
    
    def test_list_teams(self):
        response = requests.get(f"{BASE_URL}/api/teams")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            t = data[0]
            assert "team_id" in t
            assert "name" in t
            assert "slug" in t
            assert "kit_count" in t
        print(f"✓ List teams: {len(data)} teams")

    def test_teams_search(self):
        response = requests.get(f"{BASE_URL}/api/teams?search=Barcelona")
        assert response.status_code == 200
        data = response.json()
        for t in data:
            assert "barcelona" in t.get("name", "").lower() or any("barcelona" in aka.lower() for aka in t.get("aka", []))
        print(f"✓ Teams search (Barcelona): {len(data)} teams")

    def test_get_team_by_slug(self):
        # Get a team first
        list_resp = requests.get(f"{BASE_URL}/api/teams?limit=1")
        teams = list_resp.json()
        if not teams:
            pytest.skip("No teams available")
        slug = teams[0]["slug"]
        
        response = requests.get(f"{BASE_URL}/api/teams/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        assert "kits" in data, "Missing kits list in team detail"
        assert "kit_count" in data
        print(f"✓ Get team {slug}: {data.get('name')}, {data.get('kit_count')} kits")


class TestLeagues:
    """Leagues Entity Routes - /api/leagues"""
    
    def test_list_leagues(self):
        response = requests.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            lg = data[0]
            assert "league_id" in lg
            assert "name" in lg
            assert "slug" in lg
        print(f"✓ List leagues: {len(data)} leagues")

    def test_get_league_by_slug(self):
        list_resp = requests.get(f"{BASE_URL}/api/leagues?limit=1")
        leagues = list_resp.json()
        if not leagues:
            pytest.skip("No leagues available")
        slug = leagues[0]["slug"]
        
        response = requests.get(f"{BASE_URL}/api/leagues/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        assert "kits" in data
        print(f"✓ Get league {slug}: {data.get('name')}")


class TestBrands:
    """Brands Entity Routes - /api/brands"""
    
    def test_list_brands(self):
        response = requests.get(f"{BASE_URL}/api/brands")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            b = data[0]
            assert "brand_id" in b
            assert "name" in b
            assert "slug" in b
        print(f"✓ List brands: {len(data)} brands")

    def test_get_brand_by_slug(self):
        list_resp = requests.get(f"{BASE_URL}/api/brands?limit=1")
        brands = list_resp.json()
        if not brands:
            pytest.skip("No brands available")
        slug = brands[0]["slug"]
        
        response = requests.get(f"{BASE_URL}/api/brands/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        assert "kits" in data
        print(f"✓ Get brand {slug}: {data.get('name')}, {data.get('kit_count')} kits")


class TestPlayers:
    """Players Entity Routes - /api/players"""
    
    def test_list_players(self):
        response = requests.get(f"{BASE_URL}/api/players")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            p = data[0]
            assert "player_id" in p
            assert "full_name" in p
            assert "slug" in p
        print(f"✓ List players: {len(data)} players")

    def test_get_player_by_slug(self):
        list_resp = requests.get(f"{BASE_URL}/api/players?limit=1")
        players = list_resp.json()
        if not players:
            pytest.skip("No players available")
        slug = players[0]["slug"]
        
        response = requests.get(f"{BASE_URL}/api/players/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug
        print(f"✓ Get player {slug}: {data.get('full_name')}")


class TestAutocomplete:
    """Autocomplete Routes - /api/autocomplete"""
    
    def test_autocomplete_team_type(self):
        response = requests.get(f"{BASE_URL}/api/autocomplete?type=team&q=bar")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Autocomplete type=team, q=bar: {len(data)} results")

    def test_autocomplete_brand_type(self):
        response = requests.get(f"{BASE_URL}/api/autocomplete?type=brand&query=nike")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Autocomplete type=brand, query=nike: {len(data)} results")

    def test_autocomplete_field_club(self):
        response = requests.get(f"{BASE_URL}/api/autocomplete?field=club&q=Par")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Autocomplete field=club, q=Par: {len(data)} results")


class TestEstimation:
    """Estimation Route - /api/estimate"""
    
    def test_estimate_price_replica(self):
        payload = {
            "model_type": "Replica",
            "competition": "National Championship",
            "condition_origin": "Shop",
            "physical_state": "New with tag",
            "flocking_origin": "",
            "signed": False,
            "signed_proof": False,
            "season_year": 2020
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "base_price" in data
        assert "estimated_price" in data
        assert "breakdown" in data
        assert data["model_type"] == "Replica"
        print(f"✓ Estimate (Replica): base={data['base_price']}, estimated={data['estimated_price']}")

    def test_estimate_price_authentic(self):
        payload = {
            "model_type": "Authentic",
            "competition": "Continental Cup",
            "condition_origin": "Match Worn",
            "physical_state": "Very good",
            "flocking_origin": "Official",
            "signed": True,
            "signed_proof": True,
            "season_year": 2015
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["estimated_price"] > data["base_price"], "Authentic should have higher estimated price"
        print(f"✓ Estimate (Authentic, signed): base={data['base_price']}, estimated={data['estimated_price']}")


class TestSubmissions:
    """Submissions Route - /api/submissions (public list, auth required for create)"""
    
    def test_list_submissions_pending(self):
        response = requests.get(f"{BASE_URL}/api/submissions?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List submissions (pending): {len(data)}")

    def test_list_submissions_approved(self):
        response = requests.get(f"{BASE_URL}/api/submissions?status=approved")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List submissions (approved): {len(data)}")


class TestReports:
    """Reports Route - /api/reports"""
    
    def test_list_reports(self):
        response = requests.get(f"{BASE_URL}/api/reports")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List reports: {len(data)}")


class TestReviews:
    """Reviews Route - /api/reviews"""
    
    def test_get_reviews_for_version(self):
        # Get a version ID first
        ver_resp = requests.get(f"{BASE_URL}/api/versions?limit=1")
        versions = ver_resp.json()
        if not versions:
            pytest.skip("No versions available")
        version_id = versions[0]["version_id"]
        
        response = requests.get(f"{BASE_URL}/api/reviews?version_id={version_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Reviews for version {version_id}: {len(data)}")


class TestAuthProtectedEndpoints:
    """Auth-protected endpoints should return 401 without session"""
    
    def test_auth_me_requires_session(self):
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /api/auth/me returns 401 without session")

    def test_collections_requires_session(self):
        response = requests.get(f"{BASE_URL}/api/collections")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /api/collections returns 401 without session")

    def test_wishlist_requires_session(self):
        response = requests.get(f"{BASE_URL}/api/wishlist")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ /api/wishlist returns 401 without session")

    def test_create_submission_requires_session(self):
        payload = {"submission_type": "master_kit", "data": {"club": "Test"}}
        response = requests.post(f"{BASE_URL}/api/submissions", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/submissions returns 401 without session")


class TestEdgeCases:
    """Edge cases and 404 handling"""
    
    def test_get_nonexistent_kit(self):
        response = requests.get(f"{BASE_URL}/api/master-kits/nonexistent_kit_id")
        assert response.status_code == 404
        print("✓ Nonexistent kit returns 404")

    def test_get_nonexistent_version(self):
        response = requests.get(f"{BASE_URL}/api/versions/nonexistent_version_id")
        assert response.status_code == 404
        print("✓ Nonexistent version returns 404")

    def test_get_nonexistent_team(self):
        response = requests.get(f"{BASE_URL}/api/teams/nonexistent_team_slug")
        assert response.status_code == 404
        print("✓ Nonexistent team returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
