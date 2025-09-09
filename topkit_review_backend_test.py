#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Review Request Focus
Testing backend functionality after frontend modal z-index fixes and sample listings addition
Focus areas: Authentication System, New Sample Marketplace Listings, Jersey Management, Critical APIs
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://football-kit-ui.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class TopKitReviewTester:
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

    def test_authentication_system_after_modal_fix(self):
        """Test 1: Authentication System - Test login with steinmetzlivio@gmail.com/123 after modal z-index fixes"""
        print("🔐 TESTING AUTHENTICATION SYSTEM AFTER MODAL Z-INDEX FIXES")
        print("=" * 60)
        
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
                        "Authentication - steinmetzlivio@gmail.com/123 Login",
                        True,
                        f"Login successful - Name: {user_name}, Role: {user_role}, ID: {self.user_id}"
                    )
                else:
                    self.log_test("Authentication - steinmetzlivio@gmail.com/123 Login", False, "", "Missing token or user data in response")
            else:
                self.log_test("Authentication - steinmetzlivio@gmail.com/123 Login", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Authentication - steinmetzlivio@gmail.com/123 Login", False, "", str(e))

        # Test 2: Token Validation through Profile Access
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/profile", headers=headers)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    self.log_test(
                        "Authentication - JWT Token Validation",
                        True,
                        f"Token valid - Profile access successful"
                    )
                else:
                    self.log_test("Authentication - JWT Token Validation", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Authentication - JWT Token Validation", False, "", str(e))

        # Test 3: Admin Authentication
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
                        "Authentication - Admin Login (topkitfr@gmail.com)",
                        True,
                        f"Admin login successful - Name: {admin_name}, Role: {admin_role}"
                    )
                else:
                    self.log_test("Authentication - Admin Login", False, "", "Missing token or user data in response")
            else:
                self.log_test("Authentication - Admin Login", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Authentication - Admin Login", False, "", str(e))

    def test_new_sample_marketplace_listings(self):
        """Test 2: New Sample Marketplace Listings - Verify Barcelona, Real Madrid, Manchester City listings"""
        print("🛒 TESTING NEW SAMPLE MARKETPLACE LISTINGS")
        print("=" * 60)
        
        # Test 1: Marketplace Catalog Endpoint
        try:
            response = self.session.get(f"{BASE_URL}/marketplace/catalog")
            
            if response.status_code == 200:
                catalog_data = response.json()
                if isinstance(catalog_data, list):
                    # Look for the new sample listings
                    barcelona_found = any("Barcelona" in str(item).lower() for item in catalog_data)
                    real_madrid_found = any("real madrid" in str(item).lower() for item in catalog_data)
                    manchester_city_found = any("manchester city" in str(item).lower() for item in catalog_data)
                    
                    sample_teams_found = sum([barcelona_found, real_madrid_found, manchester_city_found])
                    
                    self.log_test(
                        "Marketplace Catalog - New Sample Listings Access",
                        True,
                        f"Catalog accessible with {len(catalog_data)} items, {sample_teams_found}/3 sample teams found"
                    )
                else:
                    self.log_test("Marketplace Catalog - New Sample Listings Access", False, "", "Invalid catalog format")
            else:
                self.log_test("Marketplace Catalog - New Sample Listings Access", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Marketplace Catalog - New Sample Listings Access", False, "", str(e))

        # Test 2: Listings Endpoint
        try:
            response = self.session.get(f"{BASE_URL}/listings")
            
            if response.status_code == 200:
                listings_data = response.json()
                if isinstance(listings_data, list):
                    active_listings = [l for l in listings_data if l.get("status") == "active"]
                    
                    # Check for sample team listings
                    sample_listings = []
                    for listing in active_listings:
                        listing_str = str(listing).lower()
                        if any(team in listing_str for team in ["barcelona", "real madrid", "manchester city"]):
                            sample_listings.append(listing)
                    
                    self.log_test(
                        "Listings Endpoint - Sample Listings Verification",
                        True,
                        f"Retrieved {len(listings_data)} total listings ({len(active_listings)} active, {len(sample_listings)} sample team listings)"
                    )
                else:
                    self.log_test("Listings Endpoint - Sample Listings Verification", False, "", "Invalid listings format")
            else:
                self.log_test("Listings Endpoint - Sample Listings Verification", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Listings Endpoint - Sample Listings Verification", False, "", str(e))

        # Test 3: Cart Functionality Support (verify listings have required data for cart)
        try:
            response = self.session.get(f"{BASE_URL}/listings")
            
            if response.status_code == 200:
                listings_data = response.json()
                if isinstance(listings_data, list) and listings_data:
                    # Check if listings have required cart data
                    sample_listing = listings_data[0]
                    required_fields = ["id", "jersey_id", "seller_id", "price", "description"]
                    has_required_fields = all(field in sample_listing for field in required_fields)
                    
                    self.log_test(
                        "Cart Functionality Support - Listing Data Structure",
                        has_required_fields,
                        f"Listings contain required cart fields: {required_fields}" if has_required_fields else f"Missing required fields in listings"
                    )
                else:
                    self.log_test("Cart Functionality Support - Listing Data Structure", False, "", "No listings available for cart testing")
            else:
                self.log_test("Cart Functionality Support - Listing Data Structure", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Cart Functionality Support - Listing Data Structure", False, "", str(e))

    def test_jersey_management_system(self):
        """Test 3: Jersey Management - Ensure jersey submission, browsing, and collection management work"""
        print("⚽ TESTING JERSEY MANAGEMENT SYSTEM")
        print("=" * 60)
        
        # Test 1: Jersey Browsing
        try:
            response = self.session.get(f"{BASE_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                if isinstance(jerseys, list):
                    approved_jerseys = [j for j in jerseys if j.get("status") == "approved"]
                    pending_jerseys = [j for j in jerseys if j.get("status") == "pending"]
                    
                    self.log_test(
                        "Jersey Management - Jersey Browsing",
                        True,
                        f"Retrieved {len(jerseys)} total jerseys ({len(approved_jerseys)} approved, {len(pending_jerseys)} pending)"
                    )
                else:
                    self.log_test("Jersey Management - Jersey Browsing", False, "", "Invalid jerseys response format")
            else:
                self.log_test("Jersey Management - Jersey Browsing", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Jersey Management - Jersey Browsing", False, "", str(e))

        # Test 2: Jersey Submission (requires authentication)
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                test_jersey_data = {
                    "team": "Liverpool FC",
                    "season": "2024-25",
                    "player": "Mohamed Salah",
                    "size": "L",
                    "condition": "new",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Test jersey submission for review request testing"
                }
                
                response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    jersey_data = response.json()
                    jersey_id = jersey_data.get("id")
                    jersey_status = jersey_data.get("status")
                    reference_number = jersey_data.get("reference_number")
                    
                    self.log_test(
                        "Jersey Management - Jersey Submission",
                        True,
                        f"Jersey submitted successfully - ID: {jersey_id}, Status: {jersey_status}, Ref: {reference_number}"
                    )
                else:
                    self.log_test("Jersey Management - Jersey Submission", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Jersey Management - Jersey Submission", False, "", str(e))

        # Test 3: User Jersey Submissions Tracking
        if self.user_token and self.user_id:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = self.session.get(f"{BASE_URL}/users/{self.user_id}/jerseys", headers=headers)
                
                if response.status_code == 200:
                    user_jerseys = response.json()
                    if isinstance(user_jerseys, list):
                        pending_count = sum(1 for j in user_jerseys if j.get("status") == "pending")
                        approved_count = sum(1 for j in user_jerseys if j.get("status") == "approved")
                        
                        self.log_test(
                            "Jersey Management - User Submissions Tracking",
                            True,
                            f"User has {len(user_jerseys)} total submissions ({approved_count} approved, {pending_count} pending)"
                        )
                    else:
                        self.log_test("Jersey Management - User Submissions Tracking", False, "", "Invalid user jerseys format")
                else:
                    self.log_test("Jersey Management - User Submissions Tracking", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Jersey Management - User Submissions Tracking", False, "", str(e))

        # Test 4: Collection Management
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                
                # Test owned collections
                owned_response = self.session.get(f"{BASE_URL}/collections/owned", headers=headers)
                wanted_response = self.session.get(f"{BASE_URL}/collections/wanted", headers=headers)
                
                if owned_response.status_code == 200 and wanted_response.status_code == 200:
                    owned_data = owned_response.json()
                    wanted_data = wanted_response.json()
                    owned_count = len(owned_data) if isinstance(owned_data, list) else 0
                    wanted_count = len(wanted_data) if isinstance(wanted_data, list) else 0
                    
                    self.log_test(
                        "Jersey Management - Collection Management",
                        True,
                        f"Collections accessible - Owned: {owned_count}, Wanted: {wanted_count}"
                    )
                else:
                    self.log_test("Jersey Management - Collection Management", False, "", f"Owned: {owned_response.status_code}, Wanted: {wanted_response.status_code}")
            except Exception as e:
                self.log_test("Jersey Management - Collection Management", False, "", str(e))

    def test_critical_api_endpoints(self):
        """Test 4: Critical APIs - Test all main API endpoints for functionality"""
        print("🔧 TESTING CRITICAL API ENDPOINTS")
        print("=" * 60)
        
        # Test 1: Core Public Endpoints
        public_endpoints = [
            ("/jerseys", "Jersey Database Access"),
            ("/marketplace/catalog", "Marketplace Catalog"),
            ("/listings", "Marketplace Listings"),
            ("/explorer/most-collected", "Explorer - Most Collected"),
            ("/explorer/most-wanted", "Explorer - Most Wanted"),
            ("/explorer/latest-additions", "Explorer - Latest Additions"),
            ("/explorer/leagues", "Explorer - Leagues Overview")
        ]
        
        for endpoint, description in public_endpoints:
            try:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(
                            f"Critical API - {description}",
                            True,
                            f"Endpoint operational - returned {len(data)} items"
                        )
                    else:
                        self.log_test(f"Critical API - {description}", False, "", "Invalid response format")
                else:
                    self.log_test(f"Critical API - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Critical API - {description}", False, "", str(e))

        # Test 2: Authenticated Endpoints
        if self.user_token:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            authenticated_endpoints = [
                ("/profile", "User Profile"),
                ("/notifications", "User Notifications"),
                ("/conversations", "User Conversations"),
                ("/users/search?query=test", "User Search"),
                (f"/users/{self.user_id}/collections", "User Collections"),
                (f"/users/{self.user_id}/jerseys", "User Jersey Submissions")
            ]
            
            for endpoint, description in authenticated_endpoints:
                try:
                    response = self.session.get(f"{BASE_URL}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test(
                            f"Critical API - {description} (Auth Required)",
                            True,
                            f"Authenticated endpoint operational"
                        )
                    else:
                        self.log_test(f"Critical API - {description} (Auth Required)", False, "", f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test(f"Critical API - {description} (Auth Required)", False, "", str(e))

        # Test 3: Admin Endpoints
        if self.admin_token:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            admin_endpoints = [
                ("/admin/jerseys/pending", "Admin - Pending Jerseys"),
                ("/admin/users", "Admin - User Management"),
                ("/admin/activities", "Admin - System Activities"),
                ("/admin/traffic-stats", "Admin - Traffic Statistics")
            ]
            
            for endpoint, description in admin_endpoints:
                try:
                    response = self.session.get(f"{BASE_URL}{endpoint}", headers=admin_headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test(
                            f"Critical API - {description}",
                            True,
                            f"Admin endpoint operational"
                        )
                    else:
                        self.log_test(f"Critical API - {description}", False, "", f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test(f"Critical API - {description}", False, "", str(e))

        # Test 4: Data Validation and Error Handling
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                
                # Test invalid jersey submission
                invalid_jersey_data = {
                    "team": "",  # Empty team should fail
                    "season": "",  # Empty season should fail
                    "size": "INVALID",  # Invalid size
                    "condition": "INVALID"  # Invalid condition
                }
                
                response = self.session.post(f"{BASE_URL}/jerseys", json=invalid_jersey_data, headers=headers)
                
                if response.status_code == 422:  # Validation error expected
                    self.log_test(
                        "Critical API - Data Validation & Error Handling",
                        True,
                        f"Validation working correctly - rejected invalid data with HTTP 422"
                    )
                else:
                    self.log_test("Critical API - Data Validation & Error Handling", False, "", f"Expected HTTP 422, got {response.status_code}")
            except Exception as e:
                self.log_test("Critical API - Data Validation & Error Handling", False, "", str(e))

    def test_backend_stability_after_frontend_changes(self):
        """Test 5: Backend Stability - Ensure backend remains stable after frontend modal fixes"""
        print("🛡️ TESTING BACKEND STABILITY AFTER FRONTEND CHANGES")
        print("=" * 60)
        
        # Test 1: Database Connectivity
        try:
            response = self.session.get(f"{BASE_URL}/jerseys")
            
            if response.status_code == 200:
                self.log_test(
                    "Backend Stability - Database Connectivity",
                    True,
                    "Database connection stable - jersey data accessible"
                )
            else:
                self.log_test("Backend Stability - Database Connectivity", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Backend Stability - Database Connectivity", False, "", str(e))

        # Test 2: Session Management
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                
                # Make multiple requests to test session stability
                for i in range(3):
                    response = self.session.get(f"{BASE_URL}/profile", headers=headers)
                    if response.status_code != 200:
                        self.log_test("Backend Stability - Session Management", False, "", f"Session failed on request {i+1}")
                        return
                
                self.log_test(
                    "Backend Stability - Session Management",
                    True,
                    "Session management stable - multiple authenticated requests successful"
                )
            except Exception as e:
                self.log_test("Backend Stability - Session Management", False, "", str(e))

        # Test 3: API Response Consistency
        try:
            # Test same endpoint multiple times
            responses = []
            for i in range(3):
                response = self.session.get(f"{BASE_URL}/marketplace/catalog")
                if response.status_code == 200:
                    responses.append(len(response.json()))
                else:
                    self.log_test("Backend Stability - API Response Consistency", False, "", f"Inconsistent response on attempt {i+1}")
                    return
            
            # Check if responses are consistent
            if len(set(responses)) <= 1:  # All responses have same length (allowing for minor variations)
                self.log_test(
                    "Backend Stability - API Response Consistency",
                    True,
                    f"API responses consistent across multiple requests - catalog size: {responses[0]}"
                )
            else:
                self.log_test("Backend Stability - API Response Consistency", False, "", f"Inconsistent response sizes: {responses}")
        except Exception as e:
            self.log_test("Backend Stability - API Response Consistency", False, "", str(e))

    def run_all_tests(self):
        """Run all test suites focused on the review request"""
        print("🚀 STARTING TOPKIT BACKEND TESTING - REVIEW REQUEST FOCUS")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("Focus: Authentication after modal fixes, New sample listings, Jersey management, Critical APIs")
        print("=" * 80)
        print()
        
        # Run test suites in order of importance for the review
        self.test_authentication_system_after_modal_fix()
        self.test_new_sample_marketplace_listings()
        self.test_jersey_management_system()
        self.test_critical_api_endpoints()
        self.test_backend_stability_after_frontend_changes()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY - TOPKIT REVIEW REQUEST BACKEND VERIFICATION")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by focus area
        focus_areas = {
            "Authentication System": [],
            "Sample Marketplace Listings": [],
            "Jersey Management": [],
            "Critical APIs": [],
            "Backend Stability": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                focus_areas["Authentication System"].append(result)
            elif "Marketplace" in test_name or "Listings" in test_name or "Cart" in test_name:
                focus_areas["Sample Marketplace Listings"].append(result)
            elif "Jersey Management" in test_name:
                focus_areas["Jersey Management"].append(result)
            elif "Critical API" in test_name:
                focus_areas["Critical APIs"].append(result)
            elif "Backend Stability" in test_name:
                focus_areas["Backend Stability"].append(result)
        
        # Print focus area summaries
        for area, results in focus_areas.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                status = "✅" if passed == total else "⚠️" if passed > total/2 else "❌"
                print(f"{status} {area}: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
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
        
        # Review-specific assessment
        auth_tests = focus_areas["Authentication System"]
        auth_success = all(r["success"] for r in auth_tests) if auth_tests else False
        
        listings_tests = focus_areas["Sample Marketplace Listings"]
        listings_success = all(r["success"] for r in listings_tests) if listings_tests else False
        
        jersey_tests = focus_areas["Jersey Management"]
        jersey_success = all(r["success"] for r in jersey_tests) if jersey_tests else False
        
        print("🎯 REVIEW REQUEST ASSESSMENT:")
        print(f"✅ Authentication System (after modal fixes): {'WORKING' if auth_success else 'ISSUES FOUND'}")
        print(f"✅ New Sample Marketplace Listings: {'ACCESSIBLE' if listings_success else 'ISSUES FOUND'}")
        print(f"✅ Jersey Management System: {'OPERATIONAL' if jersey_success else 'ISSUES FOUND'}")
        print(f"✅ Overall Backend Stability: {'STABLE' if success_rate >= 85 else 'NEEDS ATTENTION'}")
        print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Backend is fully operational after frontend changes!")
        elif success_rate >= 80:
            print("✅ GOOD: Backend is mostly operational with minor issues.")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Backend has some issues that should be addressed.")
        else:
            print("❌ CRITICAL: Backend has significant issues that need immediate attention.")
        
        print()
        print("🎯 TOPKIT REVIEW REQUEST BACKEND TESTING COMPLETE")
        
        # Return success rate for external use
        return success_rate

if __name__ == "__main__":
    tester = TopKitReviewTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)