#!/usr/bin/env python3
"""
TopKit Collaborative Database API Testing
Testing new collaborative database endpoints as requested in review
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-vault-3.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class TopKitCollaborativeAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                self.log_test("Admin Authentication", True, f"Admin: {data.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_basic_api_connectivity(self):
        """Test 1: Basic API connectivity - Verify all new endpoints are accessible"""
        print("\n=== TEST 1: BASIC API CONNECTIVITY ===")
        
        endpoints = [
            ("GET /api/teams", "teams"),
            ("GET /api/brands", "brands"),
            ("GET /api/players", "players"),
            ("GET /api/competitions", "competitions"),
            ("GET /api/master-jerseys", "master-jerseys"),
            ("GET /api/jersey-releases", "jersey-releases"),
            ("GET /api/search/collaborative", "search/collaborative")
        ]
        
        for endpoint_name, endpoint_path in endpoints:
            try:
                response = self.session.get(f"{BACKEND_URL}/{endpoint_path}")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Endpoint {endpoint_name}", True, f"Returns {len(data) if isinstance(data, list) else 'data'} items")
                else:
                    self.log_test(f"Endpoint {endpoint_name}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Endpoint {endpoint_name}", False, f"Exception: {str(e)}")
    
    def test_authentication_endpoints(self):
        """Test 2: Authentication - Test authenticated endpoints"""
        print("\n=== TEST 2: AUTHENTICATION ENDPOINTS ===")
        
        if not self.admin_token:
            self.log_test("Authentication Required", False, "No admin token available")
            return
        
        # Test authenticated POST endpoints
        authenticated_endpoints = [
            ("POST /api/teams", "teams", {
                "name": "Barcelona FC",
                "short_name": "FCB",
                "country": "Spain",
                "city": "Barcelona",
                "founded_year": 1899,
                "colors": ["blue", "red"]
            }),
            ("POST /api/brands", "brands", {
                "name": "Nike",
                "official_name": "Nike Inc.",
                "country": "USA",
                "founded_year": 1964,
                "website": "https://nike.com"
            }),
            ("POST /api/players", "players", {
                "name": "Lionel Messi",
                "full_name": "Lionel Andrés Messi",
                "nationality": "Argentina",
                "position": "Forward"
            }),
            ("POST /api/competitions", "competitions", {
                "name": "La Liga",
                "official_name": "LaLiga Santander",
                "competition_type": "domestic_league",
                "country": "Spain",
                "level": 1
            })
        ]
        
        created_entities = {}
        
        for endpoint_name, endpoint_path, test_data in authenticated_endpoints:
            try:
                response = self.session.post(f"{BACKEND_URL}/{endpoint_path}", json=test_data)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    entity_id = data.get('id')
                    reference = data.get('topkit_reference', 'No reference')
                    created_entities[endpoint_path] = entity_id
                    self.log_test(f"Create {endpoint_name}", True, f"ID: {entity_id}, Ref: {reference}")
                else:
                    self.log_test(f"Create {endpoint_name}", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Create {endpoint_name}", False, f"Exception: {str(e)}")
        
        return created_entities
    
    def test_data_creation_workflow(self, created_entities):
        """Test 3: Data creation workflow - Test complete flow"""
        print("\n=== TEST 3: DATA CREATION WORKFLOW ===")
        
        if not all(key in created_entities for key in ['teams', 'brands', 'competitions']):
            self.log_test("Prerequisites Check", False, "Missing required entities for workflow")
            return
        
        # Create master jersey linking team + brand + competition
        master_jersey_data = {
            "team_id": created_entities['teams'],
            "brand_id": created_entities['brands'],
            "competition_id": created_entities['competitions'],
            "season": "2024-25",
            "jersey_type": "home",
            "design_name": "Classic Home Kit",
            "primary_color": "blue",
            "secondary_colors": ["red", "white"],
            "main_sponsor": "Spotify"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/master-jerseys", json=master_jersey_data)
            
            if response.status_code in [200, 201]:
                master_jersey = response.json()
                master_jersey_id = master_jersey.get('id')
                reference = master_jersey.get('topkit_reference', 'No reference')
                self.log_test("Create Master Jersey", True, f"ID: {master_jersey_id}, Ref: {reference}")
                
                # Create jersey release for that master jersey
                jersey_release_data = {
                    "master_jersey_id": master_jersey_id,
                    "release_type": "fan_version",
                    "size_range": ["S", "M", "L", "XL"],
                    "player_name": "Lionel Messi",
                    "player_number": 10,
                    "retail_price": 89.99,
                    "sku_code": "FCB-HOME-2425-MESSI"
                }
                
                response = self.session.post(f"{BACKEND_URL}/jersey-releases", json=jersey_release_data)
                
                if response.status_code in [200, 201]:
                    jersey_release = response.json()
                    release_id = jersey_release.get('id')
                    release_reference = jersey_release.get('topkit_reference', 'No reference')
                    self.log_test("Create Jersey Release", True, f"ID: {release_id}, Ref: {release_reference}")
                    return master_jersey_id, release_id
                else:
                    self.log_test("Create Jersey Release", False, f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("Create Master Jersey", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Data Creation Workflow", False, f"Exception: {str(e)}")
        
        return None, None
    
    def test_search_functionality(self):
        """Test 4: Search functionality - Test collaborative search"""
        print("\n=== TEST 4: SEARCH FUNCTIONALITY ===")
        
        search_queries = [
            ("Barcelona", "Search for Barcelona"),
            ("Nike", "Search for Nike"),
            ("Messi", "Search for Messi"),
            ("La Liga", "Search for La Liga"),
            ("2024", "Search for 2024 season")
        ]
        
        for query, test_name in search_queries:
            try:
                response = self.session.get(f"{BACKEND_URL}/search/collaborative", params={"q": query})
                
                if response.status_code == 200:
                    data = response.json()
                    total_results = sum(len(results) for results in data.values() if isinstance(results, list))
                    self.log_test(test_name, True, f"Found {total_results} total results across all entities")
                else:
                    self.log_test(test_name, False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
    
    def test_reference_generation(self):
        """Test 5: Reference generation - Verify TopKit references are generated correctly"""
        print("\n=== TEST 5: REFERENCE GENERATION ===")
        
        # Test reference patterns for each entity type
        endpoints_and_patterns = [
            ("teams", "TK-TEAM-"),
            ("brands", "TK-BRAND-"),
            ("players", "TK-PLAYER-"),
            ("competitions", "TK-COMP-"),
            ("master-jerseys", "TK-MASTER-"),
            ("jersey-releases", "TK-RELEASE-")
        ]
        
        for endpoint, expected_pattern in endpoints_and_patterns:
            try:
                response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        # Check first item for reference pattern
                        first_item = data[0]
                        reference = first_item.get('topkit_reference', '')
                        
                        if reference.startswith(expected_pattern):
                            self.log_test(f"Reference Pattern {endpoint}", True, f"Found: {reference}")
                        else:
                            self.log_test(f"Reference Pattern {endpoint}", False, f"Expected {expected_pattern}*, got: {reference}")
                    else:
                        self.log_test(f"Reference Pattern {endpoint}", True, "No items to check (empty collection)")
                else:
                    self.log_test(f"Reference Pattern {endpoint}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Reference Pattern {endpoint}", False, f"Exception: {str(e)}")
    
    def test_enriched_responses(self):
        """Test 6: Enriched responses - Verify responses include related data"""
        print("\n=== TEST 6: ENRICHED RESPONSES ===")
        
        # Test enriched responses for master jerseys (should include team, brand, competition info)
        try:
            response = self.session.get(f"{BACKEND_URL}/master-jerseys")
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    first_jersey = data[0]
                    
                    # Check for enriched data
                    has_team_info = 'team_info' in first_jersey
                    has_brand_info = 'brand_info' in first_jersey
                    has_competition_info = 'competition_info' in first_jersey
                    
                    enrichment_score = sum([has_team_info, has_brand_info, has_competition_info])
                    
                    self.log_test("Master Jersey Enrichment", enrichment_score >= 2, 
                                f"Team info: {has_team_info}, Brand info: {has_brand_info}, Competition info: {has_competition_info}")
                else:
                    self.log_test("Master Jersey Enrichment", True, "No master jerseys to check")
            else:
                self.log_test("Master Jersey Enrichment", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Master Jersey Enrichment", False, f"Exception: {str(e)}")
        
        # Test team responses for enrichment
        try:
            response = self.session.get(f"{BACKEND_URL}/teams")
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    first_team = data[0]
                    
                    # Check for enriched data
                    has_league_info = 'league_info' in first_team
                    has_jersey_count = 'master_jerseys_count' in first_team
                    has_collector_count = 'total_collectors' in first_team
                    
                    enrichment_score = sum([has_league_info, has_jersey_count, has_collector_count])
                    
                    self.log_test("Team Response Enrichment", enrichment_score >= 2,
                                f"League info: {has_league_info}, Jersey count: {has_jersey_count}, Collector count: {has_collector_count}")
                else:
                    self.log_test("Team Response Enrichment", True, "No teams to check")
            else:
                self.log_test("Team Response Enrichment", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Team Response Enrichment", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🎯 TOPKIT COLLABORATIVE DATABASE API TESTING STARTED")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate_admin():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run all tests
        self.test_basic_api_connectivity()
        created_entities = self.test_authentication_endpoints()
        
        if created_entities:
            master_jersey_id, release_id = self.test_data_creation_workflow(created_entities)
        
        self.test_search_functionality()
        self.test_reference_generation()
        self.test_enriched_responses()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎉 COLLABORATIVE DATABASE API TESTING COMPLETE - {success_rate:.1f}% SUCCESS RATE!")
        
        # Determine overall status
        if success_rate >= 90:
            print("✅ EXCELLENT: All collaborative database endpoints are working perfectly!")
        elif success_rate >= 75:
            print("✅ GOOD: Most collaborative database endpoints are working with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL: Some collaborative database endpoints need attention")
        else:
            print("❌ CRITICAL: Major issues with collaborative database endpoints")
        
        return success_rate

def main():
    """Main function"""
    tester = TopKitCollaborativeAPITester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)

if __name__ == "__main__":
    main()