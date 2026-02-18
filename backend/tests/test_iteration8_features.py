"""
Test iteration 8 features:
- Updated estimation coefficients:
  - Base prices: Authentic=140€, Replica=90€, Other=60€ (new)
  - Competition coefficient: National Championship=0, National Cup=+0.05, Continental Cup=+1.0, Intercontinental Cup=+1.0, World Cup=+1.0
  - Updated Origin coefficients: Club Stock=+0.5, Match Prepared=+1.0, Match Worn=+1.5, Training=0, Shop=0
  - Updated Signed coefficient: +1.5
- Schema cleanup: Master kits no longer have year, colors, competition, source_url
- Filters endpoint returns 'seasons' instead of 'years'
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Auth token from setup
SESSION_TOKEN = "test_session_iter8_1771413715796"

@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SESSION_TOKEN}"
    })
    return session


class TestEstimationUpdatedCoefficients:
    """Test updated estimation coefficients per iteration 8 requirements"""
    
    def test_estimate_base_price_other(self, api_client):
        """Test 'Other' model type has base price 60€"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Other"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["base_price"] == 60, f"Other base price should be 60, got {data['base_price']}"
        assert data["estimated_price"] == 60.0, f"With no coefficients, Other should be 60€, got {data['estimated_price']}"
        print(f"✓ Other base price: {data['base_price']}€")
    
    def test_estimate_competition_national_championship(self, api_client):
        """Competition: National Championship = 0.0 coefficient"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "competition": "National Championship"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 0) = 90
        assert data["estimated_price"] == 90.0
        # Check breakdown has competition line with 0.0 coefficient
        comp_line = next((b for b in data["breakdown"] if "Competition" in b["label"]), None)
        assert comp_line is not None
        assert comp_line["coeff"] == 0.0
        print(f"✓ National Championship competition coeff: {comp_line['coeff']}")
    
    def test_estimate_competition_national_cup(self, api_client):
        """Competition: National Cup = +0.05 coefficient"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "competition": "National Cup"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 0.05) = 94.50
        assert data["estimated_price"] == 94.5
        comp_line = next((b for b in data["breakdown"] if "Competition" in b["label"]), None)
        assert comp_line is not None
        assert comp_line["coeff"] == 0.05
        print(f"✓ National Cup competition coeff: {comp_line['coeff']}")
    
    def test_estimate_competition_continental_cup(self, api_client):
        """Competition: Continental Cup = +1.0 coefficient"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "competition": "Continental Cup"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.0) = 180
        assert data["estimated_price"] == 180.0
        comp_line = next((b for b in data["breakdown"] if "Competition" in b["label"]), None)
        assert comp_line is not None
        assert comp_line["coeff"] == 1.0
        print(f"✓ Continental Cup competition coeff: {comp_line['coeff']}")
    
    def test_estimate_competition_intercontinental_cup(self, api_client):
        """Competition: Intercontinental Cup = +1.0 coefficient"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "competition": "Intercontinental Cup"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.0) = 180
        assert data["estimated_price"] == 180.0
        comp_line = next((b for b in data["breakdown"] if "Competition" in b["label"]), None)
        assert comp_line is not None
        assert comp_line["coeff"] == 1.0
        print(f"✓ Intercontinental Cup competition coeff: {comp_line['coeff']}")
    
    def test_estimate_competition_world_cup(self, api_client):
        """Competition: World Cup = +1.0 coefficient"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "competition": "World Cup"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.0) = 180
        assert data["estimated_price"] == 180.0
        comp_line = next((b for b in data["breakdown"] if "Competition" in b["label"]), None)
        assert comp_line is not None
        assert comp_line["coeff"] == 1.0
        print(f"✓ World Cup competition coeff: {comp_line['coeff']}")
    
    def test_estimate_origin_club_stock_updated(self, api_client):
        """Origin: Club Stock = +0.5 coefficient (was 0.2)"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "condition_origin": "Club Stock"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 0.5) = 135
        assert data["estimated_price"] == 135.0
        origin_line = next((b for b in data["breakdown"] if "Origin" in b["label"]), None)
        assert origin_line is not None
        assert origin_line["coeff"] == 0.5, f"Club Stock should be 0.5, got {origin_line['coeff']}"
        print(f"✓ Club Stock origin coeff: {origin_line['coeff']}")
    
    def test_estimate_origin_match_prepared_updated(self, api_client):
        """Origin: Match Prepared = +1.0 coefficient (was 0.5)"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "condition_origin": "Match Prepared"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.0) = 180
        assert data["estimated_price"] == 180.0
        origin_line = next((b for b in data["breakdown"] if "Origin" in b["label"]), None)
        assert origin_line is not None
        assert origin_line["coeff"] == 1.0, f"Match Prepared should be 1.0, got {origin_line['coeff']}"
        print(f"✓ Match Prepared origin coeff: {origin_line['coeff']}")
    
    def test_estimate_origin_match_worn_updated(self, api_client):
        """Origin: Match Worn = +1.5 coefficient (was 1.0)"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "condition_origin": "Match Worn"
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.5) = 225
        assert data["estimated_price"] == 225.0
        origin_line = next((b for b in data["breakdown"] if "Origin" in b["label"]), None)
        assert origin_line is not None
        assert origin_line["coeff"] == 1.5, f"Match Worn should be 1.5, got {origin_line['coeff']}"
        print(f"✓ Match Worn origin coeff: {origin_line['coeff']}")
    
    def test_estimate_signed_updated(self, api_client):
        """Signed = +1.5 coefficient (was 1.0)"""
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Replica",
            "signed": True,
            "signed_proof": False
        })
        assert response.status_code == 200
        data = response.json()
        # Base 90 * (1 + 1.5) = 225
        assert data["estimated_price"] == 225.0
        signed_line = next((b for b in data["breakdown"] if b["label"] == "Signed"), None)
        assert signed_line is not None
        assert signed_line["coeff"] == 1.5, f"Signed should be 1.5, got {signed_line['coeff']}"
        print(f"✓ Signed coeff: {signed_line['coeff']}")
    
    def test_full_estimate_scenario_1(self, api_client):
        """
        Test case from problem statement:
        Authentic + Continental Cup + Match Worn + New with tag + Official + Signed + Proof + 2020 = 945.00€
        
        Calculation:
        Base: 140 (Authentic)
        Competition (Continental Cup): +1.0
        Origin (Match Worn): +1.5
        State (New with tag): +0.3
        Flocking (Official): +0.15
        Signed: +1.5
        Proof: +1.0
        Age (2026-2020=6 years * 0.05): +0.3
        Total coeff: 1.0 + 1.5 + 0.3 + 0.15 + 1.5 + 1.0 + 0.3 = 5.75
        Price: 140 * (1 + 5.75) = 140 * 6.75 = 945.00€
        """
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Authentic",
            "competition": "Continental Cup",
            "condition_origin": "Match Worn",
            "physical_state": "New with tag",
            "flocking_origin": "Official",
            "signed": True,
            "signed_proof": True,
            "season_year": 2020
        })
        assert response.status_code == 200
        data = response.json()
        assert data["base_price"] == 140
        assert data["estimated_price"] == 945.0, f"Expected 945.00€, got {data['estimated_price']}"
        print(f"✓ Full estimate scenario 1: {data['estimated_price']}€")
        # Verify breakdown
        print(f"  Breakdown: {data['breakdown']}")
    
    def test_full_estimate_scenario_2(self, api_client):
        """
        Test case 2:
        Other + National Championship + Shop + Used + not signed + 2025 = 63.00€
        
        Calculation:
        Base: 60 (Other)
        Competition (National Championship): 0.0
        Origin (Shop): 0.0
        State (Used): 0.0
        Flocking: none → 0.0
        Age (2026-2025=1 year * 0.05): +0.05
        Total coeff: 0.05
        Price: 60 * (1 + 0.05) = 63.00€
        """
        response = api_client.post(f"{BASE_URL}/api/estimate", json={
            "model_type": "Other",
            "competition": "National Championship",
            "condition_origin": "Shop",
            "physical_state": "Used",
            "signed": False,
            "season_year": 2025
        })
        assert response.status_code == 200
        data = response.json()
        assert data["base_price"] == 60
        assert data["estimated_price"] == 63.0, f"Expected 63.00€, got {data['estimated_price']}"
        print(f"✓ Full estimate scenario 2: {data['estimated_price']}€")


