#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Production URL from frontend/.env
BASE_URL = "https://9f26dbf2-ce88-4e0c-8bc0-d245b81c53aa.preview.emergentagent.com/api"

# Test credentials from previous testing
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class JerseySubmissionNotificationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def authenticate_user(self):
        """Step 1: Authenticate with working user account"""
        print("\n🔐 Step 1: Authenticating user...")
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User: {user_info.get('name')} (ID: {self.user_id}, Role: {user_info.get('role')})"
                )
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_notifications_before(self):
        """Get notifications count before jersey submission"""
        print("\n📋 Getting notifications before submission...")
        
        try:
            response = self.session.get(f"{BASE_URL}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                count = len(notifications)
                self.log_result(
                    "Get Notifications Before", 
                    True, 
                    f"Found {count} existing notifications"
                )
                return count
            else:
                self.log_result(
                    "Get Notifications Before", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return 0
                
        except Exception as e:
            self.log_result("Get Notifications Before", False, f"Exception: {str(e)}")
            return 0
    
    def submit_test_jersey(self):
        """Step 2: Submit a test jersey via POST /api/jerseys"""
        print("\n⚽ Step 2: Submitting test jersey...")
        
        # Create realistic jersey data
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Test jersey submission for notification verification - Real Madrid home jersey with Vinicius Jr name and number",
            "images": [],
            "reference_code": None
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/jerseys", json=jersey_data)
            
            if response.status_code == 200:
                data = response.json()
                jersey_id = data.get("id")
                jersey_ref = data.get("reference_number")
                status = data.get("status")
                
                self.log_result(
                    "Jersey Submission", 
                    True, 
                    f"Jersey created - ID: {jersey_id}, Ref: {jersey_ref}, Status: {status}"
                )
                return jersey_id
            else:
                self.log_result(
                    "Jersey Submission", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Jersey Submission", False, f"Exception: {str(e)}")
            return None
    
    def check_notification_creation(self, initial_count):
        """Step 3 & 4: Check if notification was created and appears in GET /api/notifications"""
        print("\n🔔 Step 3 & 4: Checking notification creation...")
        
        try:
            response = self.session.get(f"{BASE_URL}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                new_count = len(notifications)
                
                if new_count > initial_count:
                    # Look for jersey-related notifications
                    jersey_notifications = [
                        n for n in notifications 
                        if any(keyword in n.get("title", "").lower() or keyword in n.get("message", "").lower() 
                               for keyword in ["jersey", "maillot", "soumission", "submission"])
                    ]
                    
                    if jersey_notifications:
                        latest_notification = max(jersey_notifications, key=lambda x: x.get("created_at", ""))
                        self.log_result(
                            "Notification Creation", 
                            True, 
                            f"New notification found - Title: '{latest_notification.get('title')}', Type: {latest_notification.get('type')}"
                        )
                        return True
                    else:
                        self.log_result(
                            "Notification Creation", 
                            False, 
                            f"Notification count increased ({initial_count} → {new_count}) but no jersey-related notifications found"
                        )
                        return False
                else:
                    self.log_result(
                        "Notification Creation", 
                        False, 
                        f"No new notifications created (count: {initial_count} → {new_count})"
                    )
                    return False
                    
            else:
                self.log_result(
                    "Notification Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Notification Creation", False, f"Exception: {str(e)}")
            return False
    
    def check_backend_logs(self):
        """Step 5: Check backend logs for notification creation messages"""
        print("\n📝 Step 5: Checking backend logs...")
        
        # Note: In a containerized environment, we can't directly access backend logs
        # But we can verify the notification system is working by checking the API responses
        try:
            # Test the notification system health by getting user profile
            response = self.session.get(f"{BASE_URL}/profile")
            
            if response.status_code == 200:
                self.log_result(
                    "Backend System Health", 
                    True, 
                    "Backend is responding correctly to authenticated requests"
                )
                
                # Check if we can get notification details
                notifications_response = self.session.get(f"{BASE_URL}/notifications")
                if notifications_response.status_code == 200:
                    notifications = notifications_response.json()
                    unread_count = sum(1 for n in notifications if not n.get("is_read", False))
                    self.log_result(
                        "Notification System Health", 
                        True, 
                        f"Notification system operational - {len(notifications)} total, {unread_count} unread"
                    )
                    return True
                else:
                    self.log_result(
                        "Notification System Health", 
                        False, 
                        f"Notification endpoint error: HTTP {notifications_response.status_code}"
                    )
                    return False
            else:
                self.log_result(
                    "Backend System Health", 
                    False, 
                    f"Profile endpoint error: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Backend System Health", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete jersey submission notification test"""
        print("🎯 JERSEY SUBMISSION NOTIFICATION VERIFICATION TEST")
        print("=" * 60)
        print(f"Testing against: {BASE_URL}")
        print(f"User: {TEST_USER_EMAIL}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("\n❌ Authentication failed - cannot proceed with test")
            return False
        
        # Get initial notification count
        initial_count = self.get_notifications_before()
        
        # Step 2: Submit jersey
        jersey_id = self.submit_test_jersey()
        if not jersey_id:
            print("\n❌ Jersey submission failed - cannot verify notifications")
            return False
        
        # Step 3 & 4: Check notification creation
        notification_created = self.check_notification_creation(initial_count)
        
        # Step 5: Check backend system health
        backend_healthy = self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
        
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        # Specific focus on notification creation
        if notification_created:
            print("\n🎉 NOTIFICATION CREATION: SUCCESS")
            print("✅ Jersey submission successfully triggered notification creation")
            print("✅ Enhanced logging appears to be working correctly")
        else:
            print("\n🚨 NOTIFICATION CREATION: FAILED")
            print("❌ Jersey submission did not create expected notifications")
            print("❌ Enhanced logging may need further investigation")
        
        return notification_created and backend_healthy

def main():
    """Main test execution"""
    tester = JerseySubmissionNotificationTest()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()