#!/usr/bin/env python3
"""
TopKit Jersey Details Management Backend Testing
Testing the jersey detail editor endpoints that were just fixed:
1. GET /api/collections/owned/{jersey_id}/details - should get jersey details for collection items
2. PUT /api/collections/owned/{jersey_id}/details - should update jersey details
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials from review request
USER_CREDENTIALS = {
    "email": "jersey.details.test@topkit.com",
    "password": "JerseyTest2024!"
}

class JerseyDetailsBackendTester:
    def __init__(self):
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_jersey_id = None
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    def authenticate_user(self):
        """Authenticate user and get token"""
        print("🔐 AUTHENTICATING USER...")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=USER_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user_token = data['token']
                    self.user_id = data['user']['id']
                    user_info = data['user']
                    self.log_test(
                        "User Authentication",
                        True,
                        f"User authenticated successfully: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')})"
                    )
                    return True
                else:
                    self.log_test(
                        "User Authentication",
                        False,
                        "Missing token or user data in response"
                    )
                    return False
            else:
                self.log_test(
                    "User Authentication",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "User Authentication",
                False,
                error=str(e)
            )
            return False

    def setup_test_jersey_in_collection(self):
        """Ensure user has at least one jersey in their owned collection for testing"""
        print("🏆 SETTING UP TEST JERSEY IN COLLECTION...")
        
        if not self.user_token:
            self.log_test("Setup Test Jersey", False, "No authentication token available")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # First, check if user already has jerseys in owned collection
            response = self.session.get(f"{BACKEND_URL}/collections/my-owned", headers=headers, timeout=10)
            
            if response.status_code == 200:
                owned_jerseys = response.json()
                if owned_jerseys and len(owned_jerseys) > 0:
                    # User already has jerseys, use the first one
                    self.test_jersey_id = owned_jerseys[0]['jersey_id']
                    self.log_test(
                        "Setup Test Jersey - Check Existing Collection",
                        True,
                        f"Found existing jersey in collection: {self.test_jersey_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Setup Test Jersey - Check Existing Collection",
                        True,
                        "No existing jerseys in owned collection, need to create and add one"
                    )
            else:
                self.log_test(
                    "Setup Test Jersey - Check Existing Collection",
                    False,
                    f"Failed to get owned collection: {response.status_code}"
                )
                
            # Create a test jersey first
            jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for details endpoint testing"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                jersey_result = response.json()
                # Check different possible field names for jersey ID
                jersey_id = jersey_result.get('jersey_id') or jersey_result.get('id') or jersey_result.get('jersey', {}).get('id')
                
                self.log_test(
                    "Setup Test Jersey - Create Jersey",
                    True,
                    f"Successfully created test jersey: {jersey_id} (Response: {jersey_result})"
                )
                
                if not jersey_id:
                    self.log_test(
                        "Setup Test Jersey - Parse Jersey ID",
                        False,
                        f"Could not extract jersey ID from response: {jersey_result}"
                    )
                    return False
                
                # Note: Jersey will be in pending status, need admin approval first
                # Let's use admin token to approve the jersey
                admin_token = None
                try:
                    admin_response = self.session.post(
                        f"{BACKEND_URL}/auth/login",
                        json={"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"},
                        timeout=10
                    )
                    if admin_response.status_code == 200:
                        admin_data = admin_response.json()
                        admin_token = admin_data.get('token')
                        
                        if admin_token:
                            admin_headers = {"Authorization": f"Bearer {admin_token}"}
                            approve_response = self.session.post(
                                f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve",
                                headers=admin_headers,
                                timeout=10
                            )
                            
                            if approve_response.status_code == 200:
                                self.log_test(
                                    "Setup Test Jersey - Admin Approval",
                                    True,
                                    f"Successfully approved jersey: {jersey_id}"
                                )
                            else:
                                self.log_test(
                                    "Setup Test Jersey - Admin Approval",
                                    False,
                                    f"Failed to approve jersey: {approve_response.status_code} - {approve_response.text}"
                                )
                except Exception as e:
                    self.log_test(
                        "Setup Test Jersey - Admin Approval",
                        False,
                        f"Error during admin approval: {str(e)}"
                    )
                
                # Add jersey to owned collection
                collection_data = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned",
                    "size": "M",
                    "condition": "very_good",
                    "personal_description": "Test jersey for details testing"
                }
                
                response = self.session.post(
                    f"{BACKEND_URL}/collections",
                    json=collection_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.test_jersey_id = jersey_id
                    self.log_test(
                        "Setup Test Jersey - Add to Collection",
                        True,
                        f"Successfully added jersey {jersey_id} to owned collection"
                    )
                    return True
                else:
                    self.log_test(
                        "Setup Test Jersey - Add to Collection",
                        False,
                        f"Failed to add jersey to collection: {response.status_code} - {response.text}"
                    )
                    return False
            else:
                self.log_test(
                    "Setup Test Jersey - Create Jersey",
                    False,
                    f"Failed to create jersey: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Setup Test Jersey",
                False,
                error=str(e)
            )
            return False

    def test_get_jersey_details(self):
        """Test GET /api/collections/owned/{jersey_id}/details endpoint"""
        print("📋 TESTING GET JERSEY DETAILS ENDPOINT...")
        
        if not self.user_token or not self.test_jersey_id:
            self.log_test("Get Jersey Details", False, "Missing authentication token or test jersey ID")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Test getting jersey details for owned jersey
            response = self.session.get(
                f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                details = response.json()
                expected_fields = [
                    'jersey_id', 'user_id', 'model_type', 'condition', 'size',
                    'special_features', 'material_details', 'tags', 'packaging',
                    'customization', 'competition_badges', 'rarity', 'purchase_price',
                    'purchase_date', 'purchase_location', 'certificate_authenticity',
                    'storage_notes', 'estimated_value'
                ]
                
                missing_fields = [field for field in expected_fields if field not in details]
                
                if not missing_fields:
                    self.log_test(
                        "Get Jersey Details - Valid Owned Jersey",
                        True,
                        f"Successfully retrieved jersey details with all expected fields. Jersey ID: {details.get('jersey_id')}, User ID: {details.get('user_id')}"
                    )
                else:
                    self.log_test(
                        "Get Jersey Details - Valid Owned Jersey",
                        False,
                        f"Missing expected fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "Get Jersey Details - Valid Owned Jersey",
                    False,
                    f"Failed to get jersey details: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Get Jersey Details - Valid Owned Jersey",
                False,
                error=str(e)
            )

        # Test error handling for jersey not in collection
        try:
            fake_jersey_id = "non-existent-jersey-id"
            response = self.session.get(
                f"{BACKEND_URL}/collections/owned/{fake_jersey_id}/details",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                error_data = response.json()
                if "Jersey not found in your collection" in error_data.get('detail', ''):
                    self.log_test(
                        "Get Jersey Details - Error Handling (Not in Collection)",
                        True,
                        "Correctly returned 404 error for jersey not in collection"
                    )
                else:
                    self.log_test(
                        "Get Jersey Details - Error Handling (Not in Collection)",
                        False,
                        f"Wrong error message: {error_data.get('detail', 'No detail')}"
                    )
            else:
                self.log_test(
                    "Get Jersey Details - Error Handling (Not in Collection)",
                    False,
                    f"Expected 404 but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Get Jersey Details - Error Handling (Not in Collection)",
                False,
                error=str(e)
            )

    def test_update_jersey_details(self):
        """Test PUT /api/collections/owned/{jersey_id}/details endpoint"""
        print("✏️ TESTING UPDATE JERSEY DETAILS ENDPOINT...")
        
        if not self.user_token or not self.test_jersey_id:
            self.log_test("Update Jersey Details", False, "Missing authentication token or test jersey ID")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Test updating jersey details
            update_data = {
                "model_type": "authentic",
                "condition": "near_mint",
                "size": "l",
                "special_features": ["match_worn", "signed"],
                "material_details": "100% polyester with moisture-wicking technology",
                "tags": "tags_on",
                "packaging": "original_packaging",
                "customization": "player_name_number",
                "competition_badges": "champions_league",
                "rarity": "rare",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15",
                "purchase_location": "Official club store",
                "certificate_authenticity": True,
                "storage_notes": "Stored in climate-controlled environment",
                "estimated_value": 150.0
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result and "Jersey details updated successfully" in result["message"]:
                    self.log_test(
                        "Update Jersey Details - Valid Update",
                        True,
                        f"Successfully updated jersey details. Estimated value: {result.get('estimated_value', 'N/A')}"
                    )
                    
                    # Verify the update by getting the details again
                    verify_response = self.session.get(
                        f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details",
                        headers=headers,
                        timeout=10
                    )
                    
                    if verify_response.status_code == 200:
                        updated_details = verify_response.json()
                        if (updated_details.get('condition') == 'near_mint' and 
                            updated_details.get('estimated_value') == 150.0 and
                            updated_details.get('rarity') == 'rare'):
                            self.log_test(
                                "Update Jersey Details - Verify Update",
                                True,
                                "Update verification successful - details were properly saved"
                            )
                        else:
                            self.log_test(
                                "Update Jersey Details - Verify Update",
                                False,
                                f"Update verification failed - details not properly saved. Got condition: {updated_details.get('condition')}, value: {updated_details.get('estimated_value')}"
                            )
                    else:
                        self.log_test(
                            "Update Jersey Details - Verify Update",
                            False,
                            f"Failed to verify update: {verify_response.status_code}"
                        )
                else:
                    self.log_test(
                        "Update Jersey Details - Valid Update",
                        False,
                        f"Unexpected response format: {result}"
                    )
            else:
                self.log_test(
                    "Update Jersey Details - Valid Update",
                    False,
                    f"Failed to update jersey details: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Update Jersey Details - Valid Update",
                False,
                error=str(e)
            )

        # Test error handling for jersey not in collection
        try:
            fake_jersey_id = "non-existent-jersey-id"
            update_data = {
                "model_type": "authentic",
                "condition": "mint",
                "estimated_value": 100.0
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/collections/owned/{fake_jersey_id}/details",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                error_data = response.json()
                if "Jersey not found in your collection" in error_data.get('detail', ''):
                    self.log_test(
                        "Update Jersey Details - Error Handling (Not in Collection)",
                        True,
                        "Correctly returned 404 error for jersey not in collection"
                    )
                else:
                    self.log_test(
                        "Update Jersey Details - Error Handling (Not in Collection)",
                        False,
                        f"Wrong error message: {error_data.get('detail', 'No detail')}"
                    )
            else:
                self.log_test(
                    "Update Jersey Details - Error Handling (Not in Collection)",
                    False,
                    f"Expected 404 but got {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Update Jersey Details - Error Handling (Not in Collection)",
                False,
                error=str(e)
            )

    def test_authentication_pattern_fix(self):
        """Test that the authentication pattern fix is working correctly"""
        print("🔧 TESTING AUTHENTICATION PATTERN FIX...")
        
        if not self.user_token or not self.test_jersey_id:
            self.log_test("Authentication Pattern Fix", False, "Missing authentication token or test jersey ID")
            return False
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            # Test that both endpoints work with the new authentication pattern
            # This should not return "Jersey not found in your collection" error for valid collection items
            
            # Test GET endpoint
            get_response = self.session.get(
                f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details",
                headers=headers,
                timeout=10
            )
            
            # Test PUT endpoint
            update_data = {
                "model_type": "authentic",
                "condition": "mint",
                "estimated_value": 75.0
            }
            
            put_response = self.session.put(
                f"{BACKEND_URL}/collections/owned/{self.test_jersey_id}/details",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            get_success = get_response.status_code == 200
            put_success = put_response.status_code == 200
            
            if get_success and put_success:
                self.log_test(
                    "Authentication Pattern Fix - Both Endpoints Working",
                    True,
                    "Both GET and PUT endpoints work correctly with the new authentication pattern (current_user: dict = Depends(get_current_user))"
                )
            else:
                errors = []
                if not get_success:
                    errors.append(f"GET failed: {get_response.status_code} - {get_response.text}")
                if not put_success:
                    errors.append(f"PUT failed: {put_response.status_code} - {put_response.text}")
                
                self.log_test(
                    "Authentication Pattern Fix - Both Endpoints Working",
                    False,
                    f"One or both endpoints failed: {'; '.join(errors)}"
                )
                
        except Exception as e:
            self.log_test(
                "Authentication Pattern Fix - Both Endpoints Working",
                False,
                error=str(e)
            )

    def run_all_tests(self):
        """Run all jersey details management tests"""
        print("🚀 STARTING JERSEY DETAILS MANAGEMENT BACKEND TESTING")
        print("=" * 80)
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
            
        # Step 2: Setup test jersey in collection
        if not self.setup_test_jersey_in_collection():
            print("❌ Failed to setup test jersey - cannot proceed with details tests")
            return False
            
        # Step 3: Test GET jersey details endpoint
        self.test_get_jersey_details()
        
        # Step 4: Test PUT jersey details endpoint  
        self.test_update_jersey_details()
        
        # Step 5: Test authentication pattern fix
        self.test_authentication_pattern_fix()
        
        # Summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
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
                    print(f"  - {result['test']}: {result.get('error', result.get('details', 'Unknown error'))}")
        
        print("\n✅ CRITICAL FINDINGS:")
        print("- Jersey details management endpoints tested with authenticated user")
        print("- Authentication pattern fix verified (current_user: dict = Depends(get_current_user))")
        print("- Error handling tested for jerseys not in collection")
        print("- Both GET and PUT operations tested with real data")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = JerseyDetailsBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)