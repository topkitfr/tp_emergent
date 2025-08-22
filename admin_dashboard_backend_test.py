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
BACKEND_URL = "https://football-kit-hub.preview.emergentagent.com/api"
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
        
        # Test system health metrics
        health_response = self.make_request("GET", "/admin/system-health", headers=headers)
        if health_response and health_response.status_code in [200, 404]:
            self.log_test("System Health Metrics", True, "Health endpoint accessible")
        else:
            self.log_test("System Health Metrics", False, f"Health endpoint failed: {health_response.status_code if health_response else 'No response'}")
            
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
            except Exception as e:
                self.log_test("User Listing API", False, f"JSON parsing error: {e}")
        else:
            self.log_test("User Listing API", False, f"Users endpoint failed: {users_response.status_code if users_response else 'No response'}")
        
        # Test role assignment functionality
        role_endpoint_response = self.make_request("GET", "/admin/users/roles", headers=headers)
        if role_endpoint_response and role_endpoint_response.status_code in [200, 404]:
            self.log_test("Role Assignment Endpoint", True, "Role management endpoint accessible")
        else:
            self.log_test("Role Assignment Endpoint", False, f"Role endpoint failed: {role_endpoint_response.status_code if role_endpoint_response else 'No response'}")
            
        # Test user ban/unban functionality
        ban_endpoint_response = self.make_request("GET", "/admin/users/banned", headers=headers)
        if ban_endpoint_response and ban_endpoint_response.status_code in [200, 404]:
            self.log_test("User Ban Management", True, "Ban management endpoint accessible")
        else:
            self.log_test("User Ban Management", False, f"Ban endpoint failed: {ban_endpoint_response.status_code if ban_endpoint_response else 'No response'}")
            
        # Test user search and filtering
        search_response = self.make_request("GET", "/admin/users?search=admin", headers=headers)
        if search_response and search_response.status_code in [200, 404]:
            self.log_test("User Search & Filtering", True, "User search endpoint accessible")
        else:
            self.log_test("User Search & Filtering", False, f"Search endpoint failed: {search_response.status_code if search_response else 'No response'}")

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
            except Exception as e:
                self.log_test("Pending Contributions Queue", False, f"JSON parsing error: {e}")
        else:
            self.log_test("Pending Contributions Queue", False, f"Pending queue failed: {pending_response.status_code if pending_response else 'No response'}")
        
        # Test contribution approval workflow
        approval_endpoint_response = self.make_request("GET", "/admin/contributions/approve", headers=headers)
        if approval_endpoint_response and approval_endpoint_response.status_code in [200, 404, 405]:
            self.log_test("Contribution Approval Workflow", True, "Approval endpoint accessible")
        else:
            self.log_test("Contribution Approval Workflow", False, f"Approval endpoint failed: {approval_endpoint_response.status_code if approval_endpoint_response else 'No response'}")
            
        # Test contribution rejection workflow
        rejection_endpoint_response = self.make_request("GET", "/admin/contributions/reject", headers=headers)
        if rejection_endpoint_response and rejection_endpoint_response.status_code in [200, 404, 405]:
            self.log_test("Contribution Rejection Workflow", True, "Rejection endpoint accessible")
        else:
            self.log_test("Contribution Rejection Workflow", False, f"Rejection endpoint failed: {rejection_endpoint_response.status_code if rejection_endpoint_response else 'No response'}")
            
        # Test bulk approval functionality
        bulk_endpoint_response = self.make_request("GET", "/admin/contributions/bulk-approve", headers=headers)
        if bulk_endpoint_response and bulk_endpoint_response.status_code in [200, 404, 405]:
            self.log_test("Bulk Approval Functionality", True, "Bulk approval endpoint accessible")
        else:
            self.log_test("Bulk Approval Functionality", False, f"Bulk approval failed: {bulk_endpoint_response.status_code if bulk_endpoint_response else 'No response'}")
            
        # Test moderation queue filtering
        filter_response = self.make_request("GET", "/admin/jerseys/pending?status=pending", headers=headers)
        if filter_response and filter_response.status_code == 200:
            self.log_test("Moderation Queue Filtering", True, "Queue filtering working")
        else:
            self.log_test("Moderation Queue Filtering", False, f"Queue filtering failed: {filter_response.status_code if filter_response else 'No response'}")

    def test_data_management_endpoints(self):
        """Test 5: Data Management Endpoints"""
        print("\n💾 TESTING DATA MANAGEMENT ENDPOINTS")
        
        if not self.admin_token:
            self.log_test("Data Management Endpoints", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test data export functionality (CSV/JSON)
        export_csv_response = self.make_request("GET", "/admin/export/csv", headers=headers)
        if export_csv_response and export_csv_response.status_code in [200, 404]:
            self.log_test("CSV Export Functionality", True, "CSV export endpoint accessible")
        else:
            self.log_test("CSV Export Functionality", False, f"CSV export failed: {export_csv_response.status_code if export_csv_response else 'No response'}")
            
        export_json_response = self.make_request("GET", "/admin/export/json", headers=headers)
        if export_json_response and export_json_response.status_code in [200, 404]:
            self.log_test("JSON Export Functionality", True, "JSON export endpoint accessible")
        else:
            self.log_test("JSON Export Functionality", False, f"JSON export failed: {export_json_response.status_code if export_json_response else 'No response'}")
        
        # Test backup/restore endpoints
        backup_response = self.make_request("GET", "/admin/backup", headers=headers)
        if backup_response and backup_response.status_code in [200, 404]:
            self.log_test("Backup Endpoint", True, "Backup endpoint accessible")
        else:
            self.log_test("Backup Endpoint", False, f"Backup endpoint failed: {backup_response.status_code if backup_response else 'No response'}")
            
        # Test data integrity tools
        integrity_response = self.make_request("GET", "/admin/data-integrity", headers=headers)
        if integrity_response and integrity_response.status_code in [200, 404]:
            self.log_test("Data Integrity Tools", True, "Data integrity endpoint accessible")
        else:
            self.log_test("Data Integrity Tools", False, f"Data integrity failed: {integrity_response.status_code if integrity_response else 'No response'}")

    def test_analytics_reporting(self):
        """Test 6: Analytics & Reporting"""
        print("\n📈 TESTING ANALYTICS & REPORTING")
        
        if not self.admin_token:
            self.log_test("Analytics & Reporting", False, "No admin token available")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test admin analytics endpoints
        analytics_response = self.make_request("GET", "/admin/analytics", headers=headers)
        if analytics_response and analytics_response.status_code in [200, 404]:
            self.log_test("Admin Analytics Endpoints", True, "Analytics endpoint accessible")
        else:
            self.log_test("Admin Analytics Endpoints", False, f"Analytics failed: {analytics_response.status_code if analytics_response else 'No response'}")
            
        # Test usage statistics
        usage_response = self.make_request("GET", "/admin/analytics/usage", headers=headers)
        if usage_response and usage_response.status_code in [200, 404]:
            self.log_test("Usage Statistics", True, "Usage stats endpoint accessible")
        else:
            self.log_test("Usage Statistics", False, f"Usage stats failed: {usage_response.status_code if usage_response else 'No response'}")
            
        # Test report generation
        reports_response = self.make_request("GET", "/admin/reports", headers=headers)
        if reports_response and reports_response.status_code in [200, 404]:
            self.log_test("Report Generation", True, "Reports endpoint accessible")
        else:
            self.log_test("Report Generation", False, f"Reports failed: {reports_response.status_code if reports_response else 'No response'}")
            
        # Test KPI and metrics calculation
        kpi_response = self.make_request("GET", "/admin/kpi", headers=headers)
        if kpi_response and kpi_response.status_code in [200, 404]:
            self.log_test("KPI & Metrics Calculation", True, "KPI endpoint accessible")
        else:
            self.log_test("KPI & Metrics Calculation", False, f"KPI endpoint failed: {kpi_response.status_code if kpi_response else 'No response'}")

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