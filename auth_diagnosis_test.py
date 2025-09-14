#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - URGENT AUTHENTICATION DIAGNOSIS
Testing authentication system to diagnose disconnection issues
"""

import requests
import json
import uuid
from datetime import datetime
import time
import jwt

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@topkit.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_NAME = "testuser"

class AuthenticationDiagnosticTester:
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
    
    def decode_jwt_token(self, token):
        """Decode JWT token to inspect its contents"""
        try:
            # Decode without verification to inspect contents
            decoded = jwt.decode(token, options={"verify_signature": False})
            return decoded
        except Exception as e:
            return {"error": str(e)}
    
    def test_priority_1_account_creation(self):
        """PRIORITY 1: Test account creation with simple credentials"""
        try:
            # Use the exact credentials from the review request
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            print(f"🎯 PRIORITY 1: Testing account creation with credentials:")
            print(f"   Email: {TEST_USER_EMAIL}")
            print(f"   Password: {TEST_USER_PASSWORD}")
            print(f"   Name: {TEST_USER_NAME}")
            print()
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            print(f"Registration Response Status: {response.status_code}")
            print(f"Registration Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Registration Response Data: {json.dumps(data, indent=2)}")
                
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    
                    # Decode and inspect the JWT token
                    token_contents = self.decode_jwt_token(self.auth_token)
                    print(f"JWT Token Contents: {json.dumps(token_contents, indent=2, default=str)}")
                    
                    # Check token expiration
                    if "exp" in token_contents:
                        exp_timestamp = token_contents["exp"]
                        exp_datetime = datetime.fromtimestamp(exp_timestamp)
                        current_time = datetime.now()
                        time_until_expiry = exp_datetime - current_time
                        
                        print(f"Token Expiration: {exp_datetime}")
                        print(f"Current Time: {current_time}")
                        print(f"Time Until Expiry: {time_until_expiry}")
                        
                        if time_until_expiry.total_seconds() > 0:
                            self.log_test("PRIORITY 1 - Account Creation", "PASS", 
                                        f"✅ Account created successfully\n" +
                                        f"   User ID: {self.user_id}\n" +
                                        f"   Token Length: {len(self.auth_token)} chars\n" +
                                        f"   Token Expires: {exp_datetime}\n" +
                                        f"   Valid For: {time_until_expiry}")
                            return True
                        else:
                            self.log_test("PRIORITY 1 - Account Creation", "FAIL", 
                                        f"❌ TOKEN EXPIRED IMMEDIATELY!\n" +
                                        f"   Token expired at: {exp_datetime}\n" +
                                        f"   Current time: {current_time}\n" +
                                        f"   This explains the disconnection issue!")
                            return False
                    else:
                        self.log_test("PRIORITY 1 - Account Creation", "FAIL", "❌ No expiration field in JWT token")
                        return False
                else:
                    self.log_test("PRIORITY 1 - Account Creation", "FAIL", 
                                f"❌ Missing token or user in response\n" +
                                f"   Response: {json.dumps(data, indent=2)}")
                    return False
            else:
                error_text = response.text
                self.log_test("PRIORITY 1 - Account Creation", "FAIL", 
                            f"❌ Registration failed\n" +
                            f"   Status: {response.status_code}\n" +
                            f"   Response: {error_text}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 1 - Account Creation", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def test_priority_2_token_validation(self):
        """PRIORITY 2: Test JWT token validation"""
        try:
            if not self.auth_token:
                self.log_test("PRIORITY 2 - Token Validation", "FAIL", "❌ No auth token available from registration")
                return False
            
            print(f"🎯 PRIORITY 2: Testing token validation")
            print(f"   Token: {self.auth_token[:50]}...")
            print()
            
            # Set authorization header
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            # Test the /api/profile endpoint
            response = self.session.get(f"{self.base_url}/profile")
            
            print(f"Profile Response Status: {response.status_code}")
            print(f"Profile Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Profile Response Data: {json.dumps(data, indent=2)}")
                
                if "user" in data and data["user"].get("id") == self.user_id:
                    self.log_test("PRIORITY 2 - Token Validation", "PASS", 
                                f"✅ JWT token is valid and working\n" +
                                f"   Profile retrieved successfully\n" +
                                f"   User ID matches: {self.user_id}")
                    return True
                else:
                    self.log_test("PRIORITY 2 - Token Validation", "FAIL", 
                                f"❌ Profile data mismatch\n" +
                                f"   Expected user ID: {self.user_id}\n" +
                                f"   Received: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("PRIORITY 2 - Token Validation", "FAIL", 
                            f"❌ TOKEN REJECTED - 401 Unauthorized\n" +
                            f"   This indicates the token is invalid or expired\n" +
                            f"   Response: {response.text}")
                return False
            elif response.status_code == 403:
                self.log_test("PRIORITY 2 - Token Validation", "FAIL", 
                            f"❌ TOKEN MISSING - 403 Forbidden\n" +
                            f"   This indicates no token was sent\n" +
                            f"   Response: {response.text}")
                return False
            else:
                self.log_test("PRIORITY 2 - Token Validation", "FAIL", 
                            f"❌ Unexpected response\n" +
                            f"   Status: {response.status_code}\n" +
                            f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 2 - Token Validation", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def test_priority_3_session_persistence(self):
        """PRIORITY 3: Test session persistence - complete flow"""
        try:
            print(f"🎯 PRIORITY 3: Testing session persistence")
            print()
            
            # Step 1: Create a new account (fresh test)
            unique_email = f"persistence_test_{int(time.time())}@topkit.com"
            
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": f"Persistence Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("PRIORITY 3 - Session Persistence", "FAIL", 
                            f"❌ Could not create test account\n" +
                            f"   Status: {register_response.status_code}")
                return False
            
            register_data = register_response.json()
            test_token = register_data["token"]
            test_user_id = register_data["user"]["id"]
            
            print(f"✅ Step 1: Account created - User ID: {test_user_id}")
            
            # Step 2: Immediately use the token
            test_headers = {'Authorization': f'Bearer {test_token}'}
            immediate_response = self.session.get(f"{self.base_url}/profile", headers=test_headers)
            
            if immediate_response.status_code != 200:
                self.log_test("PRIORITY 3 - Session Persistence", "FAIL", 
                            f"❌ Token failed immediately after creation\n" +
                            f"   Status: {immediate_response.status_code}\n" +
                            f"   Response: {immediate_response.text}")
                return False
            
            print(f"✅ Step 2: Token works immediately after creation")
            
            # Step 3: Wait a moment and test again
            print("⏳ Step 3: Waiting 2 seconds to test persistence...")
            time.sleep(2)
            
            delayed_response = self.session.get(f"{self.base_url}/profile", headers=test_headers)
            
            if delayed_response.status_code != 200:
                self.log_test("PRIORITY 3 - Session Persistence", "FAIL", 
                            f"❌ Token failed after 2 seconds\n" +
                            f"   Status: {delayed_response.status_code}\n" +
                            f"   Response: {delayed_response.text}\n" +
                            f"   This indicates immediate expiration!")
                return False
            
            print(f"✅ Step 3: Token still works after 2 seconds")
            
            # Step 4: Test multiple authenticated operations
            operations_passed = 0
            total_operations = 3
            
            # Operation 1: Get profile again
            profile_response = self.session.get(f"{self.base_url}/profile", headers=test_headers)
            if profile_response.status_code == 200:
                operations_passed += 1
                print(f"✅ Operation 1: Profile access successful")
            else:
                print(f"❌ Operation 1: Profile access failed - {profile_response.status_code}")
            
            # Operation 2: Get collections
            collections_response = self.session.get(f"{self.base_url}/collections/owned", headers=test_headers)
            if collections_response.status_code == 200:
                operations_passed += 1
                print(f"✅ Operation 2: Collections access successful")
            else:
                print(f"❌ Operation 2: Collections access failed - {collections_response.status_code}")
            
            # Operation 3: Try to create a jersey
            jersey_payload = {
                "team": "Test Team",
                "season": "2023-24",
                "player": "Test Player",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Test Brand",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for persistence testing"
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, headers=test_headers)
            if jersey_response.status_code == 200:
                operations_passed += 1
                print(f"✅ Operation 3: Jersey creation successful")
            else:
                print(f"❌ Operation 3: Jersey creation failed - {jersey_response.status_code}")
            
            if operations_passed == total_operations:
                self.log_test("PRIORITY 3 - Session Persistence", "PASS", 
                            f"✅ Session persistence working perfectly\n" +
                            f"   All {total_operations} authenticated operations successful\n" +
                            f"   No immediate disconnection detected")
                return True
            else:
                self.log_test("PRIORITY 3 - Session Persistence", "FAIL", 
                            f"❌ Session persistence issues detected\n" +
                            f"   Only {operations_passed}/{total_operations} operations successful\n" +
                            f"   This indicates authentication problems")
                return False
                
        except Exception as e:
            self.log_test("PRIORITY 3 - Session Persistence", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def run_urgent_authentication_diagnosis(self):
        """Run the urgent authentication diagnosis"""
        print("=" * 80)
        print("🚨 URGENT AUTHENTICATION DIAGNOSIS - TopKit Backend Testing")
        print("=" * 80)
        print("Testing authentication system to diagnose disconnection issues")
        print("Focus: Why users get disconnected immediately after signup/login")
        print("=" * 80)
        print()
        
        results = []
        
        # Run priority tests
        results.append(self.test_priority_1_account_creation())
        results.append(self.test_priority_2_token_validation())
        results.append(self.test_priority_3_session_persistence())
        
        # Summary
        print("=" * 80)
        print("🎯 URGENT DIAGNOSIS SUMMARY")
        print("=" * 80)
        
        passed = sum(results)
        total = len(results)
        
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        if passed == total:
            print("✅ AUTHENTICATION SYSTEM IS WORKING CORRECTLY")
            print("   - Account creation successful")
            print("   - JWT tokens are valid and not expired")
            print("   - Session persistence working")
            print("   - The disconnection issue is likely frontend-related")
        else:
            print("❌ AUTHENTICATION ISSUES DETECTED")
            print("   - Backend authentication problems found")
            print("   - This explains the user disconnection issues")
        
        print("=" * 80)
        return passed == total

if __name__ == "__main__":
    tester = AuthenticationDiagnosticTester()
    success = tester.run_urgent_authentication_diagnosis()
    exit(0 if success else 1)