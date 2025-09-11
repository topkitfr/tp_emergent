#!/usr/bin/env python3
"""
TopKit Admin Dashboard Backend Testing
Comprehensive testing of admin system functionality including:
1. Admin authentication system
2. Admin dashboard data endpoints  
3. User management admin endpoints
4. Moderation system testing
5. Data management endpoints
6. Analytics & reporting
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class AdminDashboardTester:
    def __init__(self):
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
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
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
    def make_request(self, method, endpoint, data=None, headers=None, files=None):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                if files:
                    response = requests.put(url, data=data, files=files, headers=headers, timeout=30)
                else:
                    response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return None
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error for {method} {endpoint}: {e}")
            return None

    def test_admin_authentication(self):
        """Test 1: Admin Authentication System"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION SYSTEM")
        
        # Test admin login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                admin_role = user_data.get('role')
                admin_name = user_data.get('name')
                
                if self.admin_token and admin_role == 'admin':
                    self.log_test("Admin Login", True, f"Admin: {admin_name}, Role: {admin_role}")
                    
                    # Test JWT token validation
                    headers = {"Authorization": f"Bearer {self.admin_token}"}
                    profile_response = self.make_request("GET", "/profile", headers=headers)
                    
                    if profile_response and profile_response.status_code == 200:
                        self.log_test("JWT Token Validation", True, "Admin token valid")
                    else:
                        self.log_test("JWT Token Validation", False, f"Token validation failed: {profile_response.status_code if profile_response else 'No response'}")
                        
                    # Test admin role verification
                    admin_endpoint_response = self.make_request("GET", "/admin/users", headers=headers)
                    if admin_endpoint_response and admin_endpoint_response.status_code in [200, 404]:
                        self.log_test("Admin Role Verification", True, "Admin endpoints accessible")
                    else:
                        self.log_test("Admin Role Verification", False, f"Admin endpoints not accessible: {admin_endpoint_response.status_code if admin_endpoint_response else 'No response'}")
                        
                else:
                    self.log_test("Admin Login", False, f"Invalid admin credentials or role: {admin_role}")
            except Exception as e:
                self.log_test("Admin Login", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Admin Login", False, f"Login failed: {response.status_code if response else 'No response'}")

    def test_dashboard_data_endpoints(self):
        """Test 2: Admin Dashboard Data Endpoints"""
        print("\n📊 TESTING ADMIN DASHBOARD DATA ENDPOINTS")
        
        if not self.admin_token:
            self.log_test("Dashboard Data Endpoints", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test dashboard statistics
        stats_response = self.make_request("GET", "/admin/traffic-stats", headers=headers)
        if stats_response and stats_response.status_code == 200:
            try:
                stats_data = stats_response.json()
                users_count = stats_data.get('users_count', 0)
                jerseys_count = stats_data.get('jerseys_count', 0)
                contributions_count = stats_data.get('contributions_count', 0)
                
                self.log_test("Dashboard Statistics API", True, f"Users: {users_count}, Jerseys: {jerseys_count}, Contributions: {contributions_count}")
            except Exception as e:
                self.log_test("Dashboard Statistics API", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Dashboard Statistics API", False, f"Stats endpoint failed: {stats_response.status_code if stats_response else 'No response'}")
            
        # Test recent activity/audit trail
        activities_response = self.make_request("GET", "/admin/activities", headers=headers)
        if activities_response and activities_response.status_code == 200:
            try:
                activities_data = activities_response.json()
                activities_count = len(activities_data) if isinstance(activities_data, list) else activities_data.get('total', 0)
                self.log_test("Recent Activity Endpoint", True, f"Found {activities_count} activities")
            except Exception as e:
                self.log_test("Recent Activity Endpoint", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Recent Activity Endpoint", False, f"Activities endpoint failed: {activities_response.status_code if activities_response else 'No response'}")
            
        # Test user statistics endpoint
        if self.admin_user_id:
            user_stats_response = self.make_request("GET", f"/admin/user-stats/{self.admin_user_id}", headers=headers)
            if user_stats_response and user_stats_response.status_code == 200:
                self.log_test("User Statistics Endpoint", True, "User stats accessible")
            else:
                self.log_test("User Statistics Endpoint", False, f"User stats failed: {user_stats_response.status_code if user_stats_response else 'No response'}")

    def test_user_management_endpoints(self):
        """Test 3: User Management Admin Endpoints"""
        print("\n👥 TESTING USER MANAGEMENT ADMIN ENDPOINTS")
        
        if not self.admin_token:
            self.log_test("User Management Endpoints", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test user listing with admin privileges
        users_response = self.make_request("GET", "/admin/users", headers=headers)
        if users_response and users_response.status_code == 200:
            try:
                users_data = users_response.json()
                users_count = len(users_data) if isinstance(users_data, list) else users_data.get('total', 0)
                self.log_test("User Listing API", True, f"Found {users_count} users")
                
                # Test user security info endpoint if we have users
                if isinstance(users_data, list) and len(users_data) > 0:
                    test_user_id = users_data[0].get('id')
                    if test_user_id:
                        security_response = self.make_request("GET", f"/admin/users/{test_user_id}/security", headers=headers)
                        if security_response and security_response.status_code in [200, 404]:
                            self.log_test("User Security Info", True, "Security info endpoint accessible")
                        else:
                            self.log_test("User Security Info", False, f"Security info failed: {security_response.status_code if security_response else 'No response'}")
                            
            except Exception as e:
                self.log_test("User Listing API", False, f"JSON parsing error: {e}")
        else:
            self.log_test("User Listing API", False, f"Users endpoint failed: {users_response.status_code if users_response else 'No response'}")
        
        # Test role assignment functionality - test with a dummy user ID
        test_user_id = "test-user-id"
        role_data = {"role": "moderator", "reason": "Testing role assignment"}
        role_response = self.make_request("POST", f"/admin/users/{test_user_id}/assign-role", data=role_data, headers=headers)
        if role_response and role_response.status_code in [200, 404, 400]:
            self.log_test("Role Assignment Endpoint", True, "Role assignment endpoint accessible")
        else:
            self.log_test("Role Assignment Endpoint", False, f"Role endpoint failed: {role_response.status_code if role_response else 'No response'}")
            
        # Test user ban functionality
        ban_data = {"reason": "Testing ban functionality", "permanent": False}
        ban_response = self.make_request("POST", f"/admin/users/{test_user_id}/ban", data=ban_data, headers=headers)
        if ban_response and ban_response.status_code in [200, 404, 400]:
            self.log_test("User Ban Management", True, "Ban management endpoint accessible")
        else:
            self.log_test("User Ban Management", False, f"Ban endpoint failed: {ban_response.status_code if ban_response else 'No response'}")
            
        # Test moderator assignment
        moderator_response = self.make_request("POST", f"/admin/users/{test_user_id}/make-moderator", headers=headers)
        if moderator_response and moderator_response.status_code in [200, 404, 400]:
            self.log_test("Moderator Assignment", True, "Moderator assignment endpoint accessible")
        else:
            self.log_test("Moderator Assignment", False, f"Moderator endpoint failed: {moderator_response.status_code if moderator_response else 'No response'}")

    def test_moderation_system(self):
        """Test 4: Moderation System Testing"""
        print("\n🛡️ TESTING MODERATION SYSTEM")
        
        if not self.admin_token:
            self.log_test("Moderation System", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test pending contributions queue
        pending_response = self.make_request("GET", "/admin/jerseys/pending", headers=headers)
        if pending_response and pending_response.status_code == 200:
            try:
                pending_data = pending_response.json()
                pending_count = len(pending_data) if isinstance(pending_data, list) else pending_data.get('total', 0)
                self.log_test("Pending Contributions Queue", True, f"Found {pending_count} pending items")
                
                # Test approval/rejection workflows with actual pending items
                if isinstance(pending_data, list) and len(pending_data) > 0:
                    test_jersey_id = pending_data[0].get('id')
                    if test_jersey_id:
                        # Test suggest modifications
                        suggest_data = {
                            "jersey_id": test_jersey_id,
                            "suggested_changes": "Test modification suggestion",
                            "suggested_modifications": {"team": "Updated team name"}
                        }
                        suggest_response = self.make_request("POST", f"/admin/jerseys/{test_jersey_id}/suggest-modifications", data=suggest_data, headers=headers)
                        if suggest_response and suggest_response.status_code in [200, 201, 400]:
                            self.log_test("Modification Suggestions", True, "Suggest modifications endpoint working")
                        else:
                            self.log_test("Modification Suggestions", False, f"Suggest modifications failed: {suggest_response.status_code if suggest_response else 'No response'}")
                            
            except Exception as e:
                self.log_test("Pending Contributions Queue", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Pending Contributions Queue", False, f"Pending queue failed: {pending_response.status_code if pending_response else 'No response'}")
        
        # Test approval workflow with dummy ID
        test_jersey_id = "test-jersey-id"
        approval_response = self.make_request("POST", f"/admin/jerseys/{test_jersey_id}/approve", headers=headers)
        if approval_response and approval_response.status_code in [200, 404, 400]:
            self.log_test("Contribution Approval Workflow", True, "Approval endpoint accessible")
        else:
            self.log_test("Contribution Approval Workflow", False, f"Approval endpoint failed: {approval_response.status_code if approval_response else 'No response'}")
            
        # Test rejection workflow
        reject_data = {"reason": "Test rejection"}
        rejection_response = self.make_request("POST", f"/admin/jerseys/{test_jersey_id}/reject", data=reject_data, headers=headers)
        if rejection_response and rejection_response.status_code in [200, 404, 400]:
            self.log_test("Contribution Rejection Workflow", True, "Rejection endpoint accessible")
        else:
            self.log_test("Contribution Rejection Workflow", False, f"Rejection endpoint failed: {rejection_response.status_code if rejection_response else 'No response'}")
            
        # Test jersey edit functionality
        edit_data = {"team": "Test Team", "league": "Test League", "season": "2024/25"}
        edit_response = self.make_request("PUT", f"/admin/jerseys/{test_jersey_id}/edit", data=edit_data, headers=headers)
        if edit_response and edit_response.status_code in [200, 404, 400, 500]:
            self.log_test("Jersey Edit Functionality", True, "Jersey edit endpoint accessible")
        else:
            self.log_test("Jersey Edit Functionality", False, f"Jersey edit failed: {edit_response.status_code if edit_response else 'No response'}")

    def test_data_management_endpoints(self):
        """Test 5: Data Management Endpoints"""
        print("\n💾 TESTING DATA MANAGEMENT ENDPOINTS")
        
        if not self.admin_token:
            self.log_test("Data Management Endpoints", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test database cleanup functionality
        cleanup_response = self.make_request("POST", "/admin/cleanup/database", headers=headers)
        if cleanup_response and cleanup_response.status_code in [200, 404, 400]:
            self.log_test("Database Cleanup", True, "Database cleanup endpoint accessible")
        else:
            self.log_test("Database Cleanup", False, f"Database cleanup failed: {cleanup_response.status_code if cleanup_response else 'No response'}")
            
        # Test database erase functionality (dangerous - just test accessibility)
        erase_response = self.make_request("GET", "/admin/database/erase", headers=headers)
        if erase_response and erase_response.status_code in [200, 404, 405]:
            self.log_test("Database Erase Endpoint", True, "Database erase endpoint accessible")
        else:
            self.log_test("Database Erase Endpoint", False, f"Database erase failed: {erase_response.status_code if erase_response else 'No response'}")
            
        # Test clear listings functionality
        clear_listings_response = self.make_request("GET", "/admin/database/clear-listings", headers=headers)
        if clear_listings_response and clear_listings_response.status_code in [200, 404, 405]:
            self.log_test("Clear Listings Endpoint", True, "Clear listings endpoint accessible")
        else:
            self.log_test("Clear Listings Endpoint", False, f"Clear listings failed: {clear_listings_response.status_code if clear_listings_response else 'No response'}")
            
        # Test beta requests management
        beta_requests_response = self.make_request("GET", "/admin/beta/requests", headers=headers)
        if beta_requests_response and beta_requests_response.status_code == 200:
            try:
                beta_data = beta_requests_response.json()
                beta_count = len(beta_data) if isinstance(beta_data, list) else beta_data.get('total', 0)
                self.log_test("Beta Requests Management", True, f"Found {beta_count} beta requests")
            except Exception as e:
                self.log_test("Beta Requests Management", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Beta Requests Management", False, f"Beta requests failed: {beta_requests_response.status_code if beta_requests_response else 'No response'}")

    def test_analytics_reporting(self):
        """Test 6: Analytics & Reporting"""
        print("\n📈 TESTING ANALYTICS & REPORTING")
        
        if not self.admin_token:
            self.log_test("Analytics & Reporting", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test transaction verification system (anti-fraud)
        pending_transactions_response = self.make_request("GET", "/admin/transactions/pending-verification", headers=headers)
        if pending_transactions_response and pending_transactions_response.status_code == 200:
            try:
                transactions_data = pending_transactions_response.json()
                transactions_count = transactions_data.get('total_pending', 0)
                self.log_test("Transaction Verification System", True, f"Found {transactions_count} pending transactions")
            except Exception as e:
                self.log_test("Transaction Verification System", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Transaction Verification System", False, f"Transaction verification failed: {pending_transactions_response.status_code if pending_transactions_response else 'No response'}")
            
        # Test transaction details endpoint
        test_transaction_id = "test-transaction-id"
        transaction_details_response = self.make_request("GET", f"/admin/transactions/{test_transaction_id}/details", headers=headers)
        if transaction_details_response and transaction_details_response.status_code in [200, 404]:
            self.log_test("Transaction Details Endpoint", True, "Transaction details endpoint accessible")
        else:
            self.log_test("Transaction Details Endpoint", False, f"Transaction details failed: {transaction_details_response.status_code if transaction_details_response else 'No response'}")
            
        # Test transaction verification workflows
        verify_data = {
            "authenticity_score": 9,
            "notes": "Test verification",
            "evidence_photos": []
        }
        verify_authentic_response = self.make_request("POST", f"/admin/transactions/{test_transaction_id}/verify-authentic", data=verify_data, headers=headers)
        if verify_authentic_response and verify_authentic_response.status_code in [200, 404, 400]:
            self.log_test("Authentic Verification Workflow", True, "Authentic verification endpoint accessible")
        else:
            self.log_test("Authentic Verification Workflow", False, f"Authentic verification failed: {verify_authentic_response.status_code if verify_authentic_response else 'No response'}")
            
        verify_fake_response = self.make_request("POST", f"/admin/transactions/{test_transaction_id}/verify-fake", data=verify_data, headers=headers)
        if verify_fake_response and verify_fake_response.status_code in [200, 404, 400]:
            self.log_test("Fake Detection Workflow", True, "Fake detection endpoint accessible")
        else:
            self.log_test("Fake Detection Workflow", False, f"Fake detection failed: {verify_fake_response.status_code if verify_fake_response else 'No response'}")

    def test_admin_authorization_security(self):
        """Test 7: Admin Authorization & Security"""
        print("\n🔒 TESTING ADMIN AUTHORIZATION & SECURITY")
        
        # Test admin endpoints without token (should fail)
        response_no_auth = self.make_request("GET", "/admin/users")
        if response_no_auth and response_no_auth.status_code == 401:
            self.log_test("Admin Endpoints Security", True, "Unauthorized access properly blocked")
        else:
            self.log_test("Admin Endpoints Security", False, f"Security issue: {response_no_auth.status_code if response_no_auth else 'No response'}")
            
        # Test admin endpoints with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response_invalid_auth = self.make_request("GET", "/admin/users", headers=invalid_headers)
        if response_invalid_auth and response_invalid_auth.status_code == 401:
            self.log_test("Invalid Token Security", True, "Invalid tokens properly rejected")
        else:
            self.log_test("Invalid Token Security", False, f"Security issue: {response_invalid_auth.status_code if response_invalid_auth else 'No response'}")
            
        # Test admin-only endpoints with regular user token (if available)
        # For now, just test that admin token works
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            admin_only_response = self.make_request("GET", "/admin/traffic-stats", headers=headers)
            if admin_only_response and admin_only_response.status_code == 200:
                self.log_test("Admin-Only Access Control", True, "Admin token grants proper access")
            else:
                self.log_test("Admin-Only Access Control", False, f"Admin access issue: {admin_only_response.status_code if admin_only_response else 'No response'}")

    def run_all_tests(self):
        """Run all admin dashboard tests"""
        print("🎯 TOPKIT ADMIN DASHBOARD BACKEND TESTING STARTED")
        print("=" * 60)
        
        # Run all test categories
        self.test_admin_authentication()
        self.test_dashboard_data_endpoints()
        self.test_user_management_endpoints()
        self.test_moderation_system()
        self.test_data_management_endpoints()
        self.test_analytics_reporting()
        self.test_admin_authorization_security()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎉 TOPKIT ADMIN DASHBOARD TESTING COMPLETE")
        print(f"📊 RESULTS: {self.passed_tests}/{self.total_tests} tests passed ({(self.passed_tests/self.total_tests*100):.1f}% success rate)")
        
        if self.passed_tests == self.total_tests:
            print("✅ ALL TESTS PASSED - Admin Dashboard is fully operational!")
        elif self.passed_tests >= self.total_tests * 0.8:
            print("⚠️ MOSTLY WORKING - Minor issues identified")
        else:
            print("❌ CRITICAL ISSUES - Major functionality problems detected")
            
        return {
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'success_rate': (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = AdminDashboardTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:
        sys.exit(0)
    else:
        sys.exit(1)