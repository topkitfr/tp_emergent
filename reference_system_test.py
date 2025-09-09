#!/usr/bin/env python3
"""
TopKit Enhanced Backend Testing - Jersey Reference System & Notifications
Testing the new TK-000001 reference system and enhanced notifications
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration - Use the correct backend URL from frontend/.env
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

class TopKitReferenceSystemTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.admin_token = None
        self.admin_user_id = None
        self.test_jerseys = []  # Store created jerseys for testing
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
    
    def setup_test_users(self):
        """Setup regular user and admin user for testing"""
        try:
            # Create regular user
            unique_email = f"reftest_{int(time.time())}@topkit.com"
            
            user_payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Reference Test User"
            }
            
            user_response = self.session.post(f"{self.base_url}/auth/register", json=user_payload)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                self.auth_token = user_data["token"]
                self.user_id = user_data["user"]["id"]
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                # Setup admin user (topkitfr@gmail.com)
                admin_payload = {
                    "email": "topkitfr@gmail.com",
                    "password": "adminpass123"
                }
                
                admin_response = self.session.post(f"{self.base_url}/auth/login", json=admin_payload)
                
                if admin_response.status_code == 200:
                    admin_data = admin_response.json()
                    self.admin_token = admin_data["token"]
                    self.admin_user_id = admin_data["user"]["id"]
                    
                    self.log_test("Setup Test Users", "PASS", f"Regular user: {unique_email}, Admin: topkitfr@gmail.com")
                    return True
                else:
                    self.log_test("Setup Test Users", "FAIL", f"Admin login failed: {admin_response.status_code}")
                    return False
            else:
                self.log_test("Setup Test Users", "FAIL", f"User registration failed: {user_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Setup Test Users", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_reference_generation(self):
        """Test that jersey creation generates automatic reference numbers (TK-000001, TK-000002, etc.)"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Reference Generation", "FAIL", "No auth token available")
                return False
            
            # Create first jersey
            jersey1_payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Test jersey for reference system"
            }
            
            response1 = self.session.post(f"{self.base_url}/jerseys", json=jersey1_payload)
            
            if response1.status_code == 200:
                jersey1_data = response1.json()
                reference1 = jersey1_data.get("reference_number")
                
                if reference1 and reference1.startswith("TK-"):
                    self.test_jerseys.append(jersey1_data)
                    
                    # Create second jersey
                    jersey2_payload = {
                        "team": "Liverpool FC",
                        "season": "2023-24",
                        "player": "Mohamed Salah",
                        "size": "M",
                        "condition": "very_good",
                        "manufacturer": "Nike",
                        "home_away": "home",
                        "league": "Premier League",
                        "description": "Second test jersey for reference system"
                    }
                    
                    response2 = self.session.post(f"{self.base_url}/jerseys", json=jersey2_payload)
                    
                    if response2.status_code == 200:
                        jersey2_data = response2.json()
                        reference2 = jersey2_data.get("reference_number")
                        
                        if reference2 and reference2.startswith("TK-"):
                            self.test_jerseys.append(jersey2_data)
                            
                            # Verify sequential numbering
                            ref1_num = int(reference1.split("-")[1])
                            ref2_num = int(reference2.split("-")[1])
                            
                            if ref2_num > ref1_num:
                                self.log_test("Jersey Reference Generation", "PASS", 
                                            f"Sequential references generated: {reference1} → {reference2}")
                                return True
                            else:
                                self.log_test("Jersey Reference Generation", "FAIL", 
                                            f"References not sequential: {reference1} → {reference2}")
                                return False
                        else:
                            self.log_test("Jersey Reference Generation", "FAIL", "Second jersey missing reference number")
                            return False
                    else:
                        self.log_test("Jersey Reference Generation", "FAIL", f"Second jersey creation failed: {response2.status_code}")
                        return False
                else:
                    self.log_test("Jersey Reference Generation", "FAIL", "First jersey missing reference number")
                    return False
            else:
                self.log_test("Jersey Reference Generation", "FAIL", f"First jersey creation failed: {response1.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Reference Generation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_submission_notification(self):
        """Test that jersey submission creates 'Jersey Submitted Successfully!' notification with reference number"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Submission Notification", "FAIL", "No auth token available")
                return False
            
            # Create a jersey
            jersey_payload = {
                "team": "Real Madrid",
                "season": "2023-24",
                "player": "Vinicius Jr",
                "size": "L",
                "condition": "mint",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for submission notification"
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if response.status_code == 200:
                jersey_data = response.json()
                reference_number = jersey_data.get("reference_number")
                
                # Wait a moment for notification to be created
                time.sleep(1)
                
                # Check notifications
                notifications_response = self.session.get(f"{self.base_url}/notifications")
                
                if notifications_response.status_code == 200:
                    notifications_data = notifications_response.json()
                    notifications = notifications_data.get("notifications", [])
                    
                    # Look for submission notification
                    submission_notification = None
                    for notification in notifications:
                        if "Jersey Submitted Successfully!" in notification.get("title", ""):
                            submission_notification = notification
                            break
                    
                    if submission_notification:
                        message = submission_notification.get("message", "")
                        if reference_number and reference_number in message:
                            self.log_test("Jersey Submission Notification", "PASS", 
                                        f"Submission notification created with reference {reference_number}")
                            return True
                        else:
                            self.log_test("Jersey Submission Notification", "FAIL", 
                                        f"Reference number {reference_number} not found in notification message")
                            return False
                    else:
                        self.log_test("Jersey Submission Notification", "FAIL", "No submission notification found")
                        return False
                else:
                    self.log_test("Jersey Submission Notification", "FAIL", f"Could not get notifications: {notifications_response.status_code}")
                    return False
            else:
                self.log_test("Jersey Submission Notification", "FAIL", f"Jersey creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Submission Notification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_registration_welcome_notification(self):
        """Test that user registration creates welcome notification '🎉 Welcome to TopKit!'"""
        try:
            # Create a new user
            unique_email = f"welcome_test_{int(time.time())}@topkit.com"
            
            user_payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Welcome Test User"
            }
            
            # Remove current auth to test new user registration
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.post(f"{self.base_url}/auth/register", json=user_payload)
            
            if response.status_code == 200:
                user_data = response.json()
                new_token = user_data["token"]
                
                # Set auth for new user
                self.session.headers.update({'Authorization': f'Bearer {new_token}'})
                
                # Wait a moment for notification to be created
                time.sleep(1)
                
                # Check notifications for new user
                notifications_response = self.session.get(f"{self.base_url}/notifications")
                
                if notifications_response.status_code == 200:
                    notifications_data = notifications_response.json()
                    notifications = notifications_data.get("notifications", [])
                    
                    # Look for welcome notification
                    welcome_notification = None
                    for notification in notifications:
                        if "🎉 Welcome to TopKit!" in notification.get("title", ""):
                            welcome_notification = notification
                            break
                    
                    # Restore original auth
                    if original_auth:
                        self.session.headers['Authorization'] = original_auth
                    
                    if welcome_notification:
                        self.log_test("User Registration Welcome Notification", "PASS", 
                                    f"Welcome notification created for new user: {unique_email}")
                        return True
                    else:
                        self.log_test("User Registration Welcome Notification", "FAIL", "No welcome notification found")
                        return False
                else:
                    self.log_test("User Registration Welcome Notification", "FAIL", f"Could not get notifications: {notifications_response.status_code}")
                    return False
            else:
                self.log_test("User Registration Welcome Notification", "FAIL", f"User registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Registration Welcome Notification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_approval_notification(self):
        """Test that jersey approval creates 'Jersey Approved & Now Live!' notification with reference number"""
        try:
            if not self.auth_token or not self.admin_token or not self.test_jerseys:
                self.log_test("Jersey Approval Notification", "FAIL", "Missing auth tokens or test jerseys")
                return False
            
            # Use first test jersey
            test_jersey = self.test_jerseys[0]
            jersey_id = test_jersey["id"]
            reference_number = test_jersey.get("reference_number")
            
            # Switch to admin auth
            original_auth = self.session.headers.get('Authorization')
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            # Approve the jersey
            approval_response = self.session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
            
            # Switch back to user auth
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            
            if approval_response.status_code == 200:
                # Wait a moment for notification to be created
                time.sleep(1)
                
                # Check notifications for approval
                notifications_response = self.session.get(f"{self.base_url}/notifications")
                
                if notifications_response.status_code == 200:
                    notifications_data = notifications_response.json()
                    notifications = notifications_data.get("notifications", [])
                    
                    # Look for approval notification
                    approval_notification = None
                    for notification in notifications:
                        if "Jersey Approved & Now Live!" in notification.get("title", ""):
                            approval_notification = notification
                            break
                    
                    if approval_notification:
                        message = approval_notification.get("message", "")
                        if reference_number and reference_number in message:
                            self.log_test("Jersey Approval Notification", "PASS", 
                                        f"Approval notification created with reference {reference_number}")
                            return True
                        else:
                            self.log_test("Jersey Approval Notification", "FAIL", 
                                        f"Reference number {reference_number} not found in approval notification")
                            return False
                    else:
                        self.log_test("Jersey Approval Notification", "FAIL", "No approval notification found")
                        return False
                else:
                    self.log_test("Jersey Approval Notification", "FAIL", f"Could not get notifications: {notifications_response.status_code}")
                    return False
            else:
                self.log_test("Jersey Approval Notification", "FAIL", f"Jersey approval failed: {approval_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Approval Notification", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_resubmission_preserves_reference(self):
        """Test that jersey resubmission preserves original reference number"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Resubmission Preserves Reference", "FAIL", "Missing auth tokens")
                return False
            
            # Create a jersey for modification testing
            jersey_payload = {
                "team": "Chelsea FC",
                "season": "2023-24",
                "player": "Enzo Fernandez",
                "size": "M",
                "condition": "good",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Test jersey for resubmission"
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if response.status_code == 200:
                original_jersey = response.json()
                original_id = original_jersey["id"]
                original_reference = original_jersey.get("reference_number")
                
                # Switch to admin and suggest modifications
                self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                
                suggestion_payload = {
                    "jersey_id": original_id,
                    "suggested_changes": "Please improve the description and add more details about the jersey condition."
                }
                
                suggestion_response = self.session.post(f"{self.base_url}/admin/jerseys/{original_id}/suggest-modifications", json=suggestion_payload)
                
                # Switch back to user
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                if suggestion_response.status_code == 200:
                    # Wait for suggestion to be processed
                    time.sleep(1)
                    
                    # Resubmit with modifications
                    resubmission_payload = {
                        "team": "Chelsea FC",
                        "season": "2023-24",
                        "player": "Enzo Fernandez",
                        "size": "M",
                        "condition": "good",
                        "manufacturer": "Nike",
                        "home_away": "home",
                        "league": "Premier League",
                        "description": "Improved description: Official Chelsea FC home jersey with Enzo Fernandez #5. Good condition with minor wear on the sleeves, perfect for collection or casual wear."
                    }
                    
                    resubmission_response = self.session.post(f"{self.base_url}/jerseys?resubmission_id={original_id}", json=resubmission_payload)
                    
                    if resubmission_response.status_code == 200:
                        resubmitted_jersey = resubmission_response.json()
                        resubmitted_reference = resubmitted_jersey.get("reference_number")
                        
                        if original_reference == resubmitted_reference:
                            self.log_test("Resubmission Preserves Reference", "PASS", 
                                        f"Reference preserved in resubmission: {original_reference}")
                            return True
                        else:
                            self.log_test("Resubmission Preserves Reference", "FAIL", 
                                        f"Reference changed: {original_reference} → {resubmitted_reference}")
                            return False
                    else:
                        self.log_test("Resubmission Preserves Reference", "FAIL", f"Resubmission failed: {resubmission_response.status_code}")
                        return False
                else:
                    self.log_test("Resubmission Preserves Reference", "FAIL", f"Suggestion failed: {suggestion_response.status_code}")
                    return False
            else:
                self.log_test("Resubmission Preserves Reference", "FAIL", f"Jersey creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Resubmission Preserves Reference", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_jerseys_includes_reference(self):
        """Test that GET /api/jerseys returns reference_number field"""
        try:
            # Get jerseys (should include approved ones)
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                if jerseys:
                    # Check if jerseys have reference_number field
                    has_reference = False
                    for jersey in jerseys:
                        if "reference_number" in jersey and jersey["reference_number"]:
                            has_reference = True
                            break
                    
                    if has_reference:
                        self.log_test("GET Jerseys Includes Reference", "PASS", 
                                    f"Found {len(jerseys)} jerseys with reference numbers")
                        return True
                    else:
                        self.log_test("GET Jerseys Includes Reference", "FAIL", "No jerseys have reference_number field")
                        return False
                else:
                    self.log_test("GET Jerseys Includes Reference", "PASS", "No jerseys found (acceptable for clean database)")
                    return True
            else:
                self.log_test("GET Jerseys Includes Reference", "FAIL", f"GET jerseys failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET Jerseys Includes Reference", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_collections_pending_includes_reference(self):
        """Test that GET /api/collections/pending includes reference numbers"""
        try:
            if not self.auth_token:
                self.log_test("GET Collections Pending Includes Reference", "FAIL", "No auth token available")
                return False
            
            # Get pending submissions
            response = self.session.get(f"{self.base_url}/collections/pending")
            
            if response.status_code == 200:
                pending_submissions = response.json()
                
                if pending_submissions:
                    # Check if submissions have reference_number field
                    has_reference = False
                    for submission in pending_submissions:
                        if "reference_number" in submission and submission["reference_number"]:
                            has_reference = True
                            break
                    
                    if has_reference:
                        self.log_test("GET Collections Pending Includes Reference", "PASS", 
                                    f"Found {len(pending_submissions)} pending submissions with reference numbers")
                        return True
                    else:
                        self.log_test("GET Collections Pending Includes Reference", "FAIL", "No pending submissions have reference_number field")
                        return False
                else:
                    self.log_test("GET Collections Pending Includes Reference", "PASS", "No pending submissions found (acceptable)")
                    return True
            else:
                self.log_test("GET Collections Pending Includes Reference", "FAIL", f"GET pending failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET Collections Pending Includes Reference", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_admin_endpoints_show_references(self):
        """Test that admin endpoints show reference numbers"""
        try:
            if not self.admin_token:
                self.log_test("Admin Endpoints Show References", "FAIL", "No admin token available")
                return False
            
            # Switch to admin auth
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            # Get pending jerseys from admin endpoint
            response = self.session.get(f"{self.base_url}/admin/jerseys/pending")
            
            if response.status_code == 200:
                pending_jerseys = response.json()
                
                if pending_jerseys:
                    # Check if jerseys have reference_number field
                    has_reference = False
                    for jersey in pending_jerseys:
                        if "reference_number" in jersey and jersey["reference_number"]:
                            has_reference = True
                            break
                    
                    if has_reference:
                        self.log_test("Admin Endpoints Show References", "PASS", 
                                    f"Admin endpoint shows {len(pending_jerseys)} jerseys with reference numbers")
                        return True
                    else:
                        self.log_test("Admin Endpoints Show References", "FAIL", "Admin endpoint jerseys missing reference_number field")
                        return False
                else:
                    self.log_test("Admin Endpoints Show References", "PASS", "No pending jerseys found in admin endpoint (acceptable)")
                    return True
            else:
                self.log_test("Admin Endpoints Show References", "FAIL", f"Admin endpoint failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Endpoints Show References", "FAIL", f"Exception: {str(e)}")
            return False
        finally:
            # Restore user auth
            if self.auth_token:
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
    
    def run_all_tests(self):
        """Run all reference system and notification tests"""
        print("🚀 Starting TopKit Enhanced Backend Testing - Jersey Reference System & Notifications")
        print("=" * 80)
        
        tests = [
            self.setup_test_users,
            self.test_jersey_reference_generation,
            self.test_jersey_submission_notification,
            self.test_user_registration_welcome_notification,
            self.test_jersey_approval_notification,
            self.test_resubmission_preserves_reference,
            self.test_get_jerseys_includes_reference,
            self.test_get_collections_pending_includes_reference,
            self.test_admin_endpoints_show_references
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ {test.__name__}: FAIL - Exception: {str(e)}")
                failed += 1
        
        print("=" * 80)
        print(f"🏁 Testing Complete: {passed} PASSED, {failed} FAILED")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Jersey Reference System & Enhanced Notifications are working correctly!")
        else:
            print(f"⚠️  {failed} tests failed. Please review the issues above.")
        
        return failed == 0

if __name__ == "__main__":
    tester = TopKitReferenceSystemTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)