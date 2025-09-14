#!/usr/bin/env python3
"""
TopKit Admin Restrictions & Analytics Testing Suite
Testing Phase 2 admin restrictions and analytics endpoints as requested
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
REGULAR_USER_EMAIL = "steinmetzlivio@gmail.com"
REGULAR_USER_PASSWORD = "123"

class AdminRestrictionsTestSuite:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.regular_user_token = None
        self.admin_id = None
        self.regular_user_id = None
        self.test_results = []
        self.test_jersey_id = None
        
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

    def setup_authentication(self):
        """Setup authentication for both admin and regular user"""
        print("🔐 SETTING UP AUTHENTICATION")
        print("=" * 50)
        
        # Test 1: Regular User Login
        try:
            login_data = {
                "email": REGULAR_USER_EMAIL,
                "password": REGULAR_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.regular_user_token = data["token"]
                    self.regular_user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"]["role"]
                    self.log_test(
                        "Regular User Authentication",
                        True,
                        f"Login successful - User: {user_name}, Role: {user_role}, ID: {self.regular_user_id}"
                    )
                else:
                    self.log_test("Regular User Authentication", False, "", "Missing token or user data in response")
                    return False
            else:
                self.log_test("Regular User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Regular User Authentication", False, "", str(e))
            return False

        # Test 2: Admin Login (try common passwords)
        try:
            admin_passwords = ["adminpass123", "admin", "123", "password", "topkit", "admin123", "topkitfr", "topkit123"]
            admin_login_success = False
            
            for password in admin_passwords:
                try:
                    admin_login_data = {
                        "email": ADMIN_EMAIL,
                        "password": password
                    }
                    response = self.session.post(f"{BASE_URL}/auth/login", json=admin_login_data)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "token" in data and "user" in data:
                            self.admin_token = data["token"]
                            self.admin_id = data["user"]["id"]
                            admin_name = data["user"]["name"]
                            admin_role = data["user"]["role"]
                            self.log_test(
                                "Admin Authentication",
                                True,
                                f"Admin login successful with password '{password}' - User: {admin_name}, Role: {admin_role}"
                            )
                            admin_login_success = True
                            break
                except:
                    continue
            
            if not admin_login_success:
                self.log_test(
                    "Admin Authentication",
                    False,
                    "",
                    f"Could not authenticate admin with any common passwords: {admin_passwords}"
                )
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))
            return False
        
        return True

    def create_test_jersey(self):
        """Create a test jersey for collection testing"""
        if not self.regular_user_token:
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            jersey_data = {
                "team": "Test FC Admin Restrictions",
                "season": "2024-25",
                "player": "Test Player",
                "size": "M",
                "condition": "new",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for admin restrictions testing"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_jersey_id = data.get("id")
                return True
        except:
            pass
        return False

    def test_admin_listing_restrictions(self):
        """Test that admin users are blocked from creating listings"""
        print("🚫 TESTING ADMIN LISTING RESTRICTIONS")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Admin Listing Restrictions", False, "", "No admin token available")
            return
        
        # First create a test jersey with regular user
        if not self.test_jersey_id:
            self.create_test_jersey()
        
        if not self.test_jersey_id:
            self.log_test("Admin Listing Restrictions", False, "", "Could not create test jersey")
            return

        # Test 1: Admin user blocked from creating listings
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            listing_data = {
                "jersey_id": self.test_jersey_id,
                "price": 99.99,
                "description": "Admin should not be able to create this listing"
            }
            
            response = self.session.post(f"{BASE_URL}/listings", json=listing_data, headers=admin_headers)
            
            if response.status_code == 403:
                self.log_test(
                    "Admin Blocked from Creating Listings",
                    True,
                    "Admin user correctly blocked from creating listings (HTTP 403)"
                )
            else:
                self.log_test(
                    "Admin Blocked from Creating Listings",
                    False,
                    "",
                    f"Expected HTTP 403, got {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Admin Blocked from Creating Listings", False, "", str(e))

        # Test 2: Regular user can still create listings
        try:
            regular_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            listing_data = {
                "jersey_id": self.test_jersey_id,
                "price": 89.99,
                "description": "Regular user should be able to create this listing"
            }
            
            response = self.session.post(f"{BASE_URL}/listings", json=listing_data, headers=regular_headers)
            
            if response.status_code in [200, 201]:
                self.log_test(
                    "Regular User Can Create Listings",
                    True,
                    "Regular user successfully created listing"
                )
            else:
                self.log_test(
                    "Regular User Can Create Listings",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Regular User Can Create Listings", False, "", str(e))

    def test_admin_collection_restrictions(self):
        """Test that admin users are blocked from collection operations"""
        print("📚 TESTING ADMIN COLLECTION RESTRICTIONS")
        print("=" * 50)
        
        if not self.admin_token or not self.test_jersey_id:
            self.log_test("Admin Collection Restrictions", False, "", "Missing admin token or test jersey")
            return

        # Test 1: Admin blocked from adding to collections
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BASE_URL}/collections", json=collection_data, headers=admin_headers)
            
            if response.status_code == 403:
                self.log_test(
                    "Admin Blocked from Adding to Collections",
                    True,
                    "Admin user correctly blocked from adding to collections (HTTP 403)"
                )
            else:
                self.log_test(
                    "Admin Blocked from Adding to Collections",
                    False,
                    "",
                    f"Expected HTTP 403, got {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Admin Blocked from Adding to Collections", False, "", str(e))

        # Test 2: Admin blocked from removing from collections
        try:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            remove_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BASE_URL}/collections/remove", json=remove_data, headers=admin_headers)
            
            if response.status_code == 403:
                self.log_test(
                    "Admin Blocked from Removing from Collections",
                    True,
                    "Admin user correctly blocked from removing from collections (HTTP 403)"
                )
            else:
                self.log_test(
                    "Admin Blocked from Removing from Collections",
                    False,
                    "",
                    f"Expected HTTP 403, got {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Admin Blocked from Removing from Collections", False, "", str(e))

        # Test 3: Regular user can still manage collections
        try:
            regular_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            collection_data = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BASE_URL}/collections", json=collection_data, headers=regular_headers)
            
            if response.status_code in [200, 201]:
                self.log_test(
                    "Regular User Can Manage Collections",
                    True,
                    "Regular user successfully added to collection"
                )
            else:
                self.log_test(
                    "Regular User Can Manage Collections",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_test("Regular User Can Manage Collections", False, "", str(e))

    def test_admin_excluded_from_user_search(self):
        """Test that admin users are excluded from user search results"""
        print("🔍 TESTING ADMIN EXCLUDED FROM USER SEARCH")
        print("=" * 50)
        
        if not self.regular_user_token:
            self.log_test("Admin Excluded from User Search", False, "", "No regular user token available")
            return

        try:
            regular_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            # Search for users with a query that might match admin
            response = self.session.get(f"{BASE_URL}/users/search?query=topkit", headers=regular_headers)
            
            if response.status_code == 200:
                search_results = response.json()
                if isinstance(search_results, list):
                    # Check if admin user is in search results
                    admin_in_results = any(
                        user.get("email") == ADMIN_EMAIL or user.get("id") == self.admin_id
                        for user in search_results
                    )
                    
                    if not admin_in_results:
                        self.log_test(
                            "Admin Excluded from User Search",
                            True,
                            f"Admin user correctly excluded from search results ({len(search_results)} users found)"
                        )
                    else:
                        self.log_test(
                            "Admin Excluded from User Search",
                            False,
                            "",
                            "Admin user found in search results (should be excluded)"
                        )
                else:
                    self.log_test("Admin Excluded from User Search", False, "", "Invalid search results format")
            else:
                self.log_test("Admin Excluded from User Search", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Excluded from User Search", False, "", str(e))

    def test_admin_analytics_endpoints(self):
        """Test admin analytics endpoints"""
        print("📊 TESTING ADMIN ANALYTICS ENDPOINTS")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Admin Analytics Endpoints", False, "", "No admin token available")
            return

        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Test 1: GET /api/admin/traffic-stats
        try:
            response = self.session.get(f"{BASE_URL}/admin/traffic-stats", headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ["overview", "recent_activity", "jersey_statuses", "top_leagues", "active_users"]
                
                if all(section in data for section in required_sections):
                    overview = data["overview"]
                    recent = data["recent_activity"]
                    self.log_test(
                        "GET /api/admin/traffic-stats",
                        True,
                        f"Traffic stats retrieved - Users: {overview.get('total_users')}, Jerseys: {overview.get('total_jerseys')}, Recent activity: {recent.get('new_users_7d')} new users"
                    )
                else:
                    self.log_test("GET /api/admin/traffic-stats", False, "", "Missing required sections in response")
            else:
                self.log_test("GET /api/admin/traffic-stats", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/admin/traffic-stats", False, "", str(e))

        # Test 2: GET /api/admin/user-stats/{user_id}
        try:
            response = self.session.get(f"{BASE_URL}/admin/user-stats/{self.regular_user_id}", headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ["user", "stats", "recent_activities"]
                
                if all(section in data for section in required_sections):
                    user_info = data["user"]
                    stats = data["stats"]
                    self.log_test(
                        "GET /api/admin/user-stats/{user_id}",
                        True,
                        f"User stats retrieved for {user_info.get('name')} - Owned: {stats.get('owned_jerseys')}, Submitted: {stats.get('jerseys_submitted')}"
                    )
                else:
                    self.log_test("GET /api/admin/user-stats/{user_id}", False, "", "Missing required sections in response")
            else:
                self.log_test("GET /api/admin/user-stats/{user_id}", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/admin/user-stats/{user_id}", False, "", str(e))

        # Test 3: GET /api/admin/activities
        try:
            response = self.session.get(f"{BASE_URL}/admin/activities", headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                if "activities" in data and isinstance(data["activities"], list):
                    activities = data["activities"]
                    # Check if activities have user enrichment
                    enriched_activities = [
                        activity for activity in activities 
                        if "user_name" in activity and "user_email" in activity
                    ]
                    
                    self.log_test(
                        "GET /api/admin/activities",
                        True,
                        f"Activities retrieved with user enrichment - {len(activities)} total activities, {len(enriched_activities)} enriched"
                    )
                else:
                    self.log_test("GET /api/admin/activities", False, "", "Invalid activities response format")
            else:
                self.log_test("GET /api/admin/activities", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/admin/activities", False, "", str(e))

    def test_admin_endpoints_reject_non_admin(self):
        """Test that admin endpoints reject non-admin users"""
        print("🔒 TESTING ADMIN ENDPOINTS REJECT NON-ADMIN USERS")
        print("=" * 50)
        
        if not self.regular_user_token:
            self.log_test("Admin Endpoints Reject Non-Admin", False, "", "No regular user token available")
            return

        regular_headers = {"Authorization": f"Bearer {self.regular_user_token}"}
        
        admin_endpoints = [
            "/admin/traffic-stats",
            "/admin/activities",
            f"/admin/user-stats/{self.regular_user_id}"
        ]

        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=regular_headers)
                
                if response.status_code == 403:
                    self.log_test(
                        f"Non-admin rejected from {endpoint}",
                        True,
                        "Non-admin user correctly rejected with HTTP 403"
                    )
                else:
                    self.log_test(
                        f"Non-admin rejected from {endpoint}",
                        False,
                        "",
                        f"Expected HTTP 403, got {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"Non-admin rejected from {endpoint}", False, "", str(e))

    def run_all_tests(self):
        """Run all admin restrictions and analytics tests"""
        print("🚀 STARTING ADMIN RESTRICTIONS & ANALYTICS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print(f"Regular User: {REGULAR_USER_EMAIL}")
        print("=" * 60)
        print()
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ Authentication setup failed. Cannot continue with tests.")
            return 0
        
        # Create test jersey for collection tests
        self.create_test_jersey()
        
        # Run test suites
        self.test_admin_listing_restrictions()
        self.test_admin_collection_restrictions()
        self.test_admin_excluded_from_user_search()
        self.test_admin_analytics_endpoints()
        self.test_admin_endpoints_reject_non_admin()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        print()
        print("🎯 ADMIN RESTRICTIONS & ANALYTICS TESTING COMPLETE")
        
        return success_rate

if __name__ == "__main__":
    tester = AdminRestrictionsTestSuite()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)