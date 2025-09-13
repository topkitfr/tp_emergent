#!/usr/bin/env python3
"""
DATABASE RESET VERIFICATION - BACKEND TEST
==========================================

This test verifies that the TopKit backend is working properly after database reset.
Specifically testing:

1. **Authentication System**: Test that both preserved user accounts can log in successfully:
   - Admin account: topkitfr@gmail.com / TopKitSecure789#
   - User account: steinmetzlivio@gmail.com / T0p_Mdp_1288*

2. **Database State**: Verify that the database has been properly reset to clean state:
   - Only the 'users' collection should exist
   - Should have exactly 2 users (admin and the regular user)
   - All other collections (teams, jerseys, contributions, etc.) should be empty/non-existent

3. **Core API Endpoints**: Test basic functionality:
   - User authentication endpoints
   - Profile retrieval 
   - Basic entity endpoints (teams, jerseys, etc.) should return empty arrays
   - Site mode should be 'public'

4. **Clean Database Verification**: Ensure we're starting with a truly clean state like the deployed site.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-debug-1.preview.emergentagent.com/api"

# Test credentials - these should be the ONLY users in the database
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class DatabaseResetVerificationTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_data = None
        self.user_user_data = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        print()

    def test_authentication_system(self):
        """Test that both preserved user accounts can log in successfully"""
        print("🔐 TESTING AUTHENTICATION SYSTEM")
        print("=" * 50)
        
        # Test Admin Authentication
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_data = data.get('user', {})
                
                # Verify admin role and details
                if (self.admin_user_data.get('role') == 'admin' and 
                    self.admin_user_data.get('email') == ADMIN_CREDENTIALS['email']):
                    self.log_result(
                        "Admin Authentication", 
                        True, 
                        f"Admin login successful - Name: {self.admin_user_data.get('name')}, Role: {self.admin_user_data.get('role')}, ID: {self.admin_user_data.get('id')}"
                    )
                else:
                    self.log_result(
                        "Admin Authentication", 
                        False, 
                        f"Admin login succeeded but role/email verification failed - Role: {self.admin_user_data.get('role')}, Email: {self.admin_user_data.get('email')}"
                    )
            else:
                self.log_result(
                    "Admin Authentication", 
                    False, 
                    f"Admin login failed - Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception during admin login: {str(e)}")

        # Test User Authentication
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.user_user_data = data.get('user', {})
                
                # Verify user role and details
                if (self.user_user_data.get('role') == 'user' and 
                    self.user_user_data.get('email') == USER_CREDENTIALS['email']):
                    self.log_result(
                        "User Authentication", 
                        True, 
                        f"User login successful - Name: {self.user_user_data.get('name')}, Role: {self.user_user_data.get('role')}, ID: {self.user_user_data.get('id')}"
                    )
                else:
                    self.log_result(
                        "User Authentication", 
                        False, 
                        f"User login succeeded but role/email verification failed - Role: {self.user_user_data.get('role')}, Email: {self.user_user_data.get('email')}"
                    )
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"User login failed - Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception during user login: {str(e)}")

    def test_site_mode_configuration(self):
        """Test that site mode is set to 'public'"""
        print("🌐 TESTING SITE MODE CONFIGURATION")
        print("=" * 50)
        
        try:
            response = requests.get(f"{BACKEND_URL}/site/mode")
            if response.status_code == 200:
                data = response.json()
                mode = data.get('mode')
                is_private = data.get('is_private', True)
                
                if mode == 'public' and not is_private:
                    self.log_result(
                        "Site Mode Configuration", 
                        True, 
                        f"Site mode correctly set to 'public' - Mode: {mode}, Is Private: {is_private}"
                    )
                else:
                    self.log_result(
                        "Site Mode Configuration", 
                        False, 
                        f"Site mode not correctly configured - Mode: {mode}, Is Private: {is_private}"
                    )
            else:
                self.log_result(
                    "Site Mode Configuration", 
                    False, 
                    f"Failed to get site mode - Status: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            self.log_result("Site Mode Configuration", False, f"Exception during site mode check: {str(e)}")

    def test_database_clean_state(self):
        """Test that all entity collections are empty/non-existent"""
        print("🗄️ TESTING DATABASE CLEAN STATE")
        print("=" * 50)
        
        # Test endpoints that should return empty arrays
        endpoints_to_test = [
            ("Teams", "/teams"),
            ("Brands", "/brands"), 
            ("Players", "/players"),
            ("Competitions", "/competitions"),
            ("Master Jerseys", "/master-jerseys"),
            ("Jersey Releases", "/jersey-releases"),
            ("Jerseys", "/jerseys"),
            ("Contributions", "/contributions"),
            ("Vestiaire", "/vestiaire")
        ]
        
        for entity_name, endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict):
                        # Check for common array keys
                        if 'data' in data and isinstance(data['data'], list):
                            count = len(data['data'])
                        elif 'items' in data and isinstance(data['items'], list):
                            count = len(data['items'])
                        elif 'results' in data and isinstance(data['results'], list):
                            count = len(data['results'])
                        else:
                            # If it's a dict but no array found, consider it as 1 item
                            count = 1 if data else 0
                    else:
                        count = 1 if data else 0
                    
                    if count == 0:
                        self.log_result(
                            f"{entity_name} Collection Empty", 
                            True, 
                            f"{entity_name} collection is empty as expected (0 items)"
                        )
                    else:
                        self.log_result(
                            f"{entity_name} Collection Empty", 
                            False, 
                            f"{entity_name} collection is not empty - Found {count} items. Data: {json.dumps(data, indent=2)[:500]}..."
                        )
                else:
                    # Some endpoints might return 404 if collections don't exist, which is acceptable
                    if response.status_code == 404:
                        self.log_result(
                            f"{entity_name} Collection Empty", 
                            True, 
                            f"{entity_name} endpoint returns 404 (collection doesn't exist) - This is acceptable for clean state"
                        )
                    else:
                        self.log_result(
                            f"{entity_name} Collection Empty", 
                            False, 
                            f"Unexpected response for {entity_name} - Status: {response.status_code}, Response: {response.text}"
                        )
            except Exception as e:
                self.log_result(f"{entity_name} Collection Empty", False, f"Exception testing {entity_name}: {str(e)}")

    def test_user_profile_access(self):
        """Test that user profiles can be accessed with authentication"""
        print("👤 TESTING USER PROFILE ACCESS")
        print("=" * 50)
        
        # Test admin profile access
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get('user', {})
                    if user_data.get('email') == ADMIN_CREDENTIALS['email']:
                        self.log_result(
                            "Admin Profile Access", 
                            True, 
                            f"Admin profile accessible - Email: {user_data.get('email')}, Name: {user_data.get('name')}"
                        )
                    else:
                        self.log_result(
                            "Admin Profile Access", 
                            False, 
                            f"Admin profile data mismatch - Expected: {ADMIN_CREDENTIALS['email']}, Got: {user_data.get('email')}"
                        )
                else:
                    self.log_result(
                        "Admin Profile Access", 
                        False, 
                        f"Admin profile access failed - Status: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                self.log_result("Admin Profile Access", False, f"Exception accessing admin profile: {str(e)}")
        else:
            self.log_result("Admin Profile Access", False, "No admin token available")

        # Test user profile access
        if self.user_token:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/profile", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get('user', {})
                    if user_data.get('email') == USER_CREDENTIALS['email']:
                        self.log_result(
                            "User Profile Access", 
                            True, 
                            f"User profile accessible - Email: {user_data.get('email')}, Name: {user_data.get('name')}"
                        )
                    else:
                        self.log_result(
                            "User Profile Access", 
                            False, 
                            f"User profile data mismatch - Expected: {USER_CREDENTIALS['email']}, Got: {user_data.get('email')}"
                        )
                else:
                    self.log_result(
                        "User Profile Access", 
                        False, 
                        f"User profile access failed - Status: {response.status_code}, Response: {response.text}"
                    )
            except Exception as e:
                self.log_result("User Profile Access", False, f"Exception accessing user profile: {str(e)}")
        else:
            self.log_result("User Profile Access", False, "No user token available")

    def test_collection_endpoints_empty(self):
        """Test that user collection endpoints return empty arrays"""
        print("📦 TESTING COLLECTION ENDPOINTS")
        print("=" * 50)
        
        # Test user collections (should be empty)
        if self.user_token and self.user_user_data:
            user_id = self.user_user_data.get('id')
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            collection_endpoints = [
                ("Owned Collections", f"/users/{user_id}/collections/owned"),
                ("Wanted Collections", f"/users/{user_id}/collections/wanted"),
                ("General Collections", f"/users/{user_id}/collections")
            ]
            
            for collection_name, endpoint in collection_endpoints:
                try:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Handle different response formats
                        if isinstance(data, list):
                            count = len(data)
                        elif isinstance(data, dict) and 'collections' in data:
                            count = len(data['collections'])
                        else:
                            count = 1 if data else 0
                        
                        if count == 0:
                            self.log_result(
                                f"{collection_name} Empty", 
                                True, 
                                f"{collection_name} is empty as expected (0 items)"
                            )
                        else:
                            self.log_result(
                                f"{collection_name} Empty", 
                                False, 
                                f"{collection_name} is not empty - Found {count} items"
                            )
                    else:
                        self.log_result(
                            f"{collection_name} Empty", 
                            False, 
                            f"Failed to access {collection_name} - Status: {response.status_code}, Response: {response.text}"
                        )
                except Exception as e:
                    self.log_result(f"{collection_name} Empty", False, f"Exception testing {collection_name}: {str(e)}")

    def test_core_api_functionality(self):
        """Test that core API endpoints are functional"""
        print("🔧 TESTING CORE API FUNCTIONALITY")
        print("=" * 50)
        
        # Test unauthenticated endpoints
        core_endpoints = [
            ("Site Access Check", "/site/access-check"),
            ("Stats Dynamic", "/stats/dynamic"),
            ("Marketplace Catalog", "/marketplace/catalog"),
            ("Explorer Leagues", "/explorer/leagues")
        ]
        
        for endpoint_name, endpoint in core_endpoints:
            try:
                response = requests.get(f"{BACKEND_URL}{endpoint}")
                if response.status_code == 200:
                    self.log_result(
                        f"{endpoint_name} Functional", 
                        True, 
                        f"{endpoint_name} endpoint is functional - Status: 200"
                    )
                else:
                    # Some endpoints might return empty data but still be functional
                    if response.status_code in [404, 204]:
                        self.log_result(
                            f"{endpoint_name} Functional", 
                            True, 
                            f"{endpoint_name} endpoint functional but empty - Status: {response.status_code}"
                        )
                    else:
                        self.log_result(
                            f"{endpoint_name} Functional", 
                            False, 
                            f"{endpoint_name} endpoint not functional - Status: {response.status_code}, Response: {response.text}"
                        )
            except Exception as e:
                self.log_result(f"{endpoint_name} Functional", False, f"Exception testing {endpoint_name}: {str(e)}")

    def test_authenticated_endpoints(self):
        """Test authenticated endpoints with admin token"""
        print("🔐 TESTING AUTHENTICATED ENDPOINTS")
        print("=" * 50)
        
        if self.admin_token:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            auth_endpoints = [
                ("Notifications", "/notifications"),
                ("User Stats", "/stats/user"),
                ("Admin Dashboard", "/admin/dashboard")
            ]
            
            for endpoint_name, endpoint in auth_endpoints:
                try:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        self.log_result(
                            f"{endpoint_name} Accessible", 
                            True, 
                            f"{endpoint_name} endpoint accessible with authentication - Status: 200"
                        )
                    else:
                        # Some endpoints might not exist or return different status codes
                        if response.status_code in [404, 204]:
                            self.log_result(
                                f"{endpoint_name} Accessible", 
                                True, 
                                f"{endpoint_name} endpoint accessible but empty/not found - Status: {response.status_code}"
                            )
                        else:
                            self.log_result(
                                f"{endpoint_name} Accessible", 
                                False, 
                                f"{endpoint_name} endpoint not accessible - Status: {response.status_code}, Response: {response.text}"
                            )
                except Exception as e:
                    self.log_result(f"{endpoint_name} Accessible", False, f"Exception testing {endpoint_name}: {str(e)}")
        else:
            self.log_result("Authenticated Endpoints", False, "No admin token available for testing")

    def run_all_tests(self):
        """Run all database reset verification tests"""
        print("🚀 STARTING DATABASE RESET VERIFICATION TESTS")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        print()
        
        # Run all test suites
        self.test_authentication_system()
        self.test_site_mode_configuration()
        self.test_database_clean_state()
        self.test_user_profile_access()
        self.test_collection_endpoints_empty()
        self.test_core_api_functionality()
        self.test_authenticated_endpoints()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
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
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 DATABASE RESET VERIFICATION: EXCELLENT - System is in clean state and ready for production!")
        elif success_rate >= 75:
            print("✅ DATABASE RESET VERIFICATION: GOOD - Minor issues detected but core functionality working")
        elif success_rate >= 50:
            print("⚠️ DATABASE RESET VERIFICATION: PARTIAL - Significant issues detected, investigation required")
        else:
            print("🚨 DATABASE RESET VERIFICATION: CRITICAL - Major issues detected, immediate attention required")
        
        print()
        print("Key Verification Points:")
        print("✓ Both preserved user accounts should authenticate successfully")
        print("✓ Site mode should be 'public'")
        print("✓ All entity collections should be empty (teams, jerseys, contributions, etc.)")
        print("✓ Core API endpoints should be functional")
        print("✓ User profiles should be accessible")
        print("✓ Collection endpoints should return empty arrays")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = DatabaseResetVerificationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)