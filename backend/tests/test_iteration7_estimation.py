"""
Test suite for Iteration 7: Estimation System
Tests:
- POST /api/estimate endpoint with various scenarios
- POST /api/collections accepts estimated_price and signed_proof fields  
- PUT /api/collections/{id} accepts estimated_price and signed_proof fields
- Estimation formula verification
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test session token (will be set via environment or fixture)
SESSION_TOKEN = os.environ.get('TEST_SESSION_TOKEN', 'test_session_iter7_1771411009462')

class TestEstimationEndpoint:
    """Tests for POST /api/estimate endpoint"""
    
    def test_estimate_authentic_match_worn_full_options_2020(self):
        """
        Test Case 1: Authentic, Match Worn, New with tag, Official, Signed+Proof, 2020 season
        Expected: 665.00€
        Base: 140 (Authentic)
        Coefficients: 1.0 (Match Worn) + 0.3 (New with tag) + 0.15 (Official) + 1.0 (Signed) + 1.0 (Proof) + 0.3 (6 years * 0.05 = 0.3)
        Total coeff: 3.75
        Price: 140 * (1 + 3.75) = 140 * 4.75 = 665.00
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Authentic",
                "condition_origin": "Match Worn",
                "physical_state": "New with tag",
                "flocking_origin": "Official",
                "signed": True,
                "signed_proof": True,
                "season_year": 2020
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify structure
        assert "base_price" in data
        assert "model_type" in data
        assert "coeff_sum" in data
        assert "estimated_price" in data
        assert "breakdown" in data
        
        # Verify base price
        assert data["base_price"] == 140, f"Expected base_price 140, got {data['base_price']}"
        assert data["model_type"] == "Authentic"
        
        # Verify estimated price = 665.00
        assert data["estimated_price"] == 665.0, f"Expected 665.0, got {data['estimated_price']}"
        print(f"✓ Test 1 PASSED: Authentic, Match Worn, Full options 2020 → {data['estimated_price']}€")
    
    def test_estimate_replica_shop_used_personalized_2025(self):
        """
        Test Case 2: Replica, Shop, Used, Personalized, not signed, 2025 season
        Expected: 94.50€
        Base: 90 (Replica)
        Coefficients: 0.0 (Shop) + 0.0 (Used) + 0.0 (Personalized) + 0.05 (1 year * 0.05)
        Total coeff: 0.05
        Price: 90 * (1 + 0.05) = 90 * 1.05 = 94.50
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "Shop",
                "physical_state": "Used",
                "flocking_origin": "Personalized",
                "signed": False,
                "signed_proof": False,
                "season_year": 2025
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["base_price"] == 90
        assert data["model_type"] == "Replica"
        assert data["estimated_price"] == 94.5, f"Expected 94.5, got {data['estimated_price']}"
        print(f"✓ Test 2 PASSED: Replica, Shop, Used, Personalized 2025 → {data['estimated_price']}€")
    
    def test_estimate_replica_no_options(self):
        """
        Test Case 3: Replica, no options
        Expected: base 90€
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "",
                "physical_state": "",
                "flocking_origin": "",
                "signed": False,
                "signed_proof": False,
                "season_year": 0
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["base_price"] == 90
        assert data["estimated_price"] == 90.0, f"Expected 90.0, got {data['estimated_price']}"
        print(f"✓ Test 3 PASSED: Replica, no options → {data['estimated_price']}€")
    
    def test_estimate_authentic_no_options(self):
        """
        Test Case 4: Authentic, no options
        Expected: base 140€
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Authentic",
                "condition_origin": "",
                "physical_state": "",
                "flocking_origin": "",
                "signed": False,
                "signed_proof": False,
                "season_year": 0
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["base_price"] == 140
        assert data["estimated_price"] == 140.0, f"Expected 140.0, got {data['estimated_price']}"
        print(f"✓ Test 4 PASSED: Authentic, no options → {data['estimated_price']}€")
    
    def test_estimate_replica_club_stock_very_good_official_signed_no_proof_2015(self):
        """
        Test Case 5: Replica, Club Stock, Very good, Official, Signed no proof, 2015
        Expected: 270.00€
        Base: 90 (Replica)
        Coefficients: 0.2 (Club Stock) + 0.1 (Very good) + 0.15 (Official) + 1.0 (Signed) + 0.55 (11 years * 0.05, capped at 1.0)
        Total coeff: 0.2 + 0.1 + 0.15 + 1.0 + 0.55 = 2.0
        Price: 90 * (1 + 2.0) = 90 * 3.0 = 270.00
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "Club Stock",
                "physical_state": "Very good",
                "flocking_origin": "Official",
                "signed": True,
                "signed_proof": False,
                "season_year": 2015
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["base_price"] == 90
        assert data["model_type"] == "Replica"
        # 2026 - 2015 = 11 years, 11 * 0.05 = 0.55 (not capped)
        # Total: 0.2 + 0.1 + 0.15 + 1.0 + 0.55 = 2.0
        # 90 * 3.0 = 270
        assert data["estimated_price"] == 270.0, f"Expected 270.0, got {data['estimated_price']}"
        print(f"✓ Test 5 PASSED: Replica, Club Stock, Very good, Official, Signed no proof 2015 → {data['estimated_price']}€")
    
    def test_estimate_breakdown_contains_all_factors(self):
        """
        Verify breakdown contains all applied factors
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Authentic",
                "condition_origin": "Match Worn",
                "physical_state": "New with tag",
                "flocking_origin": "Official",
                "signed": True,
                "signed_proof": True,
                "season_year": 2020
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        breakdown_labels = [item["label"] for item in data["breakdown"]]
        
        # Should contain all factors
        assert any("Match Worn" in label for label in breakdown_labels), "Breakdown missing 'Match Worn'"
        assert any("New with tag" in label for label in breakdown_labels), "Breakdown missing 'New with tag'"
        assert any("Official" in label for label in breakdown_labels), "Breakdown missing 'Official'"
        assert any("Signed" in label for label in breakdown_labels), "Breakdown missing 'Signed'"
        assert any("Proof" in label or "Certificate" in label for label in breakdown_labels), "Breakdown missing 'Proof/Certificate'"
        assert any("Age" in label for label in breakdown_labels), "Breakdown missing 'Age'"
        print(f"✓ Test 6 PASSED: Breakdown contains all expected factors")
    
    def test_estimate_with_negative_state_coefficient(self):
        """
        Test negative coefficient: Damaged should reduce price
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "",
                "physical_state": "Damaged",
                "flocking_origin": "",
                "signed": False,
                "signed_proof": False,
                "season_year": 0
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Damaged = -0.2, so 90 * (1 - 0.2) = 90 * 0.8 = 72.0
        assert data["estimated_price"] == 72.0, f"Expected 72.0, got {data['estimated_price']}"
        print(f"✓ Test 7 PASSED: Damaged state gives negative coefficient → {data['estimated_price']}€")
    
    def test_estimate_needs_restoration(self):
        """
        Test worst state: Needs restoration (-0.4)
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "",
                "physical_state": "Needs restoration",
                "flocking_origin": "",
                "signed": False,
                "signed_proof": False,
                "season_year": 0
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Needs restoration = -0.4, so 90 * (1 - 0.4) = 90 * 0.6 = 54.0
        assert data["estimated_price"] == 54.0, f"Expected 54.0, got {data['estimated_price']}"
        print(f"✓ Test 8 PASSED: Needs restoration gives worst coefficient → {data['estimated_price']}€")
    
    def test_estimate_age_coefficient_cap(self):
        """
        Test that age coefficient is capped at 1.0 (max 20 years)
        """
        response = requests.post(
            f"{BASE_URL}/api/estimate",
            json={
                "model_type": "Replica",
                "condition_origin": "",
                "physical_state": "",
                "flocking_origin": "",
                "signed": False,
                "signed_proof": False,
                "season_year": 2000  # 26 years old
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Age = 26 years, but capped at 1.0 (26 * 0.05 = 1.3, but max 1.0)
        # 90 * (1 + 1.0) = 90 * 2.0 = 180.0
        assert data["estimated_price"] == 180.0, f"Expected 180.0 (age capped), got {data['estimated_price']}"
        
        # Check breakdown shows age coefficient at 1.0
        age_item = next((item for item in data["breakdown"] if "Age" in item["label"]), None)
        assert age_item is not None, "Age should be in breakdown"
        assert age_item["coeff"] == 1.0, f"Age coeff should be capped at 1.0, got {age_item['coeff']}"
        print(f"✓ Test 9 PASSED: Age coefficient capped at 1.0 for old jerseys → {data['estimated_price']}€")
    
    def test_estimate_all_condition_origins(self):
        """
        Test all Condition Origin values return correct coefficients
        """
        origins = {
            "Club Stock": 0.2,
            "Match Prepared": 0.5,
            "Match Worn": 1.0,
            "Training": 0.05,
            "Shop": 0.0
        }
        
        for origin, expected_coeff in origins.items():
            response = requests.post(
                f"{BASE_URL}/api/estimate",
                json={
                    "model_type": "Replica",
                    "condition_origin": origin,
                    "physical_state": "",
                    "flocking_origin": "",
                    "signed": False,
                    "signed_proof": False,
                    "season_year": 0
                }
            )
            assert response.status_code == 200
            data = response.json()
            expected_price = 90 * (1 + expected_coeff)
            assert data["estimated_price"] == expected_price, f"Origin '{origin}': expected {expected_price}, got {data['estimated_price']}"
        
        print(f"✓ Test 10 PASSED: All Condition Origins return correct coefficients")
    
    def test_estimate_all_physical_states(self):
        """
        Test all Physical State values return correct coefficients
        """
        states = {
            "New with tag": 0.3,
            "Very good": 0.1,
            "Used": 0.0,
            "Damaged": -0.2,
            "Needs restoration": -0.4
        }
        
        for state, expected_coeff in states.items():
            response = requests.post(
                f"{BASE_URL}/api/estimate",
                json={
                    "model_type": "Replica",
                    "condition_origin": "",
                    "physical_state": state,
                    "flocking_origin": "",
                    "signed": False,
                    "signed_proof": False,
                    "season_year": 0
                }
            )
            assert response.status_code == 200
            data = response.json()
            expected_price = 90 * (1 + expected_coeff)
            assert data["estimated_price"] == expected_price, f"State '{state}': expected {expected_price}, got {data['estimated_price']}"
        
        print(f"✓ Test 11 PASSED: All Physical States return correct coefficients")
    
    def test_estimate_flocking_origins(self):
        """
        Test Flocking Origin values
        """
        origins = {
            "Official": 0.15,
            "Personalized": 0.0
        }
        
        for origin, expected_coeff in origins.items():
            response = requests.post(
                f"{BASE_URL}/api/estimate",
                json={
                    "model_type": "Replica",
                    "condition_origin": "",
                    "physical_state": "",
                    "flocking_origin": origin,
                    "signed": False,
                    "signed_proof": False,
                    "season_year": 0
                }
            )
            assert response.status_code == 200
            data = response.json()
            expected_price = 90 * (1 + expected_coeff)
            assert data["estimated_price"] == expected_price, f"Flocking '{origin}': expected {expected_price}, got {data['estimated_price']}"
        
        print(f"✓ Test 12 PASSED: Flocking Origins return correct coefficients")


class TestCollectionEstimationFields:
    """Tests for estimated_price and signed_proof fields in collections"""
    
    @pytest.fixture
    def session(self):
        s = requests.Session()
        s.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SESSION_TOKEN}"
        })
        return s
    
    @pytest.fixture
    def test_version_id(self, session):
        """Get a version ID from existing data"""
        # Get master kits first
        response = session.get(f"{BASE_URL}/api/master-kits?limit=1")
        if response.status_code == 200 and response.json():
            kit = response.json()[0]
            kit_id = kit["kit_id"]
            # Get versions for this kit
            kit_detail = session.get(f"{BASE_URL}/api/master-kits/{kit_id}")
            if kit_detail.status_code == 200:
                kit_data = kit_detail.json()
                if kit_data.get("versions"):
                    return kit_data["versions"][0]["version_id"]
        return None
    
    def test_post_collection_accepts_estimated_price(self, session, test_version_id):
        """
        POST /api/collections accepts estimated_price field
        """
        if not test_version_id:
            pytest.skip("No version available for testing")
        
        # First, try to delete existing collection item for this version
        col_response = session.get(f"{BASE_URL}/api/collections")
        if col_response.status_code == 200:
            items = col_response.json()
            for item in items:
                if item.get("version_id") == test_version_id:
                    session.delete(f"{BASE_URL}/api/collections/{item['collection_id']}")
        
        response = session.post(
            f"{BASE_URL}/api/collections",
            json={
                "version_id": test_version_id,
                "estimated_price": 250.50,
                "signed_proof": True,
                "signed": True,
                "signed_by": "Messi",
                "condition_origin": "Match Worn",
                "physical_state": "New with tag",
                "flocking_origin": "Official"
            }
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data.get("estimated_price") == 250.50, f"estimated_price not saved: {data}"
        assert data.get("signed_proof") == True, f"signed_proof not saved: {data}"
        
        # Clean up
        if data.get("collection_id"):
            session.delete(f"{BASE_URL}/api/collections/{data['collection_id']}")
        
        print(f"✓ Test 13 PASSED: POST /api/collections accepts estimated_price and signed_proof fields")
    
    def test_put_collection_accepts_estimated_price(self, session, test_version_id):
        """
        PUT /api/collections/{id} accepts estimated_price and signed_proof fields
        """
        if not test_version_id:
            pytest.skip("No version available for testing")
        
        # Clean up any existing item for this version
        col_response = session.get(f"{BASE_URL}/api/collections")
        if col_response.status_code == 200:
            items = col_response.json()
            for item in items:
                if item.get("version_id") == test_version_id:
                    session.delete(f"{BASE_URL}/api/collections/{item['collection_id']}")
        
        # Create a collection item first
        create_response = session.post(
            f"{BASE_URL}/api/collections",
            json={
                "version_id": test_version_id,
                "estimated_price": 100.0,
                "signed_proof": False,
                "signed": False
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip(f"Could not create collection item: {create_response.text}")
        
        collection_id = create_response.json().get("collection_id")
        
        # Now update with new estimated_price and signed_proof
        update_response = session.put(
            f"{BASE_URL}/api/collections/{collection_id}",
            json={
                "estimated_price": 500.75,
                "signed_proof": True,
                "signed": True,
                "signed_by": "Ronaldo"
            }
        )
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        data = update_response.json()
        
        assert data.get("estimated_price") == 500.75, f"estimated_price not updated: {data}"
        assert data.get("signed_proof") == True, f"signed_proof not updated: {data}"
        
        # Clean up
        session.delete(f"{BASE_URL}/api/collections/{collection_id}")
        
        print(f"✓ Test 14 PASSED: PUT /api/collections/{collection_id} accepts estimated_price and signed_proof fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
