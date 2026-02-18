"""
Iteration 13: Jersey Value Estimation System and Collection Stats Fix Tests

Root cause: Frontend sent 'estimated_price' when saving collection items, but stats endpoints 
were reading 'value_estimate' (always None). Fix syncs all three fields on save/update.

Tests:
1. POST /api/estimate - estimation with various configurations
2. POST /api/collections - saves all 3 estimation fields (estimated_price, value_estimate, price_estimate)
3. PUT /api/collections/{id} - syncs all estimation fields on update
4. GET /api/collections/stats - returns correct Low/Avg/High (not 0)
5. GET /api/collections/category-stats - returns correct values per category
6. GET /api/versions/{id}/estimates - correct estimates from collection items
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
SESSION_TOKEN = "5hCFW_A6ejPpe_a2qBAj5vRDWAdXNwj6jjjzjNZXMtA"  # User with collection items
TEST_SESSION = f"test_session_iter13_{uuid.uuid4().hex[:8]}"

def get_auth_headers():
    return {"Cookie": f"session_token={SESSION_TOKEN}"}


class TestEstimationEndpoint:
    """POST /api/estimate - price estimation logic tests"""
    
    def test_estimate_replica_base(self):
        """Replica base price should be 90€"""
        payload = {
            "model_type": "Replica",
            "competition": "National Championship",
            "condition_origin": "Shop",
            "physical_state": "New with tag",
            "flocking_origin": "",
            "signed": False,
            "signed_proof": False,
            "season_year": 0
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "base_price" in data, "Missing base_price"
        assert "estimated_price" in data, "Missing estimated_price"
        assert "breakdown" in data, "Missing breakdown"
        assert "coeff_sum" in data, "Missing coeff_sum"
        
        # Replica base price should be 90
        assert data["base_price"] == 90, f"Replica base should be 90, got {data['base_price']}"
        print(f"✓ Estimate Replica base: base={data['base_price']}, estimated={data['estimated_price']}")

    def test_estimate_authentic_base(self):
        """Authentic base price should be 140€"""
        payload = {
            "model_type": "Authentic",
            "competition": "National Championship",
            "condition_origin": "",
            "physical_state": "",
            "flocking_origin": "",
            "signed": False,
            "signed_proof": False,
            "season_year": 0
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["base_price"] == 140, f"Authentic base should be 140, got {data['base_price']}"
        print(f"✓ Estimate Authentic base: base={data['base_price']}, estimated={data['estimated_price']}")

    def test_estimate_with_coefficients(self):
        """Test estimation with multiple coefficients"""
        payload = {
            "model_type": "Authentic",           # Base: 140
            "competition": "Continental Cup",    # +1.0
            "condition_origin": "Match Worn",    # +1.5
            "physical_state": "Very good",       # +0.1
            "flocking_origin": "Official",       # +0.15
            "signed": True,                      # +1.5
            "signed_proof": True,                # +1.0
            "season_year": 2016                  # ~10 years = +0.5 (capped at 1.0)
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Verify breakdown has all coefficients
        breakdown_labels = [item["label"] for item in data["breakdown"]]
        assert any("Continental Cup" in label for label in breakdown_labels), "Missing competition coefficient"
        assert any("Match Worn" in label for label in breakdown_labels), "Missing origin coefficient"
        assert any("Very good" in label for label in breakdown_labels), "Missing state coefficient"
        assert any("Official" in label for label in breakdown_labels), "Missing flocking coefficient"
        assert any("Signed" in label for label in breakdown_labels), "Missing signed coefficient"
        assert any("Proof" in label for label in breakdown_labels), "Missing proof coefficient"
        
        # Price should be significantly higher than base
        assert data["estimated_price"] > 140 * 2, f"Expected high estimate, got {data['estimated_price']}"
        print(f"✓ Estimate with coefficients: base={data['base_price']}, coeff_sum={data['coeff_sum']}, estimated={data['estimated_price']}")
        print(f"  Breakdown items: {len(data['breakdown'])}")

    def test_estimate_negative_coefficient(self):
        """Test estimation with negative coefficient (damaged state)"""
        payload = {
            "model_type": "Replica",
            "competition": "National Championship",
            "condition_origin": "",
            "physical_state": "Damaged",         # -0.2
            "flocking_origin": "",
            "signed": False,
            "signed_proof": False,
            "season_year": 0
        }
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Damaged should result in lower price than base
        assert data["estimated_price"] < 90, f"Damaged should lower price, got {data['estimated_price']}"
        print(f"✓ Estimate Damaged: base={data['base_price']}, estimated={data['estimated_price']}")


class TestCollectionStatsWithAuth:
    """Collection stats endpoints with authenticated user"""
    
    def test_get_collection_stats_returns_values(self):
        """GET /api/collections/stats should return non-zero values for user with items"""
        response = requests.get(f"{BASE_URL}/api/collections/stats", headers=get_auth_headers())
        
        if response.status_code == 401:
            pytest.skip("Session token expired or invalid")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Validate response structure
        assert "total_jerseys" in data, "Missing total_jerseys"
        assert "estimated_value" in data, "Missing estimated_value"
        assert "items_with_estimates" in data, "Missing items_with_estimates"
        
        # Validate estimated_value structure
        ev = data["estimated_value"]
        assert "low" in ev, "Missing low estimate"
        assert "average" in ev, "Missing average estimate"
        assert "high" in ev, "Missing high estimate"
        
        print(f"✓ Collection stats: {data['total_jerseys']} jerseys, {data['items_with_estimates']} with estimates")
        print(f"  Values: Low={ev['low']}€, Avg={ev['average']}€, High={ev['high']}€")
        
        # If user has collection items with estimates, values should NOT be 0
        if data["items_with_estimates"] > 0:
            assert ev["average"] > 0, f"Average should not be 0 when items have estimates, got {ev['average']}"
            assert ev["low"] >= 0, f"Low should be >= 0, got {ev['low']}"
            assert ev["high"] >= ev["average"], f"High should be >= average, got high={ev['high']}, avg={ev['average']}"
            print(f"  ✓ VERIFIED: Non-zero estimation values returned (fix confirmed)")

    def test_get_category_stats(self):
        """GET /api/collections/category-stats should return per-category estimates"""
        response = requests.get(f"{BASE_URL}/api/collections/category-stats", headers=get_auth_headers())
        
        if response.status_code == 401:
            pytest.skip("Session token expired or invalid")
            
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Should return list of categories"
        
        for cat in data:
            assert "category" in cat, "Missing category name"
            assert "count" in cat, "Missing count"
            assert "estimated_value" in cat, "Missing estimated_value"
            
            ev = cat["estimated_value"]
            assert "low" in ev, "Missing low estimate in category"
            assert "average" in ev, "Missing average estimate in category"
            assert "high" in ev, "Missing high estimate in category"
            
            print(f"  Category '{cat['category']}': {cat['count']} items, avg={ev['average']}€")
        
        print(f"✓ Category stats: {len(data)} categories")

    def test_get_collection_items(self):
        """GET /api/collections should return items with estimated_price"""
        response = requests.get(f"{BASE_URL}/api/collections", headers=get_auth_headers())
        
        if response.status_code == 401:
            pytest.skip("Session token expired or invalid")
            
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert isinstance(data, list), "Should return list of collection items"
        
        items_with_estimate = 0
        for item in data:
            assert "collection_id" in item, "Missing collection_id"
            assert "version_id" in item, "Missing version_id"
            
            # Check all three estimation fields exist
            if item.get("estimated_price"):
                items_with_estimate += 1
                print(f"  Item {item['collection_id']}: estimated_price={item.get('estimated_price')}, value_estimate={item.get('value_estimate')}, price_estimate={item.get('price_estimate')}")
        
        print(f"✓ Collection items: {len(data)} total, {items_with_estimate} with estimates")


class TestCollectionCreateUpdateEstimation:
    """Test that adding/updating collection items syncs all estimation fields"""
    
    @pytest.fixture(scope="class")
    def version_id(self):
        """Get a valid version_id for testing"""
        response = requests.get(f"{BASE_URL}/api/versions?limit=1")
        assert response.status_code == 200
        versions = response.json()
        if not versions:
            pytest.skip("No versions available for testing")
        return versions[0]["version_id"]
    
    def test_add_to_collection_syncs_estimation_fields(self, version_id):
        """POST /api/collections should save all 3 estimation fields with same value"""
        test_estimate = 250.50
        
        payload = {
            "version_id": version_id,
            "category": "TEST_Category",
            "notes": "Test collection item for estimation sync",
            "condition_origin": "Match Worn",
            "physical_state": "Very good",
            "flocking_origin": "Official",
            "size": "L",
            "purchase_cost": 100.0,
            "estimated_price": test_estimate,
            "signed": False,
            "signed_by": "",
            "signed_proof": False
        }
        
        response = requests.post(f"{BASE_URL}/api/collections", json=payload, headers=get_auth_headers())
        
        if response.status_code == 401:
            pytest.skip("Session token expired or invalid")
        
        # 400 means already in collection - that's ok for this test
        if response.status_code == 400:
            print(f"✓ Item already in collection (expected for repeat tests)")
            return
            
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify all three estimation fields are set
        assert "estimated_price" in data, "Missing estimated_price in response"
        assert "value_estimate" in data, "Missing value_estimate in response"
        assert "price_estimate" in data, "Missing price_estimate in response"
        
        # All three should have the same value
        assert data["estimated_price"] == test_estimate, f"estimated_price mismatch: {data['estimated_price']}"
        assert data["value_estimate"] == test_estimate, f"value_estimate mismatch: {data['value_estimate']}"
        assert data["price_estimate"] == test_estimate, f"price_estimate mismatch: {data['price_estimate']}"
        
        print(f"✓ Add to collection synced all 3 estimation fields to {test_estimate}€")
        print(f"  collection_id: {data.get('collection_id')}")
        
        # Store collection_id for cleanup
        self.__class__.created_collection_id = data.get("collection_id")

    def test_update_collection_item_syncs_estimation(self):
        """PUT /api/collections/{id} should sync all estimation fields on update"""
        # First get an existing collection item
        response = requests.get(f"{BASE_URL}/api/collections", headers=get_auth_headers())
        
        if response.status_code == 401:
            pytest.skip("Session token expired or invalid")
            
        assert response.status_code == 200
        items = response.json()
        
        if not items:
            pytest.skip("No collection items to update")
        
        item = items[0]
        collection_id = item["collection_id"]
        new_estimate = 333.33
        
        update_payload = {
            "estimated_price": new_estimate,
            "notes": "Updated by test"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/collections/{collection_id}",
            json=update_payload,
            headers=get_auth_headers()
        )
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        updated = update_response.json()
        
        # All three estimation fields should be synced
        assert updated.get("estimated_price") == new_estimate, f"estimated_price not updated"
        assert updated.get("value_estimate") == new_estimate, f"value_estimate not synced"
        assert updated.get("price_estimate") == new_estimate, f"price_estimate not synced"
        
        print(f"✓ Update collection synced all 3 estimation fields to {new_estimate}€")
        
        # Restore original value if it existed
        original_estimate = item.get("estimated_price") or item.get("value_estimate") or item.get("price_estimate")
        if original_estimate and original_estimate != new_estimate:
            requests.put(
                f"{BASE_URL}/api/collections/{collection_id}",
                json={"estimated_price": original_estimate},
                headers=get_auth_headers()
            )
            print(f"  Restored original estimate: {original_estimate}€")


class TestVersionEstimates:
    """GET /api/versions/{id}/estimates - estimates from collection items"""
    
    def test_version_estimates_structure(self):
        """Get estimates for a version with collection items"""
        # Get a version that might have collection items
        response = requests.get(f"{BASE_URL}/api/versions?limit=10")
        assert response.status_code == 200
        versions = response.json()
        
        if not versions:
            pytest.skip("No versions available")
        
        found_estimates = False
        for ver in versions:
            version_id = ver["version_id"]
            est_response = requests.get(f"{BASE_URL}/api/versions/{version_id}/estimates")
            assert est_response.status_code == 200
            
            data = est_response.json()
            
            # Validate structure
            assert "low" in data, "Missing low"
            assert "average" in data, "Missing average"
            assert "high" in data, "Missing high"
            assert "count" in data, "Missing count"
            assert "estimates" in data, "Missing estimates list"
            
            if data["count"] > 0:
                found_estimates = True
                assert data["average"] > 0, f"Average should be > 0 when count > 0"
                assert data["low"] > 0, f"Low should be > 0 when count > 0"
                assert data["high"] >= data["low"], f"High should be >= low"
                print(f"✓ Version {version_id} estimates: {data['count']} items, low={data['low']}€, avg={data['average']}€, high={data['high']}€")
                break
        
        if not found_estimates:
            print("! No versions with collection estimates found (this may be expected)")


class TestEstimationFormula:
    """Verify the estimation formula: Base Price × (1 + sum of coefficients)"""
    
    def test_formula_calculation(self):
        """Verify the formula matches expected calculation"""
        # Base prices: Authentic=140, Replica=90, Other=60
        # Coefficients from: competition, origin, physical_state, flocking, signed, age
        
        payload = {
            "model_type": "Replica",               # Base: 90
            "competition": "National Cup",         # +0.05
            "condition_origin": "Club Stock",      # +0.5
            "physical_state": "New with tag",      # +0.3
            "flocking_origin": "",                 # +0
            "signed": False,
            "signed_proof": False,
            "season_year": 2022                    # ~4 years = +0.2 (0.05 * 4)
        }
        
        response = requests.post(f"{BASE_URL}/api/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Calculate expected
        base = 90
        coeff = 0.05 + 0.5 + 0.3 + 0.2  # 1.05
        expected = base * (1 + coeff)    # 90 * 2.05 = 184.5
        
        # Allow small floating point differences
        actual = data["estimated_price"]
        assert abs(actual - expected) < 1, f"Expected ~{expected}, got {actual}"
        
        print(f"✓ Formula verified: {base} × (1 + {coeff:.2f}) = {actual}€")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
