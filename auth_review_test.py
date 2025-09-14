#!/usr/bin/env python3
"""
TopKit Authentication Review Test
Testing authentication for Bacquet.florent@gmail.com with password TopKitBeta2025!
Focus: Verify backend login endpoint and token format
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"

# Review request credentials
REVIEW_CREDENTIALS = {
    "email": "Bacquet.florent@gmail.com",
    "password": "TopKitBeta2025!"
}

class AuthReviewTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
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
        
    def test_backend_connectivity(self):
        """Test basic backend connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Connectivity", 
                    True, 
                    f"Backend accessible, found {len(data)} jerseys"
                )
                return True
            else:
                self.log_test(
                    "Backend Connectivity", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", False, error=str(e))
            return False
    
    def test_review_authentication(self):
        """Test authentication with review request credentials"""
        try:
            # Test login endpoint
            login_url = f"{BACKEND_URL}/auth/login"
            response = self.session.post(
                login_url,
                json=REVIEW_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Login request to: {login_url}")
            print(f"Credentials: {REVIEW_CREDENTIALS['email']}")
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data: {json.dumps(data, indent=2)}")
                
                # Check token format
                if 'token' in data:
                    token = data['token']
                    token_parts = token.split('.')
                    
                    # JWT should have 3 parts separated by dots
                    if len(token_parts) == 3:
                        self.log_test(
                            "Review Authentication - Token Format", 
                            True, 
                            f"Valid JWT format with {len(token_parts)} parts, token length: {len(token)}"
                        )
                    else:
                        self.log_test(
                            "Review Authentication - Token Format", 
                            False, 
                            f"Invalid JWT format: {len(token_parts)} parts instead of 3"
                        )
                    
                    # Check user data
                    if 'user' in data:
                        user_data = data['user']
                        self.log_test(
                            "Review Authentication - User Data", 
                            True, 
                            f"User: {user_data.get('name', 'N/A')}, Role: {user_data.get('role', 'N/A')}, ID: {user_data.get('id', 'N/A')}"
                        )
                    else:
                        self.log_test(
                            "Review Authentication - User Data", 
                            False, 
                            "No user data in response"
                        )
                    
                    return token
                else:
                    self.log_test(
                        "Review Authentication - Token Missing", 
                        False, 
                        f"No token in response: {data}"
                    )
                    return None
                    
            elif response.status_code == 401:
                self.log_test(
                    "Review Authentication - Credentials", 
                    False, 
                    f"Authentication failed: {response.text}"
                )
                return None
            elif response.status_code == 404:
                self.log_test(
                    "Review Authentication - User Not Found", 
                    False, 
                    f"User {REVIEW_CREDENTIALS['email']} not found in system"
                )
                return None
            else:
                self.log_test(
                    "Review Authentication - Unexpected Response", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Review Authentication - Exception", False, error=str(e))
            return None
    
    def test_token_validation(self, token):
        """Test token validation with protected endpoint"""
        if not token:
            self.log_test("Token Validation", False, "No token to validate")
            return False
            
        try:
            # Test with profile endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{BACKEND_URL}/users/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Token Validation - Profile Access", 
                    True, 
                    f"Profile accessible: {data.get('name', 'N/A')} ({data.get('email', 'N/A')})"
                )
                return True
            elif response.status_code == 401:
                self.log_test(
                    "Token Validation - Invalid Token", 
                    False, 
                    "Token rejected by protected endpoint"
                )
                return False
            else:
                self.log_test(
                    "Token Validation - Unexpected Response", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Token Validation - Exception", False, error=str(e))
            return False
    
    def test_user_registration_check(self):
        """Check if the review user exists in the system"""
        try:
            # Try to register with same email to see if user exists
            register_url = f"{BACKEND_URL}/auth/register"
            register_data = {
                "email": REVIEW_CREDENTIALS['email'],
                "password": "TestPassword123!",
                "name": "Test User"
            }
            
            response = self.session.post(
                register_url,
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400 and "existe déjà" in response.text:
                self.log_test(
                    "User Existence Check", 
                    True, 
                    f"User {REVIEW_CREDENTIALS['email']} exists in system"
                )
                return True
            elif response.status_code == 201 or response.status_code == 200:
                self.log_test(
                    "User Existence Check", 
                    False, 
                    f"User {REVIEW_CREDENTIALS['email']} does not exist - registration succeeded"
                )
                return False
            else:
                self.log_test(
                    "User Existence Check", 
                    False, 
                    f"Unexpected response: HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Existence Check - Exception", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🔐 TopKit Authentication Review Test")
        print("=" * 50)
        print(f"Testing credentials: {REVIEW_CREDENTIALS['email']}")
        print(f"Backend URL: {BACKEND_URL}")
        print()
        
        # Test 1: Backend connectivity
        if not self.test_backend_connectivity():
            print("❌ Backend not accessible - stopping tests")
            return
        
        # Test 2: Check if user exists
        self.test_user_registration_check()
        
        # Test 3: Authentication test
        token = self.test_review_authentication()
        
        # Test 4: Token validation (if we got a token)
        if token:
            self.test_token_validation(token)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result.get('error', result.get('details', 'Unknown error'))}")
        
        print("\n🎯 REVIEW REQUEST FINDINGS:")
        auth_success = any(r['test'].startswith('Review Authentication') and r['success'] for r in self.test_results)
        token_valid = any(r['test'].startswith('Token Validation') and r['success'] for r in self.test_results)
        
        if auth_success and token_valid:
            print("✅ Authentication endpoint working correctly")
            print("✅ Token format is valid JWT")
            print("✅ Token validation successful")
        elif auth_success:
            print("✅ Authentication endpoint working")
            print("❌ Token validation failed")
        else:
            print("❌ Authentication failed - check credentials or user existence")

if __name__ == "__main__":
    tester = AuthReviewTester()
    tester.run_all_tests()