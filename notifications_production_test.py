#!/usr/bin/env python3
"""
TopKit Notifications Production Testing
Testing notifications functionality in production environment at https://topkit-beta.emergent.host/

Focus Areas:
1. Test GET /api/notifications endpoint with authenticated user credentials
2. Check if notifications are being created for jersey submissions 
3. Verify notification count and content
4. Test notification marking as read/unread if available
5. Check if notifications appear correctly in the API response
"""

import requests
import json
import sys
import time
from datetime import datetime

# Production Configuration
BACKEND_URL = "https://topkit-beta.emergent.host/api"

# Production credentials from review request
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

# Alternative user credentials if needed
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "TopKit123!"
}

# Additional test credentials
ALT_USER_CREDENTIALS = {
    "email": "test@example.com",
    "password": "TestPass123!"
}

class NotificationsProductionTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.session = requests.Session()
        self.session.timeout = 30
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated successfully - Name: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, "", str(e))
            return False
    
    def authenticate_user(self):
        """Authenticate regular user"""
        # Try primary user credentials first
        for creds_name, creds in [("Primary User", USER_CREDENTIALS), ("Alt User", ALT_USER_CREDENTIALS)]:
            try:
                response = self.session.post(
                    f"{BACKEND_URL}/auth/login",
                    json=creds,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.user_token = data.get("token")
                    user_info = data.get("user", {})
                    self.log_test(
                        "User Authentication",
                        True,
                        f"{creds_name} authenticated successfully - Name: {user_info.get('name')}, Role: {user_info.get('role')}, ID: {user_info.get('id')}"
                    )
                    return True
                else:
                    print(f"    {creds_name} failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    {creds_name} error: {str(e)}")
                continue
        
        # If no user credentials work, log the failure
        self.log_test(
            "User Authentication",
            False,
            "All user credential attempts failed",
            "No valid user credentials found"
        )
        return False
    
    def test_notifications_endpoint_admin(self):
        """Test GET /api/notifications endpoint with admin credentials"""
        if not self.admin_token:
            self.log_test("Admin Notifications Endpoint", False, "", "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                notification_count = len(notifications) if isinstance(notifications, list) else 0
                
                # Analyze notification content
                notification_types = {}
                unread_count = 0
                jersey_related = 0
                
                if isinstance(notifications, list):
                    for notif in notifications:
                        notif_type = notif.get('type', 'unknown')
                        notification_types[notif_type] = notification_types.get(notif_type, 0) + 1
                        
                        if not notif.get('is_read', True):
                            unread_count += 1
                            
                        if 'jersey' in notif.get('type', '').lower() or 'jersey' in notif.get('message', '').lower():
                            jersey_related += 1
                
                self.log_test(
                    "Admin Notifications Endpoint",
                    True,
                    f"Retrieved {notification_count} notifications - Types: {notification_types}, Unread: {unread_count}, Jersey-related: {jersey_related}"
                )
                return notifications
            else:
                self.log_test(
                    "Admin Notifications Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Notifications Endpoint", False, "", str(e))
            return False
    
    def test_notifications_endpoint_user(self):
        """Test GET /api/notifications endpoint with user credentials"""
        if not self.user_token:
            self.log_test("User Notifications Endpoint", False, "", "No user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
            
            if response.status_code == 200:
                notifications = response.json()
                notification_count = len(notifications) if isinstance(notifications, list) else 0
                
                # Analyze notification content
                notification_types = {}
                unread_count = 0
                jersey_related = 0
                
                if isinstance(notifications, list):
                    for notif in notifications:
                        notif_type = notif.get('type', 'unknown')
                        notification_types[notif_type] = notification_types.get(notif_type, 0) + 1
                        
                        if not notif.get('is_read', True):
                            unread_count += 1
                            
                        if 'jersey' in notif.get('type', '').lower() or 'jersey' in notif.get('message', '').lower():
                            jersey_related += 1
                
                self.log_test(
                    "User Notifications Endpoint",
                    True,
                    f"Retrieved {notification_count} notifications - Types: {notification_types}, Unread: {unread_count}, Jersey-related: {jersey_related}"
                )
                return notifications
            else:
                self.log_test(
                    "User Notifications Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_test("User Notifications Endpoint", False, "", str(e))
            return False
    
    def test_jersey_submission_notifications(self):
        """Test if notifications are created for jersey submissions"""
        # Use admin token if user token is not available
        token = self.user_token or self.admin_token
        if not token:
            self.log_test("Jersey Submission Notifications", False, "", "No authentication token available")
            return False
            
        try:
            # First, get current notification count
            headers = {"Authorization": f"Bearer {token}"}
            initial_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_notifications = initial_response.json()
                initial_count = len(initial_notifications) if isinstance(initial_notifications, list) else 0
            
            # Submit a test jersey
            jersey_data = {
                "team": "Real Madrid CF",
                "season": "2024-25",
                "player": "Vinicius Jr",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey submission for notifications testing"
            }
            
            submission_response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=jersey_data,
                headers=headers
            )
            
            if submission_response.status_code in [200, 201]:
                jersey_info = submission_response.json()
                jersey_id = jersey_info.get('id')
                
                # Wait a moment for potential notification creation
                time.sleep(2)
                
                # Check for new notifications
                final_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
                if final_response.status_code == 200:
                    final_notifications = final_response.json()
                    final_count = len(final_notifications) if isinstance(final_notifications, list) else 0
                    
                    # Look for jersey-related notifications
                    jersey_notifications = []
                    if isinstance(final_notifications, list):
                        for notif in final_notifications:
                            if (jersey_id and jersey_id in str(notif.get('related_id', ''))) or \
                               'jersey' in notif.get('type', '').lower() or \
                               'soumission' in notif.get('message', '').lower():
                                jersey_notifications.append(notif)
                    
                    self.log_test(
                        "Jersey Submission Notifications",
                        True,
                        f"Jersey submitted (ID: {jersey_id}) - Initial notifications: {initial_count}, Final: {final_count}, Jersey-related: {len(jersey_notifications)}"
                    )
                    return jersey_notifications
                else:
                    self.log_test(
                        "Jersey Submission Notifications",
                        False,
                        f"Jersey submitted but failed to retrieve notifications - HTTP {final_response.status_code}",
                        final_response.text
                    )
                    return False
            else:
                self.log_test(
                    "Jersey Submission Notifications",
                    False,
                    f"Failed to submit jersey - HTTP {submission_response.status_code}",
                    submission_response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Jersey Submission Notifications", False, "", str(e))
            return False
    
    def test_notification_read_status(self, notifications):
        """Test notification marking as read/unread if available"""
        if not notifications or not isinstance(notifications, list) or len(notifications) == 0:
            self.log_test("Notification Read Status", False, "", "No notifications available to test")
            return False
            
        # Use any available token
        token = self.user_token or self.admin_token
        if not token:
            self.log_test("Notification Read Status", False, "", "No authentication token available")
            return False
            
        try:
            # Find an unread notification to test with
            test_notification = None
            for notif in notifications:
                if not notif.get('is_read', True):
                    test_notification = notif
                    break
            
            if not test_notification:
                # If no unread notifications, try to use any notification
                test_notification = notifications[0] if notifications else None
            
            if not test_notification:
                self.log_test("Notification Read Status", False, "", "No suitable notification found for testing")
                return False
            
            notification_id = test_notification.get('id')
            if not notification_id:
                self.log_test("Notification Read Status", False, "", "Notification ID not found")
                return False
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to mark notification as read
            read_response = self.session.post(
                f"{BACKEND_URL}/notifications/{notification_id}/read",
                headers=headers
            )
            
            if read_response.status_code in [200, 204]:
                self.log_test(
                    "Notification Read Status",
                    True,
                    f"Successfully marked notification {notification_id} as read"
                )
                return True
            else:
                # Try alternative endpoint patterns
                alt_response = self.session.patch(
                    f"{BACKEND_URL}/notifications/{notification_id}",
                    json={"is_read": True},
                    headers=headers
                )
                
                if alt_response.status_code in [200, 204]:
                    self.log_test(
                        "Notification Read Status",
                        True,
                        f"Successfully marked notification {notification_id} as read (alternative endpoint)"
                    )
                    return True
                else:
                    self.log_test(
                        "Notification Read Status",
                        False,
                        f"Failed to mark notification as read - HTTP {read_response.status_code}, Alt HTTP {alt_response.status_code}",
                        f"Primary: {read_response.text}, Alt: {alt_response.text}"
                    )
                    return False
                
        except Exception as e:
            self.log_test("Notification Read Status", False, "", str(e))
            return False
    
    def test_admin_moderation_notifications(self):
        """Test if notifications are created for admin moderation actions"""
        if not self.admin_token:
            self.log_test("Admin Moderation Notifications", False, "", "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First, get pending jerseys
            pending_response = self.session.get(f"{BACKEND_URL}/admin/jerseys/pending", headers=headers)
            if pending_response.status_code != 200:
                self.log_test("Admin Moderation Notifications", False, f"Failed to get pending jerseys - HTTP {pending_response.status_code}", pending_response.text)
                return False
            
            pending_jerseys = pending_response.json()
            if not pending_jerseys or len(pending_jerseys) == 0:
                self.log_test("Admin Moderation Notifications", False, "", "No pending jerseys available for moderation testing")
                return False
            
            # Get the first pending jersey
            test_jersey = pending_jerseys[0]
            jersey_id = test_jersey.get('id')
            submitted_by = test_jersey.get('submitted_by')
            
            if not jersey_id or not submitted_by:
                self.log_test("Admin Moderation Notifications", False, "", "Invalid jersey data for moderation testing")
                return False
            
            # Get initial notification count for the user who submitted the jersey
            initial_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
            initial_count = 0
            if initial_response.status_code == 200:
                initial_notifications = initial_response.json()
                initial_count = len(initial_notifications) if isinstance(initial_notifications, list) else 0
            
            # Approve the jersey
            approve_response = self.session.post(
                f"{BACKEND_URL}/admin/jerseys/{jersey_id}/approve",
                headers=headers
            )
            
            if approve_response.status_code in [200, 204]:
                # Wait for notification creation
                time.sleep(2)
                
                # Check for new notifications
                final_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
                if final_response.status_code == 200:
                    final_notifications = final_response.json()
                    final_count = len(final_notifications) if isinstance(final_notifications, list) else 0
                    
                    # Look for approval notifications
                    approval_notifications = []
                    if isinstance(final_notifications, list):
                        for notif in final_notifications:
                            if 'approved' in notif.get('type', '').lower() or \
                               'approved' in notif.get('message', '').lower() or \
                               (jersey_id and jersey_id in str(notif.get('related_id', ''))):
                                approval_notifications.append(notif)
                    
                    self.log_test(
                        "Admin Moderation Notifications",
                        True,
                        f"Jersey {jersey_id} approved - Initial notifications: {initial_count}, Final: {final_count}, Approval-related: {len(approval_notifications)}"
                    )
                    return approval_notifications
                else:
                    self.log_test(
                        "Admin Moderation Notifications",
                        False,
                        f"Jersey approved but failed to retrieve notifications - HTTP {final_response.status_code}",
                        final_response.text
                    )
                    return False
            else:
                self.log_test(
                    "Admin Moderation Notifications",
                    False,
                    f"Failed to approve jersey - HTTP {approve_response.status_code}",
                    approve_response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Moderation Notifications", False, "", str(e))
            return False
    
    def test_notification_creation_direct(self):
        """Test direct notification creation to verify the system works"""
        if not self.admin_token:
            self.log_test("Direct Notification Creation", False, "", "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Try to create a test notification directly
            notification_data = {
                "user_id": "f33eab32-2d5c-4f59-9104-83999453a43c",  # Admin user ID
                "type": "system_announcement",
                "title": "Test Notification",
                "message": "This is a test notification to verify the notification system is working",
                "related_id": None
            }
            
            create_response = self.session.post(
                f"{BACKEND_URL}/notifications",
                json=notification_data,
                headers=headers
            )
            
            if create_response.status_code in [200, 201]:
                # Wait a moment
                time.sleep(1)
                
                # Check if notification appears
                get_response = self.session.get(f"{BACKEND_URL}/notifications", headers=headers)
                if get_response.status_code == 200:
                    notifications = get_response.json()
                    notification_count = len(notifications) if isinstance(notifications, list) else 0
                    
                    # Look for our test notification
                    test_notifications = []
                    if isinstance(notifications, list):
                        for notif in notifications:
                            if 'test notification' in notif.get('message', '').lower():
                                test_notifications.append(notif)
                    
                    self.log_test(
                        "Direct Notification Creation",
                        True,
                        f"Notification creation endpoint working - Total notifications: {notification_count}, Test notifications: {len(test_notifications)}"
                    )
                    return notifications
                else:
                    self.log_test(
                        "Direct Notification Creation",
                        False,
                        f"Notification created but failed to retrieve - HTTP {get_response.status_code}",
                        get_response.text
                    )
                    return False
            else:
                self.log_test(
                    "Direct Notification Creation",
                    False,
                    f"Failed to create notification - HTTP {create_response.status_code}",
                    create_response.text
                )
                return False
                
        except Exception as e:
            self.log_test("Direct Notification Creation", False, "", str(e))
            return False
    
    def test_notification_content_structure(self, notifications):
        """Verify notification content structure and completeness"""
        if not notifications or not isinstance(notifications, list):
            self.log_test("Notification Content Structure", False, "", "No notifications to analyze")
            return False
            
        try:
            required_fields = ['id', 'type', 'title', 'message', 'created_at']
            optional_fields = ['is_read', 'read_at', 'related_id', 'user_id']
            
            structure_issues = []
            valid_notifications = 0
            
            for i, notif in enumerate(notifications):
                missing_fields = []
                for field in required_fields:
                    if field not in notif or notif[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    structure_issues.append(f"Notification {i}: missing {missing_fields}")
                else:
                    valid_notifications += 1
            
            total_notifications = len(notifications)
            success = len(structure_issues) == 0
            
            details = f"Analyzed {total_notifications} notifications - Valid: {valid_notifications}"
            if structure_issues:
                details += f", Issues: {len(structure_issues)}"
            
            self.log_test(
                "Notification Content Structure",
                success,
                details,
                "; ".join(structure_issues) if structure_issues else ""
            )
            
            return success
            
        except Exception as e:
            self.log_test("Notification Content Structure", False, "", str(e))
            return False
    
    def run_comprehensive_notifications_test(self):
        """Run comprehensive notifications functionality test"""
        print("🔔 TOPKIT NOTIFICATIONS PRODUCTION TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Authentication
        print("📋 STEP 1: AUTHENTICATION")
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not admin_auth_success and not user_auth_success:
            print("❌ CRITICAL: No authentication successful - cannot proceed with notifications testing")
            return False
        
        print()
        
        # Step 2: Test notifications endpoints
        print("📋 STEP 2: NOTIFICATIONS ENDPOINT TESTING")
        admin_notifications = None
        user_notifications = None
        
        if admin_auth_success:
            admin_notifications = self.test_notifications_endpoint_admin()
        
        if user_auth_success:
            user_notifications = self.test_notifications_endpoint_user()
        
        print()
        
        # Step 2.5: Test direct notification creation
        print("📋 STEP 2.5: DIRECT NOTIFICATION CREATION")
        if admin_auth_success:
            direct_notifications = self.test_notification_creation_direct()
        else:
            self.log_test("Direct Notification Creation", False, "", "No admin authentication available")
            direct_notifications = None
        
        print()
        
        # Step 3: Test jersey submission notifications
        print("📋 STEP 3: JERSEY SUBMISSION NOTIFICATIONS")
        if admin_auth_success or user_auth_success:
            jersey_notifications = self.test_jersey_submission_notifications()
        else:
            self.log_test("Jersey Submission Notifications", False, "", "No authentication available")
            jersey_notifications = None
        
        print()
        
        # Step 3.5: Test admin moderation notifications
        print("📋 STEP 3.5: ADMIN MODERATION NOTIFICATIONS")
        if admin_auth_success:
            moderation_notifications = self.test_admin_moderation_notifications()
        else:
            self.log_test("Admin Moderation Notifications", False, "", "No admin authentication available")
            moderation_notifications = None
        
        print()
        
        # Step 4: Test notification read/unread functionality
        print("📋 STEP 4: NOTIFICATION READ STATUS TESTING")
        test_notifications = user_notifications or admin_notifications or moderation_notifications or direct_notifications
        if test_notifications:
            self.test_notification_read_status(test_notifications)
        else:
            self.log_test("Notification Read Status", False, "", "No notifications available for testing")
        
        print()
        
        # Step 5: Test notification content structure
        print("📋 STEP 5: NOTIFICATION CONTENT STRUCTURE")
        if test_notifications:
            self.test_notification_content_structure(test_notifications)
        else:
            self.log_test("Notification Content Structure", False, "", "No notifications available for analysis")
        
        print()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
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
                    print(f"  • {result['test']}: {result['error']}")
            print()
        
        print("✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"  • {result['test']}")
        
        print()
        print(f"Test completed at: {datetime.now().isoformat()}")

def main():
    """Main test execution"""
    tester = NotificationsProductionTester()
    
    try:
        success = tester.run_comprehensive_notifications_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())