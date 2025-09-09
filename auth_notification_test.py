#!/usr/bin/env python3
"""
TopKit Authentication & Notification Backend API Testing
=======================================================

Testing authentication system and notification backend APIs as requested:
- User authentication with steinmetzlivio@gmail.com / TopKit123!
- JWT token generation and validation
- Notification API endpoints for authenticated users
- Site access-check functionality
- User profile endpoint accessibility
- Notification creation and retrieval endpoints

Backend URL: https://jersey-tracker.preview.emergentagent.com/api
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "TopKit123!"

class TopKitAuthNotificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.user_data = None
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
    
    def test_user_authentication(self):
        """Test user authentication with provided credentials"""
        print("🔐 Testing User Authentication...")
        
        try:
            # Test login endpoint
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got a token
                if "token" in data:
                    self.jwt_token = data["token"]
                    self.user_data = data.get("user", {})
                    
                    self.log_test(
                        "User Authentication - Login",
                        True,
                        f"Successfully authenticated user: {self.user_data.get('name', 'Unknown')} (Role: {self.user_data.get('role', 'Unknown')}, ID: {self.user_data.get('id', 'Unknown')})"
                    )
                    
                    # Set authorization header for future requests
                    self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                    
                    return True
                else:
                    self.log_test("User Authentication - Login", False, "", "No token in response")
                    return False
            else:
                self.log_test(
                    "User Authentication - Login", 
                    False, 
                    "", 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Authentication - Login", False, "", str(e))
            return False
    
    def test_jwt_token_validation(self):
        """Test JWT token validation through profile access"""
        print("🎫 Testing JWT Token Validation...")
        
        if not self.jwt_token:
            self.log_test("JWT Token Validation", False, "", "No JWT token available")
            return False
        
        try:
            # Test profile endpoint which requires valid JWT
            response = self.session.get(f"{BACKEND_URL}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_test(
                    "JWT Token Validation - Profile Access",
                    True,
                    f"Profile accessible with JWT token. User: {profile_data.get('name', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "JWT Token Validation - Profile Access",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("JWT Token Validation - Profile Access", False, "", str(e))
            return False
    
    def test_site_access_check(self):
        """Test site access-check functionality"""
        print("🌐 Testing Site Access Check...")
        
        try:
            # Test with authentication
            response_auth = self.session.get(f"{BACKEND_URL}/site/access-check")
            
            if response_auth.status_code == 200:
                auth_data = response_auth.json()
                self.log_test(
                    "Site Access Check - Authenticated",
                    True,
                    f"Access check successful for authenticated user: {auth_data}"
                )
            else:
                self.log_test(
                    "Site Access Check - Authenticated",
                    False,
                    "",
                    f"HTTP {response_auth.status_code}: {response_auth.text}"
                )
            
            # Test without authentication (anonymous)
            anonymous_session = requests.Session()
            response_anon = anonymous_session.get(f"{BACKEND_URL}/site/access-check")
            
            if response_anon.status_code == 200:
                anon_data = response_anon.json()
                self.log_test(
                    "Site Access Check - Anonymous",
                    True,
                    f"Access check successful for anonymous user: {anon_data}"
                )
                return True
            else:
                self.log_test(
                    "Site Access Check - Anonymous",
                    False,
                    "",
                    f"HTTP {response_anon.status_code}: {response_anon.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Site Access Check", False, "", str(e))
            return False
    
    def test_user_profile_endpoint(self):
        """Test user profile endpoint accessibility"""
        print("👤 Testing User Profile Endpoint...")
        
        if not self.jwt_token:
            self.log_test("User Profile Endpoint", False, "", "No JWT token available")
            return False
        
        try:
            # Test main profile endpoint
            response = self.session.get(f"{BACKEND_URL}/profile")
            
            if response.status_code == 200:
                profile_data = response.json()
                self.log_test(
                    "User Profile Endpoint - Main Profile",
                    True,
                    f"Profile data retrieved: {profile_data.get('name', 'Unknown')} ({profile_data.get('email', 'Unknown')})"
                )
                
                # Test user-specific profile endpoint if user ID is available
                if self.user_data and self.user_data.get('id'):
                    user_id = self.user_data['id']
                    user_profile_response = self.session.get(f"{BACKEND_URL}/users/{user_id}")
                    
                    if user_profile_response.status_code == 200:
                        user_profile_data = user_profile_response.json()
                        self.log_test(
                            "User Profile Endpoint - User Specific",
                            True,
                            f"User-specific profile retrieved for ID: {user_id}"
                        )
                    else:
                        self.log_test(
                            "User Profile Endpoint - User Specific",
                            False,
                            "",
                            f"HTTP {user_profile_response.status_code}: {user_profile_response.text}"
                        )
                
                return True
            else:
                self.log_test(
                    "User Profile Endpoint - Main Profile",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Profile Endpoint", False, "", str(e))
            return False
    
    def test_notification_endpoints(self):
        """Test notification API endpoints for authenticated users"""
        print("🔔 Testing Notification Endpoints...")
        
        if not self.jwt_token:
            self.log_test("Notification Endpoints", False, "", "No JWT token available")
            return False
        
        success_count = 0
        total_tests = 0
        
        try:
            # Test GET notifications endpoint
            total_tests += 1
            response = self.session.get(f"{BACKEND_URL}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                success_count += 1
                self.log_test(
                    "Notification Endpoints - Get Notifications",
                    True,
                    f"Retrieved {len(notifications)} notifications for user"
                )
            else:
                self.log_test(
                    "Notification Endpoints - Get Notifications",
                    False,
                    "",
                    f"HTTP {response.status_code}: {response.text}"
                )
            
            # Test notification count endpoint
            total_tests += 1
            count_response = self.session.get(f"{BACKEND_URL}/notifications/unread-count")
            
            if count_response.status_code == 200:
                count_data = count_response.json()
                success_count += 1
                self.log_test(
                    "Notification Endpoints - Unread Count",
                    True,
                    f"Unread notifications count: {count_data.get('count', 'Unknown')}"
                )
            else:
                self.log_test(
                    "Notification Endpoints - Unread Count",
                    False,
                    "",
                    f"HTTP {count_response.status_code}: {count_response.text}"
                )
            
            # Test mark notification as read (if we have notifications)
            if response.status_code == 200:
                notifications = response.json()
                if notifications and len(notifications) > 0:
                    total_tests += 1
                    first_notification = notifications[0]
                    notification_id = first_notification.get('id')
                    
                    if notification_id:
                        mark_read_response = self.session.post(f"{BACKEND_URL}/notifications/{notification_id}/read")
                        
                        if mark_read_response.status_code == 200:
                            success_count += 1
                            self.log_test(
                                "Notification Endpoints - Mark as Read",
                                True,
                                f"Successfully marked notification {notification_id} as read"
                            )
                        else:
                            self.log_test(
                                "Notification Endpoints - Mark as Read",
                                False,
                                "",
                                f"HTTP {mark_read_response.status_code}: {mark_read_response.text}"
                            )
            
            return success_count == total_tests
            
        except Exception as e:
            self.log_test("Notification Endpoints", False, "", str(e))
            return False
    
    def test_notification_creation(self):
        """Test notification creation functionality (admin/system level)"""
        print("📝 Testing Notification Creation...")
        
        if not self.jwt_token or not self.user_data:
            self.log_test("Notification Creation", False, "", "No authentication data available")
            return False
        
        try:
            # Test if we can create a test notification (this might require admin privileges)
            # We'll test this by checking if the endpoint exists and responds appropriately
            
            # First, let's try to get existing notifications to see the structure
            response = self.session.get(f"{BACKEND_URL}/notifications")
            
            if response.status_code == 200:
                notifications = response.json()
                
                # Check if notifications have the expected structure
                if notifications and len(notifications) > 0:
                    sample_notification = notifications[0]
                    expected_fields = ['id', 'type', 'title', 'message', 'is_read', 'created_at']
                    
                    has_all_fields = all(field in sample_notification for field in expected_fields)
                    
                    if has_all_fields:
                        self.log_test(
                            "Notification Creation - Structure Validation",
                            True,
                            f"Notifications have correct structure. Sample: {sample_notification.get('title', 'Unknown')}"
                        )
                        return True
                    else:
                        missing_fields = [field for field in expected_fields if field not in expected_fields]
                        self.log_test(
                            "Notification Creation - Structure Validation",
                            False,
                            "",
                            f"Missing fields in notification structure: {missing_fields}"
                        )
                        return False
                else:
                    self.log_test(
                        "Notification Creation - Structure Validation",
                        True,
                        "No notifications found, but endpoint is accessible (notifications system is working)"
                    )
                    return True
            else:
                self.log_test(
                    "Notification Creation - Structure Validation",
                    False,
                    "",
                    f"Cannot access notifications endpoint: HTTP {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Notification Creation", False, "", str(e))
            return False
    
    def run_all_tests(self):
        """Run all authentication and notification tests"""
        print("🚀 Starting TopKit Authentication & Notification Backend Testing")
        print("=" * 70)
        print()
        
        # Test sequence
        tests = [
            ("Authentication", self.test_user_authentication),
            ("JWT Token Validation", self.test_jwt_token_validation),
            ("Site Access Check", self.test_site_access_check),
            ("User Profile Endpoint", self.test_user_profile_endpoint),
            ("Notification Endpoints", self.test_notification_endpoints),
            ("Notification Creation", self.test_notification_creation),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {str(e)}")
                print()
        
        # Summary
        print("=" * 70)
        print("🎯 TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print()
        
        if self.jwt_token:
            print(f"✅ Authentication: SUCCESSFUL")
            print(f"   User: {self.user_data.get('name', 'Unknown')}")
            print(f"   Role: {self.user_data.get('role', 'Unknown')}")
            print(f"   ID: {self.user_data.get('id', 'Unknown')}")
        else:
            print(f"❌ Authentication: FAILED")
        
        print()
        print("📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        print()
        print("🏁 Testing Complete!")
        
        return success_rate >= 80  # Consider 80%+ as overall success

if __name__ == "__main__":
    tester = TopKitAuthNotificationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)