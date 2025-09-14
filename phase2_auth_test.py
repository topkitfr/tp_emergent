#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Phase 2 Backend Authentication Verification
CRITICAL COLLECTION BUG DIAGNOSTIC - Testing specific user credentials steinmetzlivio@gmail.com / 123
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
SPECIFIC_USER_EMAIL = "steinmetzlivio@gmail.com"
SPECIFIC_USER_PASSWORD = "123"

class Phase2AuthTester:
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
    
    def test_specific_user_login(self):
        """Test POST /api/auth/login with steinmetzlivio@gmail.com / 123"""
        try:
            print("🎯 TESTING SPECIFIC USER LOGIN: steinmetzlivio@gmail.com / 123")
            
            payload = {
                "email": SPECIFIC_USER_EMAIL,
                "password": SPECIFIC_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure includes token and user data
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_data = data["user"]
                    
                    # Update session with auth token
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    # Verify user data structure
                    required_fields = ["id", "email", "name", "role"]
                    if all(field in user_data for field in required_fields):
                        self.log_test("Specific User Login", "PASS", 
                                    f"Login successful - User: {user_data['name']} ({user_data['email']}) Role: {user_data['role']}")
                        return True
                    else:
                        self.log_test("Specific User Login", "FAIL", "Missing required user fields in response")
                        return False
                else:
                    self.log_test("Specific User Login", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Specific User Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Specific User Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile_endpoint_with_token(self):
        """Test GET /api/profile with the returned token"""
        try:
            if not self.auth_token:
                self.log_test("Profile Endpoint", "FAIL", "No auth token available")
                return False
            
            print("🎯 TESTING PROFILE ENDPOINT WITH TOKEN")
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify response structure
                if "user" in profile and "stats" in profile:
                    user_data = profile["user"]
                    stats_data = profile["stats"]
                    
                    # Check required user fields
                    required_user_fields = ["id", "email", "name", "provider", "created_at"]
                    required_stats_fields = ["owned_jerseys", "wanted_jerseys", "active_listings"]
                    
                    user_valid = all(field in user_data for field in required_user_fields)
                    stats_valid = all(field in stats_data for field in required_stats_fields)
                    
                    if user_valid and stats_valid:
                        self.log_test("Profile Endpoint", "PASS", 
                                    f"Profile retrieved - Stats: Owned: {stats_data['owned_jerseys']}, Wanted: {stats_data['wanted_jerseys']}, Listings: {stats_data['active_listings']}")
                        return True
                    else:
                        self.log_test("Profile Endpoint", "FAIL", "Missing required fields in profile or stats")
                        return False
                else:
                    self.log_test("Profile Endpoint", "FAIL", "Missing user or stats in response")
                    return False
            else:
                self.log_test("Profile Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_owned_endpoint(self):
        """Test GET /api/collections/owned with authentication"""
        try:
            if not self.auth_token:
                self.log_test("Collections Owned Endpoint", "FAIL", "No auth token available")
                return False
            
            print("🎯 TESTING COLLECTIONS/OWNED ENDPOINT")
            
            response = self.session.get(f"{self.base_url}/collections/owned")
            
            if response.status_code == 200:
                collections = response.json()
                
                # Verify it's a list
                if isinstance(collections, list):
                    # Check if collections have proper structure
                    if len(collections) > 0:
                        # Verify first collection item structure
                        first_item = collections[0]
                        required_fields = ["id", "user_id", "jersey_id", "collection_type", "added_at"]
                        
                        if all(field in first_item for field in required_fields):
                            # Check if jersey data is populated
                            if "jersey" in first_item:
                                jersey_data = first_item["jersey"]
                                jersey_fields = ["id", "team", "season", "status"]
                                
                                if all(field in jersey_data for field in jersey_fields):
                                    self.log_test("Collections Owned Endpoint", "PASS", 
                                                f"Retrieved {len(collections)} owned jerseys with proper structure")
                                    return True
                                else:
                                    self.log_test("Collections Owned Endpoint", "FAIL", "Missing jersey fields in collection items")
                                    return False
                            else:
                                self.log_test("Collections Owned Endpoint", "FAIL", "Missing jersey data in collection items")
                                return False
                        else:
                            self.log_test("Collections Owned Endpoint", "FAIL", "Missing required collection fields")
                            return False
                    else:
                        # Empty collection is valid
                        self.log_test("Collections Owned Endpoint", "PASS", "Retrieved empty owned collection (valid)")
                        return True
                else:
                    self.log_test("Collections Owned Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Collections Owned Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collections Owned Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_wanted_endpoint(self):
        """Test GET /api/collections/wanted with authentication"""
        try:
            if not self.auth_token:
                self.log_test("Collections Wanted Endpoint", "FAIL", "No auth token available")
                return False
            
            print("🎯 TESTING COLLECTIONS/WANTED ENDPOINT")
            
            response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if response.status_code == 200:
                collections = response.json()
                
                # Verify it's a list
                if isinstance(collections, list):
                    # Check if collections have proper structure
                    if len(collections) > 0:
                        # Verify first collection item structure
                        first_item = collections[0]
                        required_fields = ["id", "user_id", "jersey_id", "collection_type", "added_at"]
                        
                        if all(field in first_item for field in required_fields):
                            # Check if jersey data is populated
                            if "jersey" in first_item:
                                jersey_data = first_item["jersey"]
                                jersey_fields = ["id", "team", "season", "status"]
                                
                                if all(field in jersey_data for field in jersey_fields):
                                    self.log_test("Collections Wanted Endpoint", "PASS", 
                                                f"Retrieved {len(collections)} wanted jerseys with proper structure")
                                    return True
                                else:
                                    self.log_test("Collections Wanted Endpoint", "FAIL", "Missing jersey fields in collection items")
                                    return False
                            else:
                                self.log_test("Collections Wanted Endpoint", "FAIL", "Missing jersey data in collection items")
                                return False
                        else:
                            self.log_test("Collections Wanted Endpoint", "FAIL", "Missing required collection fields")
                            return False
                    else:
                        # Empty collection is valid
                        self.log_test("Collections Wanted Endpoint", "PASS", "Retrieved empty wanted collection (valid)")
                        return True
                else:
                    self.log_test("Collections Wanted Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Collections Wanted Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collections Wanted Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_functionality_workflow(self):
        """Test complete collection functionality workflow"""
        try:
            if not self.auth_token:
                self.log_test("Collection Functionality Workflow", "FAIL", "No auth token available")
                return False
            
            print("🎯 TESTING COMPLETE COLLECTION FUNCTIONALITY WORKFLOW")
            
            # Step 1: Get available jerseys to add to collection
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=5")
            
            if jerseys_response.status_code != 200:
                self.log_test("Collection Functionality Workflow", "FAIL", "Could not get jerseys")
                return False
            
            jerseys = jerseys_response.json()
            
            if len(jerseys) == 0:
                self.log_test("Collection Functionality Workflow", "FAIL", "No jerseys available for testing")
                return False
            
            test_jersey = jerseys[0]
            test_jersey_id = test_jersey["id"]
            
            # Step 2: Add jersey to owned collection
            add_payload = {
                "jersey_id": test_jersey_id,
                "collection_type": "owned"
            }
            
            add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            # Step 3: Verify it was added (or already exists)
            if add_response.status_code == 200:
                add_success = True
            elif add_response.status_code == 400 and "already in collection" in add_response.text.lower():
                add_success = True  # Already in collection is fine
            else:
                add_success = False
            
            if not add_success:
                self.log_test("Collection Functionality Workflow", "FAIL", f"Could not add to collection: {add_response.status_code}")
                return False
            
            # Step 4: Verify jersey appears in owned collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code == 200:
                owned_collections = owned_response.json()
                jersey_in_owned = any(item.get('jersey_id') == test_jersey_id for item in owned_collections)
                
                if jersey_in_owned:
                    self.log_test("Collection Functionality Workflow", "PASS", 
                                f"Complete workflow verified - Jersey {test_jersey['team']} {test_jersey['season']} in owned collection")
                    return True
                else:
                    self.log_test("Collection Functionality Workflow", "FAIL", "Jersey not found in owned collection after adding")
                    return False
            else:
                self.log_test("Collection Functionality Workflow", "FAIL", "Could not verify owned collection")
                return False
                
        except Exception as e:
            self.log_test("Collection Functionality Workflow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_token_validation_security(self):
        """Test token validation and security"""
        try:
            print("🎯 TESTING TOKEN VALIDATION AND SECURITY")
            
            # Test with invalid token
            invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
            response = self.session.get(f"{self.base_url}/profile", headers=invalid_headers)
            
            if response.status_code == 401:
                # Test with no token
                original_auth = self.session.headers.get('Authorization')
                if 'Authorization' in self.session.headers:
                    del self.session.headers['Authorization']
                
                no_token_response = self.session.get(f"{self.base_url}/profile")
                
                # Restore auth header
                if original_auth:
                    self.session.headers['Authorization'] = original_auth
                
                if no_token_response.status_code in [401, 403]:
                    self.log_test("Token Validation Security", "PASS", "Invalid and missing tokens correctly rejected")
                    return True
                else:
                    self.log_test("Token Validation Security", "FAIL", f"Missing token not rejected: {no_token_response.status_code}")
                    return False
            else:
                self.log_test("Token Validation Security", "FAIL", f"Invalid token not rejected: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Validation Security", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_phase2_tests(self):
        """Run all Phase 2 backend verification tests"""
        print("=" * 80)
        print("🚀 PHASE 2 BACKEND VERIFICATION - CRITICAL COLLECTION BUG DIAGNOSTIC")
        print("=" * 80)
        print(f"Testing specific user: {SPECIFIC_USER_EMAIL}")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        print()
        
        tests = [
            self.test_specific_user_login,
            self.test_profile_endpoint_with_token,
            self.test_collections_owned_endpoint,
            self.test_collections_wanted_endpoint,
            self.test_collection_functionality_workflow,
            self.test_token_validation_security
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
                failed += 1
            
            print("-" * 40)
        
        print()
        print("=" * 80)
        print("🎯 PHASE 2 BACKEND VERIFICATION RESULTS")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")
        print("=" * 80)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED - BACKEND IS FULLY FUNCTIONAL!")
            print("✅ Authentication system working correctly")
            print("✅ Profile endpoint working correctly")
            print("✅ Collection endpoints working correctly")
            print("✅ Backend collection functionality verified")
            print()
            print("🔍 CONCLUSION: Issue is isolated to frontend authentication state management")
        else:
            print("🚨 SOME TESTS FAILED - BACKEND ISSUES DETECTED")
            print("❌ Backend may have issues that need to be addressed")
        
        print("=" * 80)

def main():
    """Main function to run Phase 2 backend verification"""
    tester = Phase2AuthTester()
    tester.run_phase2_tests()

if __name__ == "__main__":
    main()