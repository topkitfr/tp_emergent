#!/usr/bin/env python3
"""
TopKit Collection Detailed Debug Test
Deep dive into the collection system to find any edge cases or specific issues
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class DetailedCollectionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def authenticate(self):
        """Authenticate user"""
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data["token"]
            self.user_id = data["user"]["id"]
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            return True
        return False
    
    def test_collection_data_consistency(self):
        """Test data consistency between collections and profile stats"""
        try:
            # Get collections
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            profile_response = self.session.get(f"{self.base_url}/profile")
            
            if all(r.status_code == 200 for r in [owned_response, wanted_response, profile_response]):
                owned_collection = owned_response.json()
                wanted_collection = wanted_response.json()
                profile = profile_response.json()
                
                # Count from collections
                owned_count_actual = len(owned_collection)
                wanted_count_actual = len(wanted_collection)
                
                # Count from profile stats
                stats = profile.get("stats", {})
                owned_count_stats = stats.get("owned_jerseys", 0)
                wanted_count_stats = stats.get("wanted_jerseys", 0)
                
                # Check consistency
                owned_consistent = owned_count_actual == owned_count_stats
                wanted_consistent = wanted_count_actual == wanted_count_stats
                
                if owned_consistent and wanted_consistent:
                    self.log_test("Collection Data Consistency", "PASS", 
                                f"Owned: {owned_count_actual} (consistent), Wanted: {wanted_count_actual} (consistent)")
                    return True
                else:
                    self.log_test("Collection Data Consistency", "FAIL", 
                                f"Inconsistency - Owned: actual={owned_count_actual}, stats={owned_count_stats}; Wanted: actual={wanted_count_actual}, stats={wanted_count_stats}")
                    return False
            else:
                self.log_test("Collection Data Consistency", "FAIL", "Could not retrieve all required data")
                return False
                
        except Exception as e:
            self.log_test("Collection Data Consistency", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_jersey_details(self):
        """Test that jersey details are complete in collections"""
        try:
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_collection = owned_response.json()
                wanted_collection = wanted_response.json()
                
                all_complete = True
                incomplete_items = []
                
                for collection_type, collection in [("owned", owned_collection), ("wanted", wanted_collection)]:
                    for item in collection:
                        jersey = item.get('jersey', {})
                        required_fields = ['id', 'team', 'season', 'status']
                        
                        missing_fields = [field for field in required_fields if not jersey.get(field)]
                        
                        if missing_fields:
                            all_complete = False
                            incomplete_items.append(f"{collection_type}: missing {missing_fields}")
                
                if all_complete:
                    total_items = len(owned_collection) + len(wanted_collection)
                    self.log_test("Collection Jersey Details", "PASS", 
                                f"All {total_items} jersey items have complete details")
                    
                    # Show sample jersey details
                    if owned_collection:
                        sample = owned_collection[0]['jersey']
                        print(f"   Sample jersey: {sample.get('team')} {sample.get('season')} - {sample.get('player', 'No player')} (Status: {sample.get('status')})")
                    
                    return True
                else:
                    self.log_test("Collection Jersey Details", "FAIL", 
                                f"Incomplete jersey details found: {incomplete_items}")
                    return False
            else:
                self.log_test("Collection Jersey Details", "FAIL", "Could not retrieve collections")
                return False
                
        except Exception as e:
            self.log_test("Collection Jersey Details", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_add_remove_cycle(self):
        """Test adding and removing jerseys from collections"""
        try:
            # Get an approved jersey that's not in collections
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            
            if jerseys_response.status_code != 200:
                self.log_test("Collection Add/Remove Cycle", "FAIL", "Could not get jerseys")
                return False
            
            jerseys = jerseys_response.json()
            approved_jerseys = [j for j in jerseys if j.get('status') == 'approved']
            
            if not approved_jerseys:
                self.log_test("Collection Add/Remove Cycle", "FAIL", "No approved jerseys found")
                return False
            
            # Use the first approved jersey
            test_jersey = approved_jerseys[0]
            jersey_id = test_jersey['id']
            jersey_name = f"{test_jersey.get('team', 'Unknown')} {test_jersey.get('season', 'Unknown')}"
            
            # Step 1: Add to owned collection
            add_payload = {
                "jersey_id": jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            if add_response.status_code not in [200, 400]:  # 400 if already exists
                self.log_test("Collection Add/Remove Cycle", "FAIL", f"Add failed: {add_response.status_code}")
                return False
            
            # Step 2: Verify it's in the collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code != 200:
                self.log_test("Collection Add/Remove Cycle", "FAIL", "Could not retrieve owned collection")
                return False
            
            owned_collection = owned_response.json()
            jersey_in_collection = any(item.get('jersey_id') == jersey_id for item in owned_collection)
            
            if not jersey_in_collection:
                self.log_test("Collection Add/Remove Cycle", "FAIL", f"Jersey {jersey_name} not found in collection after adding")
                return False
            
            # Step 3: Remove from collection using POST endpoint
            remove_payload = {
                "jersey_id": jersey_id,
                "collection_type": "owned"
            }
            
            remove_response = self.session.post(f"{self.base_url}/collections/remove", json=remove_payload)
            
            if remove_response.status_code != 200:
                self.log_test("Collection Add/Remove Cycle", "FAIL", f"Remove failed: {remove_response.status_code}")
                return False
            
            # Step 4: Verify it's removed
            owned_response_after = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response_after.status_code != 200:
                self.log_test("Collection Add/Remove Cycle", "FAIL", "Could not retrieve owned collection after removal")
                return False
            
            owned_collection_after = owned_response_after.json()
            jersey_still_in_collection = any(item.get('jersey_id') == jersey_id for item in owned_collection_after)
            
            if jersey_still_in_collection:
                self.log_test("Collection Add/Remove Cycle", "FAIL", f"Jersey {jersey_name} still in collection after removal")
                return False
            
            self.log_test("Collection Add/Remove Cycle", "PASS", 
                        f"Successfully added and removed {jersey_name} from collection")
            return True
                
        except Exception as e:
            self.log_test("Collection Add/Remove Cycle", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_with_different_jersey_statuses(self):
        """Test collection behavior with jerseys of different statuses"""
        try:
            # Get all jerseys to see different statuses
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if jerseys_response.status_code != 200:
                self.log_test("Collection Different Statuses", "FAIL", "Could not get jerseys")
                return False
            
            all_jerseys = jerseys_response.json()
            
            # Count by status
            status_counts = {}
            for jersey in all_jerseys:
                status = jersey.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get collections
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_collection = owned_response.json()
                wanted_collection = wanted_response.json()
                
                # Check statuses of jerseys in collections
                collection_statuses = {}
                for item in owned_collection + wanted_collection:
                    jersey = item.get('jersey', {})
                    status = jersey.get('status', 'unknown')
                    collection_statuses[status] = collection_statuses.get(status, 0) + 1
                
                # All jerseys in collections should be approved
                if collection_statuses.keys() == {'approved'} or not collection_statuses:
                    self.log_test("Collection Different Statuses", "PASS", 
                                f"All collection jerseys are approved. DB statuses: {status_counts}, Collection statuses: {collection_statuses}")
                    return True
                else:
                    self.log_test("Collection Different Statuses", "FAIL", 
                                f"Non-approved jerseys in collections. Collection statuses: {collection_statuses}")
                    return False
            else:
                self.log_test("Collection Different Statuses", "FAIL", "Could not retrieve collections")
                return False
                
        except Exception as e:
            self.log_test("Collection Different Statuses", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_pagination_and_limits(self):
        """Test collection retrieval with large datasets"""
        try:
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_collection = owned_response.json()
                wanted_collection = wanted_response.json()
                
                # Check if we're getting reasonable amounts of data
                total_items = len(owned_collection) + len(wanted_collection)
                
                if total_items > 0:
                    # Check for duplicate jersey IDs within each collection
                    owned_ids = [item.get('jersey_id') for item in owned_collection]
                    wanted_ids = [item.get('jersey_id') for item in wanted_collection]
                    
                    owned_duplicates = len(owned_ids) != len(set(owned_ids))
                    wanted_duplicates = len(wanted_ids) != len(set(wanted_ids))
                    
                    if not owned_duplicates and not wanted_duplicates:
                        self.log_test("Collection Pagination/Limits", "PASS", 
                                    f"No duplicates found. Owned: {len(owned_collection)}, Wanted: {len(wanted_collection)}")
                        return True
                    else:
                        self.log_test("Collection Pagination/Limits", "FAIL", 
                                    f"Duplicates found - Owned: {owned_duplicates}, Wanted: {wanted_duplicates}")
                        return False
                else:
                    self.log_test("Collection Pagination/Limits", "PASS", "No items in collections (empty state)")
                    return True
            else:
                self.log_test("Collection Pagination/Limits", "FAIL", "Could not retrieve collections")
                return False
                
        except Exception as e:
            self.log_test("Collection Pagination/Limits", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_response_times(self):
        """Test collection endpoint response times"""
        try:
            # Test owned collection response time
            start_time = time.time()
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            owned_time = time.time() - start_time
            
            # Test wanted collection response time
            start_time = time.time()
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            wanted_time = time.time() - start_time
            
            # Test profile response time
            start_time = time.time()
            profile_response = self.session.get(f"{self.base_url}/profile")
            profile_time = time.time() - start_time
            
            if all(r.status_code == 200 for r in [owned_response, wanted_response, profile_response]):
                # Check if response times are reasonable (under 2 seconds)
                if owned_time < 2.0 and wanted_time < 2.0 and profile_time < 2.0:
                    self.log_test("Collection Response Times", "PASS", 
                                f"Good response times - Owned: {owned_time:.3f}s, Wanted: {wanted_time:.3f}s, Profile: {profile_time:.3f}s")
                    return True
                else:
                    self.log_test("Collection Response Times", "FAIL", 
                                f"Slow response times - Owned: {owned_time:.3f}s, Wanted: {wanted_time:.3f}s, Profile: {profile_time:.3f}s")
                    return False
            else:
                self.log_test("Collection Response Times", "FAIL", "Some endpoints failed")
                return False
                
        except Exception as e:
            self.log_test("Collection Response Times", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_edge_cases(self):
        """Test edge cases that might cause issues"""
        try:
            # Test 1: Try to add non-existent jersey to collection
            fake_jersey_id = "00000000-0000-0000-0000-000000000000"
            
            payload = {
                "jersey_id": fake_jersey_id,
                "collection_type": "owned"
            }
            
            fake_response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            # Should fail gracefully
            if fake_response.status_code in [400, 404]:
                edge_case_1_pass = True
            else:
                edge_case_1_pass = False
            
            # Test 2: Try invalid collection type
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=1")
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                if jerseys:
                    payload = {
                        "jersey_id": jerseys[0]['id'],
                        "collection_type": "invalid_type"
                    }
                    
                    invalid_type_response = self.session.post(f"{self.base_url}/collections", json=payload)
                    
                    # Should fail gracefully
                    if invalid_type_response.status_code in [400, 422]:
                        edge_case_2_pass = True
                    else:
                        edge_case_2_pass = False
                else:
                    edge_case_2_pass = True  # No jerseys to test with
            else:
                edge_case_2_pass = True  # Can't test without jerseys
            
            if edge_case_1_pass and edge_case_2_pass:
                self.log_test("Collection Edge Cases", "PASS", "All edge cases handled correctly")
                return True
            else:
                self.log_test("Collection Edge Cases", "FAIL", 
                            f"Edge case failures - Fake jersey: {edge_case_1_pass}, Invalid type: {edge_case_2_pass}")
                return False
                
        except Exception as e:
            self.log_test("Collection Edge Cases", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_detailed_tests(self):
        """Run all detailed collection tests"""
        print("🔍 DETAILED COLLECTION DEBUG TEST")
        print("=" * 50)
        print(f"Testing with user: {TEST_USER_EMAIL}")
        print("=" * 50)
        print()
        
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        tests = [
            self.test_collection_data_consistency,
            self.test_collection_jersey_details,
            self.test_collection_add_remove_cycle,
            self.test_collection_with_different_jersey_statuses,
            self.test_collection_pagination_and_limits,
            self.test_collection_response_times,
            self.test_collection_edge_cases
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            if test():
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)
        
        print("=" * 50)
        print(f"🎯 DETAILED TEST RESULTS")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print("=" * 50)

if __name__ == "__main__":
    tester = DetailedCollectionTester()
    tester.run_detailed_tests()