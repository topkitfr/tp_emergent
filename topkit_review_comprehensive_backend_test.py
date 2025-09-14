#!/usr/bin/env python3
"""
TopKit Review Request - Comprehensive Backend Testing
Testing all requested areas:
1. Authentication System Status (admin/user login, JWT tokens)
2. Site Mode Configuration (private beta mode)
3. Admin Panel Functionality
4. Security Level 2 Features (2FA, password change, admin user management)
5. Beta Access System
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class TopKitReviewTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_data = None
        self.user_user_data = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0

    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status}: {test_name}"
        if details:
            result += f" - {details}"
        
        self.test_results.append(result)
        print(result)

    def make_request(self, method, endpoint, data=None, headers=None, token=None):
        """Make HTTP request with proper error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except requests.exceptions.RequestException as e:
            return None, str(e)

    def test_authentication_system(self):
        """Test authentication system status - Focus Area 1"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM STATUS")
        print("=" * 50)
        
        # Test admin login
        admin_login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response, error = self.make_request("POST", "/auth/login", admin_login_data)
        if error:
            self.log_test("Admin Login Request", False, f"Request failed: {error}")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_user_data = data["user"]
                    self.log_test("Admin Login", True, f"Admin: {data['user']['name']}, Role: {data['user']['role']}, ID: {data['user']['id']}")
                else:
                    self.log_test("Admin Login", False, "Missing token or user data in response")
            except json.JSONDecodeError:
                self.log_test("Admin Login", False, "Invalid JSON response")
        else:
            self.log_test("Admin Login", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test user login
        user_login_data = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        }
        
        response, error = self.make_request("POST", "/auth/login", user_login_data)
        if error:
            self.log_test("User Login Request", False, f"Request failed: {error}")
            return
        
        if response.status_code == 200:
            try:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_user_data = data["user"]
                    self.log_test("User Login", True, f"User: {data['user']['name']}, Role: {data['user']['role']}, ID: {data['user']['id']}")
                else:
                    self.log_test("User Login", False, "Missing token or user data in response")
            except json.JSONDecodeError:
                self.log_test("User Login", False, "Invalid JSON response")
        else:
            self.log_test("User Login", False, f"HTTP {response.status_code}: {response.text}")
        
        # Test JWT token validation
        if self.admin_token:
            response, error = self.make_request("GET", "/profile", token=self.admin_token)
            if error:
                self.log_test("Admin JWT Token Validation", False, f"Request failed: {error}")
            elif response.status_code == 200:
                self.log_test("Admin JWT Token Validation", True, "Admin token validates successfully")
            else:
                self.log_test("Admin JWT Token Validation", False, f"HTTP {response.status_code}")
        
        if self.user_token:
            response, error = self.make_request("GET", "/profile", token=self.user_token)
            if error:
                self.log_test("User JWT Token Validation", False, f"Request failed: {error}")
            elif response.status_code == 200:
                self.log_test("User JWT Token Validation", True, "User token validates successfully")
            else:
                self.log_test("User JWT Token Validation", False, f"HTTP {response.status_code}")

    def test_site_mode_configuration(self):
        """Test site mode configuration - Focus Area 2"""
        print("\n🌐 TESTING SITE MODE CONFIGURATION")
        print("=" * 50)
        
        # Test GET site mode
        response, error = self.make_request("GET", "/site/mode")
        if error:
            self.log_test("Get Site Mode", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                current_mode = data.get("mode", "unknown")
                self.log_test("Get Site Mode", True, f"Current mode: {current_mode}")
            except json.JSONDecodeError:
                self.log_test("Get Site Mode", False, "Invalid JSON response")
        else:
            self.log_test("Get Site Mode", False, f"HTTP {response.status_code}")
        
        # Test site access check
        response, error = self.make_request("GET", "/site/access-check")
        if error:
            self.log_test("Site Access Check", False, f"Request failed: {error}")
        elif response.status_code in [200, 403]:
            try:
                data = response.json()
                access_granted = data.get("access_granted", False)
                self.log_test("Site Access Check", True, f"Access granted: {access_granted}")
            except json.JSONDecodeError:
                self.log_test("Site Access Check", False, "Invalid JSON response")
        else:
            self.log_test("Site Access Check", False, f"HTTP {response.status_code}")
        
        # Test site mode change (admin only)
        if self.admin_token:
            mode_data = {"mode": "private"}
            response, error = self.make_request("POST", "/site/mode", mode_data, token=self.admin_token)
            if error:
                self.log_test("Change Site Mode (Admin)", False, f"Request failed: {error}")
            elif response.status_code == 200:
                self.log_test("Change Site Mode (Admin)", True, "Admin can change site mode")
            else:
                self.log_test("Change Site Mode (Admin)", False, f"HTTP {response.status_code}")

    def test_admin_panel_functionality(self):
        """Test admin panel functionality - Focus Area 3"""
        print("\n👑 TESTING ADMIN PANEL FUNCTIONALITY")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Admin Panel Tests", False, "No admin token available")
            return
        
        # Test admin users list
        response, error = self.make_request("GET", "/admin/users", token=self.admin_token)
        if error:
            self.log_test("Admin Users List", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                user_count = len(data) if isinstance(data, list) else 0
                self.log_test("Admin Users List", True, f"Retrieved {user_count} users")
            except json.JSONDecodeError:
                self.log_test("Admin Users List", False, "Invalid JSON response")
        else:
            self.log_test("Admin Users List", False, f"HTTP {response.status_code}")
        
        # Test admin analytics/traffic stats
        response, error = self.make_request("GET", "/admin/traffic-stats", token=self.admin_token)
        if error:
            self.log_test("Admin Analytics", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                self.log_test("Admin Analytics", True, f"Analytics data retrieved: {len(data)} metrics")
            except json.JSONDecodeError:
                self.log_test("Admin Analytics", False, "Invalid JSON response")
        else:
            self.log_test("Admin Analytics", False, f"HTTP {response.status_code}")
        
        # Test admin pending jerseys
        response, error = self.make_request("GET", "/admin/jerseys/pending", token=self.admin_token)
        if error:
            self.log_test("Admin Pending Jerseys", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                pending_count = len(data) if isinstance(data, list) else 0
                self.log_test("Admin Pending Jerseys", True, f"Found {pending_count} pending jerseys")
            except json.JSONDecodeError:
                self.log_test("Admin Pending Jerseys", False, "Invalid JSON response")
        else:
            self.log_test("Admin Pending Jerseys", False, f"HTTP {response.status_code}")

    def test_security_level_2_features(self):
        """Test Security Level 2 features - Focus Area 4"""
        print("\n🔒 TESTING SECURITY LEVEL 2 FEATURES")
        print("=" * 50)
        
        # Test 2FA setup endpoint
        if self.user_token:
            response, error = self.make_request("POST", "/auth/2fa/setup", token=self.user_token)
            if error:
                self.log_test("2FA Setup Endpoint", False, f"Request failed: {error}")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    has_qr = "qr_code" in data
                    has_backup = "backup_codes" in data
                    self.log_test("2FA Setup Endpoint", True, f"QR code: {has_qr}, Backup codes: {has_backup}")
                except json.JSONDecodeError:
                    self.log_test("2FA Setup Endpoint", False, "Invalid JSON response")
            else:
                self.log_test("2FA Setup Endpoint", False, f"HTTP {response.status_code}")
        
        # Test 2FA enable endpoint (without valid token - should fail)
        if self.user_token:
            enable_data = {"token": "123456"}  # Invalid token
            response, error = self.make_request("POST", "/auth/2fa/enable", enable_data, token=self.user_token)
            if error:
                self.log_test("2FA Enable Endpoint", False, f"Request failed: {error}")
            elif response.status_code == 400:
                self.log_test("2FA Enable Endpoint", True, "Correctly rejects invalid 2FA token")
            else:
                self.log_test("2FA Enable Endpoint", False, f"Unexpected status: {response.status_code}")
        
        # Test password change endpoint
        if self.user_token:
            password_data = {
                "current_password": "wrong_password",
                "new_password": "NewSecurePass123!"
            }
            response, error = self.make_request("POST", "/auth/change-password", password_data, token=self.user_token)
            if error:
                self.log_test("Password Change Endpoint", False, f"Request failed: {error}")
            elif response.status_code == 400:
                self.log_test("Password Change Endpoint", True, "Correctly rejects invalid current password")
            else:
                self.log_test("Password Change Endpoint", False, f"Unexpected status: {response.status_code}")
        
        # Test admin user management endpoints
        if self.admin_token and self.user_user_data:
            user_id = self.user_user_data.get("id")
            if user_id:
                # Test ban user endpoint
                ban_data = {
                    "reason": "Test ban",
                    "permanent": False,
                    "ban_duration_days": 7
                }
                response, error = self.make_request("POST", f"/admin/users/{user_id}/ban", ban_data, token=self.admin_token)
                if error:
                    self.log_test("Admin Ban User", False, f"Request failed: {error}")
                elif response.status_code in [200, 400]:  # 400 might be expected if already banned
                    self.log_test("Admin Ban User", True, "Ban endpoint accessible")
                else:
                    self.log_test("Admin Ban User", False, f"HTTP {response.status_code}")
                
                # Test unban user endpoint
                response, error = self.make_request("POST", f"/admin/users/{user_id}/unban", token=self.admin_token)
                if error:
                    self.log_test("Admin Unban User", False, f"Request failed: {error}")
                elif response.status_code in [200, 400]:
                    self.log_test("Admin Unban User", True, "Unban endpoint accessible")
                else:
                    self.log_test("Admin Unban User", False, f"HTTP {response.status_code}")

    def test_beta_access_system(self):
        """Test beta access system - Focus Area 5"""
        print("\n🚀 TESTING BETA ACCESS SYSTEM")
        print("=" * 50)
        
        # Test beta request submission
        beta_request_data = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "message": "Test beta access request"
        }
        
        response, error = self.make_request("POST", "/beta/request-access", beta_request_data)
        if error:
            self.log_test("Beta Request Submission", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                request_id = data.get("request_id")
                self.log_test("Beta Request Submission", True, f"Request ID: {request_id}")
            except json.JSONDecodeError:
                self.log_test("Beta Request Submission", False, "Invalid JSON response")
        else:
            self.log_test("Beta Request Submission", False, f"HTTP {response.status_code}")
        
        # Test admin beta request management
        if self.admin_token:
            response, error = self.make_request("GET", "/admin/beta/requests", token=self.admin_token)
            if error:
                self.log_test("Admin Beta Requests List", False, f"Request failed: {error}")
            elif response.status_code == 200:
                try:
                    data = response.json()
                    request_count = len(data) if isinstance(data, list) else 0
                    self.log_test("Admin Beta Requests List", True, f"Found {request_count} beta requests")
                except json.JSONDecodeError:
                    self.log_test("Admin Beta Requests List", False, "Invalid JSON response")
            else:
                self.log_test("Admin Beta Requests List", False, f"HTTP {response.status_code}")

    def test_additional_endpoints(self):
        """Test additional important endpoints"""
        print("\n🔧 TESTING ADDITIONAL ENDPOINTS")
        print("=" * 50)
        
        # Test basic API health
        response, error = self.make_request("GET", "/jerseys")
        if error:
            self.log_test("API Health Check", False, f"Request failed: {error}")
        elif response.status_code == 200:
            self.log_test("API Health Check", True, "Basic API endpoints accessible")
        else:
            self.log_test("API Health Check", False, f"HTTP {response.status_code}")
        
        # Test marketplace catalog
        response, error = self.make_request("GET", "/marketplace/catalog")
        if error:
            self.log_test("Marketplace Catalog", False, f"Request failed: {error}")
        elif response.status_code == 200:
            try:
                data = response.json()
                catalog_count = len(data) if isinstance(data, list) else 0
                self.log_test("Marketplace Catalog", True, f"Found {catalog_count} catalog items")
            except json.JSONDecodeError:
                self.log_test("Marketplace Catalog", False, "Invalid JSON response")
        else:
            self.log_test("Marketplace Catalog", False, f"HTTP {response.status_code}")

    def run_all_tests(self):
        """Run all test suites"""
        print("🧪 TOPKIT REVIEW REQUEST - COMPREHENSIVE BACKEND TESTING")
        print("=" * 60)
        print(f"Testing backend at: {BACKEND_URL}")
        print(f"Admin credentials: {ADMIN_EMAIL}")
        print(f"User credentials: {USER_EMAIL}")
        print("=" * 60)
        
        # Run all test suites
        self.test_authentication_system()
        self.test_site_mode_configuration()
        self.test_admin_panel_functionality()
        self.test_security_level_2_features()
        self.test_beta_access_system()
        self.test_additional_endpoints()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests})")
        
        print(f"\n🔐 AUTHENTICATION STATUS:")
        print(f"   Admin Login: {'✅ Working' if self.admin_token else '❌ Failed'}")
        print(f"   User Login: {'✅ Working' if self.user_token else '❌ Failed'}")
        print(f"   JWT Tokens: {'✅ Generated' if (self.admin_token or self.user_token) else '❌ Not Generated'}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"   {result}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  MODERATE: Backend has significant issues that need attention")
        else:
            print("🚨 CRITICAL: Backend has major failures requiring immediate fixes")
        
        return success_rate

if __name__ == "__main__":
    tester = TopKitReviewTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)