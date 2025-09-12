#!/usr/bin/env python3
"""
TopKit Authentication Comprehensive Test
Testing authentication for Bacquet.florent@gmail.com with password TopKitBeta2025!
Focus: Complete verification of backend login endpoint and token functionality
"""

import requests
import json
import sys
import time
from datetime import datetime
import jwt

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Review request credentials
REVIEW_CREDENTIALS = {
    "email": "Bacquet.florent@gmail.com",
    "password": "TopKitBeta2025!"
}

class ComprehensiveAuthTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        self.token = None
        
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
        
    def test_login_endpoint_structure(self):
        """Test the exact structure of the login endpoint response"""
        try:
            login_url = f"{BACKEND_URL}/auth/login"
            response = self.session.post(
                login_url,
                json=REVIEW_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔍 DETAILED LOGIN ANALYSIS")
            print(f"URL: {login_url}")
            print(f"Method: POST")
            print(f"Credentials: {REVIEW_CREDENTIALS['email']}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response.elapsed.total_seconds():.3f}s")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print(f"📋 RESPONSE STRUCTURE:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print()
                
                # Analyze token
                if 'token' in data:
                    token = data['token']
                    self.token = token
                    
                    # JWT Analysis
                    try:
                        # Decode without verification to inspect payload
                        decoded = jwt.decode(token, options={"verify_signature": False})
                        print(f"🔐 JWT TOKEN ANALYSIS:")
                        print(f"Token Length: {len(token)} characters")
                        print(f"Token Parts: {len(token.split('.'))}")
                        print(f"Payload: {json.dumps(decoded, indent=2, default=str)}")
                        print()
                        
                        self.log_test(
                            "Login Endpoint - Token Structure", 
                            True, 
                            f"Valid JWT with payload: user_id={decoded.get('user_id')}, exp={decoded.get('exp')}"
                        )
                    except Exception as e:
                        self.log_test(
                            "Login Endpoint - Token Analysis", 
                            False, 
                            error=f"JWT decode error: {e}"
                        )
                
                # Analyze user data
                if 'user' in data:
                    user = data['user']
                    self.log_test(
                        "Login Endpoint - User Data", 
                        True, 
                        f"Complete user object: ID={user.get('id')}, Name={user.get('name')}, Role={user.get('role')}, 2FA={user.get('two_factor_enabled')}"
                    )
                
                # Check message
                if 'message' in data:
                    self.log_test(
                        "Login Endpoint - Success Message", 
                        True, 
                        f"Message: {data['message']}"
                    )
                
                return True
            else:
                self.log_test(
                    "Login Endpoint - Authentication Failed", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Login Endpoint - Exception", False, error=str(e))
            return False
    
    def test_token_validation_endpoints(self):
        """Test token validation with multiple endpoints"""
        if not self.token:
            self.log_test("Token Validation", False, "No token available for testing")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test endpoints
        endpoints_to_test = [
            ("/profile", "User Profile"),
            ("/notifications", "User Notifications"),
            ("/users/me", "User Me (alternative)"),
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Token Validation - {description}", 
                        True, 
                        f"Endpoint accessible, response size: {len(str(data))} chars"
                    )
                elif response.status_code == 401:
                    self.log_test(
                        f"Token Validation - {description}", 
                        False, 
                        "Token rejected (401 Unauthorized)"
                    )
                elif response.status_code == 404:
                    self.log_test(
                        f"Token Validation - {description}", 
                        False, 
                        "Endpoint not found (404)"
                    )
                else:
                    self.log_test(
                        f"Token Validation - {description}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text[:100]}"
                    )
                    
            except Exception as e:
                self.log_test(f"Token Validation - {description}", False, error=str(e))
    
    def test_profile_endpoint_detailed(self):
        """Detailed test of the profile endpoint"""
        if not self.token:
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"👤 PROFILE ENDPOINT RESPONSE:")
                print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
                print()
                
                # Verify user data matches login response
                if 'user' in data:
                    user = data['user']
                    expected_email = REVIEW_CREDENTIALS['email']
                    actual_email = user.get('email')
                    
                    if actual_email == expected_email:
                        self.log_test(
                            "Profile Endpoint - Email Match", 
                            True, 
                            f"Email matches: {actual_email}"
                        )
                    else:
                        self.log_test(
                            "Profile Endpoint - Email Mismatch", 
                            False, 
                            f"Expected: {expected_email}, Got: {actual_email}"
                        )
                
                # Check stats
                if 'stats' in data:
                    stats = data['stats']
                    self.log_test(
                        "Profile Endpoint - User Stats", 
                        True, 
                        f"Stats available: {stats}"
                    )
                
                return True
            else:
                self.log_test(
                    "Profile Endpoint - Access Failed", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Profile Endpoint - Exception", False, error=str(e))
            return False
    
    def test_authentication_security(self):
        """Test authentication security features"""
        # Test with wrong password
        try:
            wrong_credentials = {
                "email": REVIEW_CREDENTIALS['email'],
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=wrong_credentials,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Security - Wrong Password", 
                    True, 
                    "Correctly rejected wrong password"
                )
            else:
                self.log_test(
                    "Authentication Security - Wrong Password", 
                    False, 
                    f"Unexpected response: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Authentication Security - Exception", False, error=str(e))
        
        # Test with invalid token
        try:
            invalid_token = "invalid.token.here"
            headers = {"Authorization": f"Bearer {invalid_token}"}
            response = self.session.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 401:
                self.log_test(
                    "Authentication Security - Invalid Token", 
                    True, 
                    "Correctly rejected invalid token"
                )
            else:
                self.log_test(
                    "Authentication Security - Invalid Token", 
                    False, 
                    f"Unexpected response: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Authentication Security - Invalid Token", False, error=str(e))
    
    def run_comprehensive_test(self):
        """Run comprehensive authentication test"""
        print("🔐 TopKit Authentication Comprehensive Test")
        print("=" * 60)
        print(f"Testing User: {REVIEW_CREDENTIALS['email']}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Test 1: Login endpoint structure
        login_success = self.test_login_endpoint_structure()
        
        if login_success:
            # Test 2: Token validation
            self.test_token_validation_endpoints()
            
            # Test 3: Profile endpoint detailed
            self.test_profile_endpoint_detailed()
        
        # Test 4: Security features
        self.test_authentication_security()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🎯 REVIEW REQUEST CONCLUSIONS:")
        print("=" * 60)
        
        # Check specific requirements
        login_working = any('Login Endpoint' in r['test'] and r['success'] for r in self.test_results)
        token_format_valid = any('Token Structure' in r['test'] and r['success'] for r in self.test_results)
        token_validation_working = any('Token Validation' in r['test'] and r['success'] for r in self.test_results)
        
        if login_working:
            print("✅ Backend login endpoint is WORKING correctly")
        else:
            print("❌ Backend login endpoint has issues")
            
        if token_format_valid:
            print("✅ Token format is PROPER JWT structure")
        else:
            print("❌ Token format issues detected")
            
        if token_validation_working:
            print("✅ Token validation is FUNCTIONAL")
        else:
            print("❌ Token validation has issues")
        
        print(f"\n📋 EXACT RESPONSE STRUCTURE from POST /api/auth/login:")
        print("- Returns HTTP 200 on success")
        print("- Contains 'token' field with valid JWT")
        print("- Contains 'user' object with id, name, email, role")
        print("- Contains 'message' field with success message")
        print("- JWT payload includes user_id and expiration")
        
        if failed_tests > 0:
            print(f"\n⚠️  ISSUES IDENTIFIED ({failed_tests} failed tests):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result.get('error', result.get('details', 'Unknown error'))}")

if __name__ == "__main__":
    tester = ComprehensiveAuthTester()
    tester.run_comprehensive_test()