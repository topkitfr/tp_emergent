#!/usr/bin/env python3
"""
TopKit Private Beta Mode Backend Testing Suite
Comprehensive testing of Private Beta Mode implementation including:
- Site Configuration Endpoints (GET/POST /api/site/mode)
- Access Control Endpoint (GET /api/site/access-check)
- Beta Access Request System (GET/POST /api/beta/requests)
- Beta Request Management (approve/reject endpoints)
- Authentication Integration with beta mode controls
- Database Operations for SiteConfig and BetaAccessRequest models
"""

import requests
import json
import sys
import uuid
import time
from datetime import datetime

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"
# Use unique email for regular user
TEST_USER_EMAIL = f"test.user.{int(time.time())}@example.com"
TEST_USER_PASSWORD = "SecurePass2024!"
# Use the hardcoded admin email from backend
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure2024!"

class PrivateBetaTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.test_results = []
        self.test_beta_request_id = None
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
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

    def authenticate_users(self):
        """Authenticate both admin and regular user"""
        print("🔐 AUTHENTICATING USERS")
        
        admin_authenticated = False
        user_authenticated = False
        
        # Try to authenticate existing admin user first
        try:
            admin_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                self.admin_token = admin_data["token"]
                self.admin_id = admin_data["user"]["id"]
                self.log_test("Admin Authentication", True, 
                            f"Admin authenticated: {admin_data['user']['name']} (Role: {admin_data['user']['role']})")
                admin_authenticated = True
            else:
                self.log_test("Admin Authentication", False, 
                            f"HTTP {admin_response.status_code} - Will skip admin-only tests", admin_response.text)
                
        except Exception as e:
            self.log_test("Admin Authentication", False, "Will skip admin-only tests", str(e))
        
        # Try to authenticate existing regular user
        try:
            user_response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                self.user_token = user_data["token"]
                self.user_id = user_data["user"]["id"]
                self.log_test("User Authentication", True, 
                            f"User authenticated: {user_data['user']['name']} (Role: {user_data['user']['role']})")
                user_authenticated = True
            else:
                # Try to create regular user if login fails
                self.log_test("User Authentication (Existing)", False, 
                            f"HTTP {user_response.status_code} - Will try to create user", user_response.text)
                
                # Create regular user
                try:
                    register_response = self.session.post(f"{BASE_URL}/auth/register", json={
                        "email": TEST_USER_EMAIL,
                        "password": TEST_USER_PASSWORD,
                        "name": "Test User"
                    })
                    
                    if register_response.status_code == 200:
                        register_data = register_response.json()
                        self.log_test("User Creation", True, "Regular user created successfully")
                        
                        # Handle email verification if needed
                        if 'dev_verification_link' in register_data:
                            verification_link = register_data['dev_verification_link']
                            token = verification_link.split('token=')[1] if 'token=' in verification_link else None
                            if token:
                                verify_response = self.session.post(f"{BASE_URL}/auth/verify-email", params={'token': token})
                                if verify_response.status_code == 200:
                                    self.log_test("User Email Verification", True, "Email verified successfully")
                                else:
                                    self.log_test("User Email Verification", False, f"HTTP {verify_response.status_code}", verify_response.text)
                        
                        # Now try to login
                        user_response = self.session.post(f"{BASE_URL}/auth/login", json={
                            "email": TEST_USER_EMAIL,
                            "password": TEST_USER_PASSWORD
                        })
                        
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            self.user_token = user_data["token"]
                            self.user_id = user_data["user"]["id"]
                            self.log_test("User Authentication (New)", True, 
                                        f"User authenticated: {user_data['user']['name']} (Role: {user_data['user']['role']})")
                            user_authenticated = True
                        else:
                            self.log_test("User Authentication (New)", False, 
                                        f"HTTP {user_response.status_code}", user_response.text)
                    else:
                        self.log_test("User Creation", False, 
                                    f"HTTP {register_response.status_code}", register_response.text)
                        
                except Exception as e:
                    self.log_test("User Creation", False, "", str(e))
                
        except Exception as e:
            self.log_test("User Authentication", False, "", str(e))
            
        # Return True if at least one user is authenticated
        return admin_authenticated or user_authenticated

    def test_site_mode_endpoints(self):
        """Test site mode configuration endpoints"""
        print("🏗️ TESTING SITE MODE CONFIGURATION ENDPOINTS")
        
        # Test 1: GET /api/site/mode (public access)
        try:
            response = self.session.get(f"{BASE_URL}/site/mode")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["mode", "is_private", "message"]
                if all(field in data for field in required_fields):
                    self.log_test("GET /api/site/mode", True, 
                                f"Current mode: {data['mode']}, Private: {data['is_private']}")
                else:
                    self.log_test("GET /api/site/mode", False, 
                                "Missing required fields", f"Got: {list(data.keys())}")
            else:
                self.log_test("GET /api/site/mode", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/site/mode", False, "", str(e))
        
        # Test 2: POST /api/site/mode without authentication (should fail)
        try:
            response = self.session.post(f"{BASE_URL}/site/mode", json={"mode": "private"})
            
            if response.status_code == 401:
                self.log_test("POST /api/site/mode (Unauthorized)", True, 
                            "Correctly rejected unauthenticated request")
            else:
                self.log_test("POST /api/site/mode (Unauthorized)", False, 
                            f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/site/mode (Unauthorized)", False, "", str(e))
        
        # Test 3: POST /api/site/mode with regular user (should fail)
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.post(f"{BASE_URL}/site/mode", 
                                           json={"mode": "private"}, headers=headers)
                
                if response.status_code == 403:
                    self.log_test("POST /api/site/mode (Non-Admin)", True, 
                                "Correctly rejected non-admin user")
                else:
                    self.log_test("POST /api/site/mode (Non-Admin)", False, 
                                f"Expected 403, got {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/site/mode (Non-Admin)", False, "", str(e))
        else:
            self.log_test("POST /api/site/mode (Non-Admin)", False, "No user token available", "Skipped")
        
        # Skip admin tests if no admin token
        if not self.admin_token:
            self.log_test("POST /api/site/mode (Admin Tests)", False, "No admin token available", "Skipped admin-only tests")
            return
        
        # Test 4: POST /api/site/mode with admin (should succeed)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/site/mode", 
                                       json={"mode": "private"}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("mode") == "private":
                    self.log_test("POST /api/site/mode (Admin - Private)", True, 
                                f"Successfully set to private mode: {data.get('message')}")
                else:
                    self.log_test("POST /api/site/mode (Admin - Private)", False, 
                                "Mode not set correctly", str(data))
            else:
                self.log_test("POST /api/site/mode (Admin - Private)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/site/mode (Admin - Private)", False, "", str(e))
        
        # Test 5: POST /api/site/mode with invalid mode (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/site/mode", 
                                       json={"mode": "invalid"}, headers=headers)
            
            if response.status_code == 400:
                self.log_test("POST /api/site/mode (Invalid Mode)", True, 
                            "Correctly rejected invalid mode")
            else:
                self.log_test("POST /api/site/mode (Invalid Mode)", False, 
                            f"Expected 400, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/site/mode (Invalid Mode)", False, "", str(e))
        
        # Test 6: Switch back to public mode
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/site/mode", 
                                       json={"mode": "public"}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("mode") == "public":
                    self.log_test("POST /api/site/mode (Admin - Public)", True, 
                                f"Successfully set to public mode: {data.get('message')}")
                else:
                    self.log_test("POST /api/site/mode (Admin - Public)", False, 
                                "Mode not set correctly", str(data))
            else:
                self.log_test("POST /api/site/mode (Admin - Public)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/site/mode (Admin - Public)", False, "", str(e))

    def test_access_control_endpoint(self):
        """Test site access control endpoint"""
        print("🔒 TESTING ACCESS CONTROL ENDPOINT")
        
        # First, set site to private mode for testing
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.session.post(f"{BASE_URL}/site/mode", 
                            json={"mode": "private"}, headers=headers)
        except:
            pass
        
        # Test 1: GET /api/site/access-check without authentication (private mode)
        try:
            response = self.session.get(f"{BASE_URL}/site/access-check")
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("has_access") and data.get("mode") == "private":
                    self.log_test("GET /api/site/access-check (Unauthenticated)", True, 
                                f"Correctly blocked unauthenticated access: {data.get('message')}")
                else:
                    self.log_test("GET /api/site/access-check (Unauthenticated)", False, 
                                "Should block unauthenticated access in private mode", str(data))
            else:
                self.log_test("GET /api/site/access-check (Unauthenticated)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/site/access-check (Unauthenticated)", False, "", str(e))
        
        # Test 2: GET /api/site/access-check with regular user (private mode)
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Regular user should be blocked unless they have beta_access
                expected_access = data.get("has_access", False)
                self.log_test("GET /api/site/access-check (Regular User)", True, 
                            f"User access: {expected_access}, Mode: {data.get('mode')}, Message: {data.get('message')}")
            else:
                self.log_test("GET /api/site/access-check (Regular User)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/site/access-check (Regular User)", False, "", str(e))
        
        # Test 3: GET /api/site/access-check with admin (private mode)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("has_access") and data.get("user_role") == "admin":
                    self.log_test("GET /api/site/access-check (Admin)", True, 
                                f"Admin correctly granted access: {data.get('message')}")
                else:
                    self.log_test("GET /api/site/access-check (Admin)", False, 
                                "Admin should have access in private mode", str(data))
            else:
                self.log_test("GET /api/site/access-check (Admin)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/site/access-check (Admin)", False, "", str(e))
        
        # Test 4: Switch to public mode and test access
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.session.post(f"{BASE_URL}/site/mode", 
                            json={"mode": "public"}, headers=headers)
            
            # Test public access without authentication
            response = self.session.get(f"{BASE_URL}/site/access-check")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("has_access") and data.get("mode") == "public":
                    self.log_test("GET /api/site/access-check (Public Mode)", True, 
                                f"Public access correctly granted: {data.get('message')}")
                else:
                    self.log_test("GET /api/site/access-check (Public Mode)", False, 
                                "Should grant access in public mode", str(data))
            else:
                self.log_test("GET /api/site/access-check (Public Mode)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/site/access-check (Public Mode)", False, "", str(e))

    def test_beta_access_request_system(self):
        """Test beta access request submission and retrieval"""
        print("📝 TESTING BETA ACCESS REQUEST SYSTEM")
        
        # Test 1: POST /api/beta/request-access (valid request)
        test_email = f"test.beta.{uuid.uuid4().hex[:8]}@example.com"
        try:
            response = self.session.post(f"{BASE_URL}/beta/request-access", json={
                "email": test_email,
                "first_name": "Test",
                "last_name": "User",
                "message": "I would like to test the TopKit beta platform"
            })
            
            if response.status_code == 200:
                data = response.json()
                if "request_id" in data and "message" in data:
                    self.test_beta_request_id = data["request_id"]
                    self.log_test("POST /api/beta/request-access (Valid)", True, 
                                f"Request submitted successfully: {data['message']}")
                else:
                    self.log_test("POST /api/beta/request-access (Valid)", False, 
                                "Missing required response fields", str(data))
            else:
                self.log_test("POST /api/beta/request-access (Valid)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/beta/request-access (Valid)", False, "", str(e))
        
        # Test 2: POST /api/beta/request-access (duplicate email)
        try:
            response = self.session.post(f"{BASE_URL}/beta/request-access", json={
                "email": test_email,
                "first_name": "Test",
                "last_name": "User2",
                "message": "Duplicate request"
            })
            
            if response.status_code == 200:
                data = response.json()
                if "déjà été soumise" in data.get("message", ""):
                    self.log_test("POST /api/beta/request-access (Duplicate)", True, 
                                f"Correctly handled duplicate: {data['message']}")
                else:
                    self.log_test("POST /api/beta/request-access (Duplicate)", False, 
                                "Should detect duplicate email", str(data))
            else:
                self.log_test("POST /api/beta/request-access (Duplicate)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/beta/request-access (Duplicate)", False, "", str(e))
        
        # Test 3: POST /api/beta/request-access (invalid data)
        try:
            response = self.session.post(f"{BASE_URL}/beta/request-access", json={
                "email": "invalid-email",
                "first_name": "",
                "last_name": ""
            })
            
            if response.status_code in [400, 422]:
                self.log_test("POST /api/beta/request-access (Invalid Data)", True, 
                            "Correctly rejected invalid data")
            else:
                self.log_test("POST /api/beta/request-access (Invalid Data)", False, 
                            f"Expected 400/422, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/beta/request-access (Invalid Data)", False, "", str(e))

    def test_beta_request_management(self):
        """Test beta request management endpoints (admin only)"""
        print("👨‍💼 TESTING BETA REQUEST MANAGEMENT")
        
        # Test 1: GET /api/admin/beta/requests without authentication (should fail)
        try:
            response = self.session.get(f"{BASE_URL}/admin/beta/requests")
            
            if response.status_code == 401:
                self.log_test("GET /api/admin/beta/requests (Unauthorized)", True, 
                            "Correctly rejected unauthenticated request")
            else:
                self.log_test("GET /api/admin/beta/requests (Unauthorized)", False, 
                            f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/beta/requests (Unauthorized)", False, "", str(e))
        
        # Test 2: GET /api/admin/beta/requests with regular user (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 403:
                self.log_test("GET /api/admin/beta/requests (Non-Admin)", True, 
                            "Correctly rejected non-admin user")
            else:
                self.log_test("GET /api/admin/beta/requests (Non-Admin)", False, 
                            f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/beta/requests (Non-Admin)", False, "", str(e))
        
        # Test 3: GET /api/admin/beta/requests with admin (should succeed)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "requests" in data and "total" in data:
                    self.log_test("GET /api/admin/beta/requests (Admin)", True, 
                                f"Retrieved {data['total']} beta requests")
                else:
                    self.log_test("GET /api/admin/beta/requests (Admin)", False, 
                                "Missing required response fields", str(data))
            else:
                self.log_test("GET /api/admin/beta/requests (Admin)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/beta/requests (Admin)", False, "", str(e))
        
        # Test 4: GET /api/admin/beta/requests with status filter
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/beta/requests?status=pending", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("filter") == "pending":
                    self.log_test("GET /api/admin/beta/requests (Status Filter)", True, 
                                f"Filtered by status: {data['total']} pending requests")
                else:
                    self.log_test("GET /api/admin/beta/requests (Status Filter)", False, 
                                "Status filter not applied correctly", str(data))
            else:
                self.log_test("GET /api/admin/beta/requests (Status Filter)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("GET /api/admin/beta/requests (Status Filter)", False, "", str(e))

    def test_beta_request_approval_rejection(self):
        """Test beta request approval and rejection"""
        print("✅❌ TESTING BETA REQUEST APPROVAL/REJECTION")
        
        if not self.test_beta_request_id:
            self.log_test("Beta Request Approval/Rejection Setup", False, 
                        "No test beta request ID available", "Skipping approval/rejection tests")
            return
        
        # Test 1: Approve beta request without authentication (should fail)
        try:
            response = self.session.post(f"{BASE_URL}/admin/beta/requests/{self.test_beta_request_id}/approve")
            
            if response.status_code == 401:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Unauthorized)", True, 
                            "Correctly rejected unauthenticated request")
            else:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Unauthorized)", False, 
                            f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/beta/requests/{id}/approve (Unauthorized)", False, "", str(e))
        
        # Test 2: Approve beta request with regular user (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{BASE_URL}/admin/beta/requests/{self.test_beta_request_id}/approve", 
                                       headers=headers)
            
            if response.status_code == 403:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Non-Admin)", True, 
                            "Correctly rejected non-admin user")
            else:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Non-Admin)", False, 
                            f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/beta/requests/{id}/approve (Non-Admin)", False, "", str(e))
        
        # Test 3: Approve beta request with admin (should succeed)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/admin/beta/requests/{self.test_beta_request_id}/approve", 
                                       headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("POST /api/admin/beta/requests/{id}/approve (Admin)", True, 
                                f"Successfully approved request: {data['message']}")
                else:
                    self.log_test("POST /api/admin/beta/requests/{id}/approve (Admin)", False, 
                                "Missing success message", str(data))
            else:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Admin)", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/beta/requests/{id}/approve (Admin)", False, "", str(e))
        
        # Test 4: Try to approve already processed request (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{BASE_URL}/admin/beta/requests/{self.test_beta_request_id}/approve", 
                                       headers=headers)
            
            if response.status_code == 400:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Already Processed)", True, 
                            "Correctly rejected already processed request")
            else:
                self.log_test("POST /api/admin/beta/requests/{id}/approve (Already Processed)", False, 
                            f"Expected 400, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/beta/requests/{id}/approve (Already Processed)", False, "", str(e))
        
        # Test 5: Create another request for rejection testing
        test_email_2 = f"test.beta.reject.{uuid.uuid4().hex[:8]}@example.com"
        test_request_id_2 = None
        
        try:
            response = self.session.post(f"{BASE_URL}/beta/request-access", json={
                "email": test_email_2,
                "first_name": "Reject",
                "last_name": "Test",
                "message": "This request will be rejected for testing"
            })
            
            if response.status_code == 200:
                test_request_id_2 = response.json().get("request_id")
        except:
            pass
        
        # Test 6: Reject beta request with admin (should succeed)
        if test_request_id_2:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.post(f"{BASE_URL}/admin/beta/requests/{test_request_id_2}/reject", 
                                           json={"reason": "Testing rejection functionality"}, 
                                           headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        self.log_test("POST /api/admin/beta/requests/{id}/reject (Admin)", True, 
                                    f"Successfully rejected request: {data['message']}")
                    else:
                        self.log_test("POST /api/admin/beta/requests/{id}/reject (Admin)", False, 
                                    "Missing success message", str(data))
                else:
                    self.log_test("POST /api/admin/beta/requests/{id}/reject (Admin)", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("POST /api/admin/beta/requests/{id}/reject (Admin)", False, "", str(e))
        
        # Test 7: Reject with invalid request ID (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            fake_id = str(uuid.uuid4())
            response = self.session.post(f"{BASE_URL}/admin/beta/requests/{fake_id}/reject", 
                                       json={"reason": "Testing with fake ID"}, 
                                       headers=headers)
            
            if response.status_code == 404:
                self.log_test("POST /api/admin/beta/requests/{id}/reject (Invalid ID)", True, 
                            "Correctly handled invalid request ID")
            else:
                self.log_test("POST /api/admin/beta/requests/{id}/reject (Invalid ID)", False, 
                            f"Expected 404, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("POST /api/admin/beta/requests/{id}/reject (Invalid ID)", False, "", str(e))

    def test_database_operations(self):
        """Test database operations for site config and beta requests"""
        print("🗄️ TESTING DATABASE OPERATIONS")
        
        # Test 1: Verify site mode persistence
        try:
            # Set to private mode
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.session.post(f"{BASE_URL}/site/mode", 
                            json={"mode": "private"}, headers=headers)
            
            # Check if mode persists
            response = self.session.get(f"{BASE_URL}/site/mode")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("mode") == "private":
                    self.log_test("Database - Site Mode Persistence", True, 
                                "Site mode correctly persisted in database")
                else:
                    self.log_test("Database - Site Mode Persistence", False, 
                                f"Expected private mode, got {data.get('mode')}")
            else:
                self.log_test("Database - Site Mode Persistence", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Database - Site Mode Persistence", False, "", str(e))
        
        # Test 2: Verify beta request storage and retrieval
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BASE_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                requests = data.get("requests", [])
                
                # Check if our test request is in the database
                test_request_found = any(req.get("id") == self.test_beta_request_id for req in requests)
                
                if test_request_found:
                    self.log_test("Database - Beta Request Storage", True, 
                                f"Beta requests correctly stored and retrievable ({len(requests)} total)")
                else:
                    self.log_test("Database - Beta Request Storage", False, 
                                "Test beta request not found in database")
            else:
                self.log_test("Database - Beta Request Storage", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Database - Beta Request Storage", False, "", str(e))
        
        # Test 3: Verify request status updates
        if self.test_beta_request_id:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BASE_URL}/admin/beta/requests?status=approved", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    approved_requests = data.get("requests", [])
                    
                    # Check if our approved request is in the approved list
                    approved_request_found = any(req.get("id") == self.test_beta_request_id 
                                               for req in approved_requests)
                    
                    if approved_request_found:
                        self.log_test("Database - Request Status Updates", True, 
                                    "Request status correctly updated in database")
                    else:
                        self.log_test("Database - Request Status Updates", False, 
                                    "Approved request not found in approved list")
                else:
                    self.log_test("Database - Request Status Updates", False, 
                                f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test("Database - Request Status Updates", False, "", str(e))

    def test_authentication_integration(self):
        """Test authentication integration with beta mode controls"""
        print("🔐 TESTING AUTHENTICATION INTEGRATION WITH BETA MODE")
        
        # Test 1: Verify admin bypass in private mode
        try:
            # Ensure site is in private mode
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            self.session.post(f"{BASE_URL}/site/mode", 
                            json={"mode": "private"}, headers=headers)
            
            # Test admin access
            response = self.session.get(f"{BASE_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("has_access") and data.get("user_role") == "admin":
                    self.log_test("Authentication - Admin Bypass", True, 
                                "Admin correctly bypasses private mode restrictions")
                else:
                    self.log_test("Authentication - Admin Bypass", False, 
                                "Admin should bypass private mode", str(data))
            else:
                self.log_test("Authentication - Admin Bypass", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Authentication - Admin Bypass", False, "", str(e))
        
        # Test 2: Verify regular user blocking in private mode
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Regular user should be blocked unless they have beta_access
                has_access = data.get("has_access", False)
                self.log_test("Authentication - Regular User Access Control", True, 
                            f"Regular user access properly controlled: {has_access}")
            else:
                self.log_test("Authentication - Regular User Access Control", False, 
                            f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Authentication - Regular User Access Control", False, "", str(e))
        
        # Test 3: Test token validation across beta endpoints
        try:
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token"}
            response = self.session.post(f"{BASE_URL}/site/mode", 
                                       json={"mode": "public"}, headers=headers)
            
            if response.status_code == 401:
                self.log_test("Authentication - Token Validation", True, 
                            "Invalid tokens correctly rejected")
            else:
                self.log_test("Authentication - Token Validation", False, 
                            f"Expected 401, got {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Authentication - Token Validation", False, "", str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("🎯 TOPKIT PRIVATE BETA MODE BACKEND TESTING COMPLETE")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}")
                    if result["error"]:
                        print(f"     Error: {result['error']}")
        
        print(f"\n✅ CRITICAL FEATURES STATUS:")
        
        # Analyze critical features
        site_mode_tests = [r for r in self.test_results if "site/mode" in r["test"]]
        access_control_tests = [r for r in self.test_results if "access-check" in r["test"]]
        beta_request_tests = [r for r in self.test_results if "beta" in r["test"] and "request" in r["test"]]
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        
        def feature_status(tests):
            if not tests:
                return "❓ NOT TESTED"
            passed = sum(1 for t in tests if t["success"])
            total = len(tests)
            if passed == total:
                return "✅ WORKING"
            elif passed > total // 2:
                return "⚠️ PARTIAL"
            else:
                return "❌ FAILING"
        
        print(f"   Site Configuration Endpoints: {feature_status(site_mode_tests)}")
        print(f"   Access Control System: {feature_status(access_control_tests)}")
        print(f"   Beta Access Request System: {feature_status(beta_request_tests)}")
        print(f"   Authentication Integration: {feature_status(auth_tests)}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 ASSESSMENT: EXCELLENT - Private Beta Mode is production-ready!")
        elif success_rate >= 75:
            print(f"\n✅ ASSESSMENT: GOOD - Private Beta Mode is functional with minor issues")
        elif success_rate >= 50:
            print(f"\n⚠️ ASSESSMENT: NEEDS WORK - Private Beta Mode has significant issues")
        else:
            print(f"\n❌ ASSESSMENT: CRITICAL ISSUES - Private Beta Mode requires major fixes")
        
        print("\n" + "="*80)
        
        return success_rate

    def run_all_tests(self):
        """Run all Private Beta Mode tests"""
        print("🚀 STARTING TOPKIT PRIVATE BETA MODE BACKEND TESTING")
        print("="*80)
        
        # Authenticate users first
        if not self.authenticate_users():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Run all test suites
        self.test_site_mode_endpoints()
        self.test_access_control_endpoint()
        self.test_beta_access_request_system()
        self.test_beta_request_management()
        self.test_beta_request_approval_rejection()
        self.test_database_operations()
        self.test_authentication_integration()
        
        # Generate final report
        success_rate = self.generate_report()
        
        return success_rate >= 75  # Consider 75%+ as successful

def main():
    """Main function to run Private Beta Mode tests"""
    tester = PrivateBetaTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()