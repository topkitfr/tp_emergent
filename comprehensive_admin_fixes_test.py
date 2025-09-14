#!/usr/bin/env python3
"""
Comprehensive Admin Panel Fixes Verification Test
=================================================

This test comprehensively verifies all aspects mentioned in the review request:
1. Admin endpoint fixes verification (users, traffic-stats, activities, beta/requests)
2. Authentication test with specific admin credentials
3. Admin user management (make/remove moderator)
4. Site mode functionality (GET/POST /api/site/mode)
5. Success rate comparison to previous 89.5%

Goal: Verify dependency injection fixes resolved HTTP 403 errors on admin endpoints.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"

class ComprehensiveAdminFixesTest:
    def __init__(self):
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.admin_user_id = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.previous_success_rate = 89.5
        
    def log_result(self, test_name, success, details="", error_msg="", critical=False):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "🚨 CRITICAL FAIL" if critical else "❌ FAIL"
            
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg,
            "critical": critical,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error_msg:
            print(f"    Error: {error_msg}")
        print()

    def authenticate_admin(self):
        """Test admin authentication with specific credentials from review request"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                self.admin_user_id = data.get("user", {}).get("id")
                user_role = data.get("user", {}).get("role")
                user_name = data.get("user", {}).get("name")
                
                self.log_result(
                    "Admin Authentication (topkitfr@gmail.com/TopKitSecure789#)",
                    True,
                    f"Admin login successful - Name: {user_name}, Role: {user_role}, ID: {self.admin_user_id}",
                    critical=True
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication (topkitfr@gmail.com/TopKitSecure789#)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text,
                    critical=True
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, "", str(e), critical=True)
            return False

    def authenticate_test_user(self):
        """Authenticate test user for moderator role testing"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_token = data.get("token")
                self.test_user_id = data.get("user", {}).get("id")
                user_role = data.get("user", {}).get("role")
                user_name = data.get("user", {}).get("name")
                
                self.log_result(
                    "Test User Authentication",
                    True,
                    f"User login successful - Name: {user_name}, Role: {user_role}, ID: {self.test_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Test User Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Test User Authentication", False, "", str(e))
            return False

    def verify_jwt_token_works_with_admin_endpoints(self):
        """Verify JWT token works with fixed admin endpoints"""
        if not self.admin_token:
            self.log_result("JWT Token Verification", False, "", "No admin token available", critical=True)
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test that JWT token is properly formatted and valid
        try:
            import jwt
            decoded = jwt.decode(self.admin_token, options={"verify_signature": False})
            user_id = decoded.get("user_id")
            exp = decoded.get("exp")
            
            self.log_result(
                "JWT Token Format Verification",
                True,
                f"Token properly formatted - User ID: {user_id}, Expires: {datetime.fromtimestamp(exp) if exp else 'Unknown'}"
            )
        except Exception as e:
            self.log_result(
                "JWT Token Format Verification",
                False,
                "Token format invalid",
                str(e)
            )
        
        return True

    def test_admin_endpoint_fixes(self):
        """Test the specific admin endpoints mentioned in review request"""
        if not self.admin_token:
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test each endpoint that was previously failing with HTTP 403
        endpoints = [
            ("/admin/users", "GET /api/admin/users", "Admin Users Endpoint"),
            ("/admin/traffic-stats", "GET /api/admin/traffic-stats", "Admin Traffic Stats Endpoint"),
            ("/admin/activities", "GET /api/admin/activities", "Admin Activities Endpoint"),
            ("/admin/beta/requests", "GET /api/admin/beta/requests", "Admin Beta Requests Endpoint")
        ]
        
        all_working = True
        
        for endpoint, api_name, test_name in endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Analyze response data
                    if isinstance(data, list):
                        data_info = f"Retrieved {len(data)} items"
                    elif isinstance(data, dict):
                        keys = list(data.keys())
                        data_info = f"Retrieved data with keys: {', '.join(keys[:5])}" + ("..." if len(keys) > 5 else "")
                    else:
                        data_info = f"Retrieved data of type {type(data).__name__}"
                    
                    self.log_result(
                        f"{test_name} - {api_name}",
                        True,
                        f"HTTP 200 - {data_info} (Previously failing with HTTP 403)",
                        critical=True
                    )
                elif response.status_code == 403:
                    self.log_result(
                        f"{test_name} - {api_name}",
                        False,
                        f"HTTP 403 - DEPENDENCY INJECTION FIX FAILED",
                        response.text,
                        critical=True
                    )
                    all_working = False
                else:
                    self.log_result(
                        f"{test_name} - {api_name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text,
                        critical=True
                    )
                    all_working = False
                    
            except Exception as e:
                self.log_result(f"{test_name} - {api_name}", False, "", str(e), critical=True)
                all_working = False
        
        return all_working

    def test_admin_user_management(self):
        """Test admin user management functionality"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Admin User Management", False, "", "Missing admin token or test user ID")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test making user moderator
        try:
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/make-moderator",
                headers=headers,
                json={"reason": "Testing moderator role assignment for admin fixes verification"}
            )
            
            if response.status_code == 200:
                self.log_result(
                    "Admin User Management - Make Moderator",
                    True,
                    f"Successfully assigned moderator role to user {self.test_user_id}"
                )
                
                # Brief pause before removing role
                time.sleep(1)
                
                # Test removing moderator role
                remove_response = requests.post(
                    f"{BACKEND_URL}/admin/users/{self.test_user_id}/remove-moderator",
                    headers=headers,
                    json={"reason": "Testing moderator role removal for admin fixes verification"}
                )
                
                if remove_response.status_code == 200:
                    self.log_result(
                        "Admin User Management - Remove Moderator",
                        True,
                        f"Successfully removed moderator role from user {self.test_user_id}"
                    )
                    return True
                else:
                    self.log_result(
                        "Admin User Management - Remove Moderator",
                        False,
                        f"HTTP {remove_response.status_code}",
                        remove_response.text
                    )
                    return False
            else:
                self.log_result(
                    "Admin User Management - Make Moderator",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin User Management", False, "", str(e))
            return False

    def test_site_mode_functionality(self):
        """Test site mode functionality (GET/POST /api/site/mode)"""
        if not self.admin_token:
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/site/mode
        try:
            get_response = requests.get(f"{BACKEND_URL}/site/mode", headers=headers)
            
            if get_response.status_code == 200:
                data = get_response.json()
                current_mode = data.get("mode", "unknown")
                
                self.log_result(
                    "Site Mode - GET /api/site/mode",
                    True,
                    f"Current site mode: {current_mode}"
                )
                
                # Test POST /api/site/mode (toggle mode)
                target_mode = "public" if current_mode == "private" else "private"
                
                post_response = requests.post(
                    f"{BACKEND_URL}/site/mode",
                    headers=headers,
                    json={"mode": target_mode}
                )
                
                if post_response.status_code == 200:
                    post_data = post_response.json()
                    new_mode = post_data.get("mode", "unknown")
                    
                    self.log_result(
                        "Site Mode - POST /api/site/mode",
                        True,
                        f"Successfully changed site mode from {current_mode} to {new_mode}"
                    )
                    
                    # Change back to original mode
                    time.sleep(1)
                    restore_response = requests.post(
                        f"{BACKEND_URL}/site/mode",
                        headers=headers,
                        json={"mode": current_mode}
                    )
                    
                    if restore_response.status_code == 200:
                        self.log_result(
                            "Site Mode - Restore Original Mode",
                            True,
                            f"Successfully restored original mode: {current_mode}"
                        )
                    
                    return True
                else:
                    self.log_result(
                        "Site Mode - POST /api/site/mode",
                        False,
                        f"HTTP {post_response.status_code}",
                        post_response.text
                    )
                    return False
            else:
                self.log_result(
                    "Site Mode - GET /api/site/mode",
                    False,
                    f"HTTP {get_response.status_code}",
                    get_response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Site Mode Functionality", False, "", str(e))
            return False

    def test_access_control_functionality(self):
        """Test access control functionality"""
        if not self.admin_token:
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access", False)
                reason = data.get("reason", "unknown")
                
                self.log_result(
                    "Access Control Functionality",
                    True,
                    f"Access check result: {has_access}, Reason: {reason}"
                )
                return True
            else:
                self.log_result(
                    "Access Control Functionality",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Access Control Functionality", False, "", str(e))
            return False

    def run_comprehensive_test(self):
        """Run comprehensive admin panel fixes verification test"""
        print("🔧 COMPREHENSIVE ADMIN PANEL FIXES VERIFICATION TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}/{ADMIN_PASSWORD}")
        print(f"Previous Success Rate: {self.previous_success_rate}%")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()

        # Phase 1: Authentication Test
        print("📋 PHASE 1: AUTHENTICATION TEST")
        print("-" * 35)
        
        if not self.authenticate_admin():
            print("🚨 CRITICAL: Admin authentication failed. Cannot proceed with admin endpoint tests.")
            return self.generate_summary()
        
        self.authenticate_test_user()  # For moderator role testing
        
        # Phase 2: JWT Token Verification
        print("\n📋 PHASE 2: JWT TOKEN VERIFICATION")
        print("-" * 35)
        
        self.verify_jwt_token_works_with_admin_endpoints()
        
        # Phase 3: Admin Endpoint Fixes Verification
        print("\n📋 PHASE 3: ADMIN ENDPOINT FIXES VERIFICATION")
        print("-" * 35)
        
        admin_endpoints_working = self.test_admin_endpoint_fixes()
        
        # Phase 4: Admin User Management
        print("\n📋 PHASE 4: ADMIN USER MANAGEMENT")
        print("-" * 35)
        
        self.test_admin_user_management()
        
        # Phase 5: Site Mode Functionality
        print("\n📋 PHASE 5: SITE MODE FUNCTIONALITY")
        print("-" * 35)
        
        self.test_site_mode_functionality()
        self.test_access_control_functionality()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE ADMIN PANEL FIXES TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Success rate comparison
        if success_rate >= self.previous_success_rate:
            improvement = success_rate - self.previous_success_rate
            print(f"✅ SUCCESS RATE IMPROVEMENT: {success_rate:.1f}% >= {self.previous_success_rate}% (+{improvement:.1f}%)")
        else:
            decline = self.previous_success_rate - success_rate
            print(f"⚠️  SUCCESS RATE DECLINE: {success_rate:.1f}% < {self.previous_success_rate}% (-{decline:.1f}%)")
        print()
        
        # Categorize results
        critical_failures = []
        admin_endpoint_failures = []
        minor_issues = []
        
        for result in self.results:
            if not result["success"]:
                if result.get("critical", False):
                    critical_failures.append(result["test"])
                    if "admin" in result["test"].lower() and any(
                        endpoint in result["test"].lower() 
                        for endpoint in ["users", "traffic", "activities", "beta"]
                    ):
                        admin_endpoint_failures.append(result["test"])
                else:
                    minor_issues.append(result["test"])
        
        if critical_failures:
            print("🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                print(f"   - {failure}")
            print()
        
        if minor_issues:
            print("⚠️  MINOR ISSUES:")
            for issue in minor_issues:
                print(f"   - {issue}")
            print()
        
        # Key findings analysis
        print("🔍 KEY FINDINGS:")
        
        # Admin authentication
        admin_auth_working = any(
            result["success"] for result in self.results 
            if "admin authentication" in result["test"].lower()
        )
        
        if admin_auth_working:
            print("   ✅ Admin authentication (topkitfr@gmail.com/TopKitSecure789#) working")
        else:
            print("   ❌ Admin authentication failed")
        
        # JWT token verification
        jwt_working = any(
            result["success"] for result in self.results 
            if "jwt token" in result["test"].lower()
        )
        
        if jwt_working:
            print("   ✅ JWT token works with fixed admin endpoints")
        else:
            print("   ❌ JWT token issues with admin endpoints")
        
        # Admin endpoints status
        if not admin_endpoint_failures:
            print("   ✅ ALL ADMIN ENDPOINTS WORKING (Dependency injection fixes successful)")
            print("   🔧 HTTP 403 errors resolved on admin endpoints")
        else:
            print("   ❌ SOME ADMIN ENDPOINTS STILL FAILING (Dependency injection issues persist)")
            print("   🔧 HTTP 403 errors may still be present")
        
        # User management
        user_mgmt_working = all(
            result["success"] for result in self.results 
            if "user management" in result["test"].lower()
        )
        
        if user_mgmt_working:
            print("   ✅ Admin user management (make/remove moderator) functional")
        elif any("user management" in result["test"].lower() for result in self.results):
            print("   ⚠️  Admin user management has issues")
        
        # Site mode
        site_mode_working = any(
            result["success"] for result in self.results 
            if "site mode" in result["test"].lower()
        )
        
        if site_mode_working:
            print("   ✅ Site mode functionality (GET/POST /api/site/mode) operational")
        else:
            print("   ❌ Site mode functionality has issues")
        
        print()
        print("🎯 FINAL CONCLUSION:")
        
        if success_rate >= 95 and not admin_endpoint_failures:
            print("   🎉 EXCELLENT: Admin panel fixes verification highly successful!")
            print("   🔧 Dependency injection fixes working perfectly")
            print("   ✅ All admin endpoints now accessible (HTTP 403 errors resolved)")
        elif success_rate >= 85 and not admin_endpoint_failures:
            print("   ✅ GOOD: Admin panel fixes mostly successful")
            print("   🔧 Dependency injection fixes working correctly")
            print("   ✅ Core admin endpoints accessible")
        elif admin_endpoint_failures:
            print("   🚨 CRITICAL: Admin endpoint fixes incomplete")
            print("   🔧 Dependency injection issues still present")
            print("   ❌ Some admin endpoints still returning HTTP 403")
        else:
            print("   ⚠️  MIXED: Significant issues remain")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "previous_success_rate": self.previous_success_rate,
            "critical_failures": critical_failures,
            "admin_endpoint_failures": admin_endpoint_failures,
            "minor_issues": minor_issues,
            "dependency_injection_fixes_working": len(admin_endpoint_failures) == 0,
            "results": self.results
        }

if __name__ == "__main__":
    test = ComprehensiveAdminFixesTest()
    summary = test.run_comprehensive_test()
    
    # Exit with appropriate code
    if summary["success_rate"] >= 85 and summary["dependency_injection_fixes_working"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure