#!/usr/bin/env python3
"""
TopKit Beta Access Request System Testing
=========================================

This script tests the complete beta access request system including:
1. Site Access Check Fix - Test that site access check works properly after login
2. Beta Access Request Endpoints - Test submission and management endpoints  
3. Admin Authentication - Verify admin login and access to admin functions

Key Endpoints Tested:
- POST /api/auth/login (Admin login)
- GET /api/site/access-check (Site access verification)
- POST /api/beta/request-access (Submit beta access request)
- GET /api/admin/beta/requests (Fetch beta requests - admin only)
- POST /api/admin/beta/requests/{id}/approve (Approve beta request - admin only)
- POST /api/admin/beta/requests/{id}/reject (Reject beta request - admin only)
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD_1 = "TopKitSecure789#"  # From review request
ADMIN_PASSWORD_2 = "adminpass123"      # From existing tests

class BetaAccessTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        self.total_tests += 1
        if status == "PASS":
            self.passed_tests += 1
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_admin_authentication(self):
        """Test admin login with both possible passwords"""
        print("🔐 Testing Admin Authentication...")
        
        # Try first password from review request
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD_1
            })
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and data.get("user", {}).get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_test(
                        f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_1})",
                        "PASS",
                        f"Admin login successful. Role: {data['user']['role']}, ID: {data['user']['id']}"
                    )
                    return True
                else:
                    self.log_test(
                        f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_1})",
                        "FAIL",
                        f"Login successful but invalid response: {data}"
                    )
            else:
                self.log_test(
                    f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_1})",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_1})",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        # Try second password from existing tests
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD_2
            })
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and data.get("user", {}).get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_test(
                        f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_2})",
                        "PASS",
                        f"Admin login successful. Role: {data['user']['role']}, ID: {data['user']['id']}"
                    )
                    return True
                else:
                    self.log_test(
                        f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_2})",
                        "FAIL",
                        f"Login successful but invalid response: {data}"
                    )
            else:
                self.log_test(
                    f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_2})",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                f"Admin Authentication ({ADMIN_EMAIL}/{ADMIN_PASSWORD_2})",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return False

    def test_site_access_check_without_auth(self):
        """Test site access check without authentication"""
        print("🌐 Testing Site Access Check (No Auth)...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/site/access-check")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Site Access Check (No Auth)",
                    "PASS",
                    f"Response: {data}"
                )
                return data
            else:
                self.log_test(
                    "Site Access Check (No Auth)",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Site Access Check (No Auth)",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return None

    def test_site_access_check_with_admin_auth(self):
        """Test site access check with admin authentication"""
        print("🌐 Testing Site Access Check (Admin Auth)...")
        
        if not self.admin_token:
            self.log_test(
                "Site Access Check (Admin Auth)",
                "SKIP",
                "No admin token available"
            )
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/site/access-check", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("has_access") == True and data.get("user_role") == "admin":
                    self.log_test(
                        "Site Access Check (Admin Auth)",
                        "PASS",
                        f"Admin has access: {data}"
                    )
                else:
                    self.log_test(
                        "Site Access Check (Admin Auth)",
                        "FAIL",
                        f"Admin should have access but got: {data}"
                    )
                return data
            else:
                self.log_test(
                    "Site Access Check (Admin Auth)",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Site Access Check (Admin Auth)",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return None

    def test_beta_access_request_submission(self):
        """Test submitting a beta access request"""
        print("📝 Testing Beta Access Request Submission...")
        
        # Generate unique test data
        test_email = f"test.user.{int(time.time())}@example.com"
        
        try:
            response = self.session.post(f"{BACKEND_URL}/beta/request-access", json={
                "email": test_email,
                "first_name": "Test",
                "last_name": "User",
                "message": "I would like to test the TopKit beta access system."
            })
            
            if response.status_code == 200:
                data = response.json()
                if "request_id" in data:
                    self.log_test(
                        "Beta Access Request Submission",
                        "PASS",
                        f"Request submitted successfully. ID: {data['request_id']}, Email: {test_email}"
                    )
                    return data["request_id"], test_email
                else:
                    self.log_test(
                        "Beta Access Request Submission",
                        "FAIL",
                        f"Missing request_id in response: {data}"
                    )
            else:
                self.log_test(
                    "Beta Access Request Submission",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Beta Access Request Submission",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return None, None

    def test_duplicate_beta_request_prevention(self, test_email):
        """Test that duplicate beta requests are prevented"""
        print("🚫 Testing Duplicate Beta Request Prevention...")
        
        if not test_email:
            self.log_test(
                "Duplicate Beta Request Prevention",
                "SKIP",
                "No test email available"
            )
            return
        
        try:
            response = self.session.post(f"{BACKEND_URL}/beta/request-access", json={
                "email": test_email,
                "first_name": "Duplicate",
                "last_name": "Test",
                "message": "This should be prevented."
            })
            
            if response.status_code == 200:
                data = response.json()
                if "déjà été soumise" in data.get("message", "").lower():
                    self.log_test(
                        "Duplicate Beta Request Prevention",
                        "PASS",
                        f"Duplicate request properly prevented: {data['message']}"
                    )
                else:
                    self.log_test(
                        "Duplicate Beta Request Prevention",
                        "FAIL",
                        f"Duplicate request not prevented: {data}"
                    )
            else:
                self.log_test(
                    "Duplicate Beta Request Prevention",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Duplicate Beta Request Prevention",
                "FAIL",
                f"Exception: {str(e)}"
            )

    def test_admin_fetch_beta_requests(self):
        """Test admin fetching beta access requests"""
        print("📋 Testing Admin Fetch Beta Requests...")
        
        if not self.admin_token:
            self.log_test(
                "Admin Fetch Beta Requests",
                "SKIP",
                "No admin token available"
            )
            return []
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/admin/beta/requests", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "requests" in data:
                    self.log_test(
                        "Admin Fetch Beta Requests",
                        "PASS",
                        f"Found {len(data['requests'])} beta requests"
                    )
                    return data["requests"]
                else:
                    self.log_test(
                        "Admin Fetch Beta Requests",
                        "FAIL",
                        f"Missing 'requests' in response: {data}"
                    )
            else:
                self.log_test(
                    "Admin Fetch Beta Requests",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Admin Fetch Beta Requests",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return []

    def test_non_admin_access_to_beta_requests(self):
        """Test that non-admin users cannot access beta requests"""
        print("🚫 Testing Non-Admin Access to Beta Requests...")
        
        try:
            # Test without authentication
            response = self.session.get(f"{BACKEND_URL}/admin/beta/requests")
            
            if response.status_code == 401:
                self.log_test(
                    "Non-Admin Access to Beta Requests (No Auth)",
                    "PASS",
                    "Properly blocked unauthenticated access"
                )
            else:
                self.log_test(
                    "Non-Admin Access to Beta Requests (No Auth)",
                    "FAIL",
                    f"Should return 401 but got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Non-Admin Access to Beta Requests (No Auth)",
                "FAIL",
                f"Exception: {str(e)}"
            )

    def test_admin_approve_beta_request(self, request_id):
        """Test admin approving a beta access request"""
        print("✅ Testing Admin Approve Beta Request...")
        
        if not self.admin_token or not request_id:
            self.log_test(
                "Admin Approve Beta Request",
                "SKIP",
                "No admin token or request ID available"
            )
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(
                f"{BACKEND_URL}/admin/beta/requests/{request_id}/approve",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "accordé" in data["message"].lower():
                    self.log_test(
                        "Admin Approve Beta Request",
                        "PASS",
                        f"Beta request approved successfully: {data['message']}"
                    )
                    return True
                else:
                    self.log_test(
                        "Admin Approve Beta Request",
                        "FAIL",
                        f"Unexpected response: {data}"
                    )
            else:
                self.log_test(
                    "Admin Approve Beta Request",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Admin Approve Beta Request",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        return False

    def test_admin_reject_beta_request(self):
        """Test admin rejecting a beta access request"""
        print("❌ Testing Admin Reject Beta Request...")
        
        # First create a new request to reject
        test_email = f"reject.test.{int(time.time())}@example.com"
        
        try:
            # Submit a new request
            response = self.session.post(f"{BACKEND_URL}/beta/request-access", json={
                "email": test_email,
                "first_name": "Reject",
                "last_name": "Test",
                "message": "This request will be rejected for testing."
            })
            
            if response.status_code != 200:
                self.log_test(
                    "Admin Reject Beta Request",
                    "FAIL",
                    "Could not create test request for rejection"
                )
                return
            
            request_id = response.json()["request_id"]
            
            # Now reject it
            if not self.admin_token:
                self.log_test(
                    "Admin Reject Beta Request",
                    "SKIP",
                    "No admin token available"
                )
                return
            
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(
                f"{BACKEND_URL}/admin/beta/requests/{request_id}/reject",
                json={"reason": "Test rejection for automated testing"},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "rejetée" in data["message"].lower():
                    self.log_test(
                        "Admin Reject Beta Request",
                        "PASS",
                        f"Beta request rejected successfully: {data['message']}"
                    )
                else:
                    self.log_test(
                        "Admin Reject Beta Request",
                        "FAIL",
                        f"Unexpected response: {data}"
                    )
            else:
                self.log_test(
                    "Admin Reject Beta Request",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Admin Reject Beta Request",
                "FAIL",
                f"Exception: {str(e)}"
            )

    def test_invalid_request_id_handling(self):
        """Test handling of invalid request IDs"""
        print("🔍 Testing Invalid Request ID Handling...")
        
        if not self.admin_token:
            self.log_test(
                "Invalid Request ID Handling",
                "SKIP",
                "No admin token available"
            )
            return
        
        invalid_id = str(uuid.uuid4())
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(
                f"{BACKEND_URL}/admin/beta/requests/{invalid_id}/approve",
                headers=headers
            )
            
            if response.status_code == 404:
                self.log_test(
                    "Invalid Request ID Handling",
                    "PASS",
                    "Properly returned 404 for invalid request ID"
                )
            else:
                self.log_test(
                    "Invalid Request ID Handling",
                    "FAIL",
                    f"Should return 404 but got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Invalid Request ID Handling",
                "FAIL",
                f"Exception: {str(e)}"
            )

    def test_malformed_request_data(self):
        """Test handling of malformed request data"""
        print("🚫 Testing Malformed Request Data...")
        
        # Test missing required fields
        try:
            response = self.session.post(f"{BACKEND_URL}/beta/request-access", json={
                "email": "incomplete@test.com"
                # Missing first_name and last_name
            })
            
            if response.status_code == 422:  # Validation error
                self.log_test(
                    "Malformed Request Data (Missing Fields)",
                    "PASS",
                    "Properly rejected request with missing required fields"
                )
            else:
                self.log_test(
                    "Malformed Request Data (Missing Fields)",
                    "FAIL",
                    f"Should return 422 but got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Malformed Request Data (Missing Fields)",
                "FAIL",
                f"Exception: {str(e)}"
            )
        
        # Test invalid email format
        try:
            response = self.session.post(f"{BACKEND_URL}/beta/request-access", json={
                "email": "invalid-email-format",
                "first_name": "Test",
                "last_name": "User"
            })
            
            if response.status_code == 422:  # Validation error
                self.log_test(
                    "Malformed Request Data (Invalid Email)",
                    "PASS",
                    "Properly rejected request with invalid email format"
                )
            else:
                self.log_test(
                    "Malformed Request Data (Invalid Email)",
                    "FAIL",
                    f"Should return 422 but got HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test(
                "Malformed Request Data (Invalid Email)",
                "FAIL",
                f"Exception: {str(e)}"
            )

    def run_all_tests(self):
        """Run all beta access system tests"""
        print("🚀 Starting TopKit Beta Access Request System Testing")
        print("=" * 60)
        
        # 1. Test admin authentication
        admin_auth_success = self.test_admin_authentication()
        
        # 2. Test site access check without auth
        self.test_site_access_check_without_auth()
        
        # 3. Test site access check with admin auth
        self.test_site_access_check_with_admin_auth()
        
        # 4. Test beta access request submission
        request_id, test_email = self.test_beta_access_request_submission()
        
        # 5. Test duplicate request prevention
        self.test_duplicate_beta_request_prevention(test_email)
        
        # 6. Test admin fetching beta requests
        beta_requests = self.test_admin_fetch_beta_requests()
        
        # 7. Test non-admin access prevention
        self.test_non_admin_access_to_beta_requests()
        
        # 8. Test admin approve beta request
        if request_id:
            self.test_admin_approve_beta_request(request_id)
        
        # 9. Test admin reject beta request
        self.test_admin_reject_beta_request()
        
        # 10. Test invalid request ID handling
        self.test_invalid_request_id_handling()
        
        # 11. Test malformed request data
        self.test_malformed_request_data()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🎯 TOPKIT BETA ACCESS REQUEST SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}% success rate)")
        print()
        
        # Group results by status
        passed = [r for r in self.test_results if r["status"] == "PASS"]
        failed = [r for r in self.test_results if r["status"] == "FAIL"]
        skipped = [r for r in self.test_results if r["status"] == "SKIP"]
        
        if passed:
            print("✅ PASSED TESTS:")
            for result in passed:
                print(f"   • {result['test']}")
            print()
        
        if failed:
            print("❌ FAILED TESTS:")
            for result in failed:
                print(f"   • {result['test']}: {result['details']}")
            print()
        
        if skipped:
            print("⚠️ SKIPPED TESTS:")
            for result in skipped:
                print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Key findings
        print("🔍 KEY FINDINGS:")
        
        admin_auth_tests = [r for r in self.test_results if "Admin Authentication" in r["test"]]
        admin_working = any(r["status"] == "PASS" for r in admin_auth_tests)
        
        if admin_working:
            print("   ✅ Admin authentication system is working")
        else:
            print("   ❌ Admin authentication system has issues")
        
        site_access_tests = [r for r in self.test_results if "Site Access Check" in r["test"]]
        site_access_working = any(r["status"] == "PASS" for r in site_access_tests)
        
        if site_access_working:
            print("   ✅ Site access check system is working")
        else:
            print("   ❌ Site access check system has issues")
        
        beta_request_tests = [r for r in self.test_results if "Beta" in r["test"] and r["status"] == "PASS"]
        beta_system_working = len(beta_request_tests) > 0
        
        if beta_system_working:
            print("   ✅ Beta access request system is operational")
        else:
            print("   ❌ Beta access request system has issues")
        
        print()
        print("🎉 Testing completed!")

if __name__ == "__main__":
    tester = BetaAccessTester()
    tester.run_all_tests()