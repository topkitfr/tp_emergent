#!/usr/bin/env python3
"""
TopKit Notifications System Testing - Review Request Focus
Testing notifications system after the fix:
1. Authenticate as admin user
2. Check current notifications count via GET /api/notifications
3. Submit a test jersey via POST /api/jerseys
4. Verify a new notification was created
5. Confirm the notification appears in the API response
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://topkit-beta.emergent.host/api"

# Admin credentials from review request
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class NotificationsSystemTester:
    def __init__(self):
        self.admin_token = None
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
        """Step 1: Authenticate as admin user"""
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
                    f"Successfully authenticated admin user: {user_info.get('name', 'Unknown')} (Role: {user_info.get('role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')})"
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
    
    def get_current_notifications_count(self):
        """Step 2: Check current notifications count via GET /api/notifications"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/notifications",
                headers=headers
            )
            
            if response.status_code == 200:
                notifications = response.json()
                count = len(notifications) if isinstance(notifications, list) else 0
                
                self.log_test(
                    "Get Current Notifications Count",
                    True,
                    f"Current notifications count: {count}"
                )
                return count
            else:
                self.log_test(
                    "Get Current Notifications Count",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_test("Get Current Notifications Count", False, "", str(e))
            return None
    
    def submit_test_jersey(self):
        """Step 3: Submit a test jersey via POST /api/jerseys"""
        try:
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            # Create test jersey data
            jersey_data = {
                "team": "Real Madrid CF",
                "season": "2024-25",
                "player": "Vinicius Jr",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Test jersey for notifications system verification"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/jerseys",
                json=jersey_data,
                headers=headers
            )
            
            if response.status_code == 201:
                jersey = response.json()
                jersey_id = jersey.get("id")
                jersey_ref = jersey.get("reference_number")
                jersey_status = jersey.get("status")
                
                self.log_test(
                    "Submit Test Jersey",
                    True,
                    f"Successfully created test jersey (ID: {jersey_id}, Status: {jersey_status}, Ref: {jersey_ref})"
                )
                return jersey_id
            else:
                self.log_test(
                    "Submit Test Jersey",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_test("Submit Test Jersey", False, "", str(e))
            return None
    
    def verify_new_notification_created(self, initial_count):
        """Step 4: Verify a new notification was created"""
        try:
            # Wait a moment for notification to be created
            time.sleep(2)
            
            headers = {
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(
                f"{BACKEND_URL}/notifications",
                headers=headers
            )
            
            if response.status_code == 200:
                notifications = response.json()
                new_count = len(notifications) if isinstance(notifications, list) else 0
                
                if new_count > initial_count:
                    self.log_test(
                        "Verify New Notification Created",
                        True,
                        f"New notification created! Count increased from {initial_count} to {new_count}"
                    )
                    return True, notifications
                else:
                    self.log_test(
                        "Verify New Notification Created",
                        False,
                        f"No new notification created. Count remained at {new_count}",
                        "Notification system may not be working properly"
                    )
                    return False, notifications
            else:
                self.log_test(
                    "Verify New Notification Created",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
                return False, None
                
        except Exception as e:
            self.log_test("Verify New Notification Created", False, "", str(e))
            return False, None
    
    def confirm_notification_in_response(self, notifications):
        """Step 5: Confirm the notification appears in the API response"""
        try:
            if not notifications or not isinstance(notifications, list):
                self.log_test(
                    "Confirm Notification in Response",
                    False,
                    "",
                    "No notifications data to analyze"
                )
                return False
            
            # Look for recent notifications related to jersey submission
            recent_notifications = []
            jersey_related_notifications = []
            
            for notification in notifications:
                # Check if notification is recent (within last 5 minutes)
                created_at = notification.get("created_at")
                if created_at:
                    try:
                        # Parse the timestamp and check if it's recent
                        notification_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        time_diff = datetime.now().timestamp() - notification_time.timestamp()
                        if time_diff < 300:  # 5 minutes
                            recent_notifications.append(notification)
                    except:
                        pass
                
                # Check if notification is jersey-related
                notification_type = notification.get("type", "")
                title = notification.get("title", "")
                message = notification.get("message", "")
                
                if any(keyword in title.lower() or keyword in message.lower() or keyword in notification_type.lower() 
                       for keyword in ["jersey", "maillot", "submission", "soumission"]):
                    jersey_related_notifications.append(notification)
            
            if recent_notifications:
                self.log_test(
                    "Confirm Notification in Response",
                    True,
                    f"Found {len(recent_notifications)} recent notifications, {len(jersey_related_notifications)} jersey-related notifications"
                )
                
                # Show details of recent notifications
                for i, notif in enumerate(recent_notifications[:3]):  # Show first 3
                    print(f"    Recent Notification {i+1}: {notif.get('title', 'No title')} - {notif.get('type', 'No type')}")
                
                return True
            else:
                self.log_test(
                    "Confirm Notification in Response",
                    False,
                    f"No recent notifications found. Total notifications: {len(notifications)}, Jersey-related: {len(jersey_related_notifications)}",
                    "New notification may not have been created or is not recent"
                )
                return False
                
        except Exception as e:
            self.log_test("Confirm Notification in Response", False, "", str(e))
            return False
    
    def run_notifications_test(self):
        """Run the complete notifications system test"""
        print("🔔 TOPKIT NOTIFICATIONS SYSTEM TESTING - REVIEW REQUEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_CREDENTIALS['email']}")
        print()
        
        # Step 1: Authenticate as admin user
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with testing.")
            return False
        
        # Step 2: Check current notifications count
        initial_count = self.get_current_notifications_count()
        if initial_count is None:
            print("❌ CRITICAL: Could not retrieve current notifications count. Cannot proceed.")
            return False
        
        # Step 3: Submit a test jersey
        jersey_id = self.submit_test_jersey()
        if not jersey_id:
            print("❌ CRITICAL: Jersey submission failed. Cannot test notification creation.")
            return False
        
        # Step 4: Verify a new notification was created
        notification_created, notifications = self.verify_new_notification_created(initial_count)
        
        # Step 5: Confirm the notification appears in the API response
        if notification_created and notifications:
            self.confirm_notification_in_response(notifications)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 NOTIFICATIONS SYSTEM STATUS: WORKING CORRECTLY")
        elif success_rate >= 60:
            print("⚠️ NOTIFICATIONS SYSTEM STATUS: PARTIALLY WORKING")
        else:
            print("❌ NOTIFICATIONS SYSTEM STATUS: CRITICAL ISSUES DETECTED")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        return success_rate >= 80

def main():
    """Main function to run notifications system testing"""
    tester = NotificationsSystemTester()
    success = tester.run_notifications_test()
    
    if success:
        print("\n✅ CONCLUSION: Notifications system is working correctly after the fix!")
        sys.exit(0)
    else:
        print("\n❌ CONCLUSION: Notifications system has issues that need to be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main()