class TestSchemaCleanup:
    """Test that master_kits no longer have deprecated fields"""
    
    def test_master_kits_no_year_field(self, api_client):
        """Verify kits don't have 'year' field"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        if len(kits) > 0:
            for kit in kits:
                assert "year" not in kit or kit.get("year") is None, f"Kit {kit.get('kit_id')} still has 'year' field"
            print(f"✓ No 'year' field in {len(kits)} kits checked")
        else:
            pytest.skip("No kits in database to verify")
    
    def test_master_kits_no_colors_field(self, api_client):
        """Verify kits don't have 'colors' field"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        if len(kits) > 0:
            for kit in kits:
                assert "colors" not in kit or kit.get("colors") is None, f"Kit {kit.get('kit_id')} still has 'colors' field"
            print(f"✓ No 'colors' field in {len(kits)} kits checked")
        else:
            pytest.skip("No kits in database to verify")
    
    def test_master_kits_no_competition_field(self, api_client):
        """Verify master kits don't have 'competition' field (moved to version level)"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        if len(kits) > 0:
            for kit in kits:
                # competition field should not exist at master kit level (it's now on versions)
                assert "competition" not in kit or kit.get("competition") is None, f"Kit {kit.get('kit_id')} still has 'competition' field"
            print(f"✓ No 'competition' field in {len(kits)} master kits checked")
        else:
            pytest.skip("No kits in database to verify")
    
    def test_master_kits_no_source_url_field(self, api_client):
        """Verify kits don't have 'source_url' field"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        if len(kits) > 0:
            for kit in kits:
                assert "source_url" not in kit or kit.get("source_url") is None, f"Kit {kit.get('kit_id')} still has 'source_url' field"
            print(f"✓ No 'source_url' field in {len(kits)} kits checked")
        else:
            pytest.skip("No kits in database to verify")
    
    def test_master_kits_have_new_fields(self, api_client):
        """Verify kits have the new fields: design, sponsor, league, gender"""
        response = api_client.get(f"{BASE_URL}/api/master-kits?limit=5")
        assert response.status_code == 200
        kits = response.json()
        if len(kits) > 0:
            kit = kits[0]
            # These fields should exist (even if empty)
            assert "design" in kit, "Kit missing 'design' field"
            assert "sponsor" in kit, "Kit missing 'sponsor' field"
            assert "league" in kit, "Kit missing 'league' field"
            assert "gender" in kit, "Kit missing 'gender' field"
            print(f"✓ Kit has new fields: design='{kit.get('design')}', sponsor='{kit.get('sponsor')}', league='{kit.get('league')}', gender='{kit.get('gender')}'")
        else:
            pytest.skip("No kits in database to verify")


