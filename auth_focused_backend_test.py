#!/usr/bin/env python3
"""
TopKit Authentication Focused Backend Testing
Testing authentication endpoints as requested in the review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from frontend/.env
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = [
    {
        "email": "steinmetzlivio@gmail.com",
        "password": "TopKit123!",
        "name": "User Account"
    },
    {
        "email": "topkitfr@gmail.com", 
        "password": "TopKitSecure789#",
        "name": "Admin Account"
    }
]

class AuthenticationTester:
    def __init__(self):
        self.test_results = []
        self.tokens = {}
        
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

    def test_api_connectivity(self):
        """Test basic API connectivity and health"""
        print("🌐 Testing API Connectivity and Health...")
        
        # Test basic endpoint accessibility
        try:
            # Try a simple GET request to see if API is responding
            response = requests.get(f"{BACKEND_URL}/jerseys", timeout=10)
            
            if response.status_code in [200, 401]:  # 401 is expected for protected endpoint
                self.log_result(
                    "API Connectivity",
                    True,
                    f"API is responding (HTTP {response.status_code})"
                )
                return True
            else:
                self.log_result(
                    "API Connectivity",
                    False,
                    f"Unexpected HTTP status: {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return False
        except requests.exceptions.RequestException as e:
            self.log_result(
                "API Connectivity",
                False,
                "",
                f"Connection error: {str(e)}"
            )
            return False

    def test_authentication_endpoint(self, email, password, account_name):
        """Test authentication with specific credentials"""
        print(f"🔐 Testing Authentication: {account_name} ({email})...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                user_info = data.get("user", {})
                
                if token:
                    self.tokens[email] = token
                    self.log_result(
                        f"Authentication - {account_name}",
                        True,
                        f"Login successful - Name: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                    )
                    return True, token, user_info
                else:
                    self.log_result(
                        f"Authentication - {account_name}",
                        False,
                        "No token in response",
                        json.dumps(data, indent=2)
                    )
                    return False, None, None
            else:
                self.log_result(
                    f"Authentication - {account_name}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500] if response.text else "No response body"
                )
                return False, None, None
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"Authentication - {account_name}",
                False,
                "",
                f"Request error: {str(e)}"
            )
            return False, None, None

    def test_jwt_token_validation(self, email, token, account_name):
        """Test JWT token validation by accessing protected endpoint"""
        print(f"🔑 Testing JWT Token Validation: {account_name}...")
        
        if not token:
            self.log_result(
                f"JWT Token Validation - {account_name}",
                False,
                "",
                "No token available for validation"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BACKEND_URL}/auth/profile", headers=headers, timeout=10)
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_result(
                    f"JWT Token Validation - {account_name}",
                    True,
                    f"Token valid - Profile accessed: {profile_data.get('name')} ({profile_data.get('email')})"
                )
                return True
            elif response.status_code == 401:
                self.log_result(
                    f"JWT Token Validation - {account_name}",
                    False,
                    "Token rejected by server",
                    response.text[:200] if response.text else "No response body"
                )
                return False
            else:
                self.log_result(
                    f"JWT Token Validation - {account_name}",
                    False,
                    f"Unexpected HTTP status: {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"JWT Token Validation - {account_name}",
                False,
                "",
                f"Request error: {str(e)}"
            )
            return False

    def test_protected_endpoint_access(self, email, token, account_name):
        """Test access to protected endpoints with valid token"""
        print(f"🛡️ Testing Protected Endpoint Access: {account_name}...")
        
        if not token:
            self.log_result(
                f"Protected Endpoint Access - {account_name}",
                False,
                "",
                "No token available for testing"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test user-specific endpoint
            response = requests.get(f"{BACKEND_URL}/users/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.log_result(
                    f"Protected Endpoint Access - {account_name}",
                    True,
                    f"Protected endpoint accessible - User: {user_data.get('name')}"
                )
                return True
            elif response.status_code == 404:
                # Try alternative endpoint if /users/me doesn't exist
                response = requests.get(f"{BACKEND_URL}/jerseys", headers=headers, timeout=10)
                if response.status_code == 200:
                    jerseys = response.json()
                    self.log_result(
                        f"Protected Endpoint Access - {account_name}",
                        True,
                        f"Protected endpoint accessible - Found {len(jerseys) if isinstance(jerseys, list) else 'data'} jerseys"
                    )
                    return True
                else:
                    self.log_result(
                        f"Protected Endpoint Access - {account_name}",
                        False,
                        f"Alternative endpoint also failed: HTTP {response.status_code}",
                        response.text[:200] if response.text else "No response body"
                    )
                    return False
            else:
                self.log_result(
                    f"Protected Endpoint Access - {account_name}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200] if response.text else "No response body"
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result(
                f"Protected Endpoint Access - {account_name}",
                False,
                "",
                f"Request error: {str(e)}"
            )
            return False

    def test_token_format_and_structure(self, email, token, account_name):
        """Test JWT token format and basic structure"""
        print(f"📋 Testing Token Format: {account_name}...")
        
        if not token:
            self.log_result(
                f"Token Format - {account_name}",
                False,
                "",
                "No token available for format testing"
            )
            return False
        
        try:
            # Basic JWT format check (should have 3 parts separated by dots)
            parts = token.split('.')
            
            if len(parts) == 3:
                # Try to decode header (first part) to verify it's a valid JWT
                import base64
                import json
                
                # Add padding if needed
                header_part = parts[0]
                header_part += '=' * (4 - len(header_part) % 4)
                
                try:
                    header = json.loads(base64.b64decode(header_part))
                    algorithm = header.get('alg', 'unknown')
                    token_type = header.get('typ', 'unknown')
                    
                    self.log_result(
                        f"Token Format - {account_name}",
                        True,
                        f"Valid JWT format - Algorithm: {algorithm}, Type: {token_type}, Length: {len(token)} chars"
                    )
                    return True
                except Exception as decode_error:
                    self.log_result(
                        f"Token Format - {account_name}",
                        False,
                        "Token has 3 parts but header decode failed",
                        str(decode_error)
                    )
                    return False
            else:
                self.log_result(
                    f"Token Format - {account_name}",
                    False,
                    f"Invalid JWT format - Expected 3 parts, got {len(parts)}",
                    f"Token: {token[:50]}..."
                )
                return False
                
        except Exception as e:
            self.log_result(
                f"Token Format - {account_name}",
                False,
                "",
                f"Error analyzing token: {str(e)}"
            )
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting TopKit Authentication Backend Testing")
        print("=" * 70)
        print("Focus: Authentication endpoints with provided credentials")
        print("=" * 70)
        
        # Test API connectivity first
        connectivity_success = self.test_api_connectivity()
        
        if not connectivity_success:
            print("❌ API connectivity failed - cannot proceed with authentication tests")
            return self.generate_summary()
        
        # Test authentication for each credential set
        auth_results = []
        for cred in TEST_CREDENTIALS:
            success, token, user_info = self.test_authentication_endpoint(
                cred["email"], 
                cred["password"], 
                cred["name"]
            )
            auth_results.append((success, token, user_info, cred))
            
            if success and token:
                # Test JWT token validation
                self.test_jwt_token_validation(cred["email"], token, cred["name"])
                
                # Test token format
                self.test_token_format_and_structure(cred["email"], token, cred["name"])
                
                # Test protected endpoint access
                self.test_protected_endpoint_access(cred["email"], token, cred["name"])
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 70)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        # Authentication-specific summary
        print("\n🔐 AUTHENTICATION SUMMARY:")
        auth_tests = [r for r in self.test_results if "Authentication -" in r["test"]]
        successful_auths = [r for r in auth_tests if r["success"]]
        
        if successful_auths:
            print("✅ Successfully authenticated accounts:")
            for result in successful_auths:
                print(f"  • {result['test']}: {result['details']}")
        
        failed_auths = [r for r in auth_tests if not r["success"]]
        if failed_auths:
            print("❌ Failed authentication attempts:")
            for result in failed_auths:
                print(f"  • {result['test']}: {result['error']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results,
            "tokens_obtained": len(self.tokens)
        }

if __name__ == "__main__":
    tester = AuthenticationTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)