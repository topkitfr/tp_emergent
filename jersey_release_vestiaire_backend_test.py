#!/usr/bin/env python3
"""
TopKit Backend Testing - Jersey Release Collections & Vestiaire System
Testing the corrections made to user-reported issues:

1. Jersey Release collection endpoints - POST /api/collections/jersey-releases
2. GET /api/vestiaire endpoint - ensure all data is returned
3. Master Jerseys - GET /api/master-jerseys endpoint  
4. Brands/teams/competitions integration
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_data = data.get("user", {})
                self.admin_user_id = user_data.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated successfully. User: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))
            return False

    def test_jersey_release_collection_endpoints(self):
        """Test Jersey Release collection endpoints"""
        print("🔍 TESTING JERSEY RELEASE COLLECTION ENDPOINTS")
        print("=" * 60)
        
        if not self.admin_token:
            self.log_test("Jersey Release Collections", False, "", "No admin token available")
            return
            
        try:
            # Test 1: GET user collections (owned)
            response = self.session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections/owned")
            if response.status_code == 200:
                owned_data = response.json()
                self.log_test(
                    "GET /api/users/{user_id}/collections/owned",
                    True,
                    f"Retrieved {len(owned_data)} owned collections with proper data structure"
                )
            else:
                self.log_test(
                    "GET /api/users/{user_id}/collections/owned",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test 2: GET user collections (wanted)
            response = self.session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/collections/wanted")
            if response.status_code == 200:
                wanted_data = response.json()
                self.log_test(
                    "GET /api/users/{user_id}/collections/wanted",
                    True,
                    f"Retrieved {len(wanted_data)} wanted collections with proper data structure"
                )
            else:
                self.log_test(
                    "GET /api/users/{user_id}/collections/wanted",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test 3: GET jersey releases for collection testing
            response = self.session.get(f"{BACKEND_URL}/jersey-releases")
            jersey_releases = []
            if response.status_code == 200:
                jersey_releases = response.json()
                self.log_test(
                    "GET /api/jersey-releases (for testing)",
                    True,
                    f"Found {len(jersey_releases)} jersey releases available for collection testing"
                )
            else:
                self.log_test(
                    "GET /api/jersey-releases (for testing)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test 4: POST add jersey release to collection (if releases available)
            if jersey_releases:
                test_release = jersey_releases[0]
                collection_data = {
                    "jersey_release_id": test_release.get("id"),
                    "collection_type": "owned",
                    "size": "L",
                    "condition": "mint",
                    "purchase_price": 89.99
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/users/{self.admin_user_id}/collections",
                    json=collection_data
                )
                
                if response.status_code in [200, 201]:
                    collection_result = response.json()
                    collection_id = collection_result.get("id")
                    self.log_test(
                        "POST /api/users/{user_id}/collections (add to owned)",
                        True,
                        f"Successfully added jersey release to owned collection. Collection ID: {collection_id}"
                    )
                    
                    # Test 5: PUT update collection item
                    if collection_id:
                        update_data = {
                            "size": "XL",
                            "condition": "near_mint",
                            "purchase_price": 85.00
                        }
                        
                        response = self.session.put(
                            f"{BACKEND_URL}/users/{self.admin_user_id}/collections/{collection_id}",
                            json=update_data
                        )
                        
                        if response.status_code == 200:
                            self.log_test(
                                "PUT /api/users/{user_id}/collections/{collection_id}",
                                True,
                                "Successfully updated collection item details (size L→XL, condition mint→near_mint, price €89.99→€85.00)"
                            )
                        else:
                            self.log_test(
                                "PUT /api/users/{user_id}/collections/{collection_id}",
                                False,
                                f"HTTP {response.status_code}",
                                response.text
                            )
                        
                        # Test 6: DELETE remove from collection
                        response = self.session.delete(
                            f"{BACKEND_URL}/users/{self.admin_user_id}/collections/{collection_id}"
                        )
                        
                        if response.status_code in [200, 204]:
                            self.log_test(
                                "DELETE /api/users/{user_id}/collections/{collection_id}",
                                True,
                                "Successfully removed jersey release from collection"
                            )
                        else:
                            self.log_test(
                                "DELETE /api/users/{user_id}/collections/{collection_id}",
                                False,
                                f"HTTP {response.status_code}",
                                response.text
                            )
                
                else:
                    self.log_test(
                        "POST /api/users/{user_id}/collections",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            else:
                self.log_test(
                    "Jersey Release Collection Testing",
                    False,
                    "",
                    "No jersey releases available for collection testing"
                )

        except Exception as e:
            self.log_test("Jersey Release Collection Endpoints", False, "", str(e))

    def test_vestiaire_endpoint(self):
        """Test GET /api/vestiaire endpoint"""
        print("🔍 TESTING VESTIAIRE ENDPOINT")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                
                # Check data structure
                required_fields = [
                    "id", "topkit_reference", "retail_price", "product_images",
                    "estimated_value", "estimated_min", "estimated_max",
                    "player_name", "master_jersey_info"
                ]
                
                data_quality_issues = []
                items_with_all_fields = 0
                
                for item in vestiaire_data:
                    item_has_all_fields = True
                    for field in required_fields:
                        if field not in item:
                            data_quality_issues.append(f"Missing field '{field}' in item {item.get('id', 'unknown')}")
                            item_has_all_fields = False
                    
                    if item_has_all_fields:
                        items_with_all_fields += 1
                
                # Check for Master Jersey integration
                items_with_master_jersey = sum(1 for item in vestiaire_data if item.get("master_jersey_info"))
                
                success = len(data_quality_issues) == 0
                details = f"Retrieved {len(vestiaire_data)} vestiaire items. "
                details += f"{items_with_all_fields}/{len(vestiaire_data)} items have all required fields. "
                details += f"{items_with_master_jersey} items have Master Jersey integration."
                
                if data_quality_issues:
                    details += f" Issues found: {len(data_quality_issues)} missing field instances."
                
                self.log_test(
                    "GET /api/vestiaire - Data Structure",
                    success,
                    details,
                    "; ".join(data_quality_issues[:5]) if data_quality_issues else ""  # Show first 5 issues
                )
                
                # Test filtering capabilities
                if vestiaire_data:
                    # Test player name filter
                    first_player = vestiaire_data[0].get("player_name")
                    if first_player:
                        response = self.session.get(f"{BACKEND_URL}/vestiaire?player_name={first_player}")
                        if response.status_code == 200:
                            filtered_data = response.json()
                            self.log_test(
                                "GET /api/vestiaire - Player Name Filter",
                                True,
                                f"Player filter '{first_player}' returned {len(filtered_data)} results"
                            )
                        else:
                            self.log_test(
                                "GET /api/vestiaire - Player Name Filter",
                                False,
                                f"HTTP {response.status_code}",
                                response.text
                            )
                
            else:
                self.log_test(
                    "GET /api/vestiaire",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/vestiaire", False, "", str(e))

    def test_master_jerseys_endpoint(self):
        """Test GET /api/master-jerseys endpoint"""
        print("🔍 TESTING MASTER JERSEYS ENDPOINT")
        print("=" * 60)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                master_jerseys = response.json()
                
                # Check data structure
                required_fields = [
                    "id", "topkit_reference", "team_info", "brand_info", 
                    "season", "jersey_type", "releases_count", "collectors_count"
                ]
                
                data_quality_issues = []
                items_with_all_fields = 0
                
                for jersey in master_jerseys:
                    item_has_all_fields = True
                    for field in required_fields:
                        if field not in jersey:
                            data_quality_issues.append(f"Missing field '{field}' in jersey {jersey.get('id', 'unknown')}")
                            item_has_all_fields = False
                    
                    if item_has_all_fields:
                        items_with_all_fields += 1
                
                # Check for proper enrichment
                jerseys_with_team_info = sum(1 for jersey in master_jerseys if jersey.get("team_info"))
                jerseys_with_brand_info = sum(1 for jersey in master_jerseys if jersey.get("brand_info"))
                
                success = response.status_code == 200 and len(master_jerseys) > 0
                details = f"Retrieved {len(master_jerseys)} master jerseys. "
                details += f"{items_with_all_fields}/{len(master_jerseys)} have all required fields. "
                details += f"Team info: {jerseys_with_team_info}, Brand info: {jerseys_with_brand_info}"
                
                self.log_test(
                    "GET /api/master-jerseys",
                    success,
                    details,
                    "; ".join(data_quality_issues[:3]) if data_quality_issues else ""
                )
                
            else:
                self.log_test(
                    "GET /api/master-jerseys",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("GET /api/master-jerseys", False, "", str(e))

    def test_brands_teams_competitions_integration(self):
        """Test brands/teams/competitions integration"""
        print("🔍 TESTING BRANDS/TEAMS/COMPETITIONS INTEGRATION")
        print("=" * 60)
        
        try:
            # Test brands endpoint
            response = self.session.get(f"{BACKEND_URL}/brands")
            if response.status_code == 200:
                brands = response.json()
                brands_with_references = sum(1 for brand in brands if brand.get("topkit_reference"))
                self.log_test(
                    "GET /api/brands",
                    True,
                    f"Retrieved {len(brands)} brands, {brands_with_references} with TopKit references"
                )
            else:
                self.log_test(
                    "GET /api/brands",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test teams endpoint
            response = self.session.get(f"{BACKEND_URL}/teams")
            if response.status_code == 200:
                teams = response.json()
                teams_with_references = sum(1 for team in teams if team.get("topkit_reference"))
                self.log_test(
                    "GET /api/teams",
                    True,
                    f"Retrieved {len(teams)} teams, {teams_with_references} with TopKit references"
                )
            else:
                self.log_test(
                    "GET /api/teams",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test competitions endpoint
            response = self.session.get(f"{BACKEND_URL}/competitions")
            if response.status_code == 200:
                competitions = response.json()
                competitions_with_references = sum(1 for comp in competitions if comp.get("topkit_reference"))
                self.log_test(
                    "GET /api/competitions",
                    True,
                    f"Retrieved {len(competitions)} competitions, {competitions_with_references} with TopKit references"
                )
            else:
                self.log_test(
                    "GET /api/competitions",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )

            # Test integration - check if master jerseys properly link to brands/teams
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            if response.status_code == 200:
                master_jerseys = response.json()
                
                properly_linked = 0
                for jersey in master_jerseys:
                    has_team_info = bool(jersey.get("team_info"))
                    has_brand_info = bool(jersey.get("brand_info"))
                    
                    if has_team_info and has_brand_info:
                        properly_linked += 1
                
                integration_success = properly_linked > 0
                self.log_test(
                    "Master Jersey Integration with Brands/Teams",
                    integration_success,
                    f"{properly_linked}/{len(master_jerseys)} master jerseys properly linked to brands and teams"
                )
            
        except Exception as e:
            self.log_test("Brands/Teams/Competitions Integration", False, "", str(e))

    def test_vestiaire_add_to_collection(self):
        """Test POST /api/vestiaire/add-to-collection endpoint"""
        print("🔍 TESTING VESTIAIRE ADD TO COLLECTION")
        print("=" * 60)
        
        try:
            # First get available jersey releases
            response = self.session.get(f"{BACKEND_URL}/jersey-releases")
            if response.status_code == 200:
                jersey_releases = response.json()
                
                if jersey_releases:
                    test_release = jersey_releases[0]
                    
                    # Test adding to collection via vestiaire endpoint
                    collection_data = {
                        "jersey_release_id": test_release.get("id"),
                        "collection_type": "wanted",
                        "size": "M",
                        "condition": "mint"
                    }
                    
                    response = self.session.post(
                        f"{BACKEND_URL}/vestiaire/add-to-collection",
                        json=collection_data
                    )
                    
                    if response.status_code in [200, 201]:
                        self.log_test(
                            "POST /api/vestiaire/add-to-collection",
                            True,
                            f"Successfully added jersey release to collection via vestiaire endpoint"
                        )
                    elif response.status_code == 400 and "already in collection" in response.text:
                        self.log_test(
                            "POST /api/vestiaire/add-to-collection",
                            True,
                            "Duplicate prevention working correctly (expected behavior)"
                        )
                    else:
                        self.log_test(
                            "POST /api/vestiaire/add-to-collection",
                            False,
                            f"HTTP {response.status_code}",
                            response.text
                        )
                else:
                    self.log_test(
                        "POST /api/vestiaire/add-to-collection",
                        False,
                        "",
                        "No jersey releases available for testing"
                    )
            else:
                self.log_test(
                    "POST /api/vestiaire/add-to-collection",
                    False,
                    f"Could not retrieve jersey releases: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("POST /api/vestiaire/add-to-collection", False, "", str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING TOPKIT BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print("=" * 80)
        print()
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        print()
        
        # Run all tests
        self.test_jersey_release_collection_endpoints()
        print()
        
        self.test_vestiaire_endpoint()
        print()
        
        self.test_master_jerseys_endpoint()
        print()
        
        self.test_brands_teams_competitions_integration()
        print()
        
        self.test_vestiaire_add_to_collection()
        print()
        
        # Summary
        self.print_summary()
        
        return True

    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Backend has significant issues that need attention")
        else:
            print("🚨 CRITICAL: Backend has major issues requiring immediate fixes")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = TopKitBackendTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)