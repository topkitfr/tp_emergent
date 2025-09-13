#!/usr/bin/env python3
"""
TopKit Backend Testing - Review Request Comprehensive Test
Testing all backend functionality after frontend BrowseJerseysPage modifications

Focus Areas from Review Request:
1. Basic API connectivity and health
2. Authentication endpoints (login/profile) with provided credentials
3. Jersey browsing endpoints (/api/jerseys)
4. Jersey filtering and search functionality
5. User collection endpoints
6. Any other core backend functionality

Test Credentials:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / TopKitSecure456# (recreated)
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKitSecure456#"

class TopKitBackendTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
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

    def test_api_health(self):
        """Test 1: Basic API connectivity and health"""
        print("🏥 Testing Basic API Connectivity and Health...")
        
        try:
            # Test basic API health
            response = requests.get(f"{BACKEND_URL}/jerseys", timeout=10)
            
            if response.status_code in [200, 401]:  # Both are acceptable
                self.log_result(
                    "API Health Check",
                    True,
                    f"API is accessible and responding (HTTP {response.status_code})"
                )
                return True
            else:
                self.log_result(
                    "API Health Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
                return False
        except Exception as e:
            self.log_result(
                "API Health Check",
                False,
                "",
                f"Connection failed: {str(e)}"
            )
            return False

    def test_authentication_endpoints(self):
        """Test 2: Authentication endpoints (login/profile)"""
        print("🔐 Testing Authentication Endpoints...")
        
        # Test admin authentication
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
                    f"Admin: {admin_info.get('name')}, Role: {admin_info.get('role')}, ID: {admin_info.get('id')}"
                )
            else:
                self.log_result(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Admin Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test user authentication
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.log_result(
                    "User Authentication",
                    True,
                    f"User: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                )
            else:
                self.log_result(
                    "User Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "User Authentication",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test profile endpoints
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BACKEND_URL}/auth/profile", headers=headers)
                
                if response.status_code == 200:
                    profile = response.json()
                    self.log_result(
                        "Admin Profile Access",
                        True,
                        f"Admin profile accessible: {profile.get('name')} ({profile.get('email')})"
                    )
                else:
                    self.log_result(
                        "Admin Profile Access",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(
                    "Admin Profile Access",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
        
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/auth/profile", headers=headers)
                
                if response.status_code == 200:
                    profile = response.json()
                    self.log_result(
                        "User Profile Access",
                        True,
                        f"User profile accessible: {profile.get('name')} ({profile.get('email')})"
                    )
                else:
                    self.log_result(
                        "User Profile Access",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(
                    "User Profile Access",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )

    def test_jersey_browsing_endpoints(self):
        """Test 3: Jersey browsing endpoints (/api/jerseys)"""
        print("👕 Testing Jersey Browsing Endpoints...")
        
        # Test public jersey browsing
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_result(
                    "Jersey Browsing (Public)",
                    True,
                    f"Found {len(jerseys)} jerseys available for public browsing"
                )
            else:
                self.log_result(
                    "Jersey Browsing (Public)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Jersey Browsing (Public)",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test authenticated jersey browsing
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/jerseys", headers=headers)
                
                if response.status_code == 200:
                    jerseys = response.json()
                    self.log_result(
                        "Jersey Browsing (Authenticated)",
                        True,
                        f"Authenticated user can browse {len(jerseys)} jerseys"
                    )
                else:
                    self.log_result(
                        "Jersey Browsing (Authenticated)",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(
                    "Jersey Browsing (Authenticated)",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )

    def test_jersey_filtering_and_search(self):
        """Test 4: Jersey filtering and search functionality"""
        print("🔍 Testing Jersey Filtering and Search Functionality...")
        
        # Test marketplace catalog (for filtering)
        try:
            response = requests.get(f"{BACKEND_URL}/marketplace/catalog")
            
            if response.status_code == 200:
                catalog = response.json()
                self.log_result(
                    "Marketplace Catalog Access",
                    True,
                    f"Marketplace catalog accessible with {len(catalog)} items"
                )
            else:
                self.log_result(
                    "Marketplace Catalog Access",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Marketplace Catalog Access",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test explorer endpoints (for search/filtering)
        try:
            response = requests.get(f"{BACKEND_URL}/explorer/leagues")
            
            if response.status_code == 200:
                leagues = response.json()
                self.log_result(
                    "Explorer Leagues (Search/Filter)",
                    True,
                    f"Explorer leagues accessible with {len(leagues)} leagues"
                )
            else:
                self.log_result(
                    "Explorer Leagues (Search/Filter)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Explorer Leagues (Search/Filter)",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test search functionality with parameters
        try:
            response = requests.get(f"{BACKEND_URL}/jerseys", params={"team": "Barcelona"})
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_result(
                    "Jersey Search by Team",
                    True,
                    f"Search by team parameter returned {len(jerseys)} results"
                )
            else:
                self.log_result(
                    "Jersey Search by Team",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Jersey Search by Team",
                False,
                "",
                f"Exception: {str(e)}"
            )

    def test_user_collection_endpoints(self):
        """Test 5: User collection endpoints"""
        print("📚 Testing User Collection Endpoints...")
        
        if not self.user_token:
            self.log_result("User Collection Endpoints", False, "", "User not authenticated")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test user's collections
        try:
            response = requests.get(f"{BACKEND_URL}/collections/my", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                self.log_result(
                    "User Collections",
                    True,
                    f"User has {len(collections)} items in collection"
                )
            else:
                self.log_result(
                    "User Collections",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "User Collections",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test owned collections
        try:
            response = requests.get(f"{BACKEND_URL}/collections/my-owned", headers=headers)
            
            if response.status_code == 200:
                owned = response.json()
                self.log_result(
                    "User Owned Collection",
                    True,
                    f"User owns {len(owned)} jerseys"
                )
            else:
                self.log_result(
                    "User Owned Collection",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "User Owned Collection",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test wanted collections
        try:
            response = requests.get(f"{BACKEND_URL}/collections/my-wanted", headers=headers)
            
            if response.status_code == 200:
                wanted = response.json()
                self.log_result(
                    "User Wanted Collection",
                    True,
                    f"User wants {len(wanted)} jerseys"
                )
            else:
                self.log_result(
                    "User Wanted Collection",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "User Wanted Collection",
                False,
                "",
                f"Exception: {str(e)}"
            )

    def test_core_backend_functionality(self):
        """Test 6: Other core backend functionality"""
        print("⚙️ Testing Other Core Backend Functionality...")
        
        # Test site configuration
        try:
            response = requests.get(f"{BACKEND_URL}/site/mode")
            
            if response.status_code == 200:
                site_config = response.json()
                self.log_result(
                    "Site Configuration",
                    True,
                    f"Site mode: {site_config.get('mode', 'unknown')}"
                )
            else:
                self.log_result(
                    "Site Configuration",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Site Configuration",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test listings endpoint
        try:
            response = requests.get(f"{BACKEND_URL}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                self.log_result(
                    "Marketplace Listings",
                    True,
                    f"Marketplace has {len(listings)} active listings"
                )
            else:
                self.log_result(
                    "Marketplace Listings",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Marketplace Listings",
                False,
                "",
                f"Exception: {str(e)}"
            )
        
        # Test admin endpoints (if admin authenticated)
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            try:
                response = requests.get(f"{BACKEND_URL}/admin/users", headers=headers)
                
                if response.status_code == 200:
                    users_data = response.json()
                    users = users_data.get('users', [])
                    self.log_result(
                        "Admin User Management",
                        True,
                        f"Admin can access {len(users)} users"
                    )
                else:
                    self.log_result(
                        "Admin User Management",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(
                    "Admin User Management",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )
            
            try:
                response = requests.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
                
                if response.status_code == 200:
                    pending = response.json()
                    self.log_result(
                        "Admin Pending Jerseys",
                        True,
                        f"Admin can access {len(pending)} pending jerseys"
                    )
                else:
                    self.log_result(
                        "Admin Pending Jerseys",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_result(
                    "Admin Pending Jerseys",
                    False,
                    "",
                    f"Exception: {str(e)}"
                )

    def test_jersey_submission(self):
        """Test jersey submission functionality"""
        print("📝 Testing Jersey Submission Functionality...")
        
        if not self.user_token:
            self.log_result("Jersey Submission", False, "", "User not authenticated")
            return
        
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official Real Madrid home jersey for 2024-25 season featuring Vinicius Jr #7",
            "images": ["https://example.com/real-madrid-vinicius.jpg"]
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.jersey_id = data.get("id")
                jersey_ref = data.get("reference_number", "N/A")
                self.log_result(
                    "Jersey Submission",
                    True,
                    f"Jersey submitted successfully. ID: {self.jersey_id}, Ref: {jersey_ref}, Status: {data.get('status')}"
                )
            else:
                self.log_result(
                    "Jersey Submission",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_result(
                "Jersey Submission",
                False,
                "",
                f"Exception: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests in the correct sequence"""
        print("🚀 TOPKIT BACKEND TESTING - REVIEW REQUEST COMPREHENSIVE TEST")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Credentials: {ADMIN_EMAIL}")
        print(f"User Credentials: {USER_EMAIL}")
        print("=" * 80)
        
        # Run all tests
        tests = [
            self.test_api_health,
            self.test_authentication_endpoints,
            self.test_jersey_browsing_endpoints,
            self.test_jersey_filtering_and_search,
            self.test_user_collection_endpoints,
            self.test_core_backend_functionality,
            self.test_jersey_submission
        ]
        
        for test in tests:
            test()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 TOPKIT BACKEND TESTING SUMMARY - REVIEW REQUEST")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize results by review request areas
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"] or "Profile" in r["test"]]
        jersey_tests = [r for r in self.test_results if "Jersey" in r["test"]]
        collection_tests = [r for r in self.test_results if "Collection" in r["test"]]
        core_tests = [r for r in self.test_results if "API Health" in r["test"] or "Site" in r["test"] or "Admin" in r["test"] or "Marketplace" in r["test"]]
        
        auth_passed = sum(1 for r in auth_tests if r["success"])
        jersey_passed = sum(1 for r in jersey_tests if r["success"])
        collection_passed = sum(1 for r in collection_tests if r["success"])
        core_passed = sum(1 for r in core_tests if r["success"])
        
        print("🎯 REVIEW REQUEST AREAS ASSESSMENT:")
        print(f"1. Basic API Connectivity & Health: {core_passed}/{len(core_tests)} passed ({(core_passed/len(core_tests)*100) if core_tests else 0:.1f}%)")
        print(f"2. Authentication Endpoints: {auth_passed}/{len(auth_tests)} passed ({(auth_passed/len(auth_tests)*100) if auth_tests else 0:.1f}%)")
        print(f"3. Jersey Browsing & Search: {jersey_passed}/{len(jersey_tests)} passed ({(jersey_passed/len(jersey_tests)*100) if jersey_tests else 0:.1f}%)")
        print(f"4. User Collection Endpoints: {collection_passed}/{len(collection_tests)} passed ({(collection_passed/len(collection_tests)*100) if collection_tests else 0:.1f}%)")
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
        
        print("\n" + "=" * 80)
        print("🏆 FINAL ASSESSMENT:")
        
        if success_rate >= 95:
            assessment = "EXCELLENT - All systems operational"
        elif success_rate >= 85:
            assessment = "GOOD - Minor issues identified"
        elif success_rate >= 70:
            assessment = "ACCEPTABLE - Some issues need attention"
        else:
            assessment = "NEEDS ATTENTION - Multiple issues found"
        
        print(f"Backend Status: {assessment}")
        print(f"Frontend Changes Impact: {'MINIMAL' if success_rate >= 90 else 'MODERATE' if success_rate >= 75 else 'SIGNIFICANT'}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "results": self.test_results,
            "assessment": assessment
        }

if __name__ == "__main__":
    tester = TopKitBackendTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed_tests"] == 0 else 1)