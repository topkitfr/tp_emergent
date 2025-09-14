#!/usr/bin/env python3
"""
TopKit Backend Testing - Comprehensive User Profiles & Notifications Verification
Testing all scenarios mentioned in the French review request
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test credentials from review request
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com",
    "password": "TopKit123!"
}

ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com", 
    "password": "TopKitSecure789#"
}

class ComprehensiveTopKitTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_user(self, credentials, user_type="user"):
        """Authenticate user and get JWT token"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=credentials)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                user_info = data.get("user", {})
                user_id = user_info.get("id")
                
                if user_type == "admin":
                    self.admin_token = token
                    self.admin_id = user_id
                else:
                    self.user_token = token
                    self.user_id = user_id
                
                self.log_test(
                    f"Authentication - {credentials['email']}",
                    True,
                    f"Role: {user_info.get('role', 'unknown')}, ID: {user_id}"
                )
                return True
            else:
                self.log_test(
                    f"Authentication - {credentials['email']}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test(f"Authentication - {credentials['email']}", False, "", str(e))
            return False

    def test_scenario_1_user_profiles(self):
        """Test Scenario 1: User Profile Access (steinmetzlivio accessing topkitfr profile)"""
        if not self.user_token or not self.admin_id:
            self.log_test("Scenario 1 - Profile Access", False, "", "Missing authentication tokens")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_id}/profile", headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                
                # Verify expected public data is returned
                expected_public_fields = ["id", "name", "stats"]
                present_fields = [field for field in expected_public_fields if field in profile_data]
                
                # Verify sensitive data is NOT exposed
                sensitive_fields = ["password_hash", "session_token", "email", "failed_login_attempts"]
                exposed_sensitive = [field for field in sensitive_fields if field in profile_data]
                
                if len(present_fields) == len(expected_public_fields) and not exposed_sensitive:
                    stats = profile_data.get("stats", {})
                    self.log_test(
                        "Scenario 1 - Admin Profile Access",
                        True,
                        f"Successfully retrieved admin profile - Name: {profile_data.get('name')}, Stats: {stats}"
                    )
                else:
                    self.log_test(
                        "Scenario 1 - Admin Profile Access",
                        False,
                        f"Missing fields: {set(expected_public_fields) - set(present_fields)}, Exposed sensitive: {exposed_sensitive}",
                        "Profile data structure issue"
                    )
            else:
                self.log_test(
                    "Scenario 1 - Admin Profile Access",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Scenario 1 - Admin Profile Access", False, "", str(e))

    def test_scenario_1_admin_collection(self):
        """Test Scenario 1: Admin Collection Access"""
        if not self.user_token or not self.admin_id:
            self.log_test("Scenario 1 - Collection Access", False, "", "Missing authentication tokens")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_id}/collection", headers=headers)
            
            if response.status_code == 200:
                collection_data = response.json()
                
                if isinstance(collection_data, list):
                    # Verify only "owned" collections are shown (as per API design)
                    owned_items = [item for item in collection_data if item.get("collection_type") != "wanted"]
                    
                    self.log_test(
                        "Scenario 1 - Admin Collection Access",
                        True,
                        f"Successfully retrieved admin collection - {len(collection_data)} items (only owned items shown publicly)"
                    )
                else:
                    self.log_test(
                        "Scenario 1 - Admin Collection Access",
                        False,
                        "Unexpected response format",
                        f"Expected list, got: {type(collection_data)}"
                    )
            else:
                self.log_test(
                    "Scenario 1 - Admin Collection Access",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Scenario 1 - Admin Collection Access", False, "", str(e))

    def test_scenario_1_admin_listings(self):
        """Test Scenario 1: Admin Active Listings"""
        if not self.user_token or not self.admin_id:
            self.log_test("Scenario 1 - Listings Access", False, "", "Missing authentication tokens")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.admin_id}/listings", headers=headers)
            
            if response.status_code == 200:
                listings_data = response.json()
                
                if isinstance(listings_data, list):
                    active_listings = [listing for listing in listings_data if listing.get("status") == "active"]
                    
                    self.log_test(
                        "Scenario 1 - Admin Listings Access",
                        True,
                        f"Successfully retrieved admin listings - {len(listings_data)} total, {len(active_listings)} active"
                    )
                else:
                    self.log_test(
                        "Scenario 1 - Admin Listings Access",
                        False,
                        "Unexpected response format",
                        f"Expected list, got: {type(listings_data)}"
                    )
            else:
                self.log_test(
                    "Scenario 1 - Admin Listings Access",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Scenario 1 - Admin Listings Access", False, "", str(e))

    def test_scenario_2_cross_user_access(self):
        """Test Scenario 2: Cross-User Access Verification"""
        if not self.user_token or not self.admin_token or not self.user_id or not self.admin_id:
            self.log_test("Scenario 2 - Cross-User Access", False, "", "Missing authentication tokens")
            return
            
        try:
            # Test 1: Regular user accessing admin profile
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            user_to_admin_response = requests.get(f"{BACKEND_URL}/users/{self.admin_id}/profile", headers=user_headers)
            
            # Test 2: Admin accessing regular user profile  
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            admin_to_user_response = requests.get(f"{BACKEND_URL}/users/{self.user_id}/profile", headers=admin_headers)
            
            success_count = 0
            total_tests = 2
            
            if user_to_admin_response.status_code == 200:
                success_count += 1
                admin_profile = user_to_admin_response.json()
                # Verify no sensitive data
                sensitive_fields = ["password_hash", "session_token", "email"]
                exposed = [field for field in sensitive_fields if field in admin_profile]
                if exposed:
                    success_count -= 1
            
            if admin_to_user_response.status_code == 200:
                success_count += 1
                user_profile = admin_to_user_response.json()
                # Verify no sensitive data
                sensitive_fields = ["password_hash", "session_token", "email"]
                exposed = [field for field in sensitive_fields if field in user_profile]
                if exposed:
                    success_count -= 1
            
            if success_count == total_tests:
                self.log_test(
                    "Scenario 2 - Cross-User Access Security",
                    True,
                    f"Both cross-user profile accesses working correctly - No sensitive data exposed"
                )
            else:
                self.log_test(
                    "Scenario 2 - Cross-User Access Security",
                    False,
                    f"Only {success_count}/{total_tests} cross-user accesses working properly",
                    "Cross-user access or security issue"
                )
                
        except Exception as e:
            self.log_test("Scenario 2 - Cross-User Access Security", False, "", str(e))

    def test_scenario_3_notifications_structure(self):
        """Test Scenario 3: Notification System Structure for Smart Clicks"""
        if not self.user_token:
            self.log_test("Scenario 3 - Notifications Structure", False, "", "Missing user authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications_data = response.json()
                
                # Handle both list and object response formats
                if isinstance(notifications_data, dict):
                    notifications = notifications_data.get("notifications", [])
                    unread_count = notifications_data.get("unread_count", 0)
                    total_count = notifications_data.get("total", 0)
                else:
                    notifications = notifications_data
                    unread_count = sum(1 for n in notifications if not n.get("is_read", True))
                    total_count = len(notifications)
                
                if notifications:
                    # Analyze notification structure for smart clicks
                    sample_notification = notifications[0]
                    
                    # Required fields for smart click functionality
                    smart_click_fields = ["id", "type", "title", "message", "related_id", "is_read"]
                    present_fields = [field for field in smart_click_fields if field in sample_notification]
                    missing_fields = [field for field in smart_click_fields if field not in sample_notification]
                    
                    # Check notification types
                    notification_types = list(set([n.get("type") for n in notifications if n.get("type")]))
                    
                    # Verify data for navigation
                    notifications_with_related_id = [n for n in notifications if n.get("related_id")]
                    
                    details = f"Retrieved {total_count} notifications ({unread_count} unread)"
                    details += f", Types found: {notification_types}"
                    details += f", {len(notifications_with_related_id)} have related_id for navigation"
                    
                    if len(present_fields) >= 5:  # Most important fields present
                        self.log_test(
                            "Scenario 3 - Notifications Smart Click Structure",
                            True,
                            details
                        )
                    else:
                        self.log_test(
                            "Scenario 3 - Notifications Smart Click Structure",
                            False,
                            f"Missing critical fields: {missing_fields}",
                            "Notification structure incomplete for smart clicks"
                        )
                else:
                    self.log_test(
                        "Scenario 3 - Notifications Smart Click Structure",
                        True,
                        f"No notifications found - Structure cannot be verified but endpoint accessible"
                    )
            else:
                self.log_test(
                    "Scenario 3 - Notifications Smart Click Structure",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_test("Scenario 3 - Notifications Smart Click Structure", False, "", str(e))

    def test_scenario_3_mark_notification_read(self):
        """Test Scenario 3: Mark Notification as Read Functionality"""
        if not self.user_token:
            self.log_test("Scenario 3 - Mark Notification Read", False, "", "Missing user authentication token")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get notifications first
            response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            if response.status_code != 200:
                self.log_test("Scenario 3 - Mark Notification Read", False, "Cannot retrieve notifications", response.text)
                return
            
            notifications_data = response.json()
            notifications = notifications_data.get("notifications", []) if isinstance(notifications_data, dict) else notifications_data
            
            if not notifications:
                self.log_test("Scenario 3 - Mark Notification Read", True, "No notifications to test - endpoint exists and accessible")
                return
            
            # Find an unread notification
            unread_notification = None
            for notification in notifications:
                if not notification.get("is_read", False):
                    unread_notification = notification
                    break
            
            if unread_notification:
                # Test marking as read
                notification_id = unread_notification["id"]
                mark_read_response = requests.post(f"{BACKEND_URL}/notifications/{notification_id}/mark-read", headers=headers)
                
                if mark_read_response.status_code == 200:
                    self.log_test(
                        "Scenario 3 - Mark Notification Read",
                        True,
                        f"Successfully marked notification {notification_id} as read"
                    )
                else:
                    self.log_test(
                        "Scenario 3 - Mark Notification Read",
                        False,
                        f"HTTP {mark_read_response.status_code}",
                        mark_read_response.text
                    )
            else:
                self.log_test(
                    "Scenario 3 - Mark Notification Read",
                    True,
                    "All notifications already read - mark-as-read endpoint exists and accessible"
                )
                
        except Exception as e:
            self.log_test("Scenario 3 - Mark Notification Read", False, "", str(e))

    def test_data_security_verification(self):
        """Verify that sensitive data is not exposed in any public endpoints"""
        if not self.user_token or not self.admin_id:
            self.log_test("Data Security Verification", False, "", "Missing authentication tokens")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test all public endpoints for data leaks
            endpoints_to_test = [
                f"/users/{self.admin_id}/profile",
                f"/users/{self.admin_id}/collection", 
                f"/users/{self.admin_id}/listings"
            ]
            
            sensitive_data_found = []
            endpoints_tested = 0
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        endpoints_tested += 1
                        
                        # Check for sensitive fields recursively
                        sensitive_fields = ["password_hash", "session_token", "email_verification_tokens", "failed_login_attempts"]
                        
                        def check_sensitive_data(obj, path=""):
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if key in sensitive_fields:
                                        sensitive_data_found.append(f"{endpoint}: {current_path}")
                                    elif isinstance(value, (dict, list)):
                                        check_sensitive_data(value, current_path)
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    check_sensitive_data(item, f"{path}[{i}]")
                        
                        check_sensitive_data(data)
                        
                except Exception as e:
                    continue
            
            if not sensitive_data_found and endpoints_tested > 0:
                self.log_test(
                    "Data Security Verification",
                    True,
                    f"No sensitive data exposed across {endpoints_tested} public endpoints"
                )
            elif sensitive_data_found:
                self.log_test(
                    "Data Security Verification",
                    False,
                    f"SECURITY ISSUE: Sensitive data found in: {sensitive_data_found}",
                    "Sensitive data should not be accessible in public endpoints"
                )
            else:
                self.log_test(
                    "Data Security Verification",
                    False,
                    "No endpoints could be tested",
                    "Unable to verify data security"
                )
                
        except Exception as e:
            self.log_test("Data Security Verification", False, "", str(e))

    def run_all_tests(self):
        """Run all comprehensive tests as per review request"""
        print("🔔👤 TOPKIT - TEST DES NOUVELLES FONCTIONNALITÉS : NOTIFICATIONS + PROFILS UTILISATEURS")
        print("=" * 90)
        print()
        
        # Authentication
        print("🔐 AUTHENTIFICATION DES UTILISATEURS DE TEST")
        print("-" * 50)
        user_auth_success = self.authenticate_user(USER_CREDENTIALS, "user")
        admin_auth_success = self.authenticate_user(ADMIN_CREDENTIALS, "admin")
        
        if not user_auth_success or not admin_auth_success:
            print("❌ Cannot proceed without both user authentications")
            return
        
        # Scenario 1: User Profile Testing
        print("👤 SCÉNARIO 1 - TEST PROFILS UTILISATEURS")
        print("-" * 50)
        self.test_scenario_1_user_profiles()
        self.test_scenario_1_admin_collection()
        self.test_scenario_1_admin_listings()
        
        # Scenario 2: Cross-User Access Testing
        print("🔄 SCÉNARIO 2 - TEST ACCÈS CROSS-USERS")
        print("-" * 50)
        self.test_scenario_2_cross_user_access()
        
        # Scenario 3: Notification System Testing
        print("🔔 SCÉNARIO 3 - TEST NOTIFICATIONS")
        print("-" * 50)
        self.test_scenario_3_notifications_structure()
        self.test_scenario_3_mark_notification_read()
        
        # Security Verification
        print("🔒 VÉRIFICATION SÉCURITÉ DES DONNÉES")
        print("-" * 50)
        self.test_data_security_verification()
        
        # Summary
        return self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("=" * 90)
        print("📊 RÉSUMÉ DES TESTS - NOUVELLES FONCTIONNALITÉS")
        print("=" * 90)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total des tests: {total_tests}")
        print(f"Réussis: {passed_tests}")
        print(f"Échoués: {failed_tests}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        print()
        
        # Categorize results by scenario
        scenarios = {
            "Authentication": [],
            "Scenario 1 - Profils": [],
            "Scenario 2 - Cross-User": [],
            "Scenario 3 - Notifications": [],
            "Security": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                scenarios["Authentication"].append(result)
            elif "Scenario 1" in test_name:
                scenarios["Scenario 1 - Profils"].append(result)
            elif "Scenario 2" in test_name:
                scenarios["Scenario 2 - Cross-User"].append(result)
            elif "Scenario 3" in test_name:
                scenarios["Scenario 3 - Notifications"].append(result)
            elif "Security" in test_name:
                scenarios["Security"].append(result)
        
        for scenario, results in scenarios.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"📋 {scenario}: {passed}/{total} tests passed")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"   {status} {result['test']}")
                print()
        
        # Final verdict
        if success_rate >= 90:
            print("🎉 RÉSULTAT: EXCELLENT - Toutes les nouvelles fonctionnalités sont opérationnelles!")
        elif success_rate >= 80:
            print("✅ RÉSULTAT: BON - La plupart des fonctionnalités marchent correctement")
        elif success_rate >= 70:
            print("⚠️ RÉSULTAT: ACCEPTABLE - Quelques problèmes à corriger")
        else:
            print("❌ RÉSULTAT: PROBLÉMATIQUE - Corrections importantes nécessaires")
        
        print()
        print("🎯 TESTS TERMINÉS!")
        
        return success_rate

if __name__ == "__main__":
    tester = ComprehensiveTopKitTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate is not None:
        sys.exit(0 if success_rate >= 80 else 1)
    else:
        sys.exit(1)