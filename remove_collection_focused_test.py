#!/usr/bin/env python3
"""
Focused test for Remove From Collection functionality
Tests the specific scenarios mentioned in the review request
"""

import requests
import json
import uuid
import time

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"

class RemoveCollectionTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
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
    
    def setup_authenticated_user(self):
        """Setup authenticated user for testing"""
        try:
            # Register a unique user
            unique_email = f"removetest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "SecurePass123!",
                "name": "Remove Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["token"]
                self.user_id = data["user"]["id"]
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                print(f"✅ Setup: User authenticated with ID: {self.user_id}")
                return True
            else:
                print(f"❌ Setup: Authentication failed - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Setup: Exception - {str(e)}")
            return False
    
    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        try:
            payload = {
                "team": "Liverpool FC",
                "season": "2023-24",
                "player": "Mohamed Salah",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Liverpool home jersey with Salah #11",
                "images": ["https://example.com/liverpool1.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.test_jersey_id = data["id"]
                print(f"✅ Setup: Test jersey created with ID: {self.test_jersey_id}")
                return True
            else:
                print(f"❌ Setup: Jersey creation failed - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Setup: Exception creating jersey - {str(e)}")
            return False
    
    def test_1_delete_endpoint_authenticated_owned(self):
        """Test 1: DELETE endpoint with authenticated user removing jersey from owned collection"""
        try:
            # Add jersey to owned collection first
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            if add_response.status_code != 200:
                self.log_test("Test 1: Add to Owned Collection", "FAIL", f"Could not add jersey: {add_response.status_code}")
                return False
            
            # Verify it's in owned collection
            owned_before = self.session.get(f"{self.base_url}/collections/owned")
            owned_count_before = len([item for item in owned_before.json() if item.get('jersey_id') == self.test_jersey_id])
            
            # Remove from collection using DELETE endpoint
            remove_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if remove_response.status_code == 200:
                # Verify removal
                owned_after = self.session.get(f"{self.base_url}/collections/owned")
                owned_count_after = len([item for item in owned_after.json() if item.get('jersey_id') == self.test_jersey_id])
                
                if owned_count_after < owned_count_before:
                    self.log_test("Test 1: DELETE Authenticated Owned", "PASS", 
                                f"Jersey removed from owned collection ({owned_count_before}→{owned_count_after})")
                    return True
                else:
                    self.log_test("Test 1: DELETE Authenticated Owned", "FAIL", "Jersey not removed from owned collection")
                    return False
            else:
                self.log_test("Test 1: DELETE Authenticated Owned", "FAIL", f"DELETE failed: {remove_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test 1: DELETE Authenticated Owned", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_2_delete_endpoint_authenticated_wanted(self):
        """Test 2: DELETE endpoint with authenticated user removing jersey from wanted collection"""
        try:
            # Add jersey to wanted collection first
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            if add_response.status_code != 200:
                self.log_test("Test 2: Add to Wanted Collection", "FAIL", f"Could not add jersey: {add_response.status_code}")
                return False
            
            # Verify it's in wanted collection
            wanted_before = self.session.get(f"{self.base_url}/collections/wanted")
            wanted_count_before = len([item for item in wanted_before.json() if item.get('jersey_id') == self.test_jersey_id])
            
            # Remove from collection using DELETE endpoint
            remove_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if remove_response.status_code == 200:
                # Verify removal
                wanted_after = self.session.get(f"{self.base_url}/collections/wanted")
                wanted_count_after = len([item for item in wanted_after.json() if item.get('jersey_id') == self.test_jersey_id])
                
                if wanted_count_after < wanted_count_before:
                    self.log_test("Test 2: DELETE Authenticated Wanted", "PASS", 
                                f"Jersey removed from wanted collection ({wanted_count_before}→{wanted_count_after})")
                    return True
                else:
                    self.log_test("Test 2: DELETE Authenticated Wanted", "FAIL", "Jersey not removed from wanted collection")
                    return False
            else:
                self.log_test("Test 2: DELETE Authenticated Wanted", "FAIL", f"DELETE failed: {remove_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test 2: DELETE Authenticated Wanted", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_3_authentication_required(self):
        """Test 3: Verify proper authentication is required (401/403 for unauthenticated)"""
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Try to remove without authentication
            response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log_test("Test 3: Authentication Required", "PASS", 
                            f"Correctly rejected unauthenticated request with status {response.status_code}")
                return True
            else:
                self.log_test("Test 3: Authentication Required", "FAIL", 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test 3: Authentication Required", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_4_edge_cases(self):
        """Test 4: Edge cases - removing non-existent jersey or jersey not in collection"""
        try:
            # Test 4a: Non-existent jersey ID
            fake_jersey_id = str(uuid.uuid4())
            response_nonexistent = self.session.delete(f"{self.base_url}/collections/{fake_jersey_id}")
            
            if response_nonexistent.status_code == 404:
                self.log_test("Test 4a: Non-existent Jersey", "PASS", "Correctly returned 404 for non-existent jersey")
            else:
                self.log_test("Test 4a: Non-existent Jersey", "FAIL", f"Expected 404, got {response_nonexistent.status_code}")
                return False
            
            # Test 4b: Jersey not in collection (but jersey exists)
            # First ensure the jersey is NOT in any collection
            self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")  # Remove if exists
            
            # Try to remove again (should fail since not in collection)
            response_not_in_collection = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if response_not_in_collection.status_code == 404:
                self.log_test("Test 4b: Jersey Not In Collection", "PASS", "Correctly returned 404 for jersey not in collection")
                return True
            else:
                self.log_test("Test 4b: Jersey Not In Collection", "FAIL", f"Expected 404, got {response_not_in_collection.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Test 4: Edge Cases", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_5_sample_data_verification(self):
        """Test 5: Verify sample data is properly loaded (3 users, 9 jerseys)"""
        try:
            # Check jerseys
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            if jerseys_response.status_code != 200:
                self.log_test("Test 5: Sample Data Verification", "FAIL", f"Could not get jerseys: {jerseys_response.status_code}")
                return False
            
            jerseys = jerseys_response.json()
            jerseys_count = len(jerseys)
            
            # Check listings
            listings_response = self.session.get(f"{self.base_url}/listings?limit=50")
            if listings_response.status_code != 200:
                self.log_test("Test 5: Sample Data Verification", "FAIL", f"Could not get listings: {listings_response.status_code}")
                return False
            
            listings = listings_response.json()
            listings_count = len(listings)
            
            # Verify reasonable amounts of data exist
            if jerseys_count >= 9 and listings_count >= 3:
                self.log_test("Test 5: Sample Data Verification", "PASS", 
                            f"Sample data loaded: {jerseys_count} jerseys, {listings_count} listings")
                return True
            else:
                self.log_test("Test 5: Sample Data Verification", "FAIL", 
                            f"Insufficient sample data: {jerseys_count} jerseys, {listings_count} listings (expected ≥9 jerseys, ≥3 listings)")
                return False
                
        except Exception as e:
            self.log_test("Test 5: Sample Data Verification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_6_complete_integration_flow(self):
        """Test 6: Complete remove from collection flow"""
        try:
            # Step 1: GET user collections to see current jerseys
            owned_initial = self.session.get(f"{self.base_url}/collections/owned")
            wanted_initial = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_initial.status_code != 200 or wanted_initial.status_code != 200:
                self.log_test("Test 6: Integration Flow", "FAIL", "Could not get initial collections")
                return False
            
            # Step 2: Add jersey to both collections
            add_owned = self.session.post(f"{self.base_url}/collections", json={
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            })
            
            add_wanted = self.session.post(f"{self.base_url}/collections", json={
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            })
            
            # Step 3: GET collections to verify addition
            owned_after_add = self.session.get(f"{self.base_url}/collections/owned")
            wanted_after_add = self.session.get(f"{self.base_url}/collections/wanted")
            
            owned_count_after_add = len([item for item in owned_after_add.json() if item.get('jersey_id') == self.test_jersey_id])
            wanted_count_after_add = len([item for item in wanted_after_add.json() if item.get('jersey_id') == self.test_jersey_id])
            
            # Step 4: DELETE specific jersey from collection
            remove_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if remove_response.status_code != 200:
                self.log_test("Test 6: Integration Flow", "FAIL", f"DELETE failed: {remove_response.status_code}")
                return False
            
            # Step 5: GET collections again to verify removal
            owned_final = self.session.get(f"{self.base_url}/collections/owned")
            wanted_final = self.session.get(f"{self.base_url}/collections/wanted")
            
            owned_count_final = len([item for item in owned_final.json() if item.get('jersey_id') == self.test_jersey_id])
            wanted_count_final = len([item for item in wanted_final.json() if item.get('jersey_id') == self.test_jersey_id])
            
            # Verify removal worked
            if owned_count_final < owned_count_after_add or wanted_count_final < wanted_count_after_add:
                self.log_test("Test 6: Integration Flow", "PASS", 
                            f"Complete flow successful. Owned: {owned_count_after_add}→{owned_count_final}, Wanted: {wanted_count_after_add}→{wanted_count_final}")
                return True
            else:
                self.log_test("Test 6: Integration Flow", "FAIL", 
                            f"Jersey not removed. Owned: {owned_count_after_add}→{owned_count_final}, Wanted: {wanted_count_after_add}→{wanted_count_final}")
                return False
                
        except Exception as e:
            self.log_test("Test 6: Integration Flow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_focused_tests(self):
        """Run all focused tests for Remove From Collection functionality"""
        print("🎯 FOCUSED REMOVE FROM COLLECTION TESTS")
        print("=" * 60)
        print("Testing the recently fixed 'Remove From Collection' functionality")
        print()
        
        # Setup
        if not self.setup_authenticated_user():
            print("❌ Setup failed - cannot continue with tests")
            return
        
        if not self.create_test_jersey():
            print("❌ Jersey creation failed - cannot continue with tests")
            return
        
        print("🧪 RUNNING FOCUSED TESTS")
        print("-" * 40)
        
        test_results = {}
        
        # Run all focused tests
        test_results['test_1_delete_owned'] = self.test_1_delete_endpoint_authenticated_owned()
        test_results['test_2_delete_wanted'] = self.test_2_delete_endpoint_authenticated_wanted()
        test_results['test_3_auth_required'] = self.test_3_authentication_required()
        test_results['test_4_edge_cases'] = self.test_4_edge_cases()
        test_results['test_5_sample_data'] = self.test_5_sample_data_verification()
        test_results['test_6_integration_flow'] = self.test_6_complete_integration_flow()
        
        # Summary
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print(f"Total Focused Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        if passed == total:
            print("\n🎉 ALL REMOVE FROM COLLECTION TESTS PASSED!")
            print("The 'Remove From Collection' functionality is working correctly.")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Review the issues above.")
        
        return test_results

if __name__ == "__main__":
    tester = RemoveCollectionTester()
    results = tester.run_focused_tests()