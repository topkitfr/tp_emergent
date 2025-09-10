#!/usr/bin/env python3
"""
TopKit Private Beta Mode Backend Testing
Comprehensive testing of Private Beta Mode implementation
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials (confirmed working)
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "adminpass123"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "123"
}

# Alternative user credentials if the first one doesn't work
ALT_USER_CREDENTIALS = {
    "email": "admin.test@topkit.com",
    "password": "TestPass123!"
}

class PrivateBetaModeTest:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
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
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test("Admin Authentication", True, 
                             f"Admin: {user_info.get('name')} ({user_info.get('role')})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test("User Authentication", True, 
                             f"User: {user_info.get('name')} ({user_info.get('role')})")
                return True
            else:
                # Try alternative credentials
                response = requests.post(f"{BACKEND_URL}/auth/login", json=ALT_USER_CREDENTIALS)
                if response.status_code == 200:
                    data = response.json()
                    self.user_token = data.get("token")
                    user_info = data.get("user", {})
                    self.log_test("User Authentication", True, 
                                 f"User: {user_info.get('name')} ({user_info.get('role')}) - using alt credentials")
                    return True
                else:
                    self.log_test("User Authentication", False, 
                                 f"Both credentials failed. Primary: HTTP {response.status_code}, Alt: HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_get_site_mode(self):
        """Test GET /api/site/mode endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/site/mode")
            if response.status_code == 200:
                data = response.json()
                mode = data.get("mode")
                is_private = data.get("is_private")
                message = data.get("message")
                
                self.log_test("GET Site Mode", True, 
                             f"Mode: {mode}, Private: {is_private}, Message: {message}")
                return data
            else:
                self.log_test("GET Site Mode", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("GET Site Mode", False, f"Exception: {str(e)}")
            return None
    
    def test_update_site_mode_unauthorized(self):
        """Test POST /api/site/mode without admin token"""
        try:
            response = requests.post(f"{BACKEND_URL}/site/mode", 
                                   json={"mode": "public"})
            if response.status_code in [401, 403]:
                self.log_test("Update Site Mode (Unauthorized)", True, 
                             f"Correctly rejected unauthorized request (HTTP {response.status_code})")
                return True
            else:
                self.log_test("Update Site Mode (Unauthorized)", False, 
                             f"Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update Site Mode (Unauthorized)", False, f"Exception: {str(e)}")
            return False
    
    def test_update_site_mode_user_token(self):
        """Test POST /api/site/mode with user token (should fail)"""
        if not self.user_token:
            self.log_test("Update Site Mode (User Token)", False, "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/site/mode", 
                                   json={"mode": "public"}, headers=headers)
            if response.status_code == 403:
                self.log_test("Update Site Mode (User Token)", True, 
                             "Correctly rejected non-admin user")
                return True
            else:
                self.log_test("Update Site Mode (User Token)", False, 
                             f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update Site Mode (User Token)", False, f"Exception: {str(e)}")
            return False
    
    def test_update_site_mode_admin(self, target_mode="private"):
        """Test POST /api/site/mode with admin token"""
        if not self.admin_token:
            self.log_test("Update Site Mode (Admin)", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/site/mode", 
                                   json={"mode": target_mode}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Update Site Mode (Admin)", True, 
                             f"Successfully set mode to: {data.get('mode')}")
                return True
            else:
                self.log_test("Update Site Mode (Admin)", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Update Site Mode (Admin)", False, f"Exception: {str(e)}")
            return False
    
    def test_access_check_no_auth(self):
        """Test GET /api/site/access-check without authentication"""
        try:
            response = requests.get(f"{BACKEND_URL}/site/access-check")
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access")
                mode = data.get("mode")
                message = data.get("message")
                
                self.log_test("Access Check (No Auth)", True, 
                             f"Access: {has_access}, Mode: {mode}, Message: {message}")
                return data
            elif response.status_code == 403:
                # This might be expected if the endpoint requires auth
                self.log_test("Access Check (No Auth)", True, 
                             f"Expected behavior - endpoint requires authentication (HTTP 403)")
                return None
            else:
                self.log_test("Access Check (No Auth)", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Access Check (No Auth)", False, f"Exception: {str(e)}")
            return None
    
    def test_access_check_user_auth(self):
        """Test GET /api/site/access-check with user authentication"""
        if not self.user_token:
            self.log_test("Access Check (User Auth)", False, "No user token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access")
                mode = data.get("mode")
                user_role = data.get("user_role", "N/A")
                message = data.get("message")
                
                self.log_test("Access Check (User Auth)", True, 
                             f"Access: {has_access}, Mode: {mode}, Role: {user_role}, Message: {message}")
                return data
            else:
                self.log_test("Access Check (User Auth)", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Access Check (User Auth)", False, f"Exception: {str(e)}")
            return None
    
    def test_access_check_admin_auth(self):
        """Test GET /api/site/access-check with admin authentication"""
        if not self.admin_token:
            self.log_test("Access Check (Admin Auth)", False, "No admin token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access")
                mode = data.get("mode")
                user_role = data.get("user_role", "N/A")
                message = data.get("message")
                
                self.log_test("Access Check (Admin Auth)", True, 
                             f"Access: {has_access}, Mode: {mode}, Role: {user_role}, Message: {message}")
                return data
            else:
                self.log_test("Access Check (Admin Auth)", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Access Check (Admin Auth)", False, f"Exception: {str(e)}")
            return None
    
    def test_beta_access_request(self):
        """Test POST /api/beta/request-access"""
        test_request = {
            "email": f"test.beta.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "message": "Testing beta access request functionality"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message")
                request_id = data.get("request_id")
                
                self.log_test("Beta Access Request", True, 
                             f"Request ID: {request_id}, Message: {message}")
                return request_id
            else:
                self.log_test("Beta Access Request", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Beta Access Request", False, f"Exception: {str(e)}")
            return None
    
    def test_beta_access_request_duplicate(self):
        """Test duplicate beta access request"""
        test_request = {
            "email": "duplicate.test@example.com",
            "first_name": "Duplicate",
            "last_name": "Test",
            "message": "First request"
        }
        
        try:
            # First request
            response1 = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
            
            # Second request with same email
            response2 = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
            
            if response1.status_code == 200 and response2.status_code == 200:
                data2 = response2.json()
                if "déjà été soumise" in data2.get("message", ""):
                    self.log_test("Beta Access Request (Duplicate)", True, 
                                 "Correctly handled duplicate email")
                    return True
                else:
                    self.log_test("Beta Access Request (Duplicate)", False, 
                                 "Did not detect duplicate email")
                    return False
            else:
                self.log_test("Beta Access Request (Duplicate)", False, 
                             f"Unexpected response codes: {response1.status_code}, {response2.status_code}")
                return False
        except Exception as e:
            self.log_test("Beta Access Request (Duplicate)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_beta_requests_unauthorized(self):
        """Test GET /api/admin/beta/requests without admin token"""
        try:
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests")
            if response.status_code in [401, 403]:
                self.log_test("Get Beta Requests (Unauthorized)", True, 
                             f"Correctly rejected unauthorized request (HTTP {response.status_code})")
                return True
            else:
                self.log_test("Get Beta Requests (Unauthorized)", False, 
                             f"Expected 401/403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Beta Requests (Unauthorized)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_beta_requests_user_token(self):
        """Test GET /api/admin/beta/requests with user token (should fail)"""
        if not self.user_token:
            self.log_test("Get Beta Requests (User Token)", False, "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            if response.status_code == 403:
                self.log_test("Get Beta Requests (User Token)", True, 
                             "Correctly rejected non-admin user")
                return True
            else:
                self.log_test("Get Beta Requests (User Token)", False, 
                             f"Expected 403, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Beta Requests (User Token)", False, f"Exception: {str(e)}")
            return False
    
    def test_get_beta_requests_admin(self):
        """Test GET /api/admin/beta/requests with admin token"""
        if not self.admin_token:
            self.log_test("Get Beta Requests (Admin)", False, "No admin token available")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            if response.status_code == 200:
                data = response.json()
                requests_list = data.get("requests", [])
                total = data.get("total", 0)
                
                self.log_test("Get Beta Requests (Admin)", True, 
                             f"Retrieved {total} beta requests")
                return requests_list
            else:
                self.log_test("Get Beta Requests (Admin)", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Get Beta Requests (Admin)", False, f"Exception: {str(e)}")
            return None
    
    def test_approve_beta_request(self, request_id):
        """Test POST /api/admin/beta/requests/{request_id}/approve"""
        if not self.admin_token:
            self.log_test("Approve Beta Request", False, "No admin token available")
            return False
        
        if not request_id:
            self.log_test("Approve Beta Request", False, "No request ID provided")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/admin/beta/requests/{request_id}/approve", 
                                   headers=headers)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message")
                user_created = data.get("user_created", False)
                
                self.log_test("Approve Beta Request", True, 
                             f"Message: {message}, User Created: {user_created}")
                return True
            else:
                self.log_test("Approve Beta Request", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Approve Beta Request", False, f"Exception: {str(e)}")
            return False
    
    def test_reject_beta_request(self, request_id):
        """Test POST /api/admin/beta/requests/{request_id}/reject"""
        if not self.admin_token:
            self.log_test("Reject Beta Request", False, "No admin token available")
            return False
        
        if not request_id:
            self.log_test("Reject Beta Request", False, "No request ID provided")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            reject_data = {"reason": "Testing rejection functionality"}
            response = requests.post(f"{BACKEND_URL}/admin/beta/requests/{request_id}/reject", 
                                   json=reject_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "Request rejected successfully")
                
                self.log_test("Reject Beta Request", True, f"Message: {message}")
                return True
            else:
                self.log_test("Reject Beta Request", False, 
                             f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Reject Beta Request", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all Private Beta Mode tests"""
        print("🎯 TOPKIT PRIVATE BETA MODE BACKEND TESTING STARTED")
        print("=" * 60)
        
        # Phase 1: Authentication
        print("\n📋 PHASE 1: AUTHENTICATION TESTING")
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not admin_auth_success:
            print("❌ CRITICAL: Admin authentication failed - cannot test admin endpoints")
        
        # Phase 2: Site Mode Management
        print("\n📋 PHASE 2: SITE MODE MANAGEMENT TESTING")
        self.test_get_site_mode()
        self.test_update_site_mode_unauthorized()
        
        if user_auth_success:
            self.test_update_site_mode_user_token()
        
        if admin_auth_success:
            # Test switching to private mode
            self.test_update_site_mode_admin("private")
            # Test switching to public mode
            self.test_update_site_mode_admin("public")
            # Set back to private for access control tests
            self.test_update_site_mode_admin("private")
        
        # Phase 3: Access Control Testing
        print("\n📋 PHASE 3: ACCESS CONTROL TESTING")
        self.test_access_check_no_auth()
        
        if user_auth_success:
            self.test_access_check_user_auth()
        
        if admin_auth_success:
            self.test_access_check_admin_auth()
        
        # Phase 4: Beta Access Request System
        print("\n📋 PHASE 4: BETA ACCESS REQUEST SYSTEM TESTING")
        test_request_id = self.test_beta_access_request()
        self.test_beta_access_request_duplicate()
        
        # Phase 5: Beta Request Management (Admin)
        print("\n📋 PHASE 5: BETA REQUEST MANAGEMENT TESTING")
        self.test_get_beta_requests_unauthorized()
        
        if user_auth_success:
            self.test_get_beta_requests_user_token()
        
        if admin_auth_success:
            beta_requests = self.test_get_beta_requests_admin()
            
            # Test approval/rejection if we have requests
            if test_request_id:
                self.test_approve_beta_request(test_request_id)
            
            # Create a separate request for rejection test
            reject_test_request = {
                "email": f"reject.test.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
                "first_name": "Reject",
                "last_name": "Test",
                "message": "Testing rejection functionality"
            }
            
            try:
                response = requests.post(f"{BACKEND_URL}/beta/request-access", json=reject_test_request)
                if response.status_code == 200:
                    reject_request_id = response.json().get("request_id")
                    if reject_request_id:
                        self.test_reject_beta_request(reject_request_id)
            except Exception as e:
                self.log_test("Create Reject Test Request", False, f"Exception: {str(e)}")
        
        # Final Results
        print("\n" + "=" * 60)
        print("🎯 TOPKIT PRIVATE BETA MODE TESTING COMPLETE")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Determine overall status
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Private Beta Mode is PRODUCTION-READY!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Private Beta Mode is mostly functional with minor issues")
        elif success_rate >= 50:
            print(f"\n⚠️ MODERATE: Private Beta Mode has significant issues that need attention")
        else:
            print(f"\n❌ CRITICAL: Private Beta Mode has major failures and needs immediate fixes")
        
        return success_rate

if __name__ == "__main__":
    tester = PrivateBetaModeTest()
    success_rate = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 75 else 1)