#!/usr/bin/env python3
"""
TopKit Admin Moderation System Testing Suite
Focus: Admin moderation actions and notification creation after backend fixes
Testing Areas: Authentication, Jersey Submission, Admin Actions, Notification System
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BASE_URL = "https://kitfix-contrib.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"

class AdminModerationTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_id = None
        self.test_jersey_id = None
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

    def test_authentication_setup(self):
        """Test 1: Authentication Setup - Login with admin and regular user accounts"""
        print("🔐 TESTING AUTHENTICATION SETUP")
        print("=" * 50)
        
        # Test 1: Admin Login
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
                        f"Admin login successful - User: {admin_name}, Role: {admin_role}, ID: {self.admin_id}"
                    )
                else:
                    self.log_test("Admin Authentication", False, "", "Missing token or user data in response")
            else:
                self.log_test("Admin Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))

        # Test 2: Regular User Login
        try:
            user_login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=user_login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"]["role"]
                    self.log_test(
                        "Regular User Authentication (steinmetzlivio@gmail.com/123)",
                        True,
                        f"User login successful - User: {user_name}, Role: {user_role}, ID: {self.user_id}"
                    )
                else:
                    self.log_test("Regular User Authentication", False, "", "Missing token or user data in response")
            else:
                self.log_test("Regular User Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Regular User Authentication", False, "", str(e))

    def test_jersey_submission_for_testing(self):
        """Test 2: Jersey Submission - Create test jersey for admin moderation testing"""
        print("⚽ TESTING JERSEY SUBMISSION FOR MODERATION")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Jersey Submission for Testing", False, "", "No user token available")
            return

        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            test_jersey_data = {
                "team": "FC Barcelona",
                "season": "2024-25",
                "player": "Pedri",
                "size": "L",
                "condition": "near_mint",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for admin moderation and notification testing"
            }
            
            response = self.session.post(f"{BASE_URL}/jerseys", json=test_jersey_data, headers=headers)
            
            if response.status_code in [200, 201]:
                jersey_data = response.json()
                self.test_jersey_id = jersey_data.get("id")
                jersey_status = jersey_data.get("status")
                reference_number = jersey_data.get("reference_number")
                
                self.log_test(
                    "Jersey Submission for Admin Testing",
                    True,
                    f"Test jersey created - ID: {self.test_jersey_id}, Status: {jersey_status}, Ref: {reference_number}"
                )
                
                # Verify jersey enters pending status
                if jersey_status == "pending":
                    self.log_test(
                        "Jersey Pending Status Verification",
                        True,
                        "Jersey correctly entered pending status for admin moderation"
                    )
                else:
                    self.log_test(
                        "Jersey Pending Status Verification",
                        False,
                        "",
                        f"Expected 'pending' status, got '{jersey_status}'"
                    )
            else:
                self.log_test("Jersey Submission for Admin Testing", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Jersey Submission for Admin Testing", False, "", str(e))

    def test_admin_moderation_actions(self):
        """Test 3: Admin Moderation Actions - Test approve, reject, suggest-modifications endpoints"""
        print("👨‍💼 TESTING ADMIN MODERATION ACTIONS")
        print("=" * 50)
        
        if not self.admin_token or not self.test_jersey_id:
            self.log_test("Admin Moderation Actions", False, "", "Missing admin token or test jersey ID")
            return

        headers = {"Authorization": f"Bearer {self.admin_token}"}

        # Test 1: Get Pending Jerseys
        try:
            response = self.session.get(f"{BASE_URL}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                if isinstance(pending_jerseys, list):
                    # Find our test jersey
                    test_jersey = next((j for j in pending_jerseys if j.get("id") == self.test_jersey_id), None)
                    if test_jersey:
                        self.log_test(
                            "Admin Access to Pending Jerseys",
                            True,
                            f"Found {len(pending_jerseys)} pending jerseys including our test jersey"
                        )
                    else:
                        self.log_test(
                            "Admin Access to Pending Jerseys",
                            False,
                            "",
                            "Test jersey not found in pending list"
                        )
                else:
                    self.log_test("Admin Access to Pending Jerseys", False, "", "Invalid response format")
            else:
                self.log_test("Admin Access to Pending Jerseys", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Access to Pending Jerseys", False, "", str(e))

        # Test 2: Suggest Modifications
        try:
            suggestion_data = {
                "jersey_id": self.test_jersey_id,
                "suggested_changes": "Please add more details about the jersey condition and include better images.",
                "suggested_modifications": {
                    "description": "Add more detailed description",
                    "images": "Include front and back images"
                }
            }
            
            response = self.session.post(
                f"{BASE_URL}/admin/jerseys/{self.test_jersey_id}/suggest-modifications",
                json=suggestion_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestion_id = result.get("suggestion_id")
                self.log_test(
                    "Admin Suggest Modifications Action",
                    True,
                    f"Modifications suggested successfully - Suggestion ID: {suggestion_id}"
                )
                
                # Wait a moment for notification processing
                time.sleep(2)
                
                # Verify jersey status changed to needs_modification
                jersey_response = self.session.get(f"{BASE_URL}/admin/jerseys/pending", headers=headers)
                if jersey_response.status_code == 200:
                    jerseys = jersey_response.json()
                    updated_jersey = next((j for j in jerseys if j.get("id") == self.test_jersey_id), None)
                    if updated_jersey and updated_jersey.get("status") == "needs_modification":
                        self.log_test(
                            "Jersey Status Update After Suggestions",
                            True,
                            "Jersey status correctly updated to 'needs_modification'"
                        )
                    else:
                        self.log_test(
                            "Jersey Status Update After Suggestions",
                            False,
                            "",
                            f"Expected 'needs_modification', got '{updated_jersey.get('status') if updated_jersey else 'not found'}'"
                        )
            else:
                self.log_test("Admin Suggest Modifications Action", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Suggest Modifications Action", False, "", str(e))

        # Test 3: Approve Jersey (create a new test jersey for this)
        try:
            # First create another test jersey
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            approve_test_jersey = {
                "team": "Real Madrid CF",
                "season": "2024-25",
                "player": "Bellingham",
                "size": "M",
                "condition": "new",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for approval testing"
            }
            
            jersey_response = self.session.post(f"{BASE_URL}/jerseys", json=approve_test_jersey, headers=user_headers)
            if jersey_response.status_code in [200, 201]:
                approve_jersey_id = jersey_response.json().get("id")
                
                # Now approve it
                response = self.session.post(
                    f"{BASE_URL}/admin/jerseys/{approve_jersey_id}/approve",
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test(
                        "Admin Approve Jersey Action",
                        True,
                        f"Jersey approved successfully - ID: {approve_jersey_id}"
                    )
                    
                    # Wait for notification processing
                    time.sleep(2)
                else:
                    self.log_test("Admin Approve Jersey Action", False, "", f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("Admin Approve Jersey Action", False, "", "Failed to create test jersey for approval")
        except Exception as e:
            self.log_test("Admin Approve Jersey Action", False, "", str(e))

        # Test 4: Reject Jersey (create another test jersey for this)
        try:
            # Create another test jersey for rejection
            reject_test_jersey = {
                "team": "Manchester United",
                "season": "2024-25",
                "player": "Rashford",
                "size": "L",
                "condition": "good",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Test jersey for rejection testing"
            }
            
            jersey_response = self.session.post(f"{BASE_URL}/jerseys", json=reject_test_jersey, headers=user_headers)
            if jersey_response.status_code in [200, 201]:
                reject_jersey_id = jersey_response.json().get("id")
                
                # Now reject it
                rejection_data = {
                    "reason": "Jersey does not meet quality standards for the database"
                }
                
                response = self.session.post(
                    f"{BASE_URL}/admin/jerseys/{reject_jersey_id}/reject",
                    json=rejection_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test(
                        "Admin Reject Jersey Action",
                        True,
                        f"Jersey rejected successfully - ID: {reject_jersey_id}"
                    )
                    
                    # Wait for notification processing
                    time.sleep(2)
                else:
                    self.log_test("Admin Reject Jersey Action", False, "", f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("Admin Reject Jersey Action", False, "", "Failed to create test jersey for rejection")
        except Exception as e:
            self.log_test("Admin Reject Jersey Action", False, "", str(e))

    def test_notification_creation_system(self):
        """Test 4: Notification Creation - Check if notifications are created after admin actions"""
        print("🔔 TESTING NOTIFICATION CREATION SYSTEM")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Notification Creation Testing", False, "", "No user token available")
            return

        user_headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Get User Notifications
        try:
            response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "notifications" in data:
                    notifications = data["notifications"]
                    unread_count = data.get("unread_count", 0)
                    
                    # Look for notifications related to our test actions
                    jersey_notifications = [n for n in notifications if 
                                          n.get("type") in ["jersey_approved", "jersey_rejected", "jersey_needs_modification"]]
                    
                    self.log_test(
                        "User Notification Retrieval",
                        True,
                        f"Retrieved {len(notifications)} total notifications ({len(jersey_notifications)} jersey-related, {unread_count} unread)"
                    )
                    
                    # Test notification types
                    notification_types = set(n.get("type") for n in jersey_notifications)
                    expected_types = {"jersey_approved", "jersey_rejected", "jersey_needs_modification"}
                    found_types = notification_types.intersection(expected_types)
                    
                    if found_types:
                        self.log_test(
                            "Notification Types Verification",
                            True,
                            f"Found notification types: {', '.join(found_types)}"
                        )
                    else:
                        self.log_test(
                            "Notification Types Verification",
                            False,
                            "",
                            "No jersey-related notifications found after admin actions"
                        )
                    
                    # Test notification content
                    if jersey_notifications:
                        sample_notification = jersey_notifications[0]
                        has_title = bool(sample_notification.get("title"))
                        has_message = bool(sample_notification.get("message"))
                        has_related_id = bool(sample_notification.get("related_id"))
                        
                        if has_title and has_message:
                            self.log_test(
                                "Notification Content Verification",
                                True,
                                f"Notifications contain proper titles and messages (Related ID: {has_related_id})"
                            )
                        else:
                            self.log_test(
                                "Notification Content Verification",
                                False,
                                "",
                                f"Missing notification content - Title: {has_title}, Message: {has_message}"
                            )
                    
                else:
                    self.log_test("User Notification Retrieval", False, "", "Invalid notifications response format - expected object with 'notifications' array")
            else:
                self.log_test("User Notification Retrieval", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("User Notification Retrieval", False, "", str(e))

        # Test 2: Notification Unread Count
        try:
            response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "notifications" in data:
                    notifications = data["notifications"]
                    unread_count = data.get("unread_count", 0)
                    total_count = len(notifications)
                    
                    self.log_test(
                        "Notification Unread Count",
                        True,
                        f"Unread notifications: {unread_count}/{total_count}"
                    )
                else:
                    self.log_test("Notification Unread Count", False, "", "Invalid notifications format - expected object with 'notifications' array")
            else:
                self.log_test("Notification Unread Count", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Notification Unread Count", False, "", str(e))

    def test_user_notification_retrieval(self):
        """Test 5: User Notification Retrieval - Verify users can access notifications about jersey status changes"""
        print("📬 TESTING USER NOTIFICATION RETRIEVAL")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("User Notification Retrieval", False, "", "No user token available")
            return

        user_headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Access Notifications Endpoint
        try:
            response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "notifications" in data:
                    notifications = data["notifications"]
                    unread_count = data.get("unread_count", 0)
                    
                    self.log_test(
                        "Notifications Endpoint Access",
                        True,
                        f"Successfully accessed notifications endpoint - {len(notifications)} notifications found ({unread_count} unread)"
                    )
                    
                    # Test notification details
                    if notifications:
                        recent_notifications = sorted(notifications, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
                        
                        for i, notification in enumerate(recent_notifications):
                            title = notification.get("title", "")
                            message = notification.get("message", "")
                            notification_type = notification.get("type", "")
                            related_id = notification.get("related_id", "")
                            
                            self.log_test(
                                f"Notification Detail #{i+1}",
                                True,
                                f"Type: {notification_type}, Title: '{title[:50]}...', Has Related ID: {bool(related_id)}"
                            )
                    
                else:
                    self.log_test("Notifications Endpoint Access", False, "", "Invalid notifications response format - expected object with 'notifications' array")
            else:
                self.log_test("Notifications Endpoint Access", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Notifications Endpoint Access", False, "", str(e))

        # Test 2: Jersey Information in Notifications
        try:
            response = self.session.get(f"{BASE_URL}/notifications", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "notifications" in data:
                    notifications = data["notifications"]
                    jersey_notifications = [n for n in notifications if 
                                          n.get("type") in ["jersey_approved", "jersey_rejected", "jersey_needs_modification"]]
                    
                    if jersey_notifications:
                        # Check if notifications contain jersey information
                        notifications_with_jersey_info = []
                        for notification in jersey_notifications:
                            message = notification.get("message", "")
                            # Look for jersey team names or reference numbers in message
                            if any(team in message for team in ["Barcelona", "Real Madrid", "Manchester United"]) or "TK-" in message:
                                notifications_with_jersey_info.append(notification)
                        
                        if notifications_with_jersey_info:
                            self.log_test(
                                "Jersey Information in Notifications",
                                True,
                                f"{len(notifications_with_jersey_info)}/{len(jersey_notifications)} notifications contain jersey details"
                            )
                        else:
                            self.log_test(
                                "Jersey Information in Notifications",
                                False,
                                "",
                                "Notifications do not contain specific jersey information"
                            )
                    else:
                        self.log_test(
                            "Jersey Information in Notifications",
                            False,
                            "",
                            "No jersey-related notifications found"
                        )
                else:
                    self.log_test("Jersey Information in Notifications", False, "", "Invalid notifications response format")
            else:
                self.log_test("Jersey Information in Notifications", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Jersey Information in Notifications", False, "", str(e))

    def run_all_tests(self):
        """Run all admin moderation and notification tests"""
        print("🚀 STARTING ADMIN MODERATION SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print(f"Admin User: {ADMIN_EMAIL}")
        print("Focus: Admin Moderation Actions & Notification Creation")
        print("=" * 80)
        print()
        
        # Run test suites in order
        self.test_authentication_setup()
        self.test_jersey_submission_for_testing()
        self.test_admin_moderation_actions()
        self.test_notification_creation_system()
        self.test_user_notification_retrieval()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("📊 ADMIN MODERATION & NOTIFICATION TESTING SUMMARY")
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
            "Authentication Setup": [],
            "Jersey Submission": [],
            "Admin Moderation Actions": [],
            "Notification Creation": [],
            "User Notification Access": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                test_categories["Authentication Setup"].append(result)
            elif "Jersey Submission" in test_name or "Jersey Pending" in test_name:
                test_categories["Jersey Submission"].append(result)
            elif "Admin" in test_name and ("Approve" in test_name or "Reject" in test_name or "Suggest" in test_name or "Pending" in test_name):
                test_categories["Admin Moderation Actions"].append(result)
            elif "Notification" in test_name and ("Creation" in test_name or "Types" in test_name or "Content" in test_name or "Unread" in test_name):
                test_categories["Notification Creation"].append(result)
            elif "Notification" in test_name or "Jersey Information" in test_name:
                test_categories["User Notification Access"].append(result)
        
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
            print("🎉 EXCELLENT: Admin moderation and notification system working perfectly!")
        elif success_rate >= 80:
            print("✅ GOOD: Admin moderation system mostly operational with minor issues.")
        elif success_rate >= 70:
            print("⚠️ ACCEPTABLE: Admin moderation system has some issues that should be addressed.")
        else:
            print("❌ CRITICAL: Admin moderation system has significant issues that need immediate attention.")
        
        print()
        print("🎯 ADMIN MODERATION & NOTIFICATION TESTING COMPLETE")
        
        # Return success rate for external use
        return success_rate

if __name__ == "__main__":
    tester = AdminModerationTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 80 else 1)