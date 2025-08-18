#!/usr/bin/env python3
"""
TopKit Backend Testing - Review Request Focus Areas
Testing authentication, jersey submission, admin panel, database connectivity, and API health
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-vault-2.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "review.test.user@topkit.com", 
    "password": "ReviewTestPass2024!"
}

class TopKitBackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()

    def test_api_health(self):
        """Test basic API connectivity and health"""
        print("🔍 TESTING API HEALTH CHECK...")
        
        try:
            # Test basic connectivity
            response = self.session.get(f"{BACKEND_URL}/jerseys", timeout=10)
            if response.status_code == 200:
                jerseys = response.json()
                self.log_test(
                    "API Health - Basic Connectivity",
                    True,
                    f"API responding correctly, found {len(jerseys)} jerseys"
                )
            else:
                self.log_test(
                    "API Health - Basic Connectivity", 
                    False,
                    f"API returned status {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "API Health - Basic Connectivity",
                False,
                error=str(e)
            )

    def test_authentication_system(self):
        """Test authentication system with both admin and user credentials"""
        print("🔐 TESTING AUTHENTICATION SYSTEM...")
        
        # Test Admin Authentication
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.admin_token = data['token']
                    user_info = data['user']
                    self.log_test(
                        "Authentication - Admin Login",
                        True,
                        f"Admin authenticated successfully: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')})"
                    )
                else:
                    self.log_test(
                        "Authentication - Admin Login",
                        False,
                        "Missing token or user data in response"
                    )
            else:
                self.log_test(
                    "Authentication - Admin Login",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Authentication - Admin Login",
                False,
                error=str(e)
            )

        # Test User Authentication
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=USER_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data and 'user' in data:
                    self.user_token = data['token']
                    user_info = data['user']
                    self.log_test(
                        "Authentication - User Login",
                        True,
                        f"User authenticated successfully: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')})"
                    )
                else:
                    self.log_test(
                        "Authentication - User Login",
                        False,
                        "Missing token or user data in response"
                    )
            else:
                self.log_test(
                    "Authentication - User Login",
                    False,
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Authentication - User Login",
                False,
                error=str(e)
            )

        # Test JWT Token Validation
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = self.session.get(f"{BACKEND_URL}/profile", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    self.log_test(
                        "Authentication - JWT Token Validation (Admin)",
                        True,
                        f"Admin profile accessible: {profile_data.get('name', 'Unknown')}"
                    )
                else:
                    self.log_test(
                        "Authentication - JWT Token Validation (Admin)",
                        False,
                        f"Profile access failed with status {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    "Authentication - JWT Token Validation (Admin)",
                    False,
                    error=str(e)
                )

        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BACKEND_URL}/profile", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    self.log_test(
                        "Authentication - JWT Token Validation (User)",
                        True,
                        f"User profile accessible: {profile_data.get('name', 'Unknown')}"
                    )
                else:
                    self.log_test(
                        "Authentication - JWT Token Validation (User)",
                        False,
                        f"Profile access failed with status {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    "Authentication - JWT Token Validation (User)",
                    False,
                    error=str(e)
                )

    def test_jersey_submission_system(self):
        """Test jersey submission functionality for authenticated users"""
        print("⚽ TESTING JERSEY SUBMISSION SYSTEM...")
        
        if not self.user_token:
            self.log_test(
                "Jersey Submission - User Authentication Required",
                False,
                "Cannot test jersey submission without user authentication"
            )
            return

        # Test jersey submission with realistic data
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Real Madrid home jersey 2024-25 season with Vinicius Jr name and number"
        }

        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                jersey_response = response.json()
                jersey_id = jersey_response.get('id')
                jersey_ref = jersey_response.get('reference_number')
                jersey_status = jersey_response.get('status')
                
                self.log_test(
                    "Jersey Submission - Create Jersey",
                    True,
                    f"Jersey created successfully (ID: {jersey_id}, Status: {jersey_status}, Ref: {jersey_ref})"
                )
                
                # Test user's jersey submissions retrieval
                try:
                    response = self.session.get(
                        f"{BACKEND_URL}/collections/pending",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        submissions = response.json()
                        self.log_test(
                            "Jersey Submission - User Submissions List",
                            True,
                            f"User has {len(submissions)} total submissions"
                        )
                    else:
                        self.log_test(
                            "Jersey Submission - User Submissions List",
                            False,
                            f"Failed to retrieve submissions: {response.status_code}"
                        )
                except Exception as e:
                    self.log_test(
                        "Jersey Submission - User Submissions List",
                        False,
                        error=str(e)
                    )
                    
            else:
                self.log_test(
                    "Jersey Submission - Create Jersey",
                    False,
                    f"Jersey submission failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test(
                "Jersey Submission - Create Jersey",
                False,
                error=str(e)
            )

        # Test jersey submission validation
        invalid_jersey_data = {
            "team": "",  # Empty team should fail validation
            "season": "2024-25"
        }

        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=invalid_jersey_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 422:
                self.log_test(
                    "Jersey Submission - Data Validation",
                    True,
                    "Invalid jersey data correctly rejected with HTTP 422"
                )
            else:
                self.log_test(
                    "Jersey Submission - Data Validation",
                    False,
                    f"Expected HTTP 422 for invalid data, got {response.status_code}"
                )
                
        except Exception as e:
            self.log_test(
                "Jersey Submission - Data Validation",
                False,
                error=str(e)
            )

    def test_admin_panel_access(self):
        """Test admin panel endpoints and functionality"""
        print("👑 TESTING ADMIN PANEL ACCESS...")
        
        if not self.admin_token:
            self.log_test(
                "Admin Panel - Admin Authentication Required",
                False,
                "Cannot test admin panel without admin authentication"
            )
            return

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Test admin users endpoint
        try:
            response = self.session.get(
                f"{BACKEND_URL}/admin/users",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users_data = response.json()
                self.log_test(
                    "Admin Panel - Users Management",
                    True,
                    f"Admin can access users list: {len(users_data)} users found"
                )
            else:
                self.log_test(
                    "Admin Panel - Users Management",
                    False,
                    f"Admin users access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Admin Panel - Users Management",
                False,
                error=str(e)
            )

        # Test admin traffic stats
        try:
            response = self.session.get(
                f"{BACKEND_URL}/admin/traffic-stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                stats_data = response.json()
                self.log_test(
                    "Admin Panel - Traffic Statistics",
                    True,
                    f"Admin can access traffic stats: {len(stats_data)} metrics available"
                )
            else:
                self.log_test(
                    "Admin Panel - Traffic Statistics",
                    False,
                    f"Admin traffic stats access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Admin Panel - Traffic Statistics",
                False,
                error=str(e)
            )

        # Test admin pending jerseys
        try:
            response = self.session.get(
                f"{BACKEND_URL}/admin/jerseys/pending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                self.log_test(
                    "Admin Panel - Pending Jerseys",
                    True,
                    f"Admin can access pending jerseys: {len(pending_jerseys)} pending"
                )
            else:
                self.log_test(
                    "Admin Panel - Pending Jerseys",
                    False,
                    f"Admin pending jerseys access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Admin Panel - Pending Jerseys",
                False,
                error=str(e)
            )

        # Test admin activities
        try:
            response = self.session.get(
                f"{BACKEND_URL}/admin/activities",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                activities_data = response.json()
                self.log_test(
                    "Admin Panel - Activities Log",
                    True,
                    f"Admin can access activities: {len(activities_data)} activities found"
                )
            else:
                self.log_test(
                    "Admin Panel - Activities Log",
                    False,
                    f"Admin activities access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Admin Panel - Activities Log",
                False,
                error=str(e)
            )

        # Test admin beta requests
        try:
            response = self.session.get(
                f"{BACKEND_URL}/admin/beta/requests",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                beta_requests = response.json()
                self.log_test(
                    "Admin Panel - Beta Requests",
                    True,
                    f"Admin can access beta requests: {len(beta_requests)} requests found"
                )
            else:
                self.log_test(
                    "Admin Panel - Beta Requests",
                    False,
                    f"Admin beta requests access failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Admin Panel - Beta Requests",
                False,
                error=str(e)
            )

        # Test non-admin user cannot access admin endpoints
        if self.user_token:
            try:
                user_headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(
                    f"{BACKEND_URL}/admin/users",
                    headers=user_headers,
                    timeout=10
                )
                
                if response.status_code == 403:
                    self.log_test(
                        "Admin Panel - Access Control",
                        True,
                        "Regular users correctly denied admin access (HTTP 403)"
                    )
                else:
                    self.log_test(
                        "Admin Panel - Access Control",
                        False,
                        f"Expected HTTP 403 for non-admin, got {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    "Admin Panel - Access Control",
                    False,
                    error=str(e)
                )

    def test_database_connectivity(self):
        """Test database connectivity and data persistence"""
        print("🗄️ TESTING DATABASE CONNECTIVITY...")
        
        # Test jersey data retrieval (indicates database connectivity)
        try:
            response = self.session.get(f"{BACKEND_URL}/jerseys", timeout=10)
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_test(
                    "Database - Jersey Data Retrieval",
                    True,
                    f"Database connected, retrieved {len(jerseys)} jerseys"
                )
            else:
                self.log_test(
                    "Database - Jersey Data Retrieval",
                    False,
                    f"Jersey retrieval failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Database - Jersey Data Retrieval",
                False,
                error=str(e)
            )

        # Test marketplace catalog (another database operation)
        try:
            response = self.session.get(f"{BACKEND_URL}/marketplace/catalog", timeout=10)
            
            if response.status_code == 200:
                catalog = response.json()
                self.log_test(
                    "Database - Marketplace Catalog",
                    True,
                    f"Marketplace catalog accessible: {len(catalog)} items"
                )
            else:
                self.log_test(
                    "Database - Marketplace Catalog",
                    False,
                    f"Marketplace catalog failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Database - Marketplace Catalog",
                False,
                error=str(e)
            )

        # Test explorer leagues (database query)
        try:
            response = self.session.get(f"{BACKEND_URL}/explorer/leagues", timeout=10)
            
            if response.status_code == 200:
                leagues = response.json()
                self.log_test(
                    "Database - Explorer Leagues",
                    True,
                    f"Explorer leagues accessible: {len(leagues)} leagues"
                )
            else:
                self.log_test(
                    "Database - Explorer Leagues",
                    False,
                    f"Explorer leagues failed: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "Database - Explorer Leagues",
                False,
                error=str(e)
            )

        # Test user profile data (authenticated database operation)
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BACKEND_URL}/profile", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    profile = response.json()
                    self.log_test(
                        "Database - User Profile Data",
                        True,
                        f"User profile data accessible: {profile.get('name', 'Unknown')}"
                    )
                else:
                    self.log_test(
                        "Database - User Profile Data",
                        False,
                        f"User profile failed: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    "Database - User Profile Data",
                    False,
                    error=str(e)
                )

    def test_core_endpoints(self):
        """Test all core API endpoints for basic functionality"""
        print("🌐 TESTING CORE ENDPOINTS...")
        
        core_endpoints = [
            ("/jerseys", "GET", "Jersey Catalog"),
            ("/marketplace/catalog", "GET", "Marketplace Catalog"),
            ("/explorer/leagues", "GET", "Explorer Leagues"),
            ("/site/mode", "GET", "Site Configuration"),
        ]

        for endpoint, method, description in core_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Core Endpoints - {description}",
                        True,
                        f"{description} endpoint operational"
                    )
                else:
                    self.log_test(
                        f"Core Endpoints - {description}",
                        False,
                        f"{description} returned status {response.status_code}"
                    )
            except Exception as e:
                self.log_test(
                    f"Core Endpoints - {description}",
                    False,
                    error=str(e)
                )

        # Test authenticated endpoints
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            auth_endpoints = [
                ("/profile", "GET", "User Profile"),
                ("/notifications", "GET", "User Notifications"),
                ("/friends", "GET", "User Friends"),
            ]

            for endpoint, method, description in auth_endpoints:
                try:
                    if method == "GET":
                        response = self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        self.log_test(
                            f"Core Endpoints - {description} (Authenticated)",
                            True,
                            f"{description} endpoint operational"
                        )
                    else:
                        self.log_test(
                            f"Core Endpoints - {description} (Authenticated)",
                            False,
                            f"{description} returned status {response.status_code}"
                        )
                except Exception as e:
                    self.log_test(
                        f"Core Endpoints - {description} (Authenticated)",
                        False,
                        error=str(e)
                    )

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 STARTING TOPKIT BACKEND TESTING - REVIEW REQUEST FOCUS AREAS")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        print()

        # Run all test categories
        self.test_api_health()
        self.test_authentication_system()
        self.test_jersey_submission_system()
        self.test_admin_panel_access()
        self.test_database_connectivity()
        self.test_core_endpoints()

        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"  - {test['test']}")
                    if test['error']:
                        print(f"    Error: {test['error']}")
            print()
        
        # Categorize results by focus area
        focus_areas = {
            "Authentication System": [t for t in self.test_results if "Authentication" in t['test']],
            "Jersey Submission System": [t for t in self.test_results if "Jersey Submission" in t['test']],
            "Admin Panel Access": [t for t in self.test_results if "Admin Panel" in t['test']],
            "Database Connectivity": [t for t in self.test_results if "Database" in t['test']],
            "API Health Check": [t for t in self.test_results if "API Health" in t['test'] or "Core Endpoints" in t['test']]
        }
        
        print("🎯 FOCUS AREA RESULTS:")
        for area, tests in focus_areas.items():
            if tests:
                area_passed = len([t for t in tests if t['success']])
                area_total = len(tests)
                area_rate = (area_passed / area_total * 100) if area_total > 0 else 0
                status = "✅" if area_rate == 100 else "⚠️" if area_rate >= 50 else "❌"
                print(f"  {status} {area}: {area_passed}/{area_total} ({area_rate:.1f}%)")
        
        print()
        print("🏁 TESTING COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    tester = TopKitBackendTester()
    tester.run_all_tests()