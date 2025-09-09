#!/usr/bin/env python3
"""
TopKit Backend Authentication & Jersey Submission Testing
Focused testing for the specific review request:
- User authentication system (login endpoint /api/auth/login with steinmetzlivio@gmail.com/123)
- Jersey submission system (/api/jerseys) for authenticated users
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class TopKitAuthJerseyTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
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

    def test_authentication_login(self):
        """Test the specific login endpoint with steinmetzlivio@gmail.com/123"""
        print("🔐 TESTING AUTHENTICATION LOGIN ENDPOINT")
        print("=" * 60)
        
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            print(f"Testing POST {BASE_URL}/auth/login")
            print(f"Credentials: {TEST_USER_EMAIL} / {TEST_USER_PASSWORD}")
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"].get("role", "user")
                    user_email = data["user"]["email"]
                    
                    self.log_test(
                        "POST /api/auth/login - User Authentication",
                        True,
                        f"Login successful - Name: {user_name}, Email: {user_email}, Role: {user_role}, ID: {self.user_id}, Token: {self.user_token[:20]}..."
                    )
                    
                    # Test token validation by accessing profile
                    try:
                        headers = {"Authorization": f"Bearer {self.user_token}"}
                        profile_response = self.session.get(f"{BASE_URL}/profile", headers=headers)
                        
                        if profile_response.status_code == 200:
                            profile_data = profile_response.json()
                            self.log_test(
                                "Token Validation - Profile Access",
                                True,
                                f"Profile accessed successfully with token - User stats retrieved"
                            )
                        else:
                            self.log_test(
                                "Token Validation - Profile Access",
                                False,
                                "",
                                f"Profile access failed with HTTP {profile_response.status_code}: {profile_response.text}"
                            )
                    except Exception as e:
                        self.log_test("Token Validation - Profile Access", False, "", str(e))
                        
                else:
                    self.log_test(
                        "POST /api/auth/login - User Authentication",
                        False,
                        "",
                        "Response missing 'token' or 'user' fields"
                    )
            else:
                self.log_test(
                    "POST /api/auth/login - User Authentication",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("POST /api/auth/login - User Authentication", False, "", str(e))

    def test_jersey_submission_system(self):
        """Test the jersey submission system for authenticated users"""
        print("⚽ TESTING JERSEY SUBMISSION SYSTEM")
        print("=" * 60)
        
        if not self.user_token:
            self.log_test("Jersey Submission System", False, "", "No authentication token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Check current user submissions
        try:
            print(f"Testing GET {BASE_URL}/users/{self.user_id}/jerseys")
            response = self.session.get(f"{BASE_URL}/users/{self.user_id}/jerseys", headers=headers)
            
            if response.status_code == 200:
                submissions = response.json()
                if isinstance(submissions, list):
                    pending_count = sum(1 for jersey in submissions if jersey.get("status") == "pending")
                    approved_count = sum(1 for jersey in submissions if jersey.get("status") == "approved")
                    rejected_count = sum(1 for jersey in submissions if jersey.get("status") == "rejected")
                    
                    self.log_test(
                        "GET /api/users/{user_id}/jerseys - Current Submissions",
                        True,
                        f"User has {len(submissions)} total submissions (Pending: {pending_count}, Approved: {approved_count}, Rejected: {rejected_count})"
                    )
                else:
                    self.log_test("GET /api/users/{user_id}/jerseys - Current Submissions", False, "", "Invalid response format")
            else:
                self.log_test("GET /api/users/{user_id}/jerseys - Current Submissions", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/users/{user_id}/jerseys - Current Submissions", False, "", str(e))

        # Test 2: Submit a new jersey
        try:
            test_jersey_data = {
                "team": "Real Madrid CF",
                "season": "2024-25",
                "player": "Vinicius Jr",
                "size": "L",
                "condition": "new",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey submission for authentication and submission system verification"
            }
            
            print(f"Testing POST {BASE_URL}/jerseys")
            print(f"Jersey data: {test_jersey_data['team']} {test_jersey_data['season']} - {test_jersey_data['player']}")
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data, headers=headers)
            
            if response.status_code in [200, 201]:
                jersey_data = response.json()
                jersey_id = jersey_data.get("id")
                jersey_status = jersey_data.get("status")
                reference_number = jersey_data.get("reference_number")
                created_by = jersey_data.get("created_by")
                submitted_by = jersey_data.get("submitted_by")
                
                self.log_test(
                    "POST /api/jerseys - Jersey Submission",
                    True,
                    f"Jersey submitted successfully - ID: {jersey_id}, Status: {jersey_status}, Reference: {reference_number}, Created by: {created_by}, Submitted by: {submitted_by}"
                )
                
                # Test 3: Verify the jersey appears in user's submissions
                try:
                    response = self.session.get(f"{BASE_URL}/users/{self.user_id}/jerseys", headers=headers)
                    
                    if response.status_code == 200:
                        updated_submissions = response.json()
                        if isinstance(updated_submissions, list):
                            # Look for our newly created jersey
                            new_jersey_found = any(
                                jersey.get("id") == jersey_id 
                                for jersey in updated_submissions
                            )
                            
                            if new_jersey_found:
                                self.log_test(
                                    "Jersey Submission Tracking",
                                    True,
                                    f"Newly submitted jersey {jersey_id} appears in user's submission list"
                                )
                            else:
                                self.log_test(
                                    "Jersey Submission Tracking",
                                    False,
                                    "",
                                    f"Newly submitted jersey {jersey_id} not found in user's submission list"
                                )
                        else:
                            self.log_test("Jersey Submission Tracking", False, "", "Invalid submissions response format")
                    else:
                        self.log_test("Jersey Submission Tracking", False, "", f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test("Jersey Submission Tracking", False, "", str(e))
                    
            else:
                self.log_test("POST /api/jerseys - Jersey Submission", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/jerseys - Jersey Submission", False, "", str(e))

        # Test 4: Test jersey submission without authentication (should fail)
        try:
            test_jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "size": "M",
                "condition": "very_good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey submission without authentication - should fail"
            }
            
            print(f"Testing POST {BASE_URL}/jerseys without authentication")
            response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data)
            
            if response.status_code == 401:
                self.log_test(
                    "Jersey Submission Authentication Required",
                    True,
                    "Unauthenticated jersey submission correctly rejected with HTTP 401"
                )
            else:
                self.log_test(
                    "Jersey Submission Authentication Required",
                    False,
                    "",
                    f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Jersey Submission Authentication Required", False, "", str(e))

    def test_jersey_data_validation(self):
        """Test jersey submission data validation"""
        print("✅ TESTING JERSEY DATA VALIDATION")
        print("=" * 60)
        
        if not self.user_token:
            self.log_test("Jersey Data Validation", False, "", "No authentication token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Missing required fields
        try:
            invalid_jersey_data = {
                "team": "",  # Empty team
                "season": "",  # Empty season
                "size": "L",
                "condition": "new"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=invalid_jersey_data, headers=headers)
            
            if response.status_code == 422:
                self.log_test(
                    "Jersey Validation - Required Fields",
                    True,
                    "Empty team/season correctly rejected with HTTP 422"
                )
            else:
                self.log_test(
                    "Jersey Validation - Required Fields",
                    False,
                    "",
                    f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Jersey Validation - Required Fields", False, "", str(e))

        # Test 2: Invalid size
        try:
            invalid_size_data = {
                "team": "Test Team",
                "season": "2024-25",
                "size": "INVALID_SIZE",
                "condition": "new"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=invalid_size_data, headers=headers)
            
            if response.status_code == 422:
                self.log_test(
                    "Jersey Validation - Invalid Size",
                    True,
                    "Invalid size correctly rejected with HTTP 422"
                )
            else:
                self.log_test(
                    "Jersey Validation - Invalid Size",
                    False,
                    "",
                    f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Jersey Validation - Invalid Size", False, "", str(e))

        # Test 3: Invalid condition
        try:
            invalid_condition_data = {
                "team": "Test Team",
                "season": "2024-25",
                "size": "M",
                "condition": "INVALID_CONDITION"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=invalid_condition_data, headers=headers)
            
            if response.status_code == 422:
                self.log_test(
                    "Jersey Validation - Invalid Condition",
                    True,
                    "Invalid condition correctly rejected with HTTP 422"
                )
            else:
                self.log_test(
                    "Jersey Validation - Invalid Condition",
                    False,
                    "",
                    f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Jersey Validation - Invalid Condition", False, "", str(e))

    def run_focused_tests(self):
        """Run focused tests for authentication and jersey submission"""
        print("🎯 TOPKIT AUTHENTICATION & JERSEY SUBMISSION TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Test Password: {TEST_USER_PASSWORD}")
        print("=" * 70)
        print()
        
        # Run focused test suites
        self.test_authentication_login()
        self.test_jersey_submission_system()
        self.test_jersey_data_validation()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        auth_tests = [r for r in self.test_results if "auth" in r["test"].lower() or "login" in r["test"].lower() or "token" in r["test"].lower()]
        jersey_tests = [r for r in self.test_results if "jersey" in r["test"].lower()]
        
        print("🔐 AUTHENTICATION TESTS:")
        for result in auth_tests:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
        print()
        
        print("⚽ JERSEY SUBMISSION TESTS:")
        for result in jersey_tests:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        print("🎯 FOCUSED TESTING COMPLETE")
        print()
        
        # Specific conclusions for the review request
        auth_success = all(r["success"] for r in auth_tests)
        jersey_success = all(r["success"] for r in jersey_tests)
        
        print("📋 REVIEW REQUEST CONCLUSIONS:")
        print(f"✅ Authentication System (steinmetzlivio@gmail.com/123): {'OPERATIONAL' if auth_success else 'ISSUES FOUND'}")
        print(f"✅ Jersey Submission System (/api/jerseys): {'OPERATIONAL' if jersey_success else 'ISSUES FOUND'}")
        print()
        
        if auth_success and jersey_success:
            print("🎉 BACKEND IS READY FOR FRONTEND JERSEY SUBMISSION MODAL BUG FIX TESTING")
        else:
            print("⚠️  BACKEND ISSUES NEED TO BE RESOLVED BEFORE FRONTEND TESTING")
        
        return success_rate

if __name__ == "__main__":
    tester = TopKitAuthJerseyTester()
    success_rate = tester.run_focused_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)