class TestFiltersEndpoint:
    """Test filters endpoint returns seasons instead of years"""
    
    def test_filters_has_seasons_not_years(self, api_client):
        """GET /api/master-kits/filters should return 'seasons' array, not 'years'"""
        response = api_client.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        
        # Should have 'seasons' key
        assert "seasons" in data, "Filters response missing 'seasons' key"
        
        # Should NOT have 'years' key
        assert "years" not in data, "Filters response should not have 'years' key anymore"
        
        print(f"✓ Filters endpoint has 'seasons' array with {len(data['seasons'])} items")
        if data['seasons']:
            print(f"  Sample seasons: {data['seasons'][:3]}")
    
    def test_seasons_sorted_descending(self, api_client):
        """Seasons should be sorted in descending order"""
        response = api_client.get(f"{BASE_URL}/api/master-kits/filters")
        assert response.status_code == 200
        data = response.json()
        
        seasons = data.get("seasons", [])
        if len(seasons) > 1:
            # Check that seasons are in descending order
            assert seasons == sorted(seasons, reverse=True), "Seasons not sorted in descending order"
            print(f"✓ Seasons sorted descending: {seasons[0]} > {seasons[-1]}")
        else:
            pytest.skip("Not enough seasons to verify sorting")


class TestVersionCompetitionEnum:
    """Test version competition enum values"""
    
    def test_create_version_with_valid_competitions(self, api_client):
        """Create versions with all valid competition enum values"""
        valid_competitions = [
            "National Championship",
            "National Cup", 
            "Continental Cup",
            "Intercontinental Cup",
            "World Cup"
        ]
        
        # First get an existing kit
        kits_response = api_client.get(f"{BASE_URL}/api/master-kits?limit=1")
        assert kits_response.status_code == 200
        kits = kits_response.json()
        
        if not kits:
            pytest.skip("No kits available to create version")
        
        kit_id = kits[0]["kit_id"]
        
        # Test each competition value
        for competition in valid_competitions:
            response = api_client.post(f"{BASE_URL}/api/versions", json={
                "kit_id": kit_id,
                "competition": competition,
                "model": "Replica"
            })
            assert response.status_code == 200, f"Failed to create version with competition '{competition}': {response.text}"
            version = response.json()
            assert version["competition"] == competition
            print(f"✓ Created version with competition: {competition}")


class TestVersionModelEnum:
    """Test version model enum includes 'Other'"""
    
    def test_create_version_with_other_model(self, api_client):
        """Create version with 'Other' model type"""
        # First get an existing kit
        kits_response = api_client.get(f"{BASE_URL}/api/master-kits?limit=1")
        assert kits_response.status_code == 200
        kits = kits_response.json()
        
        if not kits:
            pytest.skip("No kits available to create version")
        
        kit_id = kits[0]["kit_id"]
        
        response = api_client.post(f"{BASE_URL}/api/versions", json={
            "kit_id": kit_id,
            "competition": "National Championship",
            "model": "Other"
        })
        assert response.status_code == 200, f"Failed to create version with model 'Other': {response.text}"
        version = response.json()
        assert version["model"] == "Other"
        print(f"✓ Created version with model: Other")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
