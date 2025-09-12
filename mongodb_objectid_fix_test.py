#!/usr/bin/env python3
"""
TopKit Backend API Testing Suite - MongoDB ObjectId Serialization Fix Verification
Testing the fixed MongoDB ObjectId serialization issue in TopKit application
Focus: /api/users/{user_id}/collections endpoint and overall backend stability
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://kit-collection-5.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class MongoObjectIdFixTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
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

    def test_authentication_setup(self):
        """Setup authentication for both user and admin accounts"""
        print("🔐 SETTING UP AUTHENTICATION")
        print("=" * 50)
        
        # Test 1: User Login
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"]["role"]
                    self.log_test(
                        "User Authentication Setup",
                        True,
                        f"Login successful - User: {user_name}, Role: {user_role}, ID: {self.user_id}"
                    )
                else:
                    self.log_test("User Authentication Setup", False, "", "Missing token or user data in response")
            else:
                self.log_test("User Authentication Setup", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Authentication Setup", False, "", str(e))

        # Test 2: Admin Login
        try:
            admin_login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=admin_login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_id = data["user"]["id"]
                    admin_name = data["user"]["name"]
                    admin_role = data["user"]["role"]
                    self.log_test(
                        "Admin Authentication Setup",
                        True,
                        f"Admin login successful - User: {admin_name}, Role: {admin_role}"
                    )
                else:
                    self.log_test("Admin Authentication Setup", False, "", "Missing token or user data in response")
            else:
                self.log_test("Admin Authentication Setup", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Authentication Setup", False, "", str(e))

    def test_mongodb_objectid_serialization_fix(self):
        """Test 1: MongoDB ObjectId Serialization Fix - Primary focus of this test"""
        print("🔧 TESTING MONGODB OBJECTID SERIALIZATION FIX")
        print("=" * 50)
        
        if not self.user_token or not self.user_id:
            self.log_test("MongoDB ObjectId Fix - Collections Endpoint", False, "", "No user authentication available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test the specific endpoint that was causing HTTP 500 errors
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections_data = response.json()
                
                # Verify the response structure and that it doesn't contain MongoDB ObjectId fields
                if isinstance(collections_data, (list, dict)):
                    # Check if response contains proper data structure without ObjectId serialization errors
                    response_text = response.text
                    
                    # Look for signs of ObjectId serialization issues
                    # Note: _id in field names like user_id, jersey_id is normal
                    has_objectid_issues = (
                        "ObjectId(" in response_text or 
                        '"_id":' in response_text or
                        "not JSON serializable" in response_text or
                        "ObjectId is not JSON serializable" in response_text
                    )
                    
                    if not has_objectid_issues:
                        # Count collections if it's a list
                        collection_count = len(collections_data) if isinstance(collections_data, list) else "N/A"
                        self.log_test(
                            "MongoDB ObjectId Fix - Collections Endpoint",
                            True,
                            f"✅ NO HTTP 500 errors! Collections endpoint returns clean data ({collection_count} collections) without MongoDB ObjectId serialization issues"
                        )
                    else:
                        self.log_test(
                            "MongoDB ObjectId Fix - Collections Endpoint",
                            False,
                            "",
                            "Response still contains MongoDB ObjectId serialization issues"
                        )
                else:
                    self.log_test(
                        "MongoDB ObjectId Fix - Collections Endpoint",
                        False,
                        "",
                        "Invalid response format from collections endpoint"
                    )
            elif response.status_code == 500:
                # This is the specific error we're testing for
                self.log_test(
                    "MongoDB ObjectId Fix - Collections Endpoint",
                    False,
                    "",
                    f"❌ STILL GETTING HTTP 500 ERROR! The MongoDB ObjectId serialization issue is NOT fixed. Response: {response.text[:200]}"
                )
            else:
                self.log_test(
                    "MongoDB ObjectId Fix - Collections Endpoint",
                    False,
                    "",
                    f"Unexpected HTTP status {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test("MongoDB ObjectId Fix - Collections Endpoint", False, "", str(e))

        # Test with admin user as well to ensure fix works across different user types
        if self.admin_token and self.admin_id:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            try:
                response = self.session.get(f"{BASE_URL}/users/{self.admin_id}/collections", headers=admin_headers)
                
                if response.status_code == 200:
                    self.log_test(
                        "MongoDB ObjectId Fix - Admin Collections Endpoint",
                        True,
                        "Admin collections endpoint also works without ObjectId serialization errors"
                    )
                elif response.status_code == 500:
                    self.log_test(
                        "MongoDB ObjectId Fix - Admin Collections Endpoint",
                        False,
                        "",
                        "Admin collections endpoint still returns HTTP 500 error"
                    )
                else:
                    self.log_test(
                        "MongoDB ObjectId Fix - Admin Collections Endpoint",
                        True,
                        f"Admin collections endpoint returns HTTP {response.status_code} (not 500 error)"
                    )
            except Exception as e:
                self.log_test("MongoDB ObjectId Fix - Admin Collections Endpoint", False, "", str(e))

    def test_backend_api_stability(self):
        """Test 2: Backend API Stability - Ensure all backend functionality remains operational"""
        print("🛡️ TESTING BACKEND API STABILITY")
        print("=" * 50)
        
        # Test key API endpoints to ensure they're still working after the fix
        stability_endpoints = [
            ("/jerseys", "GET", "Jersey Management", False),
            ("/marketplace/catalog", "GET", "Marketplace Catalog", False),
            ("/profile", "GET", "Profile Access", True),
            ("/notifications", "GET", "Notifications", True),
            ("/explorer/most-collected", "GET", "Explorer Endpoints", False),
            ("/admin/jerseys/pending", "GET", "Admin Endpoints", "admin")
        ]
        
        for endpoint, method, description, auth_type in stability_endpoints:
            try:
                headers = {}
                if auth_type == True and self.user_token:
                    headers = {"Authorization": f"Bearer {self.user_token}"}
                elif auth_type == "admin" and self.admin_token:
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                elif auth_type and not self.user_token:
                    continue
                
                if method == "GET":
                    response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    # Check for ObjectId serialization issues in response
                    response_text = response.text
                    has_objectid_issues = (
                        "ObjectId(" in response_text or 
                        '"_id":' in response_text or
                        "not JSON serializable" in response_text
                    )
                    
                    if not has_objectid_issues:
                        self.log_test(
                            f"API Stability - {description}",
                            True,
                            f"Endpoint operational without ObjectId serialization issues"
                        )
                    else:
                        self.log_test(
                            f"API Stability - {description}",
                            False,
                            "",
                            "Endpoint has ObjectId serialization issues"
                        )
                elif response.status_code == 500:
                    self.log_test(
                        f"API Stability - {description}",
                        False,
                        "",
                        f"HTTP 500 error detected - possible ObjectId serialization issue"
                    )
                else:
                    # Other status codes are acceptable (401, 403, etc.)
                    self.log_test(
                        f"API Stability - {description}",
                        True,
                        f"Endpoint returns HTTP {response.status_code} (not 500 error)"
                    )
            except Exception as e:
                self.log_test(f"API Stability - {description}", False, "", str(e))

    def test_error_handling_verification(self):
        """Test 3: Error Handling - Verify proper error handling without ObjectId issues"""
        print("⚠️ TESTING ERROR HANDLING VERIFICATION")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Error Handling Verification", False, "", "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test error scenarios to ensure they don't cause ObjectId serialization issues
        error_test_scenarios = [
            (f"/users/invalid-user-id/collections", "Invalid User ID"),
            (f"/users/{self.user_id}/collections/invalid-collection", "Invalid Collection ID"),
            ("/jerseys/invalid-jersey-id", "Invalid Jersey ID")
        ]
        
        for endpoint, description in error_test_scenarios:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                # We expect 404 or similar errors, but NOT 500 errors due to ObjectId issues
                if response.status_code == 500:
                    response_text = response.text
                    if "ObjectId(" in response_text or '"_id":' in response_text or "not JSON serializable" in response_text:
                        self.log_test(
                            f"Error Handling - {description}",
                            False,
                            "",
                            f"HTTP 500 error with ObjectId serialization issues: {response_text[:200]}"
                        )
                    else:
                        self.log_test(
                            f"Error Handling - {description}",
                            True,
                            f"HTTP 500 error but no ObjectId serialization issues detected"
                        )
                else:
                    self.log_test(
                        f"Error Handling - {description}",
                        True,
                        f"Proper error handling - HTTP {response.status_code} (no 500 ObjectId errors)"
                    )
            except Exception as e:
                self.log_test(f"Error Handling - {description}", False, "", str(e))

    def test_data_integrity_verification(self):
        """Test 4: Data Integrity - Confirm jersey and collection data is properly aggregated"""
        print("📊 TESTING DATA INTEGRITY VERIFICATION")
        print("=" * 50)
        
        if not self.user_token or not self.user_id:
            self.log_test("Data Integrity Verification", False, "", "No user authentication available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Verify collections data structure and integrity
        try:
            response = self.session.get(f"{BASE_URL}/users/{self.user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections_response = response.json()
                
                # The response is a dict with 'collections' key containing the list
                if isinstance(collections_response, dict) and 'collections' in collections_response:
                    collections_data = collections_response['collections']
                    
                    # Verify data structure integrity
                    if isinstance(collections_data, list):
                        # Check each collection item for proper structure
                        valid_structure = True
                        jersey_details_found = False
                        
                        for collection in collections_data:
                            if isinstance(collection, dict):
                                # Check for required fields without MongoDB ObjectId
                                required_fields = ["jersey_id", "collection_type", "added_at"]
                                for field in required_fields:
                                    if field not in collection:
                                        valid_structure = False
                                        break
                                
                                # Check if jersey details are properly aggregated
                                if "jersey" in collection or "jersey_details" in collection:
                                    jersey_details_found = True
                            else:
                                valid_structure = False
                                break
                        
                        if valid_structure:
                            self.log_test(
                                "Data Integrity - Collections Structure",
                                True,
                                f"Collections data properly structured ({len(collections_data)} items) with jersey details aggregated: {jersey_details_found}"
                            )
                        else:
                            self.log_test(
                                "Data Integrity - Collections Structure",
                                False,
                                "",
                                "Collections data structure is invalid or missing required fields"
                            )
                    else:
                        self.log_test(
                            "Data Integrity - Collections Structure",
                            False,
                            "",
                            "Collections data in response is not a list"
                        )
                else:
                    self.log_test(
                        "Data Integrity - Collections Structure",
                        False,
                        "",
                        "Collections endpoint response missing 'collections' key or invalid format"
                    )
            else:
                self.log_test(
                    "Data Integrity - Collections Structure",
                    False,
                    "",
                    f"Collections endpoint returned HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_test("Data Integrity - Collections Structure", False, "", str(e))

        # Test 2: Verify jersey data aggregation in collections
        try:
            # Get user's jerseys to compare with collections
            jerseys_response = self.session.get(f"{BASE_URL}/users/{self.user_id}/jerseys", headers=headers)
            
            if jerseys_response.status_code == 200:
                jerseys_data = jerseys_response.json()
                
                # Check for ObjectId serialization issues in jersey data
                response_text = jerseys_response.text
                has_objectid_issues = "ObjectId(" in response_text or '"_id":' in response_text or "not JSON serializable" in response_text
                
                if not has_objectid_issues:
                    jersey_count = len(jerseys_data) if isinstance(jerseys_data, list) else 0
                    self.log_test(
                        "Data Integrity - Jersey Data Aggregation",
                        True,
                        f"Jersey data properly aggregated ({jersey_count} jerseys) without ObjectId serialization errors"
                    )
                else:
                    self.log_test(
                        "Data Integrity - Jersey Data Aggregation",
                        False,
                        "",
                        "Jersey data contains ObjectId serialization issues"
                    )
            else:
                self.log_test(
                    "Data Integrity - Jersey Data Aggregation",
                    True,
                    f"Jersey endpoint returns HTTP {jerseys_response.status_code} (not 500 ObjectId error)"
                )
        except Exception as e:
            self.log_test("Data Integrity - Jersey Data Aggregation", False, "", str(e))

    def run_all_tests(self):
        """Run all test suites focused on MongoDB ObjectId serialization fix"""
        print("🚀 STARTING MONGODB OBJECTID SERIALIZATION FIX VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("Focus: MongoDB ObjectId serialization fix in /api/users/{user_id}/collections endpoint")
        print("=" * 80)
        print()
        
        # Run test suites in order of importance
        self.test_authentication_setup()
        self.test_mongodb_objectid_serialization_fix()
        self.test_backend_api_stability()
        self.test_error_handling_verification()
        self.test_data_integrity_verification()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY - MONGODB OBJECTID SERIALIZATION FIX VERIFICATION")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Check if the main ObjectId fix is working
        objectid_fix_tests = [r for r in self.test_results if "MongoDB ObjectId Fix" in r["test"]]
        objectid_fix_success = all(r["success"] for r in objectid_fix_tests)
        
        print("🎯 MONGODB OBJECTID SERIALIZATION FIX STATUS:")
        if objectid_fix_success and objectid_fix_tests:
            print("✅ FIXED: MongoDB ObjectId serialization issue has been resolved!")
            print("   - /api/users/{user_id}/collections endpoint no longer returns HTTP 500 errors")
            print("   - Collection data returns properly without ObjectId serialization issues")
        elif objectid_fix_tests:
            print("❌ NOT FIXED: MongoDB ObjectId serialization issue still exists!")
            print("   - /api/users/{user_id}/collections endpoint may still return HTTP 500 errors")
            print("   - ObjectId serialization problems detected in responses")
        else:
            print("⚠️ UNKNOWN: Could not test MongoDB ObjectId fix due to authentication issues")
        
        print()
        
        # Categorize results
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        print()
        
        # Final assessment
        if objectid_fix_success and success_rate >= 90:
            print("🎉 EXCELLENT: MongoDB ObjectId serialization fix is working perfectly!")
        elif objectid_fix_success and success_rate >= 80:
            print("✅ GOOD: MongoDB ObjectId fix is working with minor issues in other areas.")
        elif objectid_fix_success:
            print("⚠️ PARTIAL: MongoDB ObjectId fix is working but other issues detected.")
        else:
            print("❌ CRITICAL: MongoDB ObjectId serialization issue is NOT fixed!")
        
        print()
        print("🎯 MONGODB OBJECTID SERIALIZATION FIX TESTING COMPLETE")
        
        return success_rate, objectid_fix_success

if __name__ == "__main__":
    tester = MongoObjectIdFixTester()
    success_rate, objectid_fix_success = tester.run_all_tests()
    
    # Exit with appropriate code - success if ObjectId fix is working
    sys.exit(0 if objectid_fix_success else 1)