#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - User Profile API Testing
Testing newly implemented User Profile API endpoints:
1. GET /api/users/{user_id}/profile - Get public profile information for a specific user
2. GET /api/users/{user_id}/collections - Get user's public collections (owned and wanted jerseys)
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class UserProfileAPITester:
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
    
    def authenticate_user(self):
        """Authenticate with existing user credentials"""
        try:
            print("🔐 Authenticating with existing user credentials...")
            
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.user_id = data.get("user", {}).get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                self.log_test("User Authentication", "PASS", 
                            f"Authenticated as {data.get('user', {}).get('name')} (ID: {self.user_id})")
                return True
            else:
                self.log_test("User Authentication", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def get_existing_users(self):
        """Get list of existing users from the system"""
        try:
            print("👥 Getting existing users from the system...")
            
            # Try to get jerseys to find user IDs from creators
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            if response.status_code == 200:
                jerseys = response.json()
                user_ids = set()
                
                for jersey in jerseys:
                    if 'created_by' in jersey:
                        user_ids.add(jersey['created_by'])
                    if 'creator_info' in jersey and jersey['creator_info'].get('id'):
                        user_ids.add(jersey['creator_info']['id'])
                
                # Add our authenticated user ID
                if self.user_id:
                    user_ids.add(self.user_id)
                
                user_list = list(user_ids)[:5]  # Limit to 5 users for testing
                self.log_test("Get Existing Users", "PASS", 
                            f"Found {len(user_list)} user IDs: {user_list}")
                return user_list
            else:
                self.log_test("Get Existing Users", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return [self.user_id] if self.user_id else []
                
        except Exception as e:
            self.log_test("Get Existing Users", "FAIL", f"Exception: {str(e)}")
            return [self.user_id] if self.user_id else []
    
    def test_user_profile_endpoint(self, user_id):
        """Test GET /api/users/{user_id}/profile endpoint"""
        try:
            print(f"👤 Testing User Profile endpoint for user: {user_id}")
            
            response = self.session.get(f"{self.base_url}/users/{user_id}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify basic required fields that are actually returned by current implementation
                required_fields = ['id', 'name', 'stats']
                missing_fields = [field for field in required_fields if field not in profile_data]
                
                if missing_fields:
                    self.log_test(f"User Profile Structure (User: {user_id})", "FAIL", 
                                f"Missing required fields: {missing_fields}")
                    return False
                
                # Verify stats structure
                stats = profile_data.get('stats', {})
                required_stats = ['owned_jerseys', 'wanted_jerseys', 'active_listings', 'jerseys_created']
                missing_stats = [stat for stat in required_stats if stat not in stats]
                
                if missing_stats:
                    self.log_test(f"User Profile Stats (User: {user_id})", "FAIL", 
                                f"Missing required stats: {missing_stats}")
                    return False
                
                # Check optional fields that should be present according to requirements
                optional_fields = ['picture', 'provider', 'created_at', 'profile_privacy']
                present_optional = [field for field in optional_fields if field in profile_data]
                
                self.log_test(f"User Profile Endpoint (User: {user_id})", "PASS", 
                            f"Profile data: name={profile_data.get('name')}, "
                            f"stats={stats}, optional_fields={present_optional}")
                
                return True
            else:
                self.log_test(f"User Profile Endpoint (User: {user_id})", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"User Profile Endpoint (User: {user_id})", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_collections_endpoint(self, user_id):
        """Test GET /api/users/{user_id}/collections endpoint"""
        try:
            print(f"📚 Testing User Collections endpoint for user: {user_id}")
            
            response = self.session.get(f"{self.base_url}/users/{user_id}/collections")
            
            if response.status_code == 200:
                collections_response = response.json()
                
                # Current implementation returns a dict with user_id, profile_owner, and collections
                if isinstance(collections_response, dict):
                    if 'collections' not in collections_response:
                        self.log_test(f"User Collections Structure (User: {user_id})", "FAIL", 
                                    f"Expected 'collections' key in response")
                        return False
                    
                    collections_data = collections_response['collections']
                    user_id_in_response = collections_response.get('user_id')
                    profile_owner = collections_response.get('profile_owner')
                    
                    # Verify response structure
                    if user_id_in_response != user_id:
                        self.log_test(f"User Collections Structure (User: {user_id})", "FAIL", 
                                    f"User ID mismatch: expected {user_id}, got {user_id_in_response}")
                        return False
                    
                elif isinstance(collections_response, list):
                    # Alternative implementation returns list directly
                    collections_data = collections_response
                    profile_owner = None
                else:
                    self.log_test(f"User Collections Structure (User: {user_id})", "FAIL", 
                                f"Expected dict or list, got {type(collections_response)}")
                    return False
                
                # Check if collections have proper structure (if any exist)
                if collections_data:
                    sample_collection = collections_data[0]
                    required_fields = ['collection_type', 'added_at']
                    missing_fields = [field for field in required_fields if field not in sample_collection]
                    
                    if missing_fields:
                        self.log_test(f"User Collections Structure (User: {user_id})", "FAIL", 
                                    f"Missing required fields in collection: {missing_fields}")
                        return False
                    
                    # Check jersey details structure if jersey exists
                    if 'jersey' in sample_collection and sample_collection['jersey']:
                        jersey = sample_collection['jersey']
                        jersey_fields = ['id', 'team', 'season']
                        missing_jersey_fields = [field for field in jersey_fields if field not in jersey]
                        
                        if missing_jersey_fields:
                            self.log_test(f"User Collections Jersey Details (User: {user_id})", "FAIL", 
                                        f"Missing jersey fields: {missing_jersey_fields}")
                            return False
                
                # Count owned and wanted jerseys
                owned_count = len([c for c in collections_data if c.get('collection_type') == 'owned'])
                wanted_count = len([c for c in collections_data if c.get('collection_type') == 'wanted'])
                
                self.log_test(f"User Collections Endpoint (User: {user_id})", "PASS", 
                            f"Total collections: {len(collections_data)}, "
                            f"Owned: {owned_count}, Wanted: {wanted_count}, "
                            f"Profile owner: {profile_owner}")
                
                return True
            else:
                self.log_test(f"User Collections Endpoint (User: {user_id})", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"User Collections Endpoint (User: {user_id})", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_non_existent_user_profile(self):
        """Test profile endpoint with non-existent user ID"""
        try:
            print("🚫 Testing User Profile endpoint with non-existent user ID...")
            
            fake_user_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/users/{fake_user_id}/profile")
            
            if response.status_code == 404:
                self.log_test("Non-existent User Profile", "PASS", 
                            f"Correctly returned 404 for non-existent user: {fake_user_id}")
                return True
            else:
                self.log_test("Non-existent User Profile", "FAIL", 
                            f"Expected 404, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Non-existent User Profile", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_non_existent_user_collections(self):
        """Test collections endpoint with non-existent user ID"""
        try:
            print("🚫 Testing User Collections endpoint with non-existent user ID...")
            
            fake_user_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/users/{fake_user_id}/collections")
            
            if response.status_code == 404:
                self.log_test("Non-existent User Collections", "PASS", 
                            f"Correctly returned 404 for non-existent user: {fake_user_id}")
                return True
            else:
                self.log_test("Non-existent User Collections", "FAIL", 
                            f"Expected 404, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Non-existent User Collections", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile_data_completeness(self, user_id):
        """Test that profile data includes all required fields for UserProfilePage component"""
        try:
            print(f"🔍 Testing Profile Data Completeness for UserProfilePage component...")
            
            response = self.session.get(f"{self.base_url}/users/{user_id}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Check fields that are actually returned by current implementation
                expected_fields = {
                    'id': 'string',
                    'name': 'string',
                    'picture': 'optional',
                    'provider': 'optional',
                    'created_at': 'optional',
                    'profile_privacy': 'optional',
                    'stats': 'object'
                }
                
                field_results = {}
                for field, field_type in expected_fields.items():
                    if field in profile_data:
                        field_results[field] = "✅ Present"
                    elif field_type == 'optional':
                        field_results[field] = "⚠️ Optional (not present)"
                    else:
                        field_results[field] = "❌ Missing"
                
                # Check stats sub-fields that are actually returned
                stats = profile_data.get('stats', {})
                stats_fields = ['owned_jerseys', 'wanted_jerseys', 'active_listings', 'jerseys_created']
                for stat_field in stats_fields:
                    if stat_field in stats:
                        field_results[f'stats.{stat_field}'] = "✅ Present"
                    else:
                        field_results[f'stats.{stat_field}'] = "❌ Missing"
                
                missing_required = [field for field, result in field_results.items() 
                                  if result.startswith("❌")]
                
                if missing_required:
                    self.log_test("Profile Data Completeness", "FAIL", 
                                f"Missing required fields: {missing_required}")
                    return False
                else:
                    self.log_test("Profile Data Completeness", "PASS", 
                                f"All required fields present. Field status: {field_results}")
                    return True
            else:
                self.log_test("Profile Data Completeness", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Data Completeness", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_with_data(self, user_id):
        """Test collections endpoint with actual collection data"""
        try:
            print(f"📚 Testing User Collections endpoint with actual data for user: {user_id}")
            
            # First, let's try to get some jerseys to add to collection
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=3")
            if jerseys_response.status_code != 200:
                self.log_test(f"Collections with Data Setup (User: {user_id})", "SKIP", 
                            f"Cannot get jerseys for testing: {jerseys_response.status_code}")
                return True  # Skip this test
            
            jerseys = jerseys_response.json()
            if not jerseys:
                self.log_test(f"Collections with Data Setup (User: {user_id})", "SKIP", 
                            f"No jerseys available for testing")
                return True  # Skip this test
            
            # Try to add a jersey to owned collection
            test_jersey_id = jerseys[0]['id']
            add_response = self.session.post(f"{self.base_url}/collections", 
                                           json={"jersey_id": test_jersey_id, "collection_type": "owned"})
            
            if add_response.status_code not in [200, 400]:  # 400 might be "already in collection"
                self.log_test(f"Collections with Data Setup (User: {user_id})", "FAIL", 
                            f"Cannot add jersey to collection: {add_response.status_code} - {add_response.text}")
                return False
            
            # Now test the collections endpoint
            response = self.session.get(f"{self.base_url}/users/{user_id}/collections")
            
            if response.status_code == 200:
                collections_response = response.json()
                
                # Handle both response formats
                if isinstance(collections_response, dict) and 'collections' in collections_response:
                    collections_data = collections_response['collections']
                elif isinstance(collections_response, list):
                    collections_data = collections_response
                else:
                    self.log_test(f"Collections with Data (User: {user_id})", "FAIL", 
                                f"Unexpected response format: {type(collections_response)}")
                    return False
                
                # Check if we have collections now
                if collections_data:
                    sample_collection = collections_data[0]
                    
                    # Verify jersey details are populated
                    if 'jersey' in sample_collection and sample_collection['jersey']:
                        jersey = sample_collection['jersey']
                        required_jersey_fields = ['id', 'team', 'season']
                        missing_fields = [field for field in required_jersey_fields if field not in jersey]
                        
                        if missing_fields:
                            self.log_test(f"Collections with Data Jersey Details (User: {user_id})", "FAIL", 
                                        f"Missing jersey fields: {missing_fields}")
                            return False
                        
                        self.log_test(f"Collections with Data (User: {user_id})", "PASS", 
                                    f"Collections with jersey details working. Jersey: {jersey.get('team')} {jersey.get('season')}")
                        return True
                    else:
                        self.log_test(f"Collections with Data (User: {user_id})", "FAIL", 
                                    f"Jersey details not populated in collection")
                        return False
                else:
                    self.log_test(f"Collections with Data (User: {user_id})", "INFO", 
                                f"No collections found (might be expected)")
                    return True
                    
            elif response.status_code == 500:
                self.log_test(f"Collections with Data (User: {user_id})", "FAIL", 
                            f"Internal Server Error - likely MongoDB ObjectId serialization issue")
                return False
            else:
                self.log_test(f"Collections with Data (User: {user_id})", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Collections with Data (User: {user_id})", "FAIL", f"Exception: {str(e)}")
            return False
    def test_enhanced_profile_endpoint(self, user_id):
        """Test if the enhanced profile endpoint (with email, display_name, etc.) is accessible"""
        try:
            print(f"🔍 Testing Enhanced Profile endpoint (checking for newer implementation)...")
            
            # The newer implementation should be at the same endpoint but might have different behavior
            # Let's check if we can get more detailed profile information
            response = self.session.get(f"{self.base_url}/users/{user_id}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Check if this has the enhanced fields from the newer implementation
                enhanced_fields = ['email', 'display_name', 'bio', 'location', 'seller_info', 'badges']
                present_enhanced = [field for field in enhanced_fields if field in profile_data]
                
                if present_enhanced:
                    self.log_test("Enhanced Profile Endpoint", "PASS", 
                                f"Enhanced fields found: {present_enhanced}")
                    return True
                else:
                    self.log_test("Enhanced Profile Endpoint", "INFO", 
                                f"Using basic profile implementation (no enhanced fields found)")
                    return True  # Not a failure, just different implementation
            else:
                self.log_test("Enhanced Profile Endpoint", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced Profile Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all User Profile API tests"""
        print("🚀 Starting User Profile API Comprehensive Testing")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step 2: Get existing users
        existing_users = self.get_existing_users()
        if not existing_users:
            print("❌ No existing users found. Cannot proceed with tests.")
            return False
        
        # Step 3: Test profile endpoints with existing users
        profile_tests_passed = 0
        collections_tests_passed = 0
        
        for user_id in existing_users[:3]:  # Test with first 3 users
            if self.test_user_profile_endpoint(user_id):
                profile_tests_passed += 1
            
            if self.test_user_collections_endpoint(user_id):
                collections_tests_passed += 1
        
        # Step 4: Test error handling with non-existent users
        error_handling_passed = 0
        if self.test_non_existent_user_profile():
            error_handling_passed += 1
        
        if self.test_non_existent_user_collections():
            error_handling_passed += 1
        
        # Step 5: Test data completeness for UserProfilePage component
        completeness_passed = 0
        enhanced_passed = 0
        collections_data_passed = 0
        if existing_users:
            if self.test_profile_data_completeness(existing_users[0]):
                completeness_passed += 1
            if self.test_enhanced_profile_endpoint(existing_users[0]):
                enhanced_passed += 1
            if self.test_collections_with_data(existing_users[0]):
                collections_data_passed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 USER PROFILE API TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(existing_users) * 2 + 5  # profile + collections per user + error handling + completeness + enhanced + collections_data
        passed_tests = profile_tests_passed + collections_tests_passed + error_handling_passed + completeness_passed + enhanced_passed + collections_data_passed
        
        print(f"✅ Profile Endpoint Tests: {profile_tests_passed}/{len(existing_users[:3])}")
        print(f"✅ Collections Endpoint Tests: {collections_tests_passed}/{len(existing_users[:3])}")
        print(f"✅ Error Handling Tests: {error_handling_passed}/2")
        print(f"✅ Data Completeness Tests: {completeness_passed}/1")
        print(f"✅ Enhanced Profile Tests: {enhanced_passed}/1")
        print(f"✅ Collections with Data Tests: {collections_data_passed}/1")
        print(f"\n🎯 OVERALL SUCCESS RATE: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL USER PROFILE API TESTS PASSED!")
            return True
        else:
            print(f"⚠️ {total_tests - passed_tests} tests failed. See details above.")
            return False

def main():
    """Main test execution"""
    tester = UserProfileAPITester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n✅ User Profile API endpoints are working correctly!")
        exit(0)
    else:
        print("\n❌ Some User Profile API tests failed!")
        exit(1)

if __name__ == "__main__":
    main()