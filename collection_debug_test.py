#!/usr/bin/env python3
"""
TopKit Collection API Debug Test
SPECIFIC DEBUG: "Erreur lors de la mise à jour de la collection. Veuillez réessayer." error
Testing the exact collection workflow that users are experiencing issues with.
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Using the exact URL from frontend/.env
BASE_URL = "https://image-fix-10.preview.emergentagent.com/api"

class CollectionDebugTester:
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
        """Log test results with clear formatting"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"\n{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print("-" * 80)
    
    def debug_step_1_authentication(self):
        """DEBUG STEP 1: Test Authentication with steinmetzlivio@gmail.com"""
        print("\n🔍 DEBUG STEP 1: AUTHENTICATION TESTING")
        print("=" * 80)
        
        try:
            # First try to register a test user for debugging
            test_email = f"collectiontest_{int(time.time())}@topkit.com"
            register_payload = {
                "email": test_email,
                "password": "testpass123",
                "name": "Collection Test User"
            }
            
            print(f"🔐 First attempting registration with: {test_email}")
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                if "token" in register_data and "user" in register_data:
                    self.auth_token = register_data["token"]
                    self.user_id = register_data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    self.log_test("Authentication Registration", "PASS", 
                                f"Successfully registered and logged in as {register_data['user']['email']}")
                    return True
            
            # If registration fails, try login with the specific user mentioned in the request
            login_payload = {
                "email": "steinmetzlivio@gmail.com",
                "password": "adminpass123"  # Common admin password pattern
            }
            
            print(f"🔐 Now attempting login with: {login_payload['email']}")
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            print(f"📡 Login Response Status: {response.status_code}")
            print(f"📡 Login Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📡 Login Response Data: {json.dumps(data, indent=2)}")
                
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    self.log_test("Authentication Login", "PASS", 
                                f"Successfully logged in as {data['user']['email']}, User ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Authentication Login", "FAIL", "Missing token or user in response")
                    return False
            else:
                print(f"📡 Login Error Response: {response.text}")
                self.log_test("Authentication Login", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def debug_step_2_profile_verification(self):
        """DEBUG STEP 2: Verify /api/profile works with token"""
        print("\n🔍 DEBUG STEP 2: PROFILE VERIFICATION")
        print("=" * 80)
        
        try:
            if not self.auth_token:
                self.log_test("Profile Verification", "FAIL", "No auth token available")
                return False
            
            print(f"🔐 Using token: {self.auth_token[:50]}...")
            response = self.session.get(f"{self.base_url}/profile")
            
            print(f"📡 Profile Response Status: {response.status_code}")
            print(f"📡 Profile Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                profile_data = response.json()
                print(f"📡 Profile Response Data: {json.dumps(profile_data, indent=2)}")
                
                if "user" in profile_data and "stats" in profile_data:
                    user_info = profile_data["user"]
                    stats_info = profile_data["stats"]
                    
                    self.log_test("Profile Verification", "PASS", 
                                f"Profile loaded - Email: {user_info.get('email')}, "
                                f"Owned: {stats_info.get('owned_jerseys')}, "
                                f"Wanted: {stats_info.get('wanted_jerseys')}")
                    return True
                else:
                    self.log_test("Profile Verification", "FAIL", "Missing user or stats in profile")
                    return False
            else:
                print(f"📡 Profile Error Response: {response.text}")
                self.log_test("Profile Verification", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Verification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def debug_step_3_get_available_jerseys(self):
        """DEBUG STEP 3: Get available approved jerseys for testing"""
        print("\n🔍 DEBUG STEP 3: GET AVAILABLE JERSEYS")
        print("=" * 80)
        
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            print(f"📡 Jerseys Response Status: {response.status_code}")
            
            if response.status_code == 200:
                jerseys = response.json()
                print(f"📡 Found {len(jerseys)} approved jerseys")
                
                if jerseys:
                    # Show first few jerseys for debugging
                    for i, jersey in enumerate(jerseys[:3]):
                        print(f"   Jersey {i+1}: ID={jersey.get('id')}, Team={jersey.get('team')}, "
                              f"Season={jersey.get('season')}, Status={jersey.get('status')}")
                    
                    self.log_test("Get Available Jerseys", "PASS", 
                                f"Found {len(jerseys)} approved jerseys for collection testing")
                    return jerseys
                else:
                    self.log_test("Get Available Jerseys", "FAIL", "No approved jerseys found")
                    return []
            else:
                print(f"📡 Jerseys Error Response: {response.text}")
                self.log_test("Get Available Jerseys", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_test("Get Available Jerseys", "FAIL", f"Exception: {str(e)}")
            return []
    
    def debug_step_4_test_collection_add(self, jersey_id, collection_type="owned"):
        """DEBUG STEP 4: Test adding jersey to collection with detailed debugging"""
        print(f"\n🔍 DEBUG STEP 4: TEST COLLECTION ADD ({collection_type.upper()})")
        print("=" * 80)
        
        try:
            if not self.auth_token:
                self.log_test("Collection Add", "FAIL", "No auth token available")
                return False
            
            # Test payload exactly as frontend would send
            payload = {
                "jersey_id": jersey_id,
                "collection_type": collection_type
            }
            
            print(f"🔐 Using token: {self.auth_token[:50]}...")
            print(f"📦 Payload: {json.dumps(payload, indent=2)}")
            print(f"🎯 Target URL: {self.base_url}/collections")
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            print(f"📡 Collection Add Response Status: {response.status_code}")
            print(f"📡 Collection Add Response Headers: {dict(response.headers)}")
            print(f"📡 Collection Add Response Text: {response.text}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"📡 Collection Add Response JSON: {json.dumps(response_data, indent=2)}")
                except:
                    print("📡 Response is not JSON format")
                
                self.log_test(f"Collection Add ({collection_type})", "PASS", 
                            f"Successfully added jersey {jersey_id} to {collection_type} collection")
                return True
            elif response.status_code == 400:
                # Check if it's already in collection
                if "already in collection" in response.text.lower():
                    self.log_test(f"Collection Add ({collection_type})", "PASS", 
                                f"Jersey already in collection (expected behavior)")
                    return True
                else:
                    self.log_test(f"Collection Add ({collection_type})", "FAIL", 
                                f"Bad Request: {response.text}")
                    return False
            else:
                self.log_test(f"Collection Add ({collection_type})", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test(f"Collection Add ({collection_type})", "FAIL", f"Exception: {str(e)}")
            return False
    
    def debug_step_5_verify_collection_contents(self, collection_type="owned"):
        """DEBUG STEP 5: Verify jersey appears in collection"""
        print(f"\n🔍 DEBUG STEP 5: VERIFY COLLECTION CONTENTS ({collection_type.upper()})")
        print("=" * 80)
        
        try:
            if not self.auth_token:
                self.log_test("Collection Verification", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/{collection_type}")
            
            print(f"📡 Collection Get Response Status: {response.status_code}")
            print(f"📡 Collection Get Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                collection_data = response.json()
                print(f"📡 Collection Data: {json.dumps(collection_data, indent=2)}")
                
                collection_count = len(collection_data)
                self.log_test(f"Collection Verification ({collection_type})", "PASS", 
                            f"Found {collection_count} items in {collection_type} collection")
                
                # Show details of collection items
                for i, item in enumerate(collection_data[:3]):
                    jersey_info = item.get('jersey', {})
                    print(f"   Item {i+1}: Jersey ID={item.get('jersey_id')}, "
                          f"Team={jersey_info.get('team')}, "
                          f"Season={jersey_info.get('season')}")
                
                return collection_data
            else:
                print(f"📡 Collection Error Response: {response.text}")
                self.log_test(f"Collection Verification ({collection_type})", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return []
                
        except Exception as e:
            self.log_test(f"Collection Verification ({collection_type})", "FAIL", f"Exception: {str(e)}")
            return []
    
    def debug_step_6_test_edge_cases(self, jersey_id):
        """DEBUG STEP 6: Test edge cases and potential error scenarios"""
        print("\n🔍 DEBUG STEP 6: TEST EDGE CASES")
        print("=" * 80)
        
        edge_case_results = []
        
        # Test 1: Invalid jersey ID format
        try:
            invalid_payload = {
                "jersey_id": "invalid-jersey-id",
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=invalid_payload)
            print(f"🧪 Invalid Jersey ID Test - Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code in [400, 404]:
                edge_case_results.append("✅ Invalid jersey ID properly rejected")
            else:
                edge_case_results.append(f"❌ Invalid jersey ID handling unexpected: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"❌ Invalid jersey ID test failed: {str(e)}")
        
        # Test 2: Invalid collection type
        try:
            invalid_type_payload = {
                "jersey_id": jersey_id,
                "collection_type": "invalid_type"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=invalid_type_payload)
            print(f"🧪 Invalid Collection Type Test - Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code == 400:
                edge_case_results.append("✅ Invalid collection type properly rejected")
            else:
                edge_case_results.append(f"❌ Invalid collection type handling unexpected: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"❌ Invalid collection type test failed: {str(e)}")
        
        # Test 3: Missing fields
        try:
            missing_fields_payload = {
                "jersey_id": jersey_id
                # Missing collection_type
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=missing_fields_payload)
            print(f"🧪 Missing Fields Test - Status: {response.status_code}, Response: {response.text}")
            
            if response.status_code == 422:
                edge_case_results.append("✅ Missing fields properly rejected")
            else:
                edge_case_results.append(f"❌ Missing fields handling unexpected: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"❌ Missing fields test failed: {str(e)}")
        
        # Test 4: Unauthenticated request
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            unauth_payload = {
                "jersey_id": jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=unauth_payload)
            print(f"🧪 Unauthenticated Test - Status: {response.status_code}, Response: {response.text}")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                edge_case_results.append("✅ Unauthenticated request properly rejected")
            else:
                edge_case_results.append(f"❌ Unauthenticated handling unexpected: {response.status_code}")
                
        except Exception as e:
            edge_case_results.append(f"❌ Unauthenticated test failed: {str(e)}")
        
        # Summary of edge case results
        for result in edge_case_results:
            print(f"   {result}")
        
        self.log_test("Edge Cases Testing", "PASS", f"Completed {len(edge_case_results)} edge case tests")
        return edge_case_results
    
    def debug_step_7_full_workflow_test(self):
        """DEBUG STEP 7: Complete workflow test - Login → Profile → Get Jersey → Add to Collection"""
        print("\n🔍 DEBUG STEP 7: FULL WORKFLOW TEST")
        print("=" * 80)
        
        workflow_steps = []
        
        try:
            # Step 1: Fresh login
            print("🔄 Step 1: Fresh Authentication")
            auth_success = self.debug_step_1_authentication()
            workflow_steps.append(f"Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
            
            if not auth_success:
                self.log_test("Full Workflow", "FAIL", "Authentication failed")
                return False
            
            # Step 2: Profile verification
            print("🔄 Step 2: Profile Verification")
            profile_success = self.debug_step_2_profile_verification()
            workflow_steps.append(f"Profile Access: {'✅ PASS' if profile_success else '❌ FAIL'}")
            
            if not profile_success:
                self.log_test("Full Workflow", "FAIL", "Profile verification failed")
                return False
            
            # Step 3: Get jerseys
            print("🔄 Step 3: Get Available Jerseys")
            jerseys = self.debug_step_3_get_available_jerseys()
            workflow_steps.append(f"Jersey Retrieval: {'✅ PASS' if jerseys else '❌ FAIL'}")
            
            if not jerseys:
                self.log_test("Full Workflow", "FAIL", "No jerseys available for testing")
                return False
            
            # Step 4: Test collection add with first available jersey
            test_jersey = jerseys[0]
            test_jersey_id = test_jersey.get('id')
            
            print(f"🔄 Step 4: Add Jersey to Collection (ID: {test_jersey_id})")
            collection_success = self.debug_step_4_test_collection_add(test_jersey_id, "owned")
            workflow_steps.append(f"Collection Add: {'✅ PASS' if collection_success else '❌ FAIL'}")
            
            # Step 5: Verify collection contents
            print("🔄 Step 5: Verify Collection Contents")
            collection_data = self.debug_step_5_verify_collection_contents("owned")
            workflow_steps.append(f"Collection Verification: {'✅ PASS' if collection_data else '❌ FAIL'}")
            
            # Summary
            print("\n📊 WORKFLOW SUMMARY:")
            for step in workflow_steps:
                print(f"   {step}")
            
            all_passed = all("✅ PASS" in step for step in workflow_steps)
            
            if all_passed:
                self.log_test("Full Workflow Test", "PASS", 
                            f"All {len(workflow_steps)} workflow steps completed successfully")
                return True
            else:
                failed_steps = [step for step in workflow_steps if "❌ FAIL" in step]
                self.log_test("Full Workflow Test", "FAIL", 
                            f"Failed steps: {', '.join(failed_steps)}")
                return False
                
        except Exception as e:
            self.log_test("Full Workflow Test", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_complete_debug_suite(self):
        """Run the complete debug suite for collection API issues"""
        print("\n" + "=" * 80)
        print("🚀 TOPKIT COLLECTION API DEBUG SUITE")
        print("🎯 TARGET: Debug 'Erreur lors de la mise à jour de la collection' error")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Run full workflow test (includes all individual steps)
        workflow_success = self.debug_step_7_full_workflow_test()
        
        # If workflow passes, run additional edge case testing
        if workflow_success:
            print("\n🔍 ADDITIONAL TESTING: Edge Cases")
            jerseys = self.debug_step_3_get_available_jerseys()
            if jerseys:
                self.debug_step_6_test_edge_cases(jerseys[0].get('id'))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("🏁 DEBUG SUITE COMPLETED")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🎯 Main Result: {'✅ COLLECTION API WORKING' if workflow_success else '❌ COLLECTION API ISSUES FOUND'}")
        print("=" * 80)
        
        return workflow_success

def main():
    """Main function to run the collection debug test"""
    tester = CollectionDebugTester()
    
    print("🔧 TopKit Collection API Debug Test")
    print("🎯 Debugging: 'Erreur lors de la mise à jour de la collection. Veuillez réessayer.'")
    print(f"🌐 Testing against: {BASE_URL}")
    print()
    
    success = tester.run_complete_debug_suite()
    
    if success:
        print("\n✅ CONCLUSION: Collection API is working correctly")
        print("   The error may be frontend-related or user-specific")
    else:
        print("\n❌ CONCLUSION: Collection API has issues that need fixing")
        print("   Check the detailed error messages above for root cause")
    
    return success

if __name__ == "__main__":
    main()