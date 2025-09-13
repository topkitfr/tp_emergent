#!/usr/bin/env python3
"""
URGENT BUG INVESTIGATION - Jersey Submission Not Working
Testing jersey submission with specific user credentials from review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from frontend/.env
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test credentials from review request
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "T0p_Mdp_1288*"

class JerseySubmissionTester:
    def __init__(self):
        self.user_token = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
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

    def test_user_authentication(self):
        """Test user authentication with provided credentials"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"Successfully authenticated user: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'user')}, ID: {user_info.get('id', 'N/A')})"
                )
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"Authentication failed with status {response.status_code}",
                    error_detail
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, "", str(e))
            return False

    def test_user_profile_access(self):
        """Test user profile access to verify token validity"""
        if not self.user_token:
            self.log_result("User Profile Access", False, "", "No authentication token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/auth/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result(
                    "User Profile Access", 
                    True, 
                    f"Profile accessible - User: {profile_data.get('name')} ({profile_data.get('email')})"
                )
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "User Profile Access", 
                    False, 
                    f"Profile access failed with status {response.status_code}",
                    error_detail
                )
                return False
                
        except Exception as e:
            self.log_result("User Profile Access", False, "", str(e))
            return False

    def test_jersey_submission_endpoint(self):
        """Test jersey submission via POST /api/jerseys endpoint"""
        if not self.user_token:
            self.log_result("Jersey Submission", False, "", "No authentication token available")
            return False
            
        # Test jersey data as specified in review request
        test_jersey = {
            "team": "Test Team",
            "season": "2024/25", 
            "league": "Test League",
            "manufacturer": "Nike",
            "home_away": "Home",
            "description": "Test jersey submission for bug investigation"
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.user_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(f"{BACKEND_URL}/jerseys", json=test_jersey, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                jersey_data = response.json()
                jersey_id = jersey_data.get("id", "N/A")
                jersey_ref = jersey_data.get("reference_number", "N/A")
                jersey_status = jersey_data.get("status", "N/A")
                
                self.log_result(
                    "Jersey Submission", 
                    True, 
                    f"Jersey submitted successfully - ID: {jersey_id}, Ref: {jersey_ref}, Status: {jersey_status}"
                )
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Jersey Submission", 
                    False, 
                    f"Jersey submission failed with status {response.status_code}",
                    error_detail
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Submission", False, "", str(e))
            return False

    def test_jersey_validation_errors(self):
        """Test jersey submission validation with missing required fields"""
        if not self.user_token:
            self.log_result("Jersey Validation", False, "", "No authentication token available")
            return False
            
        # Test with missing required fields
        invalid_jersey = {
            "team": "",  # Empty team should fail
            "season": "2024/25"
            # Missing other required fields
        }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.user_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(f"{BACKEND_URL}/jerseys", json=invalid_jersey, headers=headers)
            
            if response.status_code == 422:  # Validation error expected
                self.log_result(
                    "Jersey Validation", 
                    True, 
                    "Validation correctly rejected invalid jersey data"
                )
                return True
            elif response.status_code == 200 or response.status_code == 201:
                self.log_result(
                    "Jersey Validation", 
                    False, 
                    "Validation should have rejected invalid data but didn't",
                    "Validation not working properly"
                )
                return False
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "Jersey Validation", 
                    False, 
                    f"Unexpected response status {response.status_code}",
                    error_detail
                )
                return False
                
        except Exception as e:
            self.log_result("Jersey Validation", False, "", str(e))
            return False

    def test_user_submissions_list(self):
        """Test retrieving user's jersey submissions"""
        if not self.user_token:
            self.log_result("User Submissions List", False, "", "No authentication token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # First get user profile to get user ID
            profile_response = requests.get(f"{BACKEND_URL}/auth/profile", headers=headers)
            if profile_response.status_code != 200:
                self.log_result("User Submissions List", False, "", "Could not get user profile")
                return False
                
            user_id = profile_response.json().get("id")
            if not user_id:
                self.log_result("User Submissions List", False, "", "Could not get user ID from profile")
                return False
            
            # Get user's jersey submissions
            response = requests.get(f"{BACKEND_URL}/users/{user_id}/jerseys", headers=headers)
            
            if response.status_code == 200:
                submissions = response.json()
                submission_count = len(submissions) if isinstance(submissions, list) else 0
                
                self.log_result(
                    "User Submissions List", 
                    True, 
                    f"Successfully retrieved {submission_count} jersey submissions"
                )
                return True
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                self.log_result(
                    "User Submissions List", 
                    False, 
                    f"Failed to retrieve submissions with status {response.status_code}",
                    error_detail
                )
                return False
                
        except Exception as e:
            self.log_result("User Submissions List", False, "", str(e))
            return False

    def test_unauthenticated_jersey_submission(self):
        """Test jersey submission without authentication (should fail)"""
        test_jersey = {
            "team": "Test Team",
            "season": "2024/25", 
            "league": "Test League",
            "manufacturer": "Nike",
            "home_away": "Home"
        }
        
        try:
            # No Authorization header
            response = requests.post(f"{BACKEND_URL}/jerseys", json=test_jersey)
            
            if response.status_code == 401:  # Unauthorized expected
                self.log_result(
                    "Unauthenticated Jersey Submission", 
                    True, 
                    "Correctly rejected unauthenticated jersey submission"
                )
                return True
            else:
                self.log_result(
                    "Unauthenticated Jersey Submission", 
                    False, 
                    f"Expected 401 Unauthorized but got {response.status_code}",
                    "Authentication not properly enforced"
                )
                return False
                
        except Exception as e:
            self.log_result("Unauthenticated Jersey Submission", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all jersey submission tests"""
        print("🚨 URGENT BUG INVESTIGATION - Jersey Submission Not Working")
        print("=" * 70)
        print(f"Testing with user: {USER_EMAIL}")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        print()
        
        # Test sequence
        tests = [
            ("User Authentication", self.test_user_authentication),
            ("User Profile Access", self.test_user_profile_access),
            ("Jersey Submission", self.test_jersey_submission_endpoint),
            ("Jersey Validation", self.test_jersey_validation_errors),
            ("User Submissions List", self.test_user_submissions_list),
            ("Unauthenticated Submission", self.test_unauthenticated_jersey_submission)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                passed += 1
        
        # Summary
        print("=" * 70)
        print("🎯 JERSEY SUBMISSION BUG INVESTIGATION RESULTS")
        print("=" * 70)
        success_rate = (passed / total) * 100
        print(f"Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Categorize results
        critical_failures = []
        working_features = []
        
        for result in self.test_results:
            if result["success"]:
                working_features.append(result["test"])
            else:
                critical_failures.append(f"{result['test']}: {result['error']}")
        
        if working_features:
            print("✅ WORKING FEATURES:")
            for feature in working_features:
                print(f"   • {feature}")
            print()
        
        if critical_failures:
            print("❌ CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   • {failure}")
            print()
        
        # Root cause analysis
        print("🔍 ROOT CAUSE ANALYSIS:")
        if not self.user_token:
            print("   • AUTHENTICATION FAILURE: User cannot authenticate with provided credentials")
            print("   • This blocks all jersey submission functionality")
        elif any("Jersey Submission" in result["test"] and not result["success"] for result in self.test_results):
            print("   • JERSEY SUBMISSION API ISSUE: Authentication works but jersey submission fails")
            print("   • Check backend jersey creation endpoint and validation logic")
        else:
            print("   • All core functionality appears to be working")
        
        print()
        print("🎯 CONCLUSION:")
        if success_rate >= 80:
            print("   Jersey submission system is mostly operational")
        elif success_rate >= 50:
            print("   Jersey submission system has significant issues that need fixing")
        else:
            print("   Jersey submission system is critically broken and needs immediate attention")
        
        return success_rate

if __name__ == "__main__":
    tester = JerseySubmissionTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)