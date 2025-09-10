#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Moderator Suggestions and User Notifications System Testing
Testing the new moderator suggestions and user notifications system implementation
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"
TEST_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_NAME = "Test User"

class ModeratorNotificationsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.admin_user_id = None
        self.user_token = None
        self.user_user_id = None
        self.test_jersey_id = None
        self.suggestion_id = None
        self.notification_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def setup_admin_authentication(self):
        """Setup admin authentication"""
        try:
            # Try to login as admin first
            login_payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.admin_user_id = data["user"]["id"]
                self.log_test("Admin Authentication Setup", "PASS", f"Admin logged in: {ADMIN_EMAIL}")
                return True
            else:
                # Try to register admin if login fails
                register_payload = {
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD,
                    "name": "TopKit Admin"
                }
                
                register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
                
                if register_response.status_code == 200:
                    data = register_response.json()
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Admin Authentication Setup", "PASS", f"Admin registered: {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Authentication Setup", "FAIL", f"Login: {response.status_code}, Register: {register_response.status_code}")
                    return False
                
        except Exception as e:
            self.log_test("Admin Authentication Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_user_authentication(self):
        """Setup regular user authentication"""
        try:
            # Register a new test user
            register_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["token"]
                self.user_user_id = data["user"]["id"]
                self.log_test("User Authentication Setup", "PASS", f"User registered: {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("User Authentication Setup", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_submission(self):
        """Test jersey submission by regular user (should be pending)"""
        try:
            if not self.user_token:
                self.log_test("Jersey Submission", "FAIL", "No user token available")
                return False
            
            # Set user auth header
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Marcus Rashford",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Manchester United home jersey with Marcus Rashford #10",
                "images": ["https://example.com/rashford-jersey.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("status") == "pending":
                    self.test_jersey_id = data["id"]
                    self.log_test("Jersey Submission", "PASS", f"Jersey submitted with pending status: {self.test_jersey_id}")
                    return True
                else:
                    self.log_test("Jersey Submission", "FAIL", f"Unexpected jersey status: {data.get('status')}")
                    return False
            else:
                self.log_test("Jersey Submission", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Submission", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_pending_jerseys_endpoint(self):
        """Test GET /api/admin/jerseys/pending - should return both pending and needs_modification jerseys"""
        try:
            if not self.admin_token:
                self.log_test("Admin Pending Jerseys Endpoint", "FAIL", "No admin token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Check if our test jersey is in the pending list
                test_jersey_found = any(jersey.get("id") == self.test_jersey_id for jersey in jerseys)
                
                if test_jersey_found:
                    self.log_test("Admin Pending Jerseys Endpoint", "PASS", f"Found {len(jerseys)} pending jerseys including test jersey")
                    return True
                else:
                    self.log_test("Admin Pending Jerseys Endpoint", "FAIL", f"Test jersey not found in {len(jerseys)} pending jerseys")
                    return False
            else:
                self.log_test("Admin Pending Jerseys Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Pending Jerseys Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_moderator_suggest_modifications(self):
        """Test POST /api/admin/jerseys/{jersey_id}/suggest-modifications"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("Moderator Suggest Modifications", "FAIL", "Missing admin token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "suggested_changes": "Please add more details about the jersey condition and provide better quality images. Also, please specify if this is an authentic or replica jersey.",
                "suggested_modifications": {
                    "description": "Please provide more detailed description including any wear marks or defects",
                    "images": "Please provide high-resolution images showing front, back, and any logos clearly",
                    "authenticity": "Please specify if this is authentic or replica"
                }
            }
            
            response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/suggest-modifications", 
                                       json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "suggestion_id" in data:
                    self.suggestion_id = data["suggestion_id"]
                    self.log_test("Moderator Suggest Modifications", "PASS", f"Modification suggestion created: {self.suggestion_id}")
                    return True
                else:
                    self.log_test("Moderator Suggest Modifications", "FAIL", "Missing suggestion_id in response")
                    return False
            else:
                self.log_test("Moderator Suggest Modifications", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Moderator Suggest Modifications", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_status_changed_to_needs_modification(self):
        """Test that jersey status changed to 'needs_modification' after suggestion"""
        try:
            if not self.test_jersey_id:
                self.log_test("Jersey Status Changed", "FAIL", "No test jersey ID available")
                return False
            
            # Check jersey status via admin pending endpoint
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending", headers=headers)
            
            if response.status_code == 200:
                jerseys = response.json()
                test_jersey = next((jersey for jersey in jerseys if jersey.get("id") == self.test_jersey_id), None)
                
                if test_jersey and test_jersey.get("status") == "needs_modification":
                    self.log_test("Jersey Status Changed", "PASS", "Jersey status changed to 'needs_modification'")
                    return True
                else:
                    self.log_test("Jersey Status Changed", "FAIL", f"Jersey status: {test_jersey.get('status') if test_jersey else 'not found'}")
                    return False
            else:
                self.log_test("Jersey Status Changed", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Status Changed", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_notifications_created(self):
        """Test GET /api/notifications - user should have notification about modification suggestion"""
        try:
            if not self.user_token:
                self.log_test("User Notifications Created", "FAIL", "No user token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.get(f"{self.base_url}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                unread_count = data.get("unread_count", 0)
                
                # Look for modification suggestion notification
                modification_notification = next((notif for notif in notifications 
                                                if notif.get("type") == "jersey_needs_modification"), None)
                
                if modification_notification:
                    self.notification_id = modification_notification["id"]
                    self.log_test("User Notifications Created", "PASS", 
                                f"Found modification notification (unread: {unread_count}): {modification_notification.get('title')}")
                    return True
                else:
                    self.log_test("User Notifications Created", "FAIL", f"No modification notification found in {len(notifications)} notifications")
                    return False
            else:
                self.log_test("User Notifications Created", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Notifications Created", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_mark_notification_read(self):
        """Test POST /api/notifications/{notification_id}/mark-read"""
        try:
            if not self.user_token or not self.notification_id:
                self.log_test("Mark Notification Read", "FAIL", "Missing user token or notification ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.post(f"{self.base_url}/notifications/{self.notification_id}/mark-read", headers=headers)
            
            if response.status_code == 200:
                # Verify notification is marked as read
                notifications_response = self.session.get(f"{self.base_url}/notifications", headers=headers)
                
                if notifications_response.status_code == 200:
                    data = notifications_response.json()
                    notifications = data.get("notifications", [])
                    
                    marked_notification = next((notif for notif in notifications 
                                              if notif.get("id") == self.notification_id), None)
                    
                    if marked_notification and marked_notification.get("is_read"):
                        self.log_test("Mark Notification Read", "PASS", "Notification successfully marked as read")
                        return True
                    else:
                        self.log_test("Mark Notification Read", "FAIL", "Notification not marked as read")
                        return False
                else:
                    self.log_test("Mark Notification Read", "FAIL", "Could not verify notification status")
                    return False
            else:
                self.log_test("Mark Notification Read", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Mark Notification Read", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_suggestions_view(self):
        """Test GET /api/jerseys/{jersey_id}/suggestions - user can see suggestions for their jerseys"""
        try:
            if not self.user_token or not self.test_jersey_id:
                self.log_test("Jersey Suggestions View", "FAIL", "Missing user token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}/suggestions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", [])
                jersey_info = data.get("jersey", {})
                
                if suggestions and len(suggestions) > 0:
                    suggestion = suggestions[0]
                    if suggestion.get("suggested_changes") and "moderator_info" in suggestion:
                        self.log_test("Jersey Suggestions View", "PASS", 
                                    f"Found {len(suggestions)} suggestions for jersey {jersey_info.get('team', 'Unknown')}")
                        return True
                    else:
                        self.log_test("Jersey Suggestions View", "FAIL", "Incomplete suggestion data")
                        return False
                else:
                    self.log_test("Jersey Suggestions View", "FAIL", "No suggestions found")
                    return False
            else:
                self.log_test("Jersey Suggestions View", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Suggestions View", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_pending_includes_needs_modification(self):
        """Test GET /api/collections/pending - should include jerseys with needs_modification status"""
        try:
            if not self.user_token:
                self.log_test("Collections Pending Includes Needs Modification", "FAIL", "No user token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.get(f"{self.base_url}/collections/pending", headers=headers)
            
            if response.status_code == 200:
                pending_submissions = response.json()
                
                # Look for our test jersey with needs_modification status
                test_jersey = next((jersey for jersey in pending_submissions 
                                  if jersey.get("id") == self.test_jersey_id), None)
                
                if test_jersey and test_jersey.get("status") == "needs_modification":
                    # Check if it has suggestion info
                    if "latest_suggestion" in test_jersey:
                        self.log_test("Collections Pending Includes Needs Modification", "PASS", 
                                    f"Found jersey with needs_modification status and suggestion info")
                        return True
                    else:
                        self.log_test("Collections Pending Includes Needs Modification", "PASS", 
                                    f"Found jersey with needs_modification status (no suggestion info)")
                        return True
                else:
                    self.log_test("Collections Pending Includes Needs Modification", "FAIL", 
                                f"Test jersey not found or wrong status in {len(pending_submissions)} submissions")
                    return False
            else:
                self.log_test("Collections Pending Includes Needs Modification", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collections Pending Includes Needs Modification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_resubmission(self):
        """Test POST /api/jerseys with resubmission_id parameter"""
        try:
            if not self.user_token or not self.test_jersey_id:
                self.log_test("Jersey Resubmission", "FAIL", "Missing user token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            
            # Create improved jersey submission addressing the feedback
            payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Marcus Rashford",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Manchester United home jersey with Marcus Rashford #10. Authentic jersey purchased from official store. Excellent condition with no visible wear marks or defects. Worn only twice for special occasions. All logos and prints are in perfect condition.",
                "images": [
                    "https://example.com/rashford-jersey-front-hd.jpg",
                    "https://example.com/rashford-jersey-back-hd.jpg",
                    "https://example.com/rashford-jersey-logo-detail.jpg"
                ]
            }
            
            # Add resubmission_id as query parameter
            response = self.session.post(f"{self.base_url}/jerseys?resubmission_id={self.test_jersey_id}", 
                                       json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("status") == "pending":
                    new_jersey_id = data["id"]
                    self.log_test("Jersey Resubmission", "PASS", f"Jersey resubmitted successfully: {new_jersey_id}")
                    
                    # Update test_jersey_id to the new one for further tests
                    self.test_jersey_id = new_jersey_id
                    return True
                else:
                    self.log_test("Jersey Resubmission", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Jersey Resubmission", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Resubmission", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_approve_needs_modification_jersey(self):
        """Test POST /api/admin/jerseys/{jersey_id}/approve - should work for needs_modification jerseys"""
        try:
            if not self.admin_token or not self.test_jersey_id:
                self.log_test("Admin Approve Needs Modification Jersey", "FAIL", "Missing admin token or jersey ID")
                return False
            
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            response = self.session.post(f"{self.base_url}/admin/jerseys/{self.test_jersey_id}/approve", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "approved" in data["message"].lower():
                    self.log_test("Admin Approve Needs Modification Jersey", "PASS", "Jersey approved successfully")
                    return True
                else:
                    self.log_test("Admin Approve Needs Modification Jersey", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Admin Approve Needs Modification Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Approve Needs Modification Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_approval_notification(self):
        """Test that user receives approval notification"""
        try:
            if not self.user_token:
                self.log_test("User Approval Notification", "FAIL", "No user token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.get(f"{self.base_url}/notifications", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                
                # Look for approval notification
                approval_notification = next((notif for notif in notifications 
                                            if notif.get("type") == "jersey_approved"), None)
                
                if approval_notification:
                    self.log_test("User Approval Notification", "PASS", 
                                f"Found approval notification: {approval_notification.get('title')}")
                    return True
                else:
                    self.log_test("User Approval Notification", "FAIL", f"No approval notification found in {len(notifications)} notifications")
                    return False
            else:
                self.log_test("User Approval Notification", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Approval Notification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_mark_all_notifications_read(self):
        """Test POST /api/notifications/mark-all-read"""
        try:
            if not self.user_token:
                self.log_test("Mark All Notifications Read", "FAIL", "No user token available")
                return False
            
            headers = {'Authorization': f'Bearer {self.user_token}'}
            response = self.session.post(f"{self.base_url}/notifications/mark-all-read", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    # Verify all notifications are marked as read
                    notifications_response = self.session.get(f"{self.base_url}/notifications", headers=headers)
                    
                    if notifications_response.status_code == 200:
                        notif_data = notifications_response.json()
                        unread_count = notif_data.get("unread_count", 0)
                        
                        if unread_count == 0:
                            self.log_test("Mark All Notifications Read", "PASS", f"All notifications marked as read: {data['message']}")
                            return True
                        else:
                            self.log_test("Mark All Notifications Read", "FAIL", f"Still have {unread_count} unread notifications")
                            return False
                    else:
                        self.log_test("Mark All Notifications Read", "FAIL", "Could not verify notification status")
                        return False
                else:
                    self.log_test("Mark All Notifications Read", "FAIL", "Missing message in response")
                    return False
            else:
                self.log_test("Mark All Notifications Read", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Mark All Notifications Read", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_reject_needs_modification_jersey(self):
        """Test POST /api/admin/jerseys/{jersey_id}/reject - should work for needs_modification jerseys"""
        try:
            # Create another test jersey to reject
            if not self.user_token:
                self.log_test("Admin Reject Needs Modification Jersey", "FAIL", "No user token available")
                return False
            
            # Create a jersey to reject
            headers = {'Authorization': f'Bearer {self.user_token}'}
            jersey_payload = {
                "team": "Liverpool FC",
                "season": "2023-24",
                "player": "Mohamed Salah",
                "size": "M",
                "condition": "good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Liverpool jersey",
                "images": []
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload, headers=headers)
            
            if jersey_response.status_code != 200:
                self.log_test("Admin Reject Needs Modification Jersey", "FAIL", "Could not create test jersey")
                return False
            
            reject_jersey_id = jersey_response.json()["id"]
            
            # Suggest modifications first
            admin_headers = {'Authorization': f'Bearer {self.admin_token}'}
            suggestion_payload = {
                "jersey_id": reject_jersey_id,
                "suggested_changes": "This jersey needs better images and more detailed description.",
                "suggested_modifications": {}
            }
            
            self.session.post(f"{self.base_url}/admin/jerseys/{reject_jersey_id}/suggest-modifications", 
                            json=suggestion_payload, headers=admin_headers)
            
            # Now reject it
            rejection_payload = {
                "reason": "Jersey does not meet quality standards even after modification suggestions."
            }
            
            response = self.session.post(f"{self.base_url}/admin/jerseys/{reject_jersey_id}/reject", 
                                       json=rejection_payload, headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "rejected" in data["message"].lower():
                    self.log_test("Admin Reject Needs Modification Jersey", "PASS", "Jersey rejected successfully")
                    return True
                else:
                    self.log_test("Admin Reject Needs Modification Jersey", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Admin Reject Needs Modification Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Reject Needs Modification Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all moderator suggestions and notifications tests"""
        print("🚀 STARTING MODERATOR SUGGESTIONS AND USER NOTIFICATIONS SYSTEM TESTING")
        print("=" * 80)
        
        tests_passed = 0
        total_tests = 0
        
        # Test sequence
        test_methods = [
            self.setup_admin_authentication,
            self.setup_user_authentication,
            self.test_jersey_submission,
            self.test_admin_pending_jerseys_endpoint,
            self.test_moderator_suggest_modifications,
            self.test_jersey_status_changed_to_needs_modification,
            self.test_user_notifications_created,
            self.test_mark_notification_read,
            self.test_jersey_suggestions_view,
            self.test_collections_pending_includes_needs_modification,
            self.test_jersey_resubmission,
            self.test_admin_approve_needs_modification_jersey,
            self.test_user_approval_notification,
            self.test_mark_all_notifications_read,
            self.test_admin_reject_needs_modification_jersey
        ]
        
        for test_method in test_methods:
            total_tests += 1
            if test_method():
                tests_passed += 1
            time.sleep(1)  # Small delay between tests
        
        print("=" * 80)
        print(f"🎯 MODERATOR SUGGESTIONS AND NOTIFICATIONS TESTING COMPLETE")
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! The moderator suggestions and user notifications system is working perfectly!")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return tests_passed == total_tests

if __name__ == "__main__":
    tester = ModeratorNotificationsTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)