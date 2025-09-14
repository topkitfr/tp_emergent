#!/usr/bin/env python3
"""
TopKit Authentication System Testing
Testing user registration, login, JWT tokens, and protected endpoints
"""

import requests
import json
import time
import jwt
from datetime import datetime

# Configuration - Using production URL from frontend/.env
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test data as specified in review request
TEST_EMAIL = "test@topkit.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"

class AuthenticationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_user_email = None
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
    
    def test_backend_connectivity(self):
        """Test if backend is running on localhost:8001 as specified in review request"""
        try:
            # Test basic connectivity to backend
            response = self.session.get(f"{self.base_url.replace('/api', '')}/")
            
            if response.status_code in [200, 404, 405]:  # Any response means server is running
                self.log_test("Backend Connectivity", "PASS", f"Backend responding on {self.base_url}")
                return True
            else:
                self.log_test("Backend Connectivity", "FAIL", f"Unexpected status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test("Backend Connectivity", "FAIL", f"CRITICAL: Cannot connect to {self.base_url} - This matches user's timeout issue!")
            return False
        except Exception as e:
            self.log_test("Backend Connectivity", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test user registration endpoint with test data from review request"""
        try:
            # Use unique email to avoid conflicts but based on test data
            unique_email = f"test_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_PASSWORD,
                "name": TEST_NAME
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.test_user_email = unique_email
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    # Verify user data
                    user_data = data["user"]
                    if (user_data.get("email") == unique_email and 
                        user_data.get("name") == TEST_NAME and
                        "id" in user_data):
                        
                        self.log_test("User Registration", "PASS", 
                                    f"User registered successfully - ID: {self.user_id}, Email: {unique_email}")
                        return True
                    else:
                        self.log_test("User Registration", "FAIL", "Invalid user data in response")
                        return False
                else:
                    self.log_test("User Registration", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("User Registration", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_login(self):
        """Test user login endpoint with created user"""
        try:
            if not self.test_user_email:
                self.log_test("User Login", "FAIL", "No test user email available")
                return False
            
            # Clear existing auth for login test
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            payload = {
                "email": self.test_user_email,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    login_token = data["token"]
                    user_data = data["user"]
                    
                    # Verify login data matches registration
                    if (user_data.get("email") == self.test_user_email and
                        user_data.get("id") == self.user_id and
                        login_token):
                        
                        # Update session with login token
                        self.auth_token = login_token
                        self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                        
                        self.log_test("User Login", "PASS", 
                                    f"Login successful - User: {user_data.get('name')}, Email: {user_data.get('email')}")
                        return True
                    else:
                        self.log_test("User Login", "FAIL", "Login data doesn't match registration")
                        return False
                else:
                    self.log_test("User Login", "FAIL", "Missing token or user in login response")
                    return False
            else:
                self.log_test("User Login", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_creation(self):
        """Test if JWT tokens are being created and returned properly"""
        try:
            if not self.auth_token:
                self.log_test("JWT Token Creation", "FAIL", "No auth token available")
                return False
            
            # Verify token structure (should be JWT format: header.payload.signature)
            token_parts = self.auth_token.split('.')
            if len(token_parts) != 3:
                self.log_test("JWT Token Creation", "FAIL", "Token is not in JWT format")
                return False
            
            # Try to decode token (without verification for testing)
            try:
                # Decode without verification to check structure
                decoded = jwt.decode(self.auth_token, options={"verify_signature": False})
                
                # Check required fields
                if "user_id" in decoded and "exp" in decoded:
                    # Check expiration
                    exp_timestamp = decoded["exp"]
                    current_timestamp = time.time()
                    
                    if exp_timestamp > current_timestamp:
                        time_until_expiry = exp_timestamp - current_timestamp
                        days_until_expiry = time_until_expiry / (24 * 60 * 60)
                        
                        self.log_test("JWT Token Creation", "PASS", 
                                    f"Valid JWT token created - User ID: {decoded['user_id']}, Expires in {days_until_expiry:.1f} days")
                        return True
                    else:
                        self.log_test("JWT Token Creation", "FAIL", "Token is already expired")
                        return False
                else:
                    self.log_test("JWT Token Creation", "FAIL", "Token missing required fields (user_id, exp)")
                    return False
                    
            except jwt.DecodeError:
                self.log_test("JWT Token Creation", "FAIL", "Token cannot be decoded as JWT")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Creation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoint_with_valid_token(self):
        """Test protected endpoints with valid JWT tokens"""
        try:
            if not self.auth_token:
                self.log_test("Protected Endpoint (Valid Token)", "FAIL", "No auth token available")
                return False
            
            # Test profile endpoint (requires authentication)
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify profile structure
                if "user" in profile_data and "stats" in profile_data:
                    user_data = profile_data["user"]
                    stats_data = profile_data["stats"]
                    
                    # Check user data matches our test user
                    if (user_data.get("id") == self.user_id and
                        user_data.get("email") == self.test_user_email):
                        
                        self.log_test("Protected Endpoint (Valid Token)", "PASS", 
                                    f"Profile accessed successfully - Stats: {stats_data}")
                        return True
                    else:
                        self.log_test("Protected Endpoint (Valid Token)", "FAIL", 
                                    "Profile data doesn't match test user")
                        return False
                else:
                    self.log_test("Protected Endpoint (Valid Token)", "FAIL", 
                                "Profile response missing required fields")
                    return False
            else:
                self.log_test("Protected Endpoint (Valid Token)", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoint (Valid Token)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test protected endpoints with invalid JWT tokens"""
        try:
            # Test with invalid token
            invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
            response = self.session.get(f"{self.base_url}/profile", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint (Invalid Token)", "PASS", 
                            "Invalid token correctly rejected with 401")
                return True
            else:
                self.log_test("Protected Endpoint (Invalid Token)", "FAIL", 
                            f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoint (Invalid Token)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_protected_endpoint_without_token(self):
        """Test protected endpoints without any token"""
        try:
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/profile")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log_test("Protected Endpoint (No Token)", "PASS", 
                            f"Missing token correctly rejected with {response.status_code}")
                return True
            else:
                self.log_test("Protected Endpoint (No Token)", "FAIL", 
                            f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoint (No Token)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_profile_endpoint(self):
        """Test if the user profile endpoint works correctly"""
        try:
            if not self.auth_token:
                self.log_test("User Profile Endpoint", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                # Check all required fields
                required_top_level = ["user", "stats", "valuations"]
                required_user_fields = ["id", "email", "name", "provider", "created_at"]
                required_stats_fields = ["owned_jerseys", "wanted_jerseys", "active_listings"]
                
                # Verify top-level structure
                if not all(field in profile for field in required_top_level):
                    missing = [f for f in required_top_level if f not in profile]
                    self.log_test("User Profile Endpoint", "FAIL", f"Missing top-level fields: {missing}")
                    return False
                
                # Verify user fields
                user_data = profile["user"]
                if not all(field in user_data for field in required_user_fields):
                    missing = [f for f in required_user_fields if f not in user_data]
                    self.log_test("User Profile Endpoint", "FAIL", f"Missing user fields: {missing}")
                    return False
                
                # Verify stats fields
                stats_data = profile["stats"]
                if not all(field in stats_data for field in required_stats_fields):
                    missing = [f for f in required_stats_fields if f not in stats_data]
                    self.log_test("User Profile Endpoint", "FAIL", f"Missing stats fields: {missing}")
                    return False
                
                # Verify data integrity
                if (user_data.get("id") == self.user_id and
                    user_data.get("email") == self.test_user_email and
                    user_data.get("name") == TEST_NAME):
                    
                    self.log_test("User Profile Endpoint", "PASS", 
                                f"Profile endpoint working correctly - User: {user_data.get('name')}, "
                                f"Stats: {stats_data['owned_jerseys']} owned, {stats_data['wanted_jerseys']} wanted, "
                                f"{stats_data['active_listings']} listings")
                    return True
                else:
                    self.log_test("User Profile Endpoint", "FAIL", "Profile data integrity check failed")
                    return False
            else:
                self.log_test("User Profile Endpoint", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Profile Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_invalid_credentials_login(self):
        """Test login with invalid credentials"""
        try:
            # Clear auth header
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test with wrong password
            payload = {
                "email": self.test_user_email if self.test_user_email else TEST_EMAIL,
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 400:
                self.log_test("Invalid Credentials Login", "PASS", 
                            "Invalid credentials correctly rejected with 400")
                return True
            else:
                self.log_test("Invalid Credentials Login", "FAIL", 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Credentials Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_duplicate_user_registration(self):
        """Test registration with existing email"""
        try:
            if not self.test_user_email:
                self.log_test("Duplicate User Registration", "FAIL", "No test user email available")
                return False
            
            # Try to register with same email
            payload = {
                "email": self.test_user_email,
                "password": TEST_PASSWORD,
                "name": "Another Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 400:
                self.log_test("Duplicate User Registration", "PASS", 
                            "Duplicate email correctly rejected with 400")
                return True
            else:
                self.log_test("Duplicate User Registration", "FAIL", 
                            f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate User Registration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚨 URGENT AUTHENTICATION TESTING - TopKit Backend")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Test data: {TEST_EMAIL} / {TEST_PASSWORD} / {TEST_NAME}")
        print("=" * 60)
        print()
        
        tests = [
            self.test_backend_connectivity,
            self.test_user_registration,
            self.test_user_login,
            self.test_jwt_token_creation,
            self.test_protected_endpoint_with_valid_token,
            self.test_protected_endpoint_with_invalid_token,
            self.test_protected_endpoint_without_token,
            self.test_user_profile_endpoint,
            self.test_invalid_credentials_login,
            self.test_duplicate_user_registration
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
                print(f"❌ {test.__name__}: FAIL - Exception: {str(e)}")
                failed += 1
        
        print("=" * 60)
        print(f"📊 URGENT AUTHENTICATION TEST RESULTS:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        print()
        
        if failed == 0:
            print("🎉 ALL AUTHENTICATION TESTS PASSED!")
            print("✅ Backend authentication is working correctly")
            print("✅ Users should be able to register and login")
            print("✅ JWT tokens are working properly")
            print("✅ Issue may be in frontend-backend communication")
        else:
            print("🚨 CRITICAL AUTHENTICATION ISSUES FOUND!")
            print("❌ This explains why users cannot connect/register")
            print("❌ Backend authentication system has problems")
            print("❌ Check server status and network configuration")
        
        print("=" * 60)
        
        return failed == 0

if __name__ == "__main__":
    tester = AuthenticationTester()
    tester.run_all_tests()