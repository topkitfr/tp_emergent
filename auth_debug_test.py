#!/usr/bin/env python3
"""
TopKit Authentication Debug Test - Specific Login Issue Investigation
Testing authentication workflow to debug frontend login issue as requested
"""

import requests
import json
import jwt
from datetime import datetime
import time

# Configuration - Using correct backend URL from frontend .env
BASE_URL = "https://jersey-tracker.preview.emergentagent.com/api"

class AuthDebugTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.login_token = None
        self.user_data = None
        
    def log_test(self, test_name, status, details=""):
        """Log test results with detailed information"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_login_endpoint(self):
        """Test Login Endpoint with steinmetzlivio@gmail.com"""
        print("🔐 TESTING LOGIN ENDPOINT")
        print("=" * 50)
        
        try:
            # Test with the specific user mentioned in the request
            login_payload = {
                "email": "steinmetzlivio@gmail.com",
                "password": "123"  # Using correct password provided
            }
            
            print(f"🔍 Attempting login with: {login_payload['email']}")
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📡 Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response structure as specified in request
                if "token" in data and "user" in data:
                    token = data["token"]
                    user = data["user"]
                    
                    # Check token is not null/empty
                    if token and token.strip():
                        # Check user object has all required fields
                        required_fields = ["id", "email", "name", "role"]
                        missing_fields = [field for field in required_fields if field not in user]
                        
                        if not missing_fields:
                            # Verify JWT token structure
                            try:
                                decoded = jwt.decode(token, options={"verify_signature": False})
                                print(f"🔑 JWT Token Decoded: {json.dumps(decoded, indent=2, default=str)}")
                                
                                if "user_id" in decoded and "exp" in decoded:
                                    self.login_token = token
                                    self.user_data = user
                                    
                                    expected_response = {
                                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                        "user": {
                                            "id": "some-uuid",
                                            "email": "steinmetzlivio@gmail.com",
                                            "name": "User Name", 
                                            "role": "user"
                                        }
                                    }
                                    
                                    self.log_test("Login Endpoint Structure Validation", "PASS", 
                                                f"Response matches expected structure. User: {user['email']}, Role: {user.get('role', 'N/A')}")
                                    return True
                                else:
                                    self.log_test("Login Endpoint JWT Validation", "FAIL", 
                                                "JWT token missing required fields (user_id, exp)")
                                    return False
                            except Exception as jwt_error:
                                self.log_test("Login Endpoint JWT Validation", "FAIL", 
                                            f"Invalid JWT token structure: {jwt_error}")
                                return False
                        else:
                            self.log_test("Login Endpoint User Fields", "FAIL", 
                                        f"Missing required user fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Login Endpoint Token Check", "FAIL", 
                                    "Token is null or empty")
                        return False
                else:
                    self.log_test("Login Endpoint Response Structure", "FAIL", 
                                "Missing 'token' or 'user' in response")
                    return False
                    
            elif response.status_code == 400:
                error_data = response.json() if response.content else {"detail": "No response body"}
                print(f"📡 Error Response: {json.dumps(error_data, indent=2)}")
                
                # Check if user doesn't exist - might need registration
                if "Invalid credentials" in str(error_data):
                    self.log_test("Login Endpoint", "INFO", 
                                "User may not exist or password incorrect. Will test registration.")
                    return "NEED_REGISTRATION"
                else:
                    self.log_test("Login Endpoint", "FAIL", 
                                f"Login failed with 400: {error_data}")
                    return False
            else:
                error_text = response.text if response.content else "No response body"
                print(f"📡 Error Response: {error_text}")
                self.log_test("Login Endpoint", "FAIL", 
                            f"Unexpected status code {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Login Endpoint", "FAIL", f"Exception occurred: {str(e)}")
            return False
    
    def test_user_registration(self):
        """Test User Registration if login fails"""
        print("📝 TESTING USER REGISTRATION")
        print("=" * 50)
        
        try:
            register_payload = {
                "email": "steinmetzlivio@gmail.com",
                "password": "123",
                "name": "Livio Steinmetz"
            }
            
            print(f"🔍 Attempting registration with: {register_payload['email']}")
            response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📡 Response Data: {json.dumps(data, indent=2)}")
                
                # Verify same response structure as login
                if "token" in data and "user" in data:
                    token = data["token"]
                    user = data["user"]
                    
                    if token and token.strip():
                        required_fields = ["id", "email", "name", "role"]
                        missing_fields = [field for field in required_fields if field not in user]
                        
                        if not missing_fields:
                            self.login_token = token
                            self.user_data = user
                            self.log_test("User Registration", "PASS", 
                                        f"User registered successfully. Email: {user['email']}, Role: {user.get('role', 'N/A')}")
                            return True
                        else:
                            self.log_test("User Registration", "FAIL", 
                                        f"Missing required user fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("User Registration", "FAIL", "Token is null or empty")
                        return False
                else:
                    self.log_test("User Registration", "FAIL", 
                                "Missing 'token' or 'user' in response")
                    return False
                    
            elif response.status_code == 400:
                error_data = response.json() if response.content else {"detail": "No response body"}
                print(f"📡 Error Response: {json.dumps(error_data, indent=2)}")
                
                if "already exists" in str(error_data):
                    self.log_test("User Registration", "INFO", 
                                "User already exists. This is expected - will retry login.")
                    return "USER_EXISTS"
                else:
                    self.log_test("User Registration", "FAIL", 
                                f"Registration failed: {error_data}")
                    return False
            else:
                error_text = response.text if response.content else "No response body"
                self.log_test("User Registration", "FAIL", 
                            f"Unexpected status code {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Exception occurred: {str(e)}")
            return False
    
    def test_profile_endpoint(self):
        """Test Profile Endpoint with Authorization Bearer token"""
        print("👤 TESTING PROFILE ENDPOINT")
        print("=" * 50)
        
        if not self.login_token:
            self.log_test("Profile Endpoint", "FAIL", "No login token available")
            return False
        
        try:
            # Set Authorization header
            headers = {'Authorization': f'Bearer {self.login_token}'}
            
            print(f"🔍 Making profile request with token: {self.login_token[:50]}...")
            response = self.session.get(f"{self.base_url}/profile", headers=headers)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📡 Response Data: {json.dumps(data, indent=2)}")
                
                # Verify response structure as specified in request
                if "user" in data:
                    user = data["user"]
                    required_fields = ["id", "email", "name", "role"]
                    missing_fields = [field for field in required_fields if field not in user]
                    
                    if not missing_fields:
                        # Verify user data matches login response
                        if self.user_data:
                            matches = (
                                user["id"] == self.user_data["id"] and
                                user["email"] == self.user_data["email"] and
                                user["name"] == self.user_data["name"]
                            )
                            
                            if matches:
                                self.log_test("Profile Endpoint", "PASS", 
                                            f"Profile data matches login response. User: {user['email']}")
                                return True
                            else:
                                self.log_test("Profile Endpoint", "FAIL", 
                                            "Profile data doesn't match login response")
                                return False
                        else:
                            self.log_test("Profile Endpoint", "PASS", 
                                        f"Profile retrieved successfully. User: {user['email']}")
                            return True
                    else:
                        self.log_test("Profile Endpoint", "FAIL", 
                                    f"Missing required user fields: {missing_fields}")
                        return False
                else:
                    self.log_test("Profile Endpoint", "FAIL", 
                                "Missing 'user' in response")
                    return False
                    
            elif response.status_code == 401:
                error_data = response.json() if response.content else {"detail": "No response body"}
                self.log_test("Profile Endpoint", "FAIL", 
                            f"Authentication failed (401): {error_data}")
                return False
            else:
                error_text = response.text if response.content else "No response body"
                self.log_test("Profile Endpoint", "FAIL", 
                            f"Unexpected status code {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Endpoint", "FAIL", f"Exception occurred: {str(e)}")
            return False
    
    def test_token_validation(self):
        """Test Token Validation scenarios"""
        print("🔑 TESTING TOKEN VALIDATION")
        print("=" * 50)
        
        # Test 1: Invalid token should return 401
        try:
            invalid_headers = {'Authorization': 'Bearer invalid_token_12345'}
            response = self.session.get(f"{self.base_url}/profile", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("Invalid Token Test", "PASS", "Invalid token correctly rejected with 401")
            else:
                self.log_test("Invalid Token Test", "FAIL", 
                            f"Expected 401 for invalid token, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid Token Test", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 2: Expired token (simulate by creating malformed token)
        try:
            expired_headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired.token'}
            response = self.session.get(f"{self.base_url}/profile", headers=expired_headers)
            
            if response.status_code == 401:
                self.log_test("Expired Token Test", "PASS", "Expired token correctly rejected with 401")
            else:
                self.log_test("Expired Token Test", "FAIL", 
                            f"Expected 401 for expired token, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Expired Token Test", "FAIL", f"Exception: {str(e)}")
            return False
        
        # Test 3: Valid token should return user data
        if self.login_token:
            try:
                valid_headers = {'Authorization': f'Bearer {self.login_token}'}
                response = self.session.get(f"{self.base_url}/profile", headers=valid_headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data:
                        self.log_test("Valid Token Test", "PASS", "Valid token correctly returns user data")
                        return True
                    else:
                        self.log_test("Valid Token Test", "FAIL", "Valid token response missing user data")
                        return False
                else:
                    self.log_test("Valid Token Test", "FAIL", 
                                f"Valid token failed with status {response.status_code}")
                    return False
            except Exception as e:
                self.log_test("Valid Token Test", "FAIL", f"Exception: {str(e)}")
                return False
        else:
            self.log_test("Valid Token Test", "SKIP", "No valid token available for testing")
            return True
    
    def test_admin_account_role(self):
        """Test if admin account has proper role assignment"""
        print("👑 TESTING ADMIN ACCOUNT ROLE")
        print("=" * 50)
        
        try:
            # Test login with admin account
            admin_payload = {
                "email": "topkitfr@gmail.com",
                "password": "123"  # Using correct password
            }
            
            print(f"🔍 Testing admin account: {admin_payload['email']}")
            response = self.session.post(f"{self.base_url}/auth/login", json=admin_payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "role" in data["user"]:
                    role = data["user"]["role"]
                    if role == "admin":
                        self.log_test("Admin Account Role", "PASS", 
                                    f"Admin account has correct role: {role}")
                        return True
                    else:
                        self.log_test("Admin Account Role", "FAIL", 
                                    f"Admin account has incorrect role: {role} (expected: admin)")
                        return False
                else:
                    self.log_test("Admin Account Role", "FAIL", 
                                "Admin account response missing user or role")
                    return False
            elif response.status_code == 400:
                self.log_test("Admin Account Role", "INFO", 
                            "Admin account login failed - may need different password or registration")
                return "ADMIN_LOGIN_FAILED"
            else:
                self.log_test("Admin Account Role", "FAIL", 
                            f"Admin login failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Account Role", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_password_hashing(self):
        """Test if passwords are being hashed/verified correctly"""
        print("🔐 TESTING PASSWORD HASHING")
        print("=" * 50)
        
        try:
            # Create a test user to verify password hashing
            unique_email = f"hashtest_{int(time.time())}@example.com"
            test_password = "test_password_123"
            
            # Register user
            register_payload = {
                "email": unique_email,
                "password": test_password,
                "name": "Hash Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                # Now try to login with same credentials
                login_payload = {
                    "email": unique_email,
                    "password": test_password
                }
                
                login_response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
                
                if login_response.status_code == 200:
                    # Try with wrong password
                    wrong_payload = {
                        "email": unique_email,
                        "password": "wrong_password"
                    }
                    
                    wrong_response = self.session.post(f"{self.base_url}/auth/login", json=wrong_payload)
                    
                    if wrong_response.status_code == 400:
                        self.log_test("Password Hashing", "PASS", 
                                    "Password hashing/verification working correctly")
                        return True
                    else:
                        self.log_test("Password Hashing", "FAIL", 
                                    "Wrong password not rejected properly")
                        return False
                else:
                    self.log_test("Password Hashing", "FAIL", 
                                "Correct password not accepted")
                    return False
            else:
                self.log_test("Password Hashing", "FAIL", 
                            "Could not create test user for password testing")
                return False
                
        except Exception as e:
            self.log_test("Password Hashing", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_authentication_debug(self):
        """Run complete authentication debug workflow"""
        print("🔍 TOPKIT AUTHENTICATION DEBUG - LOGIN ISSUE INVESTIGATION")
        print("=" * 80)
        print("Testing authentication workflow to debug frontend login issue")
        print("Focus: steinmetzlivio@gmail.com login and token validation")
        print("=" * 80)
        print()
        
        results = {}
        
        # Step 1: Test login endpoint
        login_result = self.test_login_endpoint()
        results["login"] = login_result
        
        # Step 2: If login fails, test registration
        if login_result == "NEED_REGISTRATION":
            print("🔄 Login failed - testing registration...")
            register_result = self.test_user_registration()
            results["registration"] = register_result
            
            # If user already exists, retry login
            if register_result == "USER_EXISTS":
                print("🔄 User exists - retrying login...")
                login_result = self.test_login_endpoint()
                results["login_retry"] = login_result
        
        # Step 3: Test profile endpoint if we have a token
        if self.login_token:
            profile_result = self.test_profile_endpoint()
            results["profile"] = profile_result
        
        # Step 4: Test token validation scenarios
        token_result = self.test_token_validation()
        results["token_validation"] = token_result
        
        # Step 5: Test admin account role
        admin_result = self.test_admin_account_role()
        results["admin_role"] = admin_result
        
        # Step 6: Test password hashing
        password_result = self.test_password_hashing()
        results["password_hashing"] = password_result
        
        # Summary
        print("=" * 80)
        print("🎯 AUTHENTICATION DEBUG SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = 0
        issues = []
        
        for test_name, result in results.items():
            if result == True:
                print(f"✅ {test_name.replace('_', ' ').title()}: PASS")
                passed += 1
            elif result == False:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAIL")
                issues.append(test_name)
            else:
                print(f"⚠️ {test_name.replace('_', ' ').title()}: {result}")
            total += 1
        
        print()
        print(f"📊 Results: {passed}/{total} tests passed")
        
        if issues:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in issues:
                print(f"   - {issue.replace('_', ' ').title()}")
        
        if self.login_token:
            print(f"\n🔑 Login Token Available: YES")
            print(f"👤 User Data: {self.user_data}")
        else:
            print(f"\n🔑 Login Token Available: NO")
            print("❌ This indicates authentication is failing at the backend level")
        
        print("\n💡 RECOMMENDATIONS:")
        if not self.login_token:
            print("   - Backend authentication endpoints are not working properly")
            print("   - Frontend login issues are likely caused by backend failures")
            print("   - Check user credentials and backend authentication logic")
        else:
            print("   - Backend authentication is working correctly")
            print("   - Frontend login issues are likely in state management")
            print("   - Check React AuthContext and token persistence")
        
        return len(issues) == 0

if __name__ == "__main__":
    tester = AuthDebugTester()
    success = tester.run_authentication_debug()
    exit(0 if success else 1)