#!/usr/bin/env python3
"""
TopKit Admin Endpoints Verification Test
========================================

This test verifies that the admin panel endpoints that were just fixed are now working properly.
Focus areas:
1. Admin endpoint fixes verification (users, traffic-stats, activities, beta/requests)
2. Authentication test with admin credentials
3. Admin user management (make/remove moderator)
4. Site mode functionality
5. Success rate comparison to previous 89.5%

The goal is to verify that dependency injection fixes resolved HTTP 403 errors.
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"

class AdminEndpointsVerificationTest:
    def __init__(self):
        self.admin_token = None
        self.test_user_token = None
        self.test_user_id = None
        self.admin_user_id = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
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

    def authenticate_admin(self):
        """Test admin authentication"""
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
                    "Admin Authentication",
                    True,
                    f"Admin login successful - Name: {user_name}, Role: {user_role}, ID: {self.admin_user_id}"
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
            self.log_result("Admin Authentication", False, "", str(e))
            return False

    def authenticate_test_user(self):
        """Test user authentication for moderator role testing"""
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

    def test_admin_users_endpoint(self):
        """Test GET /api/admin/users endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_count = len(data) if isinstance(data, list) else data.get("count", 0)
                self.log_result(
                    "Admin Users Endpoint",
                    True,
                    f"Retrieved {user_count} users successfully"
                )
                return True
            else:
                self.log_result(
                    "Admin Users Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Users Endpoint", False, "", str(e))
            return False

    def test_admin_traffic_stats_endpoint(self):
        """Test GET /api/admin/traffic-stats endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/traffic-stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats_keys = list(data.keys()) if isinstance(data, dict) else []
                self.log_result(
                    "Admin Traffic Stats Endpoint",
                    True,
                    f"Retrieved traffic statistics with {len(stats_keys)} metrics"
                )
                return True
            else:
                self.log_result(
                    "Admin Traffic Stats Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Traffic Stats Endpoint", False, "", str(e))
            return False

    def test_admin_activities_endpoint(self):
        """Test GET /api/admin/activities endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/activities", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                activity_count = len(data) if isinstance(data, list) else data.get("count", 0)
                self.log_result(
                    "Admin Activities Endpoint",
                    True,
                    f"Retrieved {activity_count} activities successfully"
                )
                return True
            else:
                self.log_result(
                    "Admin Activities Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Activities Endpoint", False, "", str(e))
            return False

    def test_admin_beta_requests_endpoint(self):
        """Test GET /api/admin/beta/requests endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                request_count = len(data) if isinstance(data, list) else data.get("count", 0)
                self.log_result(
                    "Admin Beta Requests Endpoint",
                    True,
                    f"Retrieved {request_count} beta requests successfully"
                )
                return True
            else:
                self.log_result(
                    "Admin Beta Requests Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Beta Requests Endpoint", False, "", str(e))
            return False

    def test_make_user_moderator(self):
        """Test POST /api/admin/users/{user_id}/make-moderator"""
        if not self.test_user_id:
            self.log_result("Make User Moderator", False, "", "Test user ID not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/make-moderator",
                headers=headers,
                json={"reason": "Testing moderator role assignment"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Make User Moderator",
                    True,
                    f"Successfully assigned moderator role to user {self.test_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Make User Moderator",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Make User Moderator", False, "", str(e))
            return False

    def test_remove_user_moderator(self):
        """Test POST /api/admin/users/{user_id}/remove-moderator"""
        if not self.test_user_id:
            self.log_result("Remove User Moderator", False, "", "Test user ID not available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/admin/users/{self.test_user_id}/remove-moderator",
                headers=headers,
                json={"reason": "Testing moderator role removal"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Remove User Moderator",
                    True,
                    f"Successfully removed moderator role from user {self.test_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Remove User Moderator",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Remove User Moderator", False, "", str(e))
            return False

    def test_site_mode_get(self):
        """Test GET /api/site/mode"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/site/mode", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                current_mode = data.get("mode", "unknown")
                self.log_result(
                    "Site Mode Get",
                    True,
                    f"Current site mode: {current_mode}"
                )
                return True, current_mode
            else:
                self.log_result(
                    "Site Mode Get",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False, None
                
        except Exception as e:
            self.log_result("Site Mode Get", False, "", str(e))
            return False, None

    def test_site_mode_post(self, target_mode):
        """Test POST /api/site/mode"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(
                f"{BACKEND_URL}/site/mode",
                headers=headers,
                json={"mode": target_mode}
            )
            
            if response.status_code == 200:
                data = response.json()
                new_mode = data.get("mode", "unknown")
                self.log_result(
                    "Site Mode Post",
                    True,
                    f"Successfully changed site mode to: {new_mode}"
                )
                return True
            else:
                self.log_result(
                    "Site Mode Post",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Site Mode Post", False, "", str(e))
            return False

    def test_site_access_check(self):
        """Test GET /api/site/access-check"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access", False)
                reason = data.get("reason", "unknown")
                self.log_result(
                    "Site Access Check",
                    True,
                    f"Access check result: {has_access}, Reason: {reason}"
                )
                return True
            else:
                self.log_result(
                    "Site Access Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Site Access Check", False, "", str(e))
            return False

    def run_all_tests(self):
        """Run all admin endpoint verification tests"""
        print("🔧 TOPKIT ADMIN ENDPOINTS VERIFICATION TEST")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()

        # Phase 1: Authentication
        print("📋 PHASE 1: AUTHENTICATION TESTING")
        print("-" * 30)
        
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with admin endpoint tests.")
            return self.generate_summary()
        
        self.authenticate_test_user()  # Optional for moderator role testing
        
        # Phase 2: Admin Endpoint Fixes Verification
        print("\n📋 PHASE 2: ADMIN ENDPOINT FIXES VERIFICATION")
        print("-" * 30)
        
        self.test_admin_users_endpoint()
        self.test_admin_traffic_stats_endpoint()
        self.test_admin_activities_endpoint()
        self.test_admin_beta_requests_endpoint()
        
        # Phase 3: Admin User Management
        print("\n📋 PHASE 3: ADMIN USER MANAGEMENT")
        print("-" * 30)
        
        if self.test_user_id:
            self.test_make_user_moderator()
            time.sleep(1)  # Brief pause between role changes
            self.test_remove_user_moderator()
        else:
            self.log_result("Admin User Management", False, "", "Test user not available for role testing")
        
        # Phase 4: Site Mode Functionality
        print("\n📋 PHASE 4: SITE MODE FUNCTIONALITY")
        print("-" * 30)
        
        success, current_mode = self.test_site_mode_get()
        if success and current_mode:
            # Test changing mode (toggle between private/public)
            target_mode = "public" if current_mode == "private" else "private"
            if self.test_site_mode_post(target_mode):
                # Change back to original mode
                time.sleep(1)
                self.test_site_mode_post(current_mode)
        
        self.test_site_access_check()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 ADMIN ENDPOINTS VERIFICATION TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Compare to previous 89.5% success rate
        previous_rate = 89.5
        if success_rate >= previous_rate:
            print(f"✅ SUCCESS RATE IMPROVEMENT: {success_rate:.1f}% >= {previous_rate}% (Previous)")
        else:
            print(f"⚠️  SUCCESS RATE DECLINE: {success_rate:.1f}% < {previous_rate}% (Previous)")
        print()
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.results:
            if not result["success"]:
                if "admin" in result["test"].lower() and ("users" in result["test"].lower() or 
                    "traffic" in result["test"].lower() or "activities" in result["test"].lower() or 
                    "beta" in result["test"].lower()):
                    critical_failures.append(result["test"])
                else:
                    minor_issues.append(result["test"])
        
        if critical_failures:
            print("🚨 CRITICAL FAILURES (Admin Endpoints):")
            for failure in critical_failures:
                print(f"   - {failure}")
            print()
        
        if minor_issues:
            print("⚠️  MINOR ISSUES:")
            for issue in minor_issues:
                print(f"   - {issue}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        admin_endpoints_working = all(
            result["success"] for result in self.results 
            if "admin" in result["test"].lower() and any(
                endpoint in result["test"].lower() 
                for endpoint in ["users", "traffic", "activities", "beta"]
            )
        )
        
        if admin_endpoints_working:
            print("   ✅ All core admin endpoints are working (dependency injection fixes successful)")
        else:
            print("   ❌ Some admin endpoints still failing (dependency injection issues may persist)")
        
        auth_working = any(
            result["success"] for result in self.results 
            if "authentication" in result["test"].lower()
        )
        
        if auth_working:
            print("   ✅ Admin authentication system operational")
        else:
            print("   ❌ Admin authentication system has issues")
        
        role_management_working = all(
            result["success"] for result in self.results 
            if "moderator" in result["test"].lower()
        )
        
        if role_management_working:
            print("   ✅ Admin user role management functional")
        elif any("moderator" in result["test"].lower() for result in self.results):
            print("   ⚠️  Admin user role management has issues")
        
        site_mode_working = any(
            result["success"] for result in self.results 
            if "site mode" in result["test"].lower()
        )
        
        if site_mode_working:
            print("   ✅ Site mode functionality operational")
        else:
            print("   ❌ Site mode functionality has issues")
        
        print()
        print("🎯 CONCLUSION:")
        if success_rate >= 90:
            print("   🎉 EXCELLENT: Admin endpoints verification highly successful!")
        elif success_rate >= 75:
            print("   ✅ GOOD: Most admin endpoints working with minor issues")
        elif success_rate >= 50:
            print("   ⚠️  MIXED: Significant issues remain with admin endpoints")
        else:
            print("   🚨 CRITICAL: Major failures in admin endpoint functionality")
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "success_rate": success_rate,
            "critical_failures": critical_failures,
            "minor_issues": minor_issues,
            "admin_endpoints_working": admin_endpoints_working,
            "results": self.results
        }

if __name__ == "__main__":
    test = AdminEndpointsVerificationTest()
    summary = test.run_all_tests()
    
    # Exit with appropriate code
    if summary["success_rate"] >= 75:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure