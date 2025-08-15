#!/usr/bin/env python3
"""
TopKit Backend API Testing Suite - Post Discogs-Style Header Implementation
Testing backend functionality after implementing the new Discogs-style header
Focus areas: API Connectivity, Authentication, Jersey Operations, User Profile, Navigation Integration
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://kit-trading.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class TopKitTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.test_results = []
        
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

    def test_api_connectivity(self):
        """Test 1: API Connectivity - Verify all main API endpoints are accessible"""
        print("🌐 TESTING API CONNECTIVITY")
        print("=" * 50)
        
        # Test core endpoints accessibility
        endpoints_to_test = [
            ("/jerseys", "GET", "Jersey browsing endpoint"),
            ("/auth/login", "POST", "Authentication endpoint"),
            ("/profile", "GET", "Profile endpoint (requires auth)"),
            ("/marketplace/catalog", "GET", "Marketplace catalog endpoint"),
            ("/explorer/most-collected", "GET", "Explorer most collected endpoint"),
            ("/explorer/latest-additions", "GET", "Explorer latest additions endpoint"),
            ("/users/search", "GET", "User search endpoint (requires auth)")
        ]
        
        for endpoint, method, description in endpoints_to_test:
            try:
                if method == "GET":
                    if "profile" in endpoint or "users/search" in endpoint:
                        # Skip auth-required endpoints for now
                        continue
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                elif method == "POST":
                    if endpoint == "/auth/login":
                        # Test with invalid credentials to check endpoint exists
                        response = self.session.post(f"{BASE_URL}{endpoint}", json={"email": "test", "password": "test"})
                    else:
                        continue
                
                if response.status_code in [200, 400, 401, 422]:  # Valid responses
                    self.log_test(
                        f"API Connectivity - {description}",
                        True,
                        f"Endpoint accessible (HTTP {response.status_code})"
                    )
                else:
                    self.log_test(
                        f"API Connectivity - {description}",
                        False,
                        "",
                        f"Unexpected status code: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"API Connectivity - {description}", False, "", str(e))

    def test_authentication_system(self):
        """Test 2: Authentication System - Test user login/logout functionality"""
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test 1: User Login with provided credentials
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"]["role"]
                    self.log_test(
                        "User Authentication (steinmetzlivio@gmail.com/123)",
                        True,
                        f"Login successful - User: {user_name}, Role: {user_role}, ID: {self.user_id}"
                    )
                else:
                    self.log_test("User Authentication", False, "", "Missing token or user data in response")
            else:
                self.log_test("User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Authentication", False, "", str(e))

        # Test 2: Admin Login with provided credentials
        try:
            admin_login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
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
                        "Admin Authentication (topkitfr@gmail.com/adminpass123)",
                        True,
                        f"Admin login successful - User: {admin_name}, Role: {admin_role}"
                    )
                else:
                    self.log_test("Admin Authentication", False, "", "Missing token or user data in response")
            else:
                self.log_test("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))

        # Test 3: Token Validation
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/profile", headers=headers)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    self.log_test(
                        "Token Validation via Profile Access",
                        True,
                        f"Token valid - Profile data retrieved successfully"
                    )
                else:
                    self.log_test("Token Validation via Profile Access", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Token Validation via Profile Access", False, "", str(e))

    def test_core_jersey_operations(self):
        """Test 3: Core Jersey Operations - Test jersey browsing, search, and basic CRUD operations"""
        print("⚽ TESTING CORE JERSEY OPERATIONS")
        print("=" * 50)
        
        # Test 1: GET /api/jerseys for Explorez page functionality
        try:
            response = self.session.get(f"{BASE_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                if isinstance(jerseys, list):
                    approved_jerseys = [j for j in jerseys if j.get("status") == "approved"]
                    self.log_test(
                        "GET /api/jerseys - Explorez Page Functionality",
                        True,
                        f"Retrieved {len(jerseys)} total jerseys ({len(approved_jerseys)} approved) for browsing"
                    )
                else:
                    self.log_test("GET /api/jerseys - Explorez Page Functionality", False, "", "Invalid response format")
            else:
                self.log_test("GET /api/jerseys - Explorez Page Functionality", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/jerseys - Explorez Page Functionality", False, "", str(e))

        # Test 2: Jersey Search Functionality
        try:
            search_params = {"search": "Real Madrid"}
            response = self.session.get(f"{BASE_URL}/jerseys", params=search_params)
            
            if response.status_code == 200:
                search_results = response.json()
                if isinstance(search_results, list):
                    self.log_test(
                        "Jersey Search Functionality",
                        True,
                        f"Search for 'Real Madrid' returned {len(search_results)} results"
                    )
                else:
                    self.log_test("Jersey Search Functionality", False, "", "Invalid search results format")
            else:
                self.log_test("Jersey Search Functionality", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Jersey Search Functionality", False, "", str(e))

        # Test 3: Jersey Submission (CRUD - Create)
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                test_jersey_data = {
                    "team": "Real Madrid CF",
                    "season": "2024-25",
                    "player": "Vinicius Jr",
                    "size": "M",
                    "condition": "new",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": "Test jersey submission for Discogs header testing"
                }
                
                response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    jersey_data = response.json()
                    jersey_id = jersey_data.get("id")
                    jersey_status = jersey_data.get("status")
                    reference_number = jersey_data.get("reference_number")
                    
                    self.log_test(
                        "Jersey Submission (CRUD - Create)",
                        True,
                        f"Jersey created successfully - ID: {jersey_id}, Status: {jersey_status}, Ref: {reference_number}"
                    )
                else:
                    self.log_test("Jersey Submission (CRUD - Create)", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Jersey Submission (CRUD - Create)", False, "", str(e))

        # Test 4: Explorer Endpoints for Header Navigation
        explorer_endpoints = [
            ("/explorer/most-collected", "Most Collected Jerseys"),
            ("/explorer/most-wanted", "Most Wanted Jerseys"),
            ("/explorer/latest-additions", "Latest Additions"),
            ("/explorer/leagues", "Leagues Overview")
        ]
        
        for endpoint, description in explorer_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(
                            f"Explorer - {description}",
                            True,
                            f"Retrieved {len(data)} items"
                        )
                    else:
                        self.log_test(f"Explorer - {description}", False, "", "Invalid response format")
                else:
                    self.log_test(f"Explorer - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Explorer - {description}", False, "", str(e))

    def test_user_profile_access(self):
        """Test 4: User Profile Access - Verify profile data retrieval works correctly"""
        print("👤 TESTING USER PROFILE ACCESS")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("User Profile Access", False, "", "No user token available for testing")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Profile Data Retrieval
        try:
            response = self.session.get(f"{BASE_URL}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                owned_jerseys = profile_data.get("owned_jerseys", 0)
                wanted_jerseys = profile_data.get("wanted_jerseys", 0)
                active_listings = profile_data.get("active_listings", 0)
                self.log_test(
                    "Profile Data Retrieval",
                    True,
                    f"Profile data retrieved - Owned: {owned_jerseys}, Wanted: {wanted_jerseys}, Listings: {active_listings}"
                )
            else:
                self.log_test("Profile Data Retrieval", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Profile Data Retrieval", False, "", str(e))

        # Test 2: User Profile Endpoints for Profile Dropdown
        profile_endpoints = [
            (f"/users/{self.user_id}/profile", "User Profile Details"),
            (f"/users/{self.user_id}/collections", "User Collections"),
            (f"/users/{self.user_id}/jerseys", "User Submissions")
        ]
        
        for endpoint, description in profile_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Profile Dropdown - {description}",
                        True,
                        f"Data retrieved successfully"
                    )
                else:
                    self.log_test(f"Profile Dropdown - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Profile Dropdown - {description}", False, "", str(e))

        # Test 3: Collections Access
        try:
            owned_response = self.session.get(f"{BASE_URL}/collections/owned", headers=headers)
            wanted_response = self.session.get(f"{BASE_URL}/collections/wanted", headers=headers)
            
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                owned_data = owned_response.json()
                wanted_data = wanted_response.json()
                owned_count = len(owned_data) if isinstance(owned_data, list) else 0
                wanted_count = len(wanted_data) if isinstance(wanted_data, list) else 0
                
                self.log_test(
                    "Collections Access",
                    True,
                    f"Collections retrieved - Owned: {owned_count}, Wanted: {wanted_count}"
                )
            else:
                self.log_test("Collections Access", False, "", f"Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}")
        except Exception as e:
            self.log_test("Collections Access", False, "", str(e))

    def test_marketplace_api_endpoints(self):
        """Test 5: Marketplace API Endpoints - Test marketplace API endpoints for navigation"""
        print("🛒 TESTING MARKETPLACE API ENDPOINTS")
        print("=" * 50)
        
        # Test 1: Marketplace Catalog (Discogs-style)
        try:
            response = self.session.get(f"{BASE_URL}/marketplace/catalog")
            
            if response.status_code == 200:
                catalog_data = response.json()
                if isinstance(catalog_data, list):
                    self.log_test(
                        "Marketplace Catalog (Discogs-style)",
                        True,
                        f"Catalog retrieved with {len(catalog_data)} items"
                    )
                else:
                    self.log_test("Marketplace Catalog (Discogs-style)", False, "", "Invalid catalog format")
            else:
                self.log_test("Marketplace Catalog (Discogs-style)", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Marketplace Catalog (Discogs-style)", False, "", str(e))

        # Test 2: Listings Endpoints
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            try:
                response = self.session.get(f"{BASE_URL}/listings", headers=headers)
                
                if response.status_code == 200:
                    listings_data = response.json()
                    if isinstance(listings_data, list):
                        active_listings = [l for l in listings_data if l.get("status") == "active"]
                        self.log_test(
                            "Marketplace Listings",
                            True,
                            f"Retrieved {len(listings_data)} total listings ({len(active_listings)} active)"
                        )
                    else:
                        self.log_test("Marketplace Listings", False, "", "Invalid listings format")
                else:
                    self.log_test("Marketplace Listings", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Marketplace Listings", False, "", str(e))

    def test_search_related_api_endpoints(self):
        """Test 6: Search-Related API Endpoints - Verify search-related API endpoints work with new search bar"""
        print("🔍 TESTING SEARCH-RELATED API ENDPOINTS")
        print("=" * 50)
        
        # Test 1: Jersey Search with various parameters
        search_tests = [
            ({"search": "Real Madrid"}, "Team Search"),
            ({"search": "2024"}, "Season Search"),
            ({"league": "La Liga"}, "League Filter"),
            ({"team": "Barcelona"}, "Team Filter")
        ]
        
        for params, description in search_tests:
            try:
                response = self.session.get(f"{BASE_URL}/jerseys", params=params)
                
                if response.status_code == 200:
                    results = response.json()
                    if isinstance(results, list):
                        self.log_test(
                            f"Search API - {description}",
                            True,
                            f"Search returned {len(results)} results"
                        )
                    else:
                        self.log_test(f"Search API - {description}", False, "", "Invalid search results format")
                else:
                    self.log_test(f"Search API - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Search API - {description}", False, "", str(e))

        # Test 2: User Search (for header search functionality)
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            try:
                response = self.session.get(f"{BASE_URL}/users/search?query=test", headers=headers)
                
                if response.status_code == 200:
                    user_results = response.json()
                    if isinstance(user_results, list):
                        self.log_test(
                            "User Search API",
                            True,
                            f"User search returned {len(user_results)} results"
                        )
                    else:
                        self.log_test("User Search API", False, "", "Invalid user search results format")
                else:
                    self.log_test("User Search API", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("User Search API", False, "", str(e))

    def test_navigation_integration(self):
        """Test 7: Navigation Integration - Ensure backend properly supports the new header navigation flow"""
        print("🧭 TESTING NAVIGATION INTEGRATION")
        print("=" * 50)
        
        # Test navigation-related endpoints that support the new header
        navigation_endpoints = [
            ("/jerseys", "Home/Explorez Navigation"),
            ("/marketplace/catalog", "Marketplace Navigation"),
            ("/explorer/leagues", "Explorer Navigation"),
            ("/notifications", "Notifications (Header Bell)", True),  # Requires auth
            ("/profile", "Profile Dropdown", True)  # Requires auth
        ]
        
        for endpoint_info in navigation_endpoints:
            endpoint = endpoint_info[0]
            description = endpoint_info[1]
            requires_auth = len(endpoint_info) > 2 and endpoint_info[2]
            
            try:
                headers = {}
                if requires_auth and self.user_token:
                    headers = {"Authorization": f"Bearer {self.user_token}"}
                elif requires_auth and not self.user_token:
                    self.log_test(f"Navigation - {description}", False, "", "No auth token available")
                    continue
                
                response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"Navigation - {description}",
                        True,
                        f"Endpoint accessible and returns data"
                    )
                else:
                    self.log_test(f"Navigation - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Navigation - {description}", False, "", str(e))

        # Test messaging endpoints for header messages icon
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            try:
                response = self.session.get(f"{BASE_URL}/conversations", headers=headers)
                
                if response.status_code == 200:
                    conversations = response.json()
                    if isinstance(conversations, list):
                        self.log_test(
                            "Navigation - Messages Integration",
                            True,
                            f"Messages endpoint accessible - {len(conversations)} conversations"
                        )
                    else:
                        self.log_test("Navigation - Messages Integration", False, "", "Invalid conversations format")
                else:
                    self.log_test("Navigation - Messages Integration", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Navigation - Messages Integration", False, "", str(e))

    def run_all_tests(self):
        """Run all test suites focused on Discogs-style header backend support"""
        print("🚀 STARTING TOPKIT BACKEND TESTING - POST DISCOGS-STYLE HEADER IMPLEMENTATION")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("Focus: API Connectivity, Authentication, Jersey Operations, Profile Access, Navigation")
        print("=" * 80)
        print()
        
        # Run test suites in order of importance
        self.test_api_connectivity()
        self.test_authentication_system()
        self.test_core_jersey_operations()
        self.test_user_profile_access()
        self.test_marketplace_api_endpoints()
        self.test_search_related_api_endpoints()
        self.test_navigation_integration()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY - DISCOGS-STYLE HEADER BACKEND VERIFICATION")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by test area
        test_categories = {
            "API Connectivity": [],
            "Authentication System": [],
            "Core Jersey Operations": [],
            "User Profile Access": [],
            "Marketplace API": [],
            "Search-Related API": [],
            "Navigation Integration": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "API Connectivity" in test_name:
                test_categories["API Connectivity"].append(result)
            elif "Authentication" in test_name or "Token" in test_name:
                test_categories["Authentication System"].append(result)
            elif "Jersey" in test_name or "Explorer" in test_name:
                test_categories["Core Jersey Operations"].append(result)
            elif "Profile" in test_name or "Collections" in test_name:
                test_categories["User Profile Access"].append(result)
            elif "Marketplace" in test_name or "Listings" in test_name:
                test_categories["Marketplace API"].append(result)
            elif "Search" in test_name:
                test_categories["Search-Related API"].append(result)
            elif "Navigation" in test_name or "Messages" in test_name:
                test_categories["Navigation Integration"].append(result)
        
        # Print category summaries
        for category, results in test_categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"📋 {category}: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
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
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is fully operational and ready for Discogs-style header!")
        elif success_rate >= 80:
            print("✅ GOOD: Backend is mostly operational with minor issues.")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Backend has some issues that should be addressed.")
        else:
            print("❌ CRITICAL: Backend has significant issues that need immediate attention.")
        
        print()
        print("🎯 DISCOGS-STYLE HEADER BACKEND TESTING COMPLETE")
        
        # Return success rate for external use
        return success_rate

if __name__ == "__main__":
    tester = TopKitTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)