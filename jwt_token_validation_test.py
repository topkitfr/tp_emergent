#!/usr/bin/env python3
"""
JWT Token Validation Test for Admin Endpoints
==============================================

This test specifically validates that JWT tokens work correctly with the fixed admin endpoints
and verifies the dependency injection fixes are working properly.
"""

import requests
import json
import jwt
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class JWTTokenValidationTest:
    def __init__(self):
        self.admin_token = None
        self.results = []
        
    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error_msg:
            print(f"    Error: {error_msg}")
        print()

    def authenticate_and_get_token(self):
        """Get admin JWT token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                
                # Decode token to inspect payload (without verification for inspection)
                try:
                    decoded = jwt.decode(self.admin_token, options={"verify_signature": False})
                    user_id = decoded.get("user_id")
                    exp = decoded.get("exp")
                    
                    self.log_result(
                        "JWT Token Generation",
                        True,
                        f"Token generated successfully - User ID: {user_id}, Expires: {datetime.fromtimestamp(exp) if exp else 'Unknown'}"
                    )
                    return True
                except Exception as decode_error:
                    self.log_result(
                        "JWT Token Generation",
                        True,
                        f"Token generated but decode failed: {str(decode_error)}"
                    )
                    return True
            else:
                self.log_result(
                    "JWT Token Generation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("JWT Token Generation", False, "", str(e))
            return False

    def test_token_with_admin_endpoints(self):
        """Test JWT token with all admin endpoints that were previously failing"""
        if not self.admin_token:
            self.log_result("Token Validation", False, "", "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test endpoints that were previously failing with HTTP 403
        endpoints_to_test = [
            ("/admin/users", "Admin Users"),
            ("/admin/traffic-stats", "Admin Traffic Stats"),
            ("/admin/activities", "Admin Activities"),
            ("/admin/beta/requests", "Admin Beta Requests")
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    data_info = ""
                    if isinstance(data, list):
                        data_info = f"Retrieved {len(data)} items"
                    elif isinstance(data, dict):
                        data_info = f"Retrieved data with {len(data.keys())} keys"
                    
                    self.log_result(
                        f"JWT Token with {name}",
                        True,
                        f"HTTP 200 - {data_info}"
                    )
                elif response.status_code == 403:
                    self.log_result(
                        f"JWT Token with {name}",
                        False,
                        f"HTTP 403 - Dependency injection issue still present",
                        response.text
                    )
                else:
                    self.log_result(
                        f"JWT Token with {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_result(f"JWT Token with {name}", False, "", str(e))

    def test_token_authorization_header_formats(self):
        """Test different authorization header formats"""
        if not self.admin_token:
            return
        
        # Test different header formats
        header_formats = [
            ({"Authorization": f"Bearer {self.admin_token}"}, "Bearer Token"),
            ({"Authorization": f"bearer {self.admin_token}"}, "Lowercase Bearer"),
            ({"Authorization": self.admin_token}, "Token Only"),
        ]
        
        for headers, format_name in header_formats:
            try:
                response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
                
                if response.status_code == 200:
                    self.log_result(
                        f"Authorization Format - {format_name}",
                        True,
                        "Token accepted"
                    )
                elif response.status_code == 401:
                    self.log_result(
                        f"Authorization Format - {format_name}",
                        False,
                        "Token rejected - Invalid format",
                        response.text
                    )
                else:
                    self.log_result(
                        f"Authorization Format - {format_name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_result(f"Authorization Format - {format_name}", False, "", str(e))

    def test_dependency_injection_fix_verification(self):
        """Specifically test that dependency injection fixes are working"""
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test the profile endpoint to verify get_current_user function works
        try:
            response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_role = data.get("role")
                user_id = data.get("id")
                
                self.log_result(
                    "Dependency Injection - get_current_user",
                    True,
                    f"Profile endpoint returns user object correctly - Role: {user_role}, ID: {user_id}"
                )
                
                # Now test admin endpoint that should use the same dependency
                admin_response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
                
                if admin_response.status_code == 200:
                    self.log_result(
                        "Dependency Injection - Admin Endpoint Consistency",
                        True,
                        "Admin endpoint works with same token that works for profile"
                    )
                else:
                    self.log_result(
                        "Dependency Injection - Admin Endpoint Consistency",
                        False,
                        f"Admin endpoint fails (HTTP {admin_response.status_code}) while profile works",
                        admin_response.text
                    )
                    
            else:
                self.log_result(
                    "Dependency Injection - get_current_user",
                    False,
                    f"Profile endpoint failed - HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result("Dependency Injection - get_current_user", False, "", str(e))

    def run_all_tests(self):
        """Run all JWT token validation tests"""
        print("🔐 JWT TOKEN VALIDATION TEST FOR ADMIN ENDPOINTS")
        print("=" * 55)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()

        # Phase 1: Get JWT Token
        print("📋 PHASE 1: JWT TOKEN GENERATION")
        print("-" * 30)
        
        if not self.authenticate_and_get_token():
            print("❌ CRITICAL: Cannot get JWT token. Cannot proceed with validation tests.")
            return self.generate_summary()
        
        # Phase 2: Test Token with Admin Endpoints
        print("\n📋 PHASE 2: JWT TOKEN WITH ADMIN ENDPOINTS")
        print("-" * 30)
        
        self.test_token_with_admin_endpoints()
        
        # Phase 3: Test Authorization Header Formats
        print("\n📋 PHASE 3: AUTHORIZATION HEADER FORMATS")
        print("-" * 30)
        
        self.test_token_authorization_header_formats()
        
        # Phase 4: Dependency Injection Fix Verification
        print("\n📋 PHASE 4: DEPENDENCY INJECTION FIX VERIFICATION")
        print("-" * 30)
        
        self.test_dependency_injection_fix_verification()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 55)
        print("📊 JWT TOKEN VALIDATION TEST SUMMARY")
        print("=" * 55)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        token_generation_working = any(
            result["success"] for result in self.results 
            if "token generation" in result["test"].lower()
        )
        
        if token_generation_working:
            print("   ✅ JWT token generation working correctly")
        else:
            print("   ❌ JWT token generation has issues")
        
        admin_endpoints_working = all(
            result["success"] for result in self.results 
            if "jwt token with admin" in result["test"].lower()
        )
        
        if admin_endpoints_working:
            print("   ✅ All admin endpoints accept JWT tokens (dependency injection fixes successful)")
        else:
            print("   ❌ Some admin endpoints still rejecting JWT tokens (dependency injection issues persist)")
        
        dependency_injection_working = any(
            result["success"] for result in self.results 
            if "dependency injection" in result["test"].lower()
        )
        
        if dependency_injection_working:
            print("   ✅ Dependency injection consistency verified")
        else:
            print("   ⚠️  Dependency injection consistency issues detected")
        
        print()
        print("🎯 CONCLUSION:")
        if success_rate >= 90:
            print("   🎉 EXCELLENT: JWT token validation highly successful!")
            print("   🔧 Dependency injection fixes appear to be working correctly")
        elif success_rate >= 75:
            print("   ✅ GOOD: Most JWT token validation working")
            print("   🔧 Minor issues with dependency injection fixes")
        else:
            print("   🚨 CRITICAL: Major JWT token validation failures")
            print("   🔧 Dependency injection fixes may not be working properly")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": self.results
        }

if __name__ == "__main__":
    test = JWTTokenValidationTest()
    summary = test.run_all_tests()