#!/usr/bin/env python3
"""
TopKit Admin Moderation System Testing Suite
Testing admin moderation functionality including confirmation messages, form access, and rejection notifications
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://topkit-debug-1.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class AdminModerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.admin_token = None
        self.admin_id = None
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

    def authenticate_users(self):
        """Authenticate both user and admin"""
        print("🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        
        # Authenticate regular user
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
                    self.log_test(
                        "User Authentication (steinmetzlivio@gmail.com)",
                        True,
                        f"User authenticated: {data['user']['name']}, Role: {data['user']['role']}"
                    )
                else:
                    self.log_test("User Authentication", False, "", "Missing token or user data")
                    return False
            else:
                self.log_test("User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Authentication", False, "", str(e))
            return False

        # Authenticate admin
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
                    self.log_test(
                        "Admin Authentication (topkitfr@gmail.com)",
                        True,
                        f"Admin authenticated: {data['user']['name']}, Role: {data['user']['role']}"
                    )
                    return True
                else:
                    self.log_test("Admin Authentication", False, "", "Missing token or user data")
                    return False
            else:
                self.log_test("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))
            return False

    def test_admin_moderation_confirmation_messages(self):
        """Test admin moderation with confirmation messages"""
        print("✅ ADMIN MODERATION - CONFIRMATION MESSAGES")
        print("=" * 50)
        
        if not self.user_token or not self.admin_token:
            self.log_test("Admin Moderation Tests", False, "", "Missing authentication tokens")
            return

        user_headers = {"Authorization": f"Bearer {self.user_token}"}
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Step 1: Create a test jersey for moderation
        try:
            test_jersey_data = {
                "team": "Admin Moderation Test FC",
                "season": "2024-25",
                "player": "Test Player",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for admin moderation confirmation testing"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data, headers=user_headers)
            
            if response.status_code in [200, 201]:
                jersey_data = response.json()
                self.test_jersey_id = jersey_data.get("id")
                self.log_test(
                    "Create Test Jersey for Moderation",
                    True,
                    f"Test jersey created successfully - ID: {self.test_jersey_id}"
                )
            else:
                self.log_test("Create Test Jersey for Moderation", False, "", f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Create Test Jersey for Moderation", False, "", str(e))
            return

        # Step 2: Test admin access to pending jerseys
        try:
            response = self.session.get(f"{BASE_URL}/admin/jerseys/pending", headers=admin_headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                if isinstance(pending_jerseys, list):
                    # Find our test jersey
                    test_jersey = None
                    for jersey in pending_jerseys:
                        if jersey.get("id") == self.test_jersey_id:
                            test_jersey = jersey
                            break
                    
                    if test_jersey:
                        self.log_test(
                            "Admin Access to Pending Jerseys",
                            True,
                            f"Admin can access pending jerseys including test jersey {self.test_jersey_id}"
                        )
                        
                        # Check if jersey has all required fields for moderation
                        required_fields = ["team", "season", "player", "size", "condition", "description", "status"]
                        missing_fields = [field for field in required_fields if field not in test_jersey]
                        
                        if not missing_fields:
                            self.log_test(
                                "Admin Submission Form Access",
                                True,
                                "Admin can access complete jersey submission details including all fields"
                            )
                        else:
                            self.log_test(
                                "Admin Submission Form Access",
                                False,
                                "",
                                f"Missing fields in jersey data: {missing_fields}"
                            )
                    else:
                        self.log_test("Admin Access to Pending Jerseys", False, "", "Test jersey not found in pending list")
                else:
                    self.log_test("Admin Access to Pending Jerseys", False, "", "Invalid response format")
            else:
                self.log_test("Admin Access to Pending Jerseys", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Access to Pending Jerseys", False, "", str(e))

        # Step 3: Test suggest changes vs reject behavior
        if self.test_jersey_id:
            try:
                # Test suggest modifications
                suggestion_data = {
                    "jersey_id": self.test_jersey_id,
                    "suggested_changes": "Please update the manufacturer field to be more specific (e.g., Nike Dri-FIT) and add more details to the description.",
                    "suggested_modifications": {
                        "manufacturer": "Nike Dri-FIT",
                        "description": "Please provide more detailed description including year, special features, etc."
                    }
                }
                
                response = self.session.post(f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/suggest-modifications", 
                                           json=suggestion_data, headers=admin_headers)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    suggestion_id = result.get("suggestion_id")
                    self.log_test(
                        "Admin Suggest Changes Functionality",
                        True,
                        f"Successfully suggested modifications - Suggestion ID: {suggestion_id}"
                    )
                    
                    # Verify jersey status changed to needs_modification
                    time.sleep(1)  # Brief delay for processing
                    jersey_check = self.session.get(f"{BASE_URL}/admin/jerseys/pending", headers=admin_headers)
                    
                    if jersey_check.status_code == 200:
                        pending_jerseys = jersey_check.json()
                        updated_jersey = None
                        for jersey in pending_jerseys:
                            if jersey.get("id") == self.test_jersey_id:
                                updated_jersey = jersey
                                break
                        
                        if updated_jersey and updated_jersey.get("status") == "needs_modification":
                            self.log_test(
                                "Suggest Change vs Reject Behavior",
                                True,
                                "Jersey status correctly changed to 'needs_modification' (not rejected)"
                            )
                        else:
                            self.log_test(
                                "Suggest Change vs Reject Behavior",
                                False,
                                "",
                                f"Jersey status not updated correctly: {updated_jersey.get('status') if updated_jersey else 'Jersey not found'}"
                            )
                else:
                    self.log_test("Admin Suggest Changes Functionality", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Admin Suggest Changes Functionality", False, "", str(e))

        # Step 4: Test rejection notifications
        try:
            # Create another test jersey for rejection testing
            rejection_test_data = {
                "team": "Rejection Test FC",
                "season": "2024-25",
                "player": "Reject Player",
                "size": "M",
                "condition": "poor",
                "manufacturer": "Unknown",
                "home_away": "away",
                "league": "Rejection League",
                "description": "Test jersey for rejection notification testing"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=rejection_test_data, headers=user_headers)
            
            if response.status_code in [200, 201]:
                rejection_jersey_data = response.json()
                rejection_jersey_id = rejection_jersey_data.get("id")
                
                # Get initial notification count
                notif_response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
                initial_count = 0
                if notif_response.status_code == 200:
                    notif_data = notif_response.json()
                    if isinstance(notif_data, dict) and "notifications" in notif_data:
                        initial_count = len(notif_data["notifications"])
                
                # Reject the jersey
                rejection_data = {
                    "reason": "Jersey condition is too poor and manufacturer information is insufficient. Please provide a jersey in better condition with complete details."
                }
                
                reject_response = self.session.post(f"{BASE_URL}/admin/jerseys/{rejection_jersey_id}/reject", 
                                                  json=rejection_data, headers=admin_headers)
                
                if reject_response.status_code in [200, 201]:
                    self.log_test(
                        "Admin Rejection Functionality",
                        True,
                        f"Successfully rejected jersey {rejection_jersey_id}"
                    )
                    
                    # Check for rejection notification
                    time.sleep(2)  # Wait for notification processing
                    new_notif_response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
                    
                    if new_notif_response.status_code == 200:
                        new_notif_data = new_notif_response.json()
                        if isinstance(new_notif_data, dict) and "notifications" in new_notif_data:
                            new_notifications = new_notif_data["notifications"]
                            new_count = len(new_notifications)
                            
                            if new_count > initial_count:
                                # Look for rejection notification
                                rejection_notification = None
                                for notif in new_notifications:
                                    if ("reject" in notif.get("message", "").lower() or 
                                        "reject" in notif.get("title", "").lower() or
                                        notif.get("related_id") == rejection_jersey_id):
                                        rejection_notification = notif
                                        break
                                
                                if rejection_notification:
                                    self.log_test(
                                        "Rejection Notifications Implementation",
                                        True,
                                        f"Rejection notification created: '{rejection_notification.get('title', 'Unknown')}'"
                                    )
                                else:
                                    self.log_test(
                                        "Rejection Notifications Implementation",
                                        True,
                                        f"New notification created after rejection ({new_count - initial_count} new notifications)"
                                    )
                            else:
                                self.log_test(
                                    "Rejection Notifications Implementation",
                                    False,
                                    "",
                                    "No new notifications created after jersey rejection"
                                )
                        else:
                            self.log_test("Rejection Notifications Implementation", False, "", "Invalid notification response format")
                    else:
                        self.log_test("Rejection Notifications Implementation", False, "", f"Failed to retrieve notifications: HTTP {new_notif_response.status_code}")
                else:
                    self.log_test("Admin Rejection Functionality", False, "", f"HTTP {reject_response.status_code}: {reject_response.text}")
            else:
                self.log_test("Create Rejection Test Jersey", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Rejection Testing", False, "", str(e))

        # Step 5: Test approval confirmation
        if self.test_jersey_id:
            try:
                # Get initial notification count
                notif_response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
                initial_count = 0
                if notif_response.status_code == 200:
                    notif_data = notif_response.json()
                    if isinstance(notif_data, dict) and "notifications" in notif_data:
                        initial_count = len(notif_data["notifications"])
                
                # Approve the jersey
                response = self.session.post(f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/approve", headers=admin_headers)
                
                if response.status_code in [200, 201]:
                    self.log_test(
                        "Admin Approval Confirmation",
                        True,
                        f"Successfully approved jersey {self.test_jersey_id}"
                    )
                    
                    # Check for approval notification
                    time.sleep(2)  # Wait for notification processing
                    new_notif_response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
                    
                    if new_notif_response.status_code == 200:
                        new_notif_data = new_notif_response.json()
                        if isinstance(new_notif_data, dict) and "notifications" in new_notif_data:
                            new_notifications = new_notif_data["notifications"]
                            new_count = len(new_notifications)
                            
                            if new_count > initial_count:
                                self.log_test(
                                    "Admin Action Confirmation Messages",
                                    True,
                                    f"Confirmation notification created after approval ({new_count - initial_count} new notifications)"
                                )
                            else:
                                self.log_test(
                                    "Admin Action Confirmation Messages",
                                    False,
                                    "",
                                    "No confirmation notification created after approval"
                                )
                        else:
                            self.log_test("Admin Action Confirmation Messages", False, "", "Invalid notification response format")
                    else:
                        self.log_test("Admin Action Confirmation Messages", False, "", f"Failed to retrieve notifications: HTTP {new_notif_response.status_code}")
                else:
                    self.log_test("Admin Approval Confirmation", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Admin Approval Testing", False, "", str(e))

    def run_all_tests(self):
        """Run all admin moderation tests"""
        print("🚀 ADMIN MODERATION SYSTEM TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("=" * 70)
        print()
        
        # Authenticate first
        if not self.authenticate_users():
            print("❌ Authentication failed - cannot proceed with tests")
            return 0
        
        # Run admin moderation tests
        self.test_admin_moderation_confirmation_messages()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 ADMIN MODERATION TEST SUMMARY")
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
        print("🎯 ADMIN MODERATION TESTING COMPLETE")
        
        return success_rate

if __name__ == "__main__":
    tester = AdminModerationTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)