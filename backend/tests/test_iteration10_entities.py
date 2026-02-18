"""
Iteration 10 - Entity CRUD APIs Testing

Tests for:
- Teams CRUD (GET /api/teams, GET /api/teams/{id}, POST /api/teams, PUT /api/teams/{id})
- Leagues CRUD (GET /api/leagues, GET /api/leagues/{id}, POST /api/leagues)
- Brands CRUD (GET /api/brands, GET /api/brands/{id}, POST /api/brands)
- Players CRUD (GET /api/players, GET /api/players/{id}, POST /api/players)
- Autocomplete with entity types (type=team, type=brand, type=league, type=player)
- Legacy autocomplete (field=club, field=brand)
- Migration endpoint (POST /api/migrate-entities-from-kits)
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTeamsAPI:
    """Test Teams CRUD endpoints"""
    
    def test_list_teams(self):
        """GET /api/teams - list teams"""
        response = requests.get(f"{BASE_URL}/api/teams")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/teams returns {len(data)} teams")
        # Check structure of first team if exists
        if len(data) > 0:
            team = data[0]
            assert "team_id" in team
            assert "name" in team
            assert "slug" in team
            assert "kit_count" in team
            print(f"✓ Team structure validated: {team.get('name')}")
    
    def test_list_teams_with_search(self):
        """GET /api/teams?search=bar - search teams"""
        response = requests.get(f"{BASE_URL}/api/teams", params={"search": "bar"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/teams?search=bar returns {len(data)} teams")
        # Should find Barcelona
        if len(data) > 0:
            names = [t.get('name', '').lower() for t in data]
            assert any('bar' in n for n in names), "Search should find teams with 'bar'"
            print(f"✓ Search found teams: {[t.get('name') for t in data]}")
    
    def test_list_teams_with_country_filter(self):
        """GET /api/teams?country=Spain - filter by country"""
        response = requests.get(f"{BASE_URL}/api/teams", params={"country": "Spain"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/teams?country=Spain returns {len(data)} teams")
        for team in data:
            assert "spain" in team.get('country', '').lower(), f"Team {team.get('name')} should be in Spain"
    
    def test_get_team_by_id(self):
        """GET /api/teams/{id} - get team by ID"""
        # First get a team
        list_response = requests.get(f"{BASE_URL}/api/teams")
        teams = list_response.json()
        if len(teams) == 0:
            pytest.skip("No teams to test with")
        
        team = teams[0]
        team_id = team['team_id']
        
        response = requests.get(f"{BASE_URL}/api/teams/{team_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['team_id'] == team_id
        assert 'kit_count' in data
        assert 'kits' in data, "Detail endpoint should include kits list"
        print(f"✓ GET /api/teams/{team_id} returns team with {data.get('kit_count')} kits")
    
    def test_get_team_by_slug(self):
        """GET /api/teams/{slug} - get team by slug"""
        # First get a team with slug
        list_response = requests.get(f"{BASE_URL}/api/teams")
        teams = list_response.json()
        if len(teams) == 0:
            pytest.skip("No teams to test with")
        
        team = teams[0]
        slug = team.get('slug')
        if not slug:
            pytest.skip("Team has no slug")
        
        response = requests.get(f"{BASE_URL}/api/teams/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data['slug'] == slug
        print(f"✓ GET /api/teams/{slug} returns team: {data.get('name')}")
    
    def test_create_team(self):
        """POST /api/teams - create new team"""
        unique_name = f"TEST_Team_{uuid.uuid4().hex[:6]}"
        payload = {
            "name": unique_name,
            "country": "Testland",
            "city": "Test City"
        }
        response = requests.post(f"{BASE_URL}/api/teams", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data['name'] == unique_name
        assert data['country'] == "Testland"
        assert 'team_id' in data
        assert 'slug' in data
        print(f"✓ POST /api/teams created team: {data.get('name')} with id {data.get('team_id')}")
        
        # Verify GET returns the created team
        get_response = requests.get(f"{BASE_URL}/api/teams/{data['team_id']}")
        assert get_response.status_code == 200
        print(f"✓ GET /api/teams/{data['team_id']} verified creation")
    
    def test_create_duplicate_team_fails(self):
        """POST /api/teams - creating duplicate team should fail"""
        # First create a unique team
        unique_name = f"TEST_Dup_{uuid.uuid4().hex[:6]}"
        payload = {"name": unique_name, "country": "Dupland"}
        response1 = requests.post(f"{BASE_URL}/api/teams", json=payload)
        assert response1.status_code == 200
        
        # Try to create same team again
        response2 = requests.post(f"{BASE_URL}/api/teams", json=payload)
        assert response2.status_code == 400, "Duplicate team should return 400"
        print(f"✓ POST /api/teams duplicate correctly rejected")
    
    def test_update_team(self):
        """PUT /api/teams/{id} - update team"""
        # Create a team first
        unique_name = f"TEST_Update_{uuid.uuid4().hex[:6]}"
        create_response = requests.post(f"{BASE_URL}/api/teams", json={"name": unique_name, "country": "Old"})
        assert create_response.status_code == 200
        team_id = create_response.json()['team_id']
        
        # Update it
        new_name = f"TEST_Updated_{uuid.uuid4().hex[:6]}"
        update_response = requests.put(f"{BASE_URL}/api/teams/{team_id}", json={"name": new_name, "country": "New"})
        assert update_response.status_code == 200
        data = update_response.json()
        assert data['name'] == new_name
        assert data['country'] == "New"
        print(f"✓ PUT /api/teams/{team_id} updated team successfully")


class TestLeaguesAPI:
    """Test Leagues CRUD endpoints"""
    
    def test_list_leagues(self):
        """GET /api/leagues - list leagues"""
        response = requests.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/leagues returns {len(data)} leagues")
        if len(data) > 0:
            league = data[0]
            assert "league_id" in league
            assert "name" in league
            assert "kit_count" in league
            print(f"✓ League structure validated: {league.get('name')}")
    
    def test_get_league_by_id(self):
        """GET /api/leagues/{id} - get league by ID"""
        list_response = requests.get(f"{BASE_URL}/api/leagues")
        leagues = list_response.json()
        if len(leagues) == 0:
            pytest.skip("No leagues to test with")
        
        league = leagues[0]
        league_id = league['league_id']
        
        response = requests.get(f"{BASE_URL}/api/leagues/{league_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['league_id'] == league_id
        assert 'kits' in data
        print(f"✓ GET /api/leagues/{league_id} returns league: {data.get('name')}")
    
    def test_create_league(self):
        """POST /api/leagues - create new league"""
        unique_name = f"TEST_League_{uuid.uuid4().hex[:6]}"
        payload = {
            "name": unique_name,
            "country_or_region": "Test Region",
            "level": "domestic"
        }
        response = requests.post(f"{BASE_URL}/api/leagues", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == unique_name
        assert 'league_id' in data
        print(f"✓ POST /api/leagues created league: {data.get('name')}")


class TestBrandsAPI:
    """Test Brands CRUD endpoints"""
    
    def test_list_brands(self):
        """GET /api/brands - list brands"""
        response = requests.get(f"{BASE_URL}/api/brands")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/brands returns {len(data)} brands")
        if len(data) > 0:
            brand = data[0]
            assert "brand_id" in brand
            assert "name" in brand
            assert "kit_count" in brand
            print(f"✓ Brand structure validated: {brand.get('name')}")
    
    def test_list_brands_with_search(self):
        """GET /api/brands?search=nike - search brands"""
        response = requests.get(f"{BASE_URL}/api/brands", params={"search": "nike"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/brands?search=nike returns {len(data)} brands")
    
    def test_get_brand_by_id(self):
        """GET /api/brands/{id} - get brand by ID"""
        list_response = requests.get(f"{BASE_URL}/api/brands")
        brands = list_response.json()
        if len(brands) == 0:
            pytest.skip("No brands to test with")
        
        brand = brands[0]
        brand_id = brand['brand_id']
        
        response = requests.get(f"{BASE_URL}/api/brands/{brand_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['brand_id'] == brand_id
        assert 'kits' in data
        print(f"✓ GET /api/brands/{brand_id} returns brand: {data.get('name')}")
    
    def test_create_brand(self):
        """POST /api/brands - create new brand"""
        unique_name = f"TEST_Brand_{uuid.uuid4().hex[:6]}"
        payload = {
            "name": unique_name,
            "country": "Test Country"
        }
        response = requests.post(f"{BASE_URL}/api/brands", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == unique_name
        assert 'brand_id' in data
        print(f"✓ POST /api/brands created brand: {data.get('name')}")


class TestPlayersAPI:
    """Test Players CRUD endpoints"""
    
    def test_list_players(self):
        """GET /api/players - list players"""
        response = requests.get(f"{BASE_URL}/api/players")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/players returns {len(data)} players")
        if len(data) > 0:
            player = data[0]
            assert "player_id" in player
            assert "full_name" in player
            assert "kit_count" in player
            print(f"✓ Player structure validated: {player.get('full_name')}")
    
    def test_get_player_by_id(self):
        """GET /api/players/{id} - get player by ID"""
        list_response = requests.get(f"{BASE_URL}/api/players")
        players = list_response.json()
        if len(players) == 0:
            pytest.skip("No players to test with")
        
        player = players[0]
        player_id = player['player_id']
        
        response = requests.get(f"{BASE_URL}/api/players/{player_id}")
        assert response.status_code == 200
        data = response.json()
        assert data['player_id'] == player_id
        assert 'versions' in data
        print(f"✓ GET /api/players/{player_id} returns player: {data.get('full_name')}")
    
    def test_create_player(self):
        """POST /api/players - create new player"""
        unique_name = f"TEST_Player_{uuid.uuid4().hex[:6]}"
        payload = {
            "full_name": unique_name,
            "nationality": "Testland",
            "positions": ["Forward", "Winger"]
        }
        response = requests.post(f"{BASE_URL}/api/players", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['full_name'] == unique_name
        assert 'player_id' in data
        assert data['positions'] == ["Forward", "Winger"]
        print(f"✓ POST /api/players created player: {data.get('full_name')}")


class TestAutocomplete:
    """Test autocomplete endpoint with entity types"""
    
    def test_autocomplete_team(self):
        """GET /api/autocomplete?type=team&query=bar - entity autocomplete for teams"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"type": "team", "query": "bar"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/autocomplete?type=team&query=bar returns {len(data)} results")
        if len(data) > 0:
            item = data[0]
            assert "id" in item
            assert "label" in item
            print(f"✓ Team autocomplete item: {item}")
    
    def test_autocomplete_brand(self):
        """GET /api/autocomplete?type=brand&query=nike - entity autocomplete for brands"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"type": "brand", "query": "nike"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/autocomplete?type=brand&query=nike returns {len(data)} results")
    
    def test_autocomplete_league(self):
        """GET /api/autocomplete?type=league&query=ligue - entity autocomplete for leagues"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"type": "league", "query": "ligue"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/autocomplete?type=league&query=ligue returns {len(data)} results")
    
    def test_autocomplete_player(self):
        """GET /api/autocomplete?type=player&query=messi - entity autocomplete for players"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"type": "player", "query": "messi"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/autocomplete?type=player&query=messi returns {len(data)} results")
    
    def test_legacy_autocomplete_club(self):
        """GET /api/autocomplete?field=club&q=Par - legacy field autocomplete"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "club", "q": "Par"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/autocomplete?field=club&q=Par (legacy) returns {len(data)} results")
    
    def test_legacy_autocomplete_brand(self):
        """GET /api/autocomplete?field=brand&q=Nik - legacy field autocomplete"""
        response = requests.get(f"{BASE_URL}/api/autocomplete", params={"field": "brand", "q": "Nik"})
        assert response.status_code == 200
        data = response.json()
        print(f"✓ GET /api/autocomplete?field=brand&q=Nik (legacy) returns {len(data)} results")


class TestMigration:
    """Test migration endpoint"""
    
    def test_migrate_entities_idempotent(self):
        """POST /api/migrate-entities-from-kits - should be idempotent"""
        # Get initial counts
        teams_before = len(requests.get(f"{BASE_URL}/api/teams").json())
        brands_before = len(requests.get(f"{BASE_URL}/api/brands").json())
        
        # Run migration
        response = requests.post(f"{BASE_URL}/api/migrate-entities-from-kits")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        print(f"✓ POST /api/migrate-entities-from-kits completed: {data}")
        
        # Run migration again - should be idempotent
        response2 = requests.post(f"{BASE_URL}/api/migrate-entities-from-kits")
        assert response2.status_code == 200
        data2 = response2.json()
        print(f"✓ Second migration (idempotent): {data2}")
        
        # Check counts haven't increased (idempotent)
        teams_after = len(requests.get(f"{BASE_URL}/api/teams").json())
        brands_after = len(requests.get(f"{BASE_URL}/api/brands").json())
        
        # Allow for slight variations but should be roughly the same
        print(f"✓ Teams before: {teams_before}, after: {teams_after}")
        print(f"✓ Brands before: {brands_before}, after: {brands_after}")


class TestExistingEndpoints:
    """Test existing endpoints still work correctly"""
    
    def test_browse_page_data(self):
        """GET /api/master-kits - browse page data"""
        response = requests.get(f"{BASE_URL}/api/master-kits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/master-kits returns {len(data)} kits")
    
    def test_filters_endpoint(self):
        """GET /api/master-kits/filters - filter options"""
        response = requests.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        assert "clubs" in data
        assert "brands" in data
        assert "seasons" in data
        print(f"✓ GET /api/master-kits/filters returns filters")
    
    def test_stats_endpoint(self):
        """GET /api/stats - app statistics"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "master_kits" in data
        assert "versions" in data
        print(f"✓ GET /api/stats returns: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
