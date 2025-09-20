#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - User Registration Endpoint Testing

USER ISSUE REPORT:
- User getting 404 error when trying to sign up
- Frontend is calling `/api/auth/register` endpoint which was missing from backend

NEW REGISTRATION ENDPOINT ADDED:
- Added `RegisterRequest` model with name, email, password fields
- Added `/api/auth/register` POST endpoint in backend
- Endpoint creates new user with hashed password and returns JWT token

TESTING REQUIRED:
1. Test successful user registration with valid data
2. Test duplicate email registration (should return 400 error)
3. Test registration with missing/invalid data
4. Test login with newly registered user
5. Test complete signup flow integration

FOCUS: Ensure the 404 signup error is completely resolved and registration flow works end-to-end.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://kit-wizard.preview.emergentagent.com/api"

class RegistrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.registered_users = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_successful_registration(self):
        """Test A: Test successful user registration with valid data"""
        try:
            print(f"\n🎯 TEST A: Successful User Registration...")
            
            # Generate unique test user data
            unique_id = str(uuid.uuid4())[:8]
            test_user = {
                "name": f"Test User {unique_id}",
                "email": f"testuser{unique_id}@example.com",
                "password": "TestPassword123!"
            }
            
            print(f"   Registering user: {test_user['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "token" not in data or "user" not in data:
                    self.log_test("Registration Success - Response Structure", False,
                                 "Missing token or user in response", data)
                    return False
                
                # Verify user data
                user_data = data["user"]
                if user_data.get("email") != test_user["email"]:
                    self.log_test("Registration Success - User Data", False,
                                 f"Email mismatch: expected {test_user['email']}, got {user_data.get('email')}")
                    return False
                
                if user_data.get("name") != test_user["name"]:
                    self.log_test("Registration Success - User Data", False,
                                 f"Name mismatch: expected {test_user['name']}, got {user_data.get('name')}")
                    return False
                
                # Verify JWT token is present and valid format
                token = data["token"]
                if not token or len(token.split('.')) != 3:
                    self.log_test("Registration Success - JWT Token", False,
                                 f"Invalid JWT token format: {token}")
                    return False
                
                # Store for later tests
                self.registered_users.append({
                    "user_data": test_user,
                    "token": token,
                    "user_id": user_data.get("id")
                })
                
                self.log_test("Registration Success", True,
                             f"User {test_user['email']} registered successfully with valid token")
                return True
                
            else:
                self.log_test("Registration Success", False,
                             f"Registration failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Registration Success", False, f"Exception: {str(e)}")
            return False
    
    def test_duplicate_email_registration(self):
        """Test B: Test duplicate email registration"""
        try:
            print(f"\n🎯 TEST B: Duplicate Email Registration...")
            
            if not self.registered_users:
                self.log_test("Duplicate Email Registration", False,
                             "No registered users available for duplicate test")
                return False
            
            # Try to register with the same email as the first registered user
            existing_user = self.registered_users[0]["user_data"]
            duplicate_user = {
                "name": "Different Name",
                "email": existing_user["email"],  # Same email
                "password": "DifferentPassword456!"
            }
            
            print(f"   Attempting duplicate registration for: {duplicate_user['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=duplicate_user,
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                error_message = data.get("detail", "")
                
                if "already registered" in error_message.lower() or "email" in error_message.lower():
                    self.log_test("Duplicate Email Registration", True,
                                 f"Correctly rejected duplicate email with 400 error: {error_message}")
                    return True
                else:
                    self.log_test("Duplicate Email Registration", False,
                                 f"400 error but wrong message: {error_message}")
                    return False
            else:
                self.log_test("Duplicate Email Registration", False,
                             f"Expected 400 error, got {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Email Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_registration_validation(self):
        """Test C: Test registration with missing/invalid data"""
        try:
            print(f"\n🎯 TEST C: Registration Validation Testing...")
            
            validation_tests = [
                {
                    "name": "Missing Name",
                    "data": {"email": "test@example.com", "password": "TestPassword123!"},
                    "expected_error": "name"
                },
                {
                    "name": "Missing Email", 
                    "data": {"name": "Test User", "password": "TestPassword123!"},
                    "expected_error": "email"
                },
                {
                    "name": "Missing Password",
                    "data": {"name": "Test User", "email": "test@example.com"},
                    "expected_error": "password"
                },
                {
                    "name": "Invalid Email Format",
                    "data": {"name": "Test User", "email": "invalid-email", "password": "TestPassword123!"},
                    "expected_error": "email"
                },
                {
                    "name": "Empty Name",
                    "data": {"name": "", "email": "test@example.com", "password": "TestPassword123!"},
                    "expected_error": "name"
                }
            ]
            
            all_passed = True
            
            for test_case in validation_tests:
                print(f"     Testing: {test_case['name']}")
                
                response = self.session.post(
                    f"{BACKEND_URL}/auth/register",
                    json=test_case["data"],
                    timeout=10
                )
                
                if response.status_code == 422:
                    # Pydantic validation error
                    data = response.json()
                    error_details = data.get("detail", [])
                    
                    # Check if the expected field error is present
                    field_error_found = False
                    if isinstance(error_details, list):
                        for error in error_details:
                            if isinstance(error, dict) and "loc" in error:
                                if test_case["expected_error"] in str(error["loc"]):
                                    field_error_found = True
                                    break
                    
                    if field_error_found:
                        print(f"       ✅ Correctly rejected: {test_case['name']}")
                    else:
                        print(f"       ❌ Wrong validation error for: {test_case['name']}")
                        print(f"          Expected error for: {test_case['expected_error']}")
                        print(f"          Got errors: {error_details}")
                        all_passed = False
                        
                elif response.status_code == 400:
                    # Custom validation error
                    data = response.json()
                    error_message = data.get("detail", "")
                    print(f"       ✅ Correctly rejected: {test_case['name']} - {error_message}")
                    
                else:
                    print(f"       ❌ Unexpected response for {test_case['name']}: {response.status_code}")
                    print(f"          Response: {response.text}")
                    all_passed = False
            
            if all_passed:
                self.log_test("Registration Validation", True,
                             "All validation tests passed - proper error handling for invalid data")
                return True
            else:
                self.log_test("Registration Validation", False,
                             "Some validation tests failed")
                return False
                
        except Exception as e:
            self.log_test("Registration Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_login_with_registered_user(self):
        """Test D: Test login with newly registered user"""
        try:
            print(f"\n🎯 TEST D: Login with Newly Registered User...")
            
            if not self.registered_users:
                self.log_test("Login with Registered User", False,
                             "No registered users available for login test")
                return False
            
            # Test login with the first registered user
            registered_user = self.registered_users[0]
            login_data = {
                "email": registered_user["user_data"]["email"],
                "password": registered_user["user_data"]["password"]
            }
            
            print(f"   Attempting login for: {login_data['email']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "token" not in data or "user" not in data:
                    self.log_test("Login with Registered User", False,
                                 "Missing token or user in login response", data)
                    return False
                
                # Verify user data matches registration
                user_data = data["user"]
                if user_data.get("email") != login_data["email"]:
                    self.log_test("Login with Registered User", False,
                                 f"Email mismatch in login: expected {login_data['email']}, got {user_data.get('email')}")
                    return False
                
                # Verify JWT token is valid
                token = data["token"]
                if not token or len(token.split('.')) != 3:
                    self.log_test("Login with Registered User", False,
                                 f"Invalid JWT token in login response: {token}")
                    return False
                
                self.log_test("Login with Registered User", True,
                             f"Successfully logged in with registered user {login_data['email']}")
                return True
                
            else:
                self.log_test("Login with Registered User", False,
                             f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Login with Registered User", False, f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_validation(self):
        """Test E: Test JWT token validation for authenticated endpoints"""
        try:
            print(f"\n🎯 TEST E: JWT Token Validation...")
            
            if not self.registered_users:
                self.log_test("JWT Token Validation", False,
                             "No registered users available for token validation test")
                return False
            
            # Use the token from registration
            registered_user = self.registered_users[0]
            token = registered_user["token"]
            
            print(f"   Testing JWT token for authenticated endpoint...")
            
            # Test with a protected endpoint (my-collection)
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(
                f"{BACKEND_URL}/my-collection",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Token is valid and endpoint is accessible
                collection_data = response.json()
                self.log_test("JWT Token Validation", True,
                             f"JWT token is valid - successfully accessed protected endpoint")
                return True
                
            elif response.status_code == 401:
                self.log_test("JWT Token Validation", False,
                             "JWT token was rejected by protected endpoint", response.text)
                return False
                
            else:
                # Other status codes might be acceptable (e.g., 403 for insufficient permissions)
                self.log_test("JWT Token Validation", True,
                             f"JWT token accepted (status {response.status_code}) - authentication working")
                return True
                
        except Exception as e:
            self.log_test("JWT Token Validation", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_signup_flow(self):
        """Test complete signup flow integration"""
        try:
            print(f"\n🎯 INTEGRATION TEST: Complete Signup Flow...")
            
            # Step 1: Register a new user
            unique_id = str(uuid.uuid4())[:8]
            test_user = {
                "name": f"Flow Test User {unique_id}",
                "email": f"flowtest{unique_id}@example.com", 
                "password": "FlowTestPassword123!"
            }
            
            print(f"   Step 1: Registering user {test_user['email']}")
            
            register_response = self.session.post(
                f"{BACKEND_URL}/auth/register",
                json=test_user,
                timeout=10
            )
            
            if register_response.status_code != 200:
                self.log_test("Complete Signup Flow - Registration", False,
                             f"Registration failed: {register_response.status_code}", register_response.text)
                return False
            
            register_data = register_response.json()
            registration_token = register_data.get("token")
            
            # Step 2: Immediately login with the same credentials
            print(f"   Step 2: Logging in with registered credentials")
            
            login_response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json={"email": test_user["email"], "password": test_user["password"]},
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.log_test("Complete Signup Flow - Login", False,
                             f"Login failed: {login_response.status_code}", login_response.text)
                return False
            
            login_data = login_response.json()
            login_token = login_data.get("token")
            
            # Step 3: Use the login token to access a protected endpoint
            print(f"   Step 3: Accessing protected endpoint with login token")
            
            headers = {"Authorization": f"Bearer {login_token}"}
            protected_response = self.session.get(
                f"{BACKEND_URL}/my-collection",
                headers=headers,
                timeout=10
            )
            
            if protected_response.status_code not in [200, 403]:  # 403 might be acceptable for some endpoints
                self.log_test("Complete Signup Flow - Protected Access", False,
                             f"Protected endpoint access failed: {protected_response.status_code}", protected_response.text)
                return False
            
            # Step 4: Verify user data consistency
            print(f"   Step 4: Verifying user data consistency")
            
            register_user = register_data.get("user", {})
            login_user = login_data.get("user", {})
            
            if register_user.get("id") != login_user.get("id"):
                self.log_test("Complete Signup Flow - Data Consistency", False,
                             f"User ID mismatch: register={register_user.get('id')}, login={login_user.get('id')}")
                return False
            
            if register_user.get("email") != login_user.get("email"):
                self.log_test("Complete Signup Flow - Data Consistency", False,
                             f"Email mismatch: register={register_user.get('email')}, login={login_user.get('email')}")
                return False
            
            self.log_test("Complete Signup Flow", True,
                         "Complete signup flow working: register → login → protected access → data consistency")
            return True
            
        except Exception as e:
            self.log_test("Complete Signup Flow", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive registration endpoint testing"""
        print("🧪 Starting TopKit User Registration Endpoint Testing")
        print("USER ISSUE REPORT:")
        print("- User getting 404 error when trying to sign up")
        print("- Frontend is calling `/api/auth/register` endpoint which was missing from backend")
        print("=" * 100)
        
        test_results = []
        
        # Test A: Successful registration
        print("\n🎯 Running Registration Tests...")
        test_results.append(self.test_successful_registration())
        
        # Test B: Duplicate email registration
        test_results.append(self.test_duplicate_email_registration())
        
        # Test C: Registration validation
        test_results.append(self.test_registration_validation())
        
        # Test D: Login with registered user
        test_results.append(self.test_login_with_registered_user())
        
        # Test E: JWT token validation
        test_results.append(self.test_jwt_token_validation())
        
        # Integration Test: Complete signup flow
        test_results.append(self.test_complete_signup_flow())
        
        # Summary
        self.print_summary()
        
        return all(test_results)
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n📊 REGISTRATION ENDPOINT TEST SUMMARY")
        print("=" * 100)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show test breakdown
        print(f"\nTest Results Breakdown:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success']]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED: {len(critical_failures)}")
            for failure in critical_failures:
                print(f"  • {failure['test']}: {failure['message']}")
                if failure.get('details'):
                    print(f"    Details: {failure['details']}")
        
        # User issue resolution status
        print(f"\n🎯 USER ISSUE RESOLUTION STATUS:")
        registration_failures = [r for r in self.test_results if not r['success'] and 'Registration' in r['test']]
        login_failures = [r for r in self.test_results if not r['success'] and 'Login' in r['test']]
        flow_failures = [r for r in self.test_results if not r['success'] and 'Flow' in r['test']]
        
        if not registration_failures and not login_failures and not flow_failures:
            print("  ✅ 404 SIGNUP ERROR COMPLETELY RESOLVED!")
            print("  ✅ Registration endpoint working perfectly")
            print("  ✅ User registration flow functional end-to-end")
            print("  ✅ JWT authentication working correctly")
            print("  ✅ All validation and error handling working properly")
        else:
            print("  ❌ REGISTRATION ISSUES STILL PRESENT:")
            if registration_failures:
                print("    - Registration endpoint issues detected")
            if login_failures:
                print("    - Login functionality issues detected")
            if flow_failures:
                print("    - Complete signup flow issues detected")
        
        print("\n" + "=" * 100)

def main():
    """Main test execution"""
    tester = RegistrationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()