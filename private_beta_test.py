#!/usr/bin/env python3
"""
TopKit Private Beta Mode Backend Testing Suite
Comprehensive testing of Private Beta Mode implementation
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

# Test credentials - Updated based on actual working credentials
ADMIN_EMAIL = "admin.test@topkit.com"  # Note: This user may not have admin privileges
ADMIN_PASSWORD = "TopKitSecure2024!"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "Livio2024!Secure"

class TopKitPrivateBetaTester:
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
        
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test("Admin Authentication", True, 
                            f"Admin logged in: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})")
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
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test("User Authentication", True, 
                            f"User logged in: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')})")
                return True
            else:
                self.log_test("User Authentication", False, 
                            f"HTTP {response.status_code}: {response.text}")
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
                message = data.get("message", "")
                
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
    
    def test_update_site_mode(self, mode, token, expected_success=True):
        """Test POST /api/site/mode endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.post(f"{BACKEND_URL}/site/mode", 
                                   json={"mode": mode}, 
                                   headers=headers)
            
            if expected_success:
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Update Site Mode to {mode}", True, 
                                f"Response: {data.get('message', 'Success')}")
                    return True
                else:
                    self.log_test(f"Update Site Mode to {mode}", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return False
            else:
                # Expecting failure
                if response.status_code in [401, 403]:
                    self.log_test(f"Update Site Mode to {mode} (Unauthorized)", True, 
                                f"Correctly rejected: HTTP {response.status_code}")
                    return True
                else:
                    self.log_test(f"Update Site Mode to {mode} (Unauthorized)", False, 
                                f"Should have been rejected but got HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test(f"Update Site Mode to {mode}", False, f"Exception: {str(e)}")
            return False
    
    def test_site_access_check(self, token, expected_access=True):
        """Test GET /api/site/access-check endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                has_access = data.get("has_access")
                mode = data.get("mode")
                message = data.get("message", "")
                
                if has_access == expected_access:
                    self.log_test("Site Access Check", True, 
                                f"Access: {has_access}, Mode: {mode}, Message: {message}")
                    return True
                else:
                    self.log_test("Site Access Check", False, 
                                f"Expected access: {expected_access}, Got: {has_access}")
                    return False
            else:
                self.log_test("Site Access Check", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Site Access Check", False, f"Exception: {str(e)}")
            return False
    
    def test_beta_access_request_submission(self):
        """Test POST /api/beta/request-access endpoint"""
        try:
            test_request = {
                "email": f"test.beta.{int(time.time())}@example.com",
                "first_name": "Test",
                "last_name": "User",
                "message": "I would like to test the TopKit beta platform for jersey collection management."
            }
            
            response = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                message = data.get("message", "")
                
                self.log_test("Beta Access Request Submission", True, 
                            f"Request ID: {request_id}, Message: {message}")
                return request_id
            else:
                self.log_test("Beta Access Request Submission", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Beta Access Request Submission", False, f"Exception: {str(e)}")
            return None
    
    def test_duplicate_beta_request(self):
        """Test duplicate beta access request handling"""
        try:
            test_email = f"duplicate.test.{int(time.time())}@example.com"
            test_request = {
                "email": test_email,
                "first_name": "Duplicate",
                "last_name": "Test",
                "message": "First request"
            }
            
            # Submit first request
            response1 = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
            
            if response1.status_code == 200:
                # Submit duplicate request
                test_request["message"] = "Duplicate request"
                response2 = requests.post(f"{BACKEND_URL}/beta/request-access", json=test_request)
                
                if response2.status_code == 400:
                    self.log_test("Duplicate Beta Request Prevention", True, 
                                "Duplicate request correctly rejected")
                    return True
                else:
                    self.log_test("Duplicate Beta Request Prevention", False, 
                                f"Duplicate should be rejected but got HTTP {response2.status_code}")
                    return False
            else:
                self.log_test("Duplicate Beta Request Prevention", False, 
                            f"First request failed: HTTP {response1.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Beta Request Prevention", False, f"Exception: {str(e)}")
            return False
    
    def test_get_beta_requests(self, token, expected_success=True):
        """Test GET /api/admin/beta/requests endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            
            if expected_success:
                if response.status_code == 200:
                    data = response.json()
                    requests_list = data.get("requests", [])
                    total = data.get("total", 0)
                    
                    self.log_test("Get Beta Requests (Admin)", True, 
                                f"Found {total} beta requests")
                    return requests_list
                else:
                    self.log_test("Get Beta Requests (Admin)", False, 
                                f"HTTP {response.status_code}: {response.text}")
                    return None
            else:
                # Expecting failure
                if response.status_code in [401, 403]:
                    self.log_test("Get Beta Requests (Non-Admin)", True, 
                                f"Correctly rejected: HTTP {response.status_code}")
                    return True
                else:
                    self.log_test("Get Beta Requests (Non-Admin)", False, 
                                f"Should have been rejected but got HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            self.log_test("Get Beta Requests", False, f"Exception: {str(e)}")
            return None
    
    def test_beta_request_approval(self, request_id, token):
        """Test POST /api/admin/beta/requests/{request_id}/approve endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{BACKEND_URL}/admin/beta/requests/{request_id}/approve", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_test("Beta Request Approval", True, f"Message: {message}")
                return True
            else:
                self.log_test("Beta Request Approval", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Beta Request Approval", False, f"Exception: {str(e)}")
            return False
    
    def test_beta_request_rejection(self, request_id, token):
        """Test POST /api/admin/beta/requests/{request_id}/reject endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            rejection_data = {
                "reason": "Test rejection - application does not meet beta criteria"
            }
            response = requests.post(f"{BACKEND_URL}/admin/beta/requests/{request_id}/reject", 
                                   json=rejection_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_test("Beta Request Rejection", True, f"Message: {message}")
                return True
            else:
                self.log_test("Beta Request Rejection", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Beta Request Rejection", False, f"Exception: {str(e)}")
            return False
    
    def test_database_operations(self):
        """Test database operations for SiteConfig and BetaAccessRequest models"""
        try:
            # Test site mode persistence by switching modes
            if not self.admin_token:
                self.log_test("Database Operations", False, "Admin token required")
                return False
            
            # Get current mode
            current_mode_data = self.test_get_site_mode()
            if not current_mode_data:
                return False
            
            current_mode = current_mode_data.get("mode", "public")
            new_mode = "private" if current_mode == "public" else "public"
            
            # Switch mode
            if self.test_update_site_mode(new_mode, self.admin_token):
                # Verify mode changed
                updated_mode_data = self.test_get_site_mode()
                if updated_mode_data and updated_mode_data.get("mode") == new_mode:
                    # Switch back to original mode
                    self.test_update_site_mode(current_mode, self.admin_token)
                    self.log_test("Database Operations - Site Config", True, 
                                "Site mode persistence working correctly")
                    return True
                else:
                    self.log_test("Database Operations - Site Config", False, 
                                "Site mode not persisted correctly")
                    return False
            else:
                return False
                
        except Exception as e:
            self.log_test("Database Operations", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all Private Beta Mode tests"""
        print("🎯 STARTING TOPKIT PRIVATE BETA MODE COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        
        # Phase 1: Authentication
        print("\n📋 PHASE 1: AUTHENTICATION TESTING")
        print("-" * 40)
        
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not admin_auth_success:
            print("❌ CRITICAL: Admin authentication failed - cannot test admin endpoints")
            return False
        
        # Phase 2: Site Configuration Endpoints
        print("\n📋 PHASE 2: SITE CONFIGURATION ENDPOINTS")
        print("-" * 40)
        
        # Test GET site mode
        self.test_get_site_mode()
        
        # Test POST site mode with admin token
        self.test_update_site_mode("private", self.admin_token, expected_success=True)
        
        # Test POST site mode without token (should fail)
        self.test_update_site_mode("public", None, expected_success=False)
        
        # Test POST site mode with user token (should fail)
        if user_auth_success:
            self.test_update_site_mode("private", self.user_token, expected_success=False)
        
        # Phase 3: Access Control Testing
        print("\n📋 PHASE 3: ACCESS CONTROL TESTING")
        print("-" * 40)
        
        # Test access check with admin token (should always have access)
        self.test_site_access_check(self.admin_token, expected_access=True)
        
        # Test access check with user token (depends on site mode)
        if user_auth_success:
            # First set to public mode
            self.test_update_site_mode("public", self.admin_token)
            self.test_site_access_check(self.user_token, expected_access=True)
            
            # Then set to private mode
            self.test_update_site_mode("private", self.admin_token)
            # Note: Regular users might not have access in private mode
            self.test_site_access_check(self.user_token, expected_access=False)
        
        # Test access check without token
        self.test_site_access_check(None, expected_access=False)
        
        # Phase 4: Beta Access Request System
        print("\n📋 PHASE 4: BETA ACCESS REQUEST SYSTEM")
        print("-" * 40)
        
        # Test beta access request submission
        request_id = self.test_beta_access_request_submission()
        
        # Test duplicate request prevention
        self.test_duplicate_beta_request()
        
        # Phase 5: Beta Request Management
        print("\n📋 PHASE 5: BETA REQUEST MANAGEMENT")
        print("-" * 40)
        
        # Test getting beta requests (admin only)
        beta_requests = self.test_get_beta_requests(self.admin_token, expected_success=True)
        
        # Test getting beta requests with user token (should fail)
        if user_auth_success:
            self.test_get_beta_requests(self.user_token, expected_success=False)
        
        # Test beta request approval/rejection if we have requests
        if request_id and beta_requests:
            # Create another request for rejection test
            rejection_request_id = self.test_beta_access_request_submission()
            
            if rejection_request_id:
                # Test approval
                self.test_beta_request_approval(request_id, self.admin_token)
                
                # Test rejection
                self.test_beta_request_rejection(rejection_request_id, self.admin_token)
        
        # Phase 6: Database Operations
        print("\n📋 PHASE 6: DATABASE OPERATIONS")
        print("-" * 40)
        
        self.test_database_operations()
        
        # Final Results
        print("\n" + "=" * 80)
        print("🎉 TOPKIT PRIVATE BETA MODE TESTING COMPLETE")
        print("=" * 80)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 RESULTS SUMMARY:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ EXCELLENT: Private Beta Mode is production-ready!")
        elif success_rate >= 75:
            print("⚠️  GOOD: Private Beta Mode is mostly functional with minor issues")
        else:
            print("❌ CRITICAL: Private Beta Mode has significant issues requiring fixes")
        
        # Reset to public mode for clean state
        self.test_update_site_mode("public", self.admin_token)
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = TopKitPrivateBetaTester()
    success = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()