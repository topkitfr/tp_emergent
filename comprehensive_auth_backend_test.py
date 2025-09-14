#!/usr/bin/env python3
"""
TopKit Comprehensive Authentication Backend Testing
Testing authentication endpoints and basic backend functionality as requested
"""

import requests
import json
import sys
from datetime import datetime

# Configuration from frontend/.env
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

# Test credentials from review request
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ComprehensiveAuthTester:
    def __init__(self):
        self.test_results = []
        self.user_token = None
        self.admin_token = None
        self.user_info = None
        self.admin_info = None
        
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

    def test_api_health(self):
        """Test basic API health and connectivity"""
        print("🌐 Testing API Health and Connectivity...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys", timeout=10)
            
            if response.status_code in [200, 401]:  # Both are acceptable
                self.log_result(
                    "API Health Check",
                    True,
                    f"API responding correctly (HTTP {response.status_code})"
                )
                return True
            else:
                self.log_result(
                    "API Health Check",
                    False,
                    f"Unexpected status: {response.status_code}",
                    response.text[:200]
                )
                return False
        except Exception as e:
            self.log_result(
                "API Health Check",
                False,
                "",
                f"Connection error: {str(e)}"
            )
            return False

    def test_user_authentication(self):
        """Test user authentication with provided credentials"""
        print(f"🔐 Testing User Authentication ({USER_EMAIL})...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                self.user_info = data.get("user", {})
                
                self.log_result(
                    "User Authentication",
                    True,
                    f"Login successful - Name: {self.user_info.get('name')}, Role: {self.user_info.get('role')}, ID: {self.user_info.get('id')}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "User Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        print(f"🔐 Testing Admin Authentication ({ADMIN_EMAIL})...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.admin_info = data.get("user", {})
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Login successful - Name: {self.admin_info.get('name')}, Role: {self.admin_info.get('role')}, ID: {self.admin_info.get('id')}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_jwt_token_generation(self):
        """Test JWT token generation and format"""
        print("🔑 Testing JWT Token Generation...")
        
        tokens_valid = 0
        total_tokens = 0
        
        for token_name, token in [("User Token", self.user_token), ("Admin Token", self.admin_token)]:
            if token:
                total_tokens += 1
                try:
                    parts = token.split('.')
                    if len(parts) == 3:
                        import base64
                        import json
                        
                        # Decode header
                        header_part = parts[0] + '=' * (4 - len(parts[0]) % 4)
                        header = json.loads(base64.b64decode(header_part))
                        
                        tokens_valid += 1
                        self.log_result(
                            f"JWT Token Generation - {token_name}",
                            True,
                            f"Valid JWT format - Algorithm: {header.get('alg')}, Type: {header.get('typ')}"
                        )
                    else:
                        self.log_result(
                            f"JWT Token Generation - {token_name}",
                            False,
                            f"Invalid format - {len(parts)} parts instead of 3"
                        )
                except Exception as e:
                    self.log_result(
                        f"JWT Token Generation - {token_name}",
                        False,
                        "",
                        f"Token decode error: {str(e)}"
                    )
        
        return tokens_valid == total_tokens and total_tokens > 0

    def test_jwt_token_validation(self):
        """Test JWT token validation with protected endpoints"""
        print("🛡️ Testing JWT Token Validation...")
        
        validation_results = []
        
        for token_name, token in [("User", self.user_token), ("Admin", self.admin_token)]:
            if token:
                try:
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(f"{BACKEND_URL}/jerseys", headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        validation_results.append(True)
                        self.log_result(
                            f"JWT Token Validation - {token_name}",
                            True,
                            f"Token validated successfully - Access granted to protected endpoint"
                        )
                    else:
                        validation_results.append(False)
                        self.log_result(
                            f"JWT Token Validation - {token_name}",
                            False,
                            f"Token validation failed - HTTP {response.status_code}",
                            response.text[:200]
                        )
                except Exception as e:
                    validation_results.append(False)
                    self.log_result(
                        f"JWT Token Validation - {token_name}",
                        False,
                        "",
                        f"Exception: {str(e)}"
                    )
        
        return all(validation_results) and len(validation_results) > 0

    def test_basic_api_endpoints(self):
        """Test basic API endpoints functionality"""
        print("📡 Testing Basic API Endpoints...")
        
        endpoints_to_test = [
            ("/jerseys", "GET", "Jerseys Endpoint"),
            ("/marketplace/catalog", "GET", "Marketplace Catalog"),
            ("/explorer/leagues", "GET", "Explorer Leagues")
        ]
        
        successful_endpoints = 0
        
        for endpoint, method, name in endpoints_to_test:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
                
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    successful_endpoints += 1
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "data"
                    self.log_result(
                        f"Basic API - {name}",
                        True,
                        f"Endpoint accessible - Returned {count} items"
                    )
                else:
                    self.log_result(
                        f"Basic API - {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_result(
                    f"Basic API - {name}",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
        
        return successful_endpoints >= 2  # At least 2 out of 3 should work

    def test_admin_endpoints(self):
        """Test admin-specific endpoints"""
        print("👨‍💼 Testing Admin Endpoints...")
        
        if not self.admin_token:
            self.log_result(
                "Admin Endpoints",
                False,
                "",
                "No admin token available"
            )
            return False
        
        admin_endpoints = [
            ("/admin/jerseys/pending", "GET", "Pending Jerseys"),
            ("/admin/users", "GET", "Admin Users List")
        ]
        
        successful_admin_endpoints = 0
        
        for endpoint, method, name in admin_endpoints:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    successful_admin_endpoints += 1
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "data"
                    self.log_result(
                        f"Admin Endpoint - {name}",
                        True,
                        f"Admin endpoint accessible - Returned {count} items"
                    )
                else:
                    self.log_result(
                        f"Admin Endpoint - {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_result(
                    f"Admin Endpoint - {name}",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
        
        return successful_admin_endpoints >= 1  # At least 1 admin endpoint should work

    def test_user_specific_endpoints(self):
        """Test user-specific endpoints"""
        print("👤 Testing User-Specific Endpoints...")
        
        if not self.user_token:
            self.log_result(
                "User-Specific Endpoints",
                False,
                "",
                "No user token available"
            )
            return False
        
        user_endpoints = [
            (f"/users/{self.user_info.get('id')}/jerseys", "GET", "User Jerseys"),
            ("/notifications", "GET", "User Notifications")
        ]
        
        successful_user_endpoints = 0
        
        for endpoint, method, name in user_endpoints:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    successful_user_endpoints += 1
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "data"
                    self.log_result(
                        f"User Endpoint - {name}",
                        True,
                        f"User endpoint accessible - Returned {count} items"
                    )
                else:
                    self.log_result(
                        f"User Endpoint - {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_result(
                    f"User Endpoint - {name}",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
        
        return successful_user_endpoints >= 1  # At least 1 user endpoint should work

    def run_all_tests(self):
        """Run all authentication and backend tests"""
        print("🚀 Starting TopKit Comprehensive Authentication Backend Testing")
        print("=" * 80)
        print("Focus: Authentication endpoints and basic backend functionality")
        print("=" * 80)
        
        # Core authentication tests
        api_health = self.test_api_health()
        user_auth = self.test_user_authentication()
        admin_auth = self.test_admin_authentication()
        
        if not (user_auth and admin_auth):
            print("❌ Authentication failed - limited backend testing possible")
        
        # JWT token tests
        jwt_generation = self.test_jwt_token_generation()
        jwt_validation = self.test_jwt_token_validation()
        
        # API functionality tests
        basic_api = self.test_basic_api_endpoints()
        admin_endpoints = self.test_admin_endpoints()
        user_endpoints = self.test_user_specific_endpoints()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AUTHENTICATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        jwt_tests = [r for r in self.test_results if "JWT" in r["test"]]
        api_tests = [r for r in self.test_results if "API" in r["test"] or "Endpoint" in r["test"]]
        
        print("🔐 AUTHENTICATION RESULTS:")
        for result in auth_tests:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
        
        print("\n🔑 JWT TOKEN RESULTS:")
        for result in jwt_tests:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
        
        print("\n📡 API ENDPOINT RESULTS:")
        for result in api_tests:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
        
        # Authentication summary
        auth_success = all(r["success"] for r in auth_tests)
        jwt_success = all(r["success"] for r in jwt_tests)
        
        print(f"\n🎯 CRITICAL AUTHENTICATION STATUS:")
        print(f"  Authentication System: {'✅ OPERATIONAL' if auth_success else '❌ ISSUES DETECTED'}")
        print(f"  JWT Token System: {'✅ OPERATIONAL' if jwt_success else '❌ ISSUES DETECTED'}")
        print(f"  Backend API Health: {'✅ OPERATIONAL' if success_rate >= 70 else '❌ ISSUES DETECTED'}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results,
            "authentication_working": auth_success,
            "jwt_working": jwt_success,
            "backend_healthy": success_rate >= 70
        }

if __name__ == "__main__":
    tester = ComprehensiveAuthTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)