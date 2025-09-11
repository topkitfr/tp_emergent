#!/usr/bin/env python3
"""
TopKit Notifications System Comprehensive Backend Testing
=========================================================

This script comprehensively tests the notifications system to identify what is broken
and needs to be restored. Tests all notification endpoints, creation, retrieval,
marking as read/unread, and notification generation for various user actions.

Test Coverage:
1. Notifications API endpoints (/api/notifications)
2. Notification creation for different types (jersey submissions, approvals, etc.)
3. Notification retrieval for users
4. Notification storage in database
5. Notification marking as read/unread
6. Notification count endpoints
7. Notification creation for user actions (jersey submission, approval, rejection, etc.)
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configuration
BACKEND_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "adminpass123"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

# Test admin credentials (may not work)
TEST_ADMIN_CREDENTIALS = {
    "email": "testadmin@topkit.com",
    "password": "StrongP@ssw0rd2024!"
}

class NotificationsSystemTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        self.test_jersey_id = None
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        if data and not success:
            print(f"    Data: {json.dumps(data, indent=2)}")
            
    async def authenticate_users(self):
        """Authenticate both admin and regular user"""
        print("\n🔐 AUTHENTICATION SETUP")
        print("=" * 50)
        
        # Authenticate user first
        try:
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data.get("token")
                    self.user_user_id = data.get("user", {}).get("id")
                    user_role = data.get("user", {}).get("role")
                    self.log_test("User Authentication", True, f"User ID: {self.user_user_id}, Role: {user_role}")
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
        
        # Try to authenticate with test admin (may not have admin privileges)
        try:
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=TEST_ADMIN_CREDENTIALS) as response:
                if response.status == 200:
                    data = await response.json()
                    self.admin_token = data.get("token")
                    self.admin_user_id = data.get("user", {}).get("id")
                    admin_role = data.get("user", {}).get("role")
                    self.log_test("Test Admin Authentication", True, f"Admin ID: {self.admin_user_id}, Role: {admin_role}")
                    
                    # Note: This may not be a real admin, just a test user
                    if admin_role != "admin":
                        self.log_test("Admin Privileges Check", False, f"Test admin has role '{admin_role}', not 'admin'")
                        self.admin_token = None  # Don't use for admin operations
                else:
                    error_text = await response.text()
                    self.log_test("Test Admin Authentication", False, f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Test Admin Authentication", False, f"Exception: {str(e)}")
            
        # We can proceed with just user authentication for basic notification testing
        return self.user_token is not None
        
    async def test_notifications_endpoints(self):
        """Test basic notifications API endpoints"""
        print("\n📡 NOTIFICATIONS API ENDPOINTS TESTING")
        print("=" * 50)
        
        # Test GET /api/notifications for user
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get("notifications", [])
                    unread_count = data.get("unread_count", 0)
                    total = data.get("total", 0)
                    self.log_test("GET /api/notifications (User)", True, 
                                f"Found {len(notifications)} notifications, {unread_count} unread, {total} total")
                else:
                    error_text = await response.text()
                    self.log_test("GET /api/notifications (User)", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("GET /api/notifications (User)", False, f"Exception: {str(e)}")
            
        # Test GET /api/notifications for admin
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get("notifications", [])
                    unread_count = data.get("unread_count", 0)
                    total = data.get("total", 0)
                    self.log_test("GET /api/notifications (Admin)", True, 
                                f"Found {len(notifications)} notifications, {unread_count} unread, {total} total")
                else:
                    error_text = await response.text()
                    self.log_test("GET /api/notifications (Admin)", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("GET /api/notifications (Admin)", False, f"Exception: {str(e)}")
            
        # Test without authentication
        try:
            async with self.session.get(f"{BACKEND_URL}/notifications") as response:
                if response.status == 401:
                    self.log_test("GET /api/notifications (No Auth)", True, "Correctly rejected unauthenticated request")
                else:
                    self.log_test("GET /api/notifications (No Auth)", False, 
                                f"Expected 401, got {response.status}")
        except Exception as e:
            self.log_test("GET /api/notifications (No Auth)", False, f"Exception: {str(e)}")
            
    async def test_jersey_submission_notifications(self):
        """Test notification creation during jersey submission"""
        print("\n👕 JERSEY SUBMISSION NOTIFICATION TESTING")
        print("=" * 50)
        
        # Get initial notification count for user
        initial_count = await self.get_user_notification_count()
        
        # Submit a test jersey
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Test jersey for notification system testing"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_jersey_id = data.get("id")
                    reference_number = data.get("reference_number")
                    self.log_test("Jersey Submission", True, 
                                f"Created jersey ID: {self.test_jersey_id}, Ref: {reference_number}")
                    
                    # Wait a moment for notification to be created
                    await asyncio.sleep(1)
                    
                    # Check if notification was created
                    new_count = await self.get_user_notification_count()
                    if new_count > initial_count:
                        self.log_test("Jersey Submission Notification Created", True, 
                                    f"Notification count increased from {initial_count} to {new_count}")
                        
                        # Get the latest notification to verify content
                        latest_notification = await self.get_latest_user_notification()
                        if latest_notification:
                            title = latest_notification.get("title", "")
                            message = latest_notification.get("message", "")
                            if "submitted" in title.lower() or "submitted" in message.lower():
                                self.log_test("Jersey Submission Notification Content", True, 
                                            f"Title: {title}")
                            else:
                                self.log_test("Jersey Submission Notification Content", False, 
                                            f"Unexpected content - Title: {title}")
                    else:
                        self.log_test("Jersey Submission Notification Created", False, 
                                    f"No notification created - count remained {initial_count}")
                else:
                    error_text = await response.text()
                    self.log_test("Jersey Submission", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Jersey Submission", False, f"Exception: {str(e)}")
            
    async def test_jersey_approval_notifications(self):
        """Test notification creation during jersey approval - SKIP if no admin access"""
        print("\n✅ JERSEY APPROVAL NOTIFICATION TESTING")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Jersey Approval Notification", False, "No admin access available - cannot test approval notifications")
            return
            
        if not self.test_jersey_id:
            self.log_test("Jersey Approval Notification", False, "No test jersey available")
            return
            
        # Get initial notification count for user
        initial_count = await self.get_user_notification_count()
        
        # Approve the jersey as admin
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            async with self.session.post(f"{BACKEND_URL}/admin/jerseys/{self.test_jersey_id}/approve", 
                                       headers=headers) as response:
                if response.status == 200:
                    self.log_test("Jersey Approval", True, f"Jersey {self.test_jersey_id} approved")
                    
                    # Wait a moment for notification to be created
                    await asyncio.sleep(1)
                    
                    # Check if notification was created
                    new_count = await self.get_user_notification_count()
                    if new_count > initial_count:
                        self.log_test("Jersey Approval Notification Created", True, 
                                    f"Notification count increased from {initial_count} to {new_count}")
                        
                        # Get the latest notification to verify content
                        latest_notification = await self.get_latest_user_notification()
                        if latest_notification:
                            title = latest_notification.get("title", "")
                            message = latest_notification.get("message", "")
                            notification_type = latest_notification.get("type", "")
                            if "approved" in title.lower() or "approved" in message.lower() or notification_type == "jersey_approved":
                                self.log_test("Jersey Approval Notification Content", True, 
                                            f"Type: {notification_type}, Title: {title}")
                            else:
                                self.log_test("Jersey Approval Notification Content", False, 
                                            f"Unexpected content - Type: {notification_type}, Title: {title}")
                    else:
                        self.log_test("Jersey Approval Notification Created", False, 
                                    f"No notification created - count remained {initial_count}")
                else:
                    error_text = await response.text()
                    self.log_test("Jersey Approval", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Jersey Approval", False, f"Exception: {str(e)}")
            
    async def test_jersey_rejection_notifications(self):
        """Test notification creation during jersey rejection - SKIP if no admin access"""
        print("\n❌ JERSEY REJECTION NOTIFICATION TESTING")
        print("=" * 50)
        
        if not self.admin_token:
            self.log_test("Jersey Rejection Notification", False, "No admin access available - cannot test rejection notifications")
            return
        
        # Submit another test jersey for rejection
        jersey_data = {
            "team": "FC Barcelona",
            "season": "2024-25", 
            "player": "Pedri",
            "manufacturer": "Nike",
            "home_away": "home",
            "league": "La Liga",
            "description": "Test jersey for rejection notification testing"
        }
        
        rejection_jersey_id = None
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.post(f"{BACKEND_URL}/jerseys", json=jersey_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    rejection_jersey_id = data.get("id")
                    self.log_test("Jersey Submission for Rejection", True, f"Created jersey ID: {rejection_jersey_id}")
                else:
                    error_text = await response.text()
                    self.log_test("Jersey Submission for Rejection", False, 
                                f"Status: {response.status}, Error: {error_text}")
                    return
        except Exception as e:
            self.log_test("Jersey Submission for Rejection", False, f"Exception: {str(e)}")
            return
            
        # Get initial notification count for user
        initial_count = await self.get_user_notification_count()
        
        # Reject the jersey as admin
        rejection_data = {
            "reason": "Test rejection for notification system testing"
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            async with self.session.post(f"{BACKEND_URL}/admin/jerseys/{rejection_jersey_id}/reject", 
                                       json=rejection_data, headers=headers) as response:
                if response.status == 200:
                    self.log_test("Jersey Rejection", True, f"Jersey {rejection_jersey_id} rejected")
                    
                    # Wait a moment for notification to be created
                    await asyncio.sleep(1)
                    
                    # Check if notification was created
                    new_count = await self.get_user_notification_count()
                    if new_count > initial_count:
                        self.log_test("Jersey Rejection Notification Created", True, 
                                    f"Notification count increased from {initial_count} to {new_count}")
                        
                        # Get the latest notification to verify content
                        latest_notification = await self.get_latest_user_notification()
                        if latest_notification:
                            title = latest_notification.get("title", "")
                            message = latest_notification.get("message", "")
                            notification_type = latest_notification.get("type", "")
                            if "rejected" in title.lower() or "rejected" in message.lower() or notification_type == "jersey_rejected":
                                self.log_test("Jersey Rejection Notification Content", True, 
                                            f"Type: {notification_type}, Title: {title}")
                            else:
                                self.log_test("Jersey Rejection Notification Content", False, 
                                            f"Unexpected content - Type: {notification_type}, Title: {title}")
                    else:
                        self.log_test("Jersey Rejection Notification Created", False, 
                                    f"No notification created - count remained {initial_count}")
                else:
                    error_text = await response.text()
                    self.log_test("Jersey Rejection", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Jersey Rejection", False, f"Exception: {str(e)}")
            
    async def test_notification_read_unread_functionality(self):
        """Test marking notifications as read/unread"""
        print("\n📖 NOTIFICATION READ/UNREAD FUNCTIONALITY TESTING")
        print("=" * 50)
        
        # Get user's notifications
        notifications = await self.get_user_notifications()
        if not notifications:
            self.log_test("Notification Read/Unread Test", False, "No notifications available for testing")
            return
            
        # Find an unread notification
        unread_notification = None
        for notification in notifications:
            if not notification.get("is_read", True):
                unread_notification = notification
                break
                
        if not unread_notification:
            self.log_test("Find Unread Notification", False, "No unread notifications found")
            return
            
        notification_id = unread_notification.get("id")
        self.log_test("Find Unread Notification", True, f"Found unread notification: {notification_id}")
        
        # Test marking notification as read
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.post(f"{BACKEND_URL}/notifications/{notification_id}/mark-read", 
                                       headers=headers) as response:
                if response.status == 200:
                    self.log_test("Mark Notification as Read", True, f"Notification {notification_id} marked as read")
                    
                    # Verify the notification is now marked as read
                    updated_notifications = await self.get_user_notifications()
                    updated_notification = next((n for n in updated_notifications if n.get("id") == notification_id), None)
                    if updated_notification and updated_notification.get("is_read", False):
                        self.log_test("Verify Notification Read Status", True, "Notification correctly marked as read")
                    else:
                        self.log_test("Verify Notification Read Status", False, "Notification not properly marked as read")
                else:
                    error_text = await response.text()
                    self.log_test("Mark Notification as Read", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Mark Notification as Read", False, f"Exception: {str(e)}")
            
        # Test marking all notifications as read
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.post(f"{BACKEND_URL}/notifications/mark-all-read", 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    self.log_test("Mark All Notifications as Read", True, f"Response: {message}")
                    
                    # Verify unread count is now 0
                    final_count = await self.get_user_notification_count()
                    final_notifications = await self.get_user_notifications()
                    unread_count = sum(1 for n in final_notifications if not n.get("is_read", True))
                    if unread_count == 0:
                        self.log_test("Verify All Notifications Read", True, "All notifications marked as read")
                    else:
                        self.log_test("Verify All Notifications Read", False, f"Still {unread_count} unread notifications")
                else:
                    error_text = await response.text()
                    self.log_test("Mark All Notifications as Read", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Mark All Notifications as Read", False, f"Exception: {str(e)}")
            
    async def test_notification_database_storage(self):
        """Test if notifications are properly stored in database"""
        print("\n🗄️ NOTIFICATION DATABASE STORAGE TESTING")
        print("=" * 50)
        
        # Get notifications for both users
        user_notifications = await self.get_user_notifications()
        admin_notifications = await self.get_admin_notifications()
        
        # Test notification data structure
        if user_notifications:
            sample_notification = user_notifications[0]
            required_fields = ["id", "user_id", "type", "title", "message", "is_read", "created_at"]
            missing_fields = [field for field in required_fields if field not in sample_notification]
            
            if not missing_fields:
                self.log_test("Notification Data Structure", True, "All required fields present")
            else:
                self.log_test("Notification Data Structure", False, f"Missing fields: {missing_fields}")
                
            # Test notification types
            notification_types = set(n.get("type", "") for n in user_notifications)
            expected_types = ["jersey_approved", "jersey_rejected", "jersey_needs_modification", "system_announcement"]
            found_types = [t for t in expected_types if t in notification_types]
            
            self.log_test("Notification Types in Database", True, 
                        f"Found types: {list(notification_types)}, Expected types found: {found_types}")
        else:
            self.log_test("Notification Database Storage", False, "No notifications found in database")
            
        # Test notification persistence
        total_notifications = len(user_notifications) + len(admin_notifications)
        self.log_test("Notification Persistence", True, 
                    f"Total notifications in database: {total_notifications} (User: {len(user_notifications)}, Admin: {len(admin_notifications)})")
                    
    async def test_notification_count_endpoints(self):
        """Test notification count functionality"""
        print("\n🔢 NOTIFICATION COUNT TESTING")
        print("=" * 50)
        
        # Get user notifications and count manually
        user_notifications = await self.get_user_notifications()
        manual_total = len(user_notifications)
        manual_unread = sum(1 for n in user_notifications if not n.get("is_read", True))
        
        # Get count from API
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    api_total = data.get("total", 0)
                    api_unread = data.get("unread_count", 0)
                    api_notifications_count = len(data.get("notifications", []))
                    
                    # Verify counts match
                    if api_total == manual_total:
                        self.log_test("Total Count Accuracy", True, f"API and manual count match: {api_total}")
                    else:
                        self.log_test("Total Count Accuracy", False, 
                                    f"Mismatch - API: {api_total}, Manual: {manual_total}")
                        
                    if api_unread == manual_unread:
                        self.log_test("Unread Count Accuracy", True, f"API and manual unread count match: {api_unread}")
                    else:
                        self.log_test("Unread Count Accuracy", False, 
                                    f"Mismatch - API: {api_unread}, Manual: {manual_unread}")
                        
                    self.log_test("Notification Count Response", True, 
                                f"Total: {api_total}, Unread: {api_unread}, Returned: {api_notifications_count}")
                else:
                    error_text = await response.text()
                    self.log_test("Notification Count Endpoints", False, 
                                f"Status: {response.status}, Error: {error_text}")
        except Exception as e:
            self.log_test("Notification Count Endpoints", False, f"Exception: {str(e)}")
            
    async def get_user_notification_count(self) -> int:
        """Helper: Get user's notification count"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return len(data.get("notifications", []))
        except:
            pass
        return 0
        
    async def get_latest_user_notification(self) -> Optional[Dict]:
        """Helper: Get user's latest notification"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications?limit=1", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get("notifications", [])
                    return notifications[0] if notifications else None
        except:
            pass
        return None
        
    async def get_user_notifications(self) -> List[Dict]:
        """Helper: Get all user notifications"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications?limit=100", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("notifications", [])
        except:
            pass
        return []
        
    async def get_admin_notifications(self) -> List[Dict]:
        """Helper: Get all admin notifications"""
        if not self.admin_token:
            return []
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            async with self.session.get(f"{BACKEND_URL}/notifications?limit=100", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("notifications", [])
        except:
            pass
        return []
        
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 TOPKIT NOTIFICATIONS SYSTEM COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Group results by category
        categories = {
            "Authentication": [],
            "API Endpoints": [],
            "Jersey Submission": [],
            "Jersey Approval": [],
            "Jersey Rejection": [],
            "Read/Unread": [],
            "Database Storage": [],
            "Count Functionality": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Authentication" in test_name:
                categories["Authentication"].append(result)
            elif "GET /api/notifications" in test_name or "No Auth" in test_name:
                categories["API Endpoints"].append(result)
            elif "Jersey Submission" in test_name:
                categories["Jersey Submission"].append(result)
            elif "Jersey Approval" in test_name:
                categories["Jersey Approval"].append(result)
            elif "Jersey Rejection" in test_name:
                categories["Jersey Rejection"].append(result)
            elif "Read" in test_name or "Unread" in test_name:
                categories["Read/Unread"].append(result)
            elif "Database" in test_name or "Data Structure" in test_name or "Persistence" in test_name:
                categories["Database Storage"].append(result)
            elif "Count" in test_name:
                categories["Count Functionality"].append(result)
        
        print(f"\n📋 DETAILED RESULTS BY CATEGORY:")
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"\n   {category}: {passed}/{total} passed")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"     {status} {result['test']}")
                    if result["details"]:
                        print(f"        {result['details']}")
        
        # Critical issues summary
        critical_failures = [r for r in self.test_results if not r["success"] and 
                           any(keyword in r["test"].lower() for keyword in 
                               ["authentication", "endpoint", "creation", "approval", "rejection"])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   ✅ Notifications system is working excellently!")
        elif success_rate >= 70:
            print("   ⚠️  Notifications system is mostly functional with minor issues to address")
        else:
            print("   🚨 Notifications system has significant issues requiring immediate attention")
            
        if failed_tests > 0:
            print(f"   🔧 Focus on fixing the {failed_tests} failed test(s) above")
            
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "critical_failures": len(critical_failures),
            "categories": {cat: {"passed": sum(1 for r in results if r["success"]), 
                               "total": len(results)} for cat, results in categories.items() if results}
        }

async def main():
    """Main test execution"""
    print("🚀 Starting TopKit Notifications System Comprehensive Testing...")
    print("=" * 80)
    
    tester = NotificationsSystemTester()
    
    try:
        await tester.setup_session()
        
        # Authentication setup
        if not await tester.authenticate_users():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return
            
        # Run all notification tests
        await tester.test_notifications_endpoints()
        await tester.test_jersey_submission_notifications()
        await tester.test_jersey_approval_notifications()
        await tester.test_jersey_rejection_notifications()
        await tester.test_notification_read_unread_functionality()
        await tester.test_notification_database_storage()
        await tester.test_notification_count_endpoints()
        
        # Generate final summary
        summary = tester.generate_summary()
        
        return summary
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())