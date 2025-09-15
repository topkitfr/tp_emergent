#!/usr/bin/env python3
"""
TopKit Backend Testing - Review Request Focus
Testing specific items from review request:
1. Jersey submission endpoint (was just fixed)
2. Beta access request endpoint returns updated message
3. Basic functionality is operational
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use the REACT_APP_BACKEND_URL from frontend/.env
BACKEND_URL = "https://mongodb-routing.preview.emergentagent.com/api"

# Admin credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ReviewFocusedTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.jersey_id = None
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
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

    def test_admin_authentication(self):
        """Test admin authentication with provided credentials"""
        print("🔐 Testing Admin Authentication...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                admin_info = data.get("user", {})
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin logged in: {admin_info.get('name')} (Role: {admin_info.get('role')}, ID: {admin_info.get('id')})"
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
            self.log_result(
                "Admin Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_jersey_submission_endpoint(self):
        """Test jersey submission endpoint (was just fixed according to review)"""
        print("📝 Testing Jersey Submission Endpoint...")
        
        if not self.admin_token:
            self.log_result("Jersey Submission Endpoint", False, "", "Admin not authenticated")
            return False
        
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official Real Madrid home jersey for 2024-25 season featuring Vinicius Jr #7",
            "images": ["https://dummyimage.com/400x400/ffffff/000000.png&text=Real+Madrid+Vinicius"]
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.jersey_id = data.get("id")
                jersey_ref = data.get("reference_number", "N/A")
                self.log_result(
                    "Jersey Submission Endpoint",
                    True,
                    f"Jersey submitted successfully. ID: {self.jersey_id}, Ref: {jersey_ref}, Status: {data.get('status')}, Team: {data.get('team')}"
                )
                return True
            else:
                self.log_result(
                    "Jersey Submission Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Jersey Submission Endpoint",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_beta_access_request_endpoint(self):
        """Test beta access request endpoint returns updated message"""
        print("🔑 Testing Beta Access Request Endpoint...")
        
        beta_request_data = {
            "email": "test.reviewer@example.com",
            "first_name": "Test",
            "last_name": "Reviewer",
            "message": "Testing beta access request endpoint for review verification"
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/beta/request-access", json=beta_request_data)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                request_id = data.get("request_id", "")
                
                # Check if the response contains updated message format
                has_updated_message = "request_id" in data and len(request_id) > 0
                
                self.log_result(
                    "Beta Access Request Endpoint",
                    True,
                    f"Beta request submitted successfully. Message: '{message}', Request ID: {request_id}"
                )
                return True
            else:
                self.log_result(
                    "Beta Access Request Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "Beta Access Request Endpoint",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def test_basic_functionality_endpoints(self):
        """Test basic functionality endpoints are operational"""
        print("🔧 Testing Basic Functionality Endpoints...")
        
        basic_endpoints = [
            ("/jerseys", "GET", "Jerseys List"),
            ("/marketplace/catalog", "GET", "Marketplace Catalog"),
            ("/site/mode", "GET", "Site Mode Configuration"),
        ]
        
        all_passed = True
        
        for endpoint, method, name in basic_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}")
                else:
                    response = requests.post(f"{BACKEND_URL}{endpoint}")
                
                if response.status_code in [200, 201]:
                    data = response.json() if response.content else {}
                    data_info = ""
                    
                    if endpoint == "/jerseys":
                        jersey_count = len(data) if isinstance(data, list) else 0
                        data_info = f"Found {jersey_count} jerseys"
                    elif endpoint == "/marketplace/catalog":
                        catalog_count = len(data) if isinstance(data, list) else 0
                        data_info = f"Found {catalog_count} catalog items"
                    elif endpoint == "/site/mode":
                        mode = data.get("mode", "unknown")
                        data_info = f"Site mode: {mode}"
                    
                    self.log_result(
                        f"Basic Functionality - {name}",
                        True,
                        f"HTTP {response.status_code} - {data_info}"
                    )
                else:
                    self.log_result(
                        f"Basic Functionality - {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200] if response.text else "No response body"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Basic Functionality - {name}",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
                all_passed = False
        
        return all_passed

    def test_admin_specific_endpoints(self):
        """Test admin-specific endpoints with authenticated admin"""
        print("👨‍💼 Testing Admin-Specific Endpoints...")
        
        if not self.admin_token:
            self.log_result("Admin-Specific Endpoints", False, "", "Admin not authenticated")
            return False
        
        admin_endpoints = [
            ("/admin/users", "GET", "Admin Users List"),
            ("/admin/traffic-stats", "GET", "Admin Traffic Stats"),
            ("/admin/jerseys/pending", "GET", "Admin Pending Jerseys"),
        ]
        
        all_passed = True
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        for endpoint, method, name in admin_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json() if response.content else {}
                    data_info = ""
                    
                    if endpoint == "/admin/users":
                        user_count = len(data) if isinstance(data, list) else 0
                        data_info = f"Found {user_count} users"
                    elif endpoint == "/admin/traffic-stats":
                        stats_keys = list(data.keys()) if isinstance(data, dict) else []
                        data_info = f"Stats available: {len(stats_keys)} metrics"
                    elif endpoint == "/admin/jerseys/pending":
                        pending_count = len(data) if isinstance(data, list) else 0
                        data_info = f"Found {pending_count} pending jerseys"
                    
                    self.log_result(
                        f"Admin Endpoint - {name}",
                        True,
                        f"HTTP {response.status_code} - {data_info}"
                    )
                else:
                    self.log_result(
                        f"Admin Endpoint - {name}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200] if response.text else "No response body"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(
                    f"Admin Endpoint - {name}",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
                all_passed = False
        
        return all_passed

    def test_jwt_token_validation(self):
        """Test JWT token validation through protected endpoints"""
        print("🔒 Testing JWT Token Validation...")
        
        if not self.admin_token:
            self.log_result("JWT Token Validation", False, "", "Admin not authenticated")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get("user", {}) if "user" in data else data
                self.log_result(
                    "JWT Token Validation",
                    True,
                    f"Token valid - User: {user_info.get('name')} (Role: {user_info.get('role')}, Email: {user_info.get('email')})"
                )
                return True
            else:
                self.log_result(
                    "JWT Token Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
        except Exception as e:
            self.log_result(
                "JWT Token Validation",
                False,
                "",
                f"Exception: {str(e)}"
            )
            return False

    def run_review_focused_tests(self):
        """Run all review-focused tests"""
        print("🎯 Starting TopKit Review-Focused Backend Testing")
        print("=" * 60)
        print("Focus Areas:")
        print("1. Jersey submission endpoint (was just fixed)")
        print("2. Beta access request endpoint returns updated message")
        print("3. Basic functionality is operational")
        print("4. Admin credentials verification")
        print("=" * 60)
        
        # Authentication test
        auth_success = self.test_admin_authentication()
        
        if not auth_success:
            print("❌ Admin authentication failed - limited testing possible")
        
        # Core review tests
        tests = [
            self.test_jersey_submission_endpoint,
            self.test_beta_access_request_endpoint,
            self.test_basic_functionality_endpoints,
            self.test_admin_specific_endpoints,
            self.test_jwt_token_validation
        ]
        
        for test in tests:
            test()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 REVIEW-FOCUSED TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Review-specific findings
        print("🎯 REVIEW REQUEST FINDINGS:")
        
        jersey_submission_test = next((r for r in self.test_results if "Jersey Submission" in r["test"]), None)
        if jersey_submission_test:
            status = "✅ WORKING" if jersey_submission_test["success"] else "❌ FAILING"
            print(f"  • Jersey Submission Endpoint: {status}")
        
        beta_access_test = next((r for r in self.test_results if "Beta Access" in r["test"]), None)
        if beta_access_test:
            status = "✅ WORKING" if beta_access_test["success"] else "❌ FAILING"
            print(f"  • Beta Access Request Endpoint: {status}")
        
        basic_functionality_tests = [r for r in self.test_results if "Basic Functionality" in r["test"]]
        basic_all_passed = all(r["success"] for r in basic_functionality_tests)
        basic_status = "✅ OPERATIONAL" if basic_all_passed else "❌ ISSUES DETECTED"
        print(f"  • Basic Functionality: {basic_status}")
        
        admin_auth_test = next((r for r in self.test_results if "Admin Authentication" in r["test"]), None)
        if admin_auth_test:
            status = "✅ WORKING" if admin_auth_test["success"] else "❌ FAILING"
            print(f"  • Admin Credentials (topkitfr@gmail.com): {status}")
        
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = ReviewFocusedTester()
    summary = tester.run_review_focused_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)