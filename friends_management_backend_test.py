#!/usr/bin/env python3
"""
TopKit Friends Management System Backend Testing
==============================================

Testing the newly implemented friends management features:
1. GET /api/friends - Complete structure with friends, pending_requests, stats
2. POST /api/friends/respond - Accept/reject friend requests with current_user fix
3. DELETE /api/friends/{friend_id} - Remove friends with notification system
4. Authentication testing with specified credentials

Test Users:
- steinmetzlivio@gmail.com / 123
- topkitfr@gmail.com / adminpass123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://footkit-hub.preview.emergentagent.com/api"
TEST_USERS = {
    "user": {"email": "friendstest@example.com", "password": "SecurePass789!"},
    "admin": {"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"}
}

class FriendsManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.test_results = []
        self.friendship_ids = []  # Store created friendship IDs for cleanup
        
    def log_result(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result with timestamp"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")

    def authenticate_user(self, user_type: str) -> bool:
        """Authenticate user and store token"""
        try:
            user_creds = TEST_USERS[user_type]
            response = self.session.post(f"{BASE_URL}/auth/login", json=user_creds)
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data["token"]
                user_info = data["user"]
                self.log_result(
                    f"Authentication - {user_type}",
                    True,
                    f"Successfully authenticated {user_info['name']} (Role: {user_info.get('role', 'user')}, ID: {user_info['id']})"
                )
                return True
            else:
                self.log_result(
                    f"Authentication - {user_type}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result(f"Authentication - {user_type}", False, f"Exception: {str(e)}")
            return False

    def get_auth_headers(self, user_type: str) -> Dict[str, str]:
        """Get authorization headers for user"""
        if user_type not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[user_type]}"}

    def test_friends_api_structure(self, user_type: str) -> bool:
        """Test GET /api/friends returns complete structure"""
        try:
            headers = self.get_auth_headers(user_type)
            response = self.session.get(f"{BASE_URL}/friends", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required structure
                required_keys = ["friends", "pending_requests", "stats"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_result(
                        f"Friends API Structure - {user_type}",
                        False,
                        f"Missing keys: {missing_keys}",
                        data
                    )
                    return False
                
                # Check pending_requests structure
                pending_req = data["pending_requests"]
                if not isinstance(pending_req, dict) or "received" not in pending_req or "sent" not in pending_req:
                    self.log_result(
                        f"Friends API Structure - {user_type}",
                        False,
                        "pending_requests missing 'received' or 'sent' keys",
                        data
                    )
                    return False
                
                # Check stats structure
                stats = data["stats"]
                required_stats = ["total_friends", "pending_received", "pending_sent"]
                missing_stats = [key for key in required_stats if key not in stats]
                
                if missing_stats:
                    self.log_result(
                        f"Friends API Structure - {user_type}",
                        False,
                        f"Stats missing keys: {missing_stats}",
                        data
                    )
                    return False
                
                self.log_result(
                    f"Friends API Structure - {user_type}",
                    True,
                    f"Complete structure returned - {stats['total_friends']} friends, {stats['pending_received']} received, {stats['pending_sent']} sent",
                    {
                        "friends_count": len(data["friends"]),
                        "pending_received_count": len(data["pending_requests"]["received"]),
                        "pending_sent_count": len(data["pending_requests"]["sent"]),
                        "stats": stats
                    }
                )
                return True
                
            else:
                self.log_result(
                    f"Friends API Structure - {user_type}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result(f"Friends API Structure - {user_type}", False, f"Exception: {str(e)}")
            return False

    def create_test_friendship(self) -> Optional[str]:
        """Create a test friendship between user and admin for testing"""
        try:
            # User sends friend request to admin
            user_headers = self.get_auth_headers("user")
            
            # First get admin user ID
            admin_headers = self.get_auth_headers("admin")
            admin_profile = self.session.get(f"{BASE_URL}/profile", headers=admin_headers)
            if admin_profile.status_code != 200:
                return None
                
            admin_id = admin_profile.json()["user"]["id"]
            
            # Send friend request
            friend_request_data = {"user_id": admin_id, "message": "Test friend request"}
            response = self.session.post(f"{BASE_URL}/friends/request", json=friend_request_data, headers=user_headers)
            
            if response.status_code == 200:
                request_id = response.json()["request_id"]
                self.friendship_ids.append(request_id)
                self.log_result(
                    "Create Test Friendship",
                    True,
                    f"Friend request sent successfully (ID: {request_id})"
                )
                return request_id
            else:
                self.log_result(
                    "Create Test Friendship",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Create Test Friendship", False, f"Exception: {str(e)}")
            return None

    def test_friends_respond_accept(self, request_id: str) -> bool:
        """Test POST /api/friends/respond with accept=true"""
        try:
            admin_headers = self.get_auth_headers("admin")
            response_data = {"request_id": request_id, "accept": True}
            
            response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "Friend request accepted"
                
                if data.get("message") == expected_message:
                    self.log_result(
                        "Friends Respond - Accept",
                        True,
                        f"Successfully accepted friend request: {data['message']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Friends Respond - Accept",
                        False,
                        f"Unexpected response message: {data.get('message')}",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Friends Respond - Accept",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result("Friends Respond - Accept", False, f"Exception: {str(e)}")
            return False

    def test_friends_respond_reject(self) -> bool:
        """Test POST /api/friends/respond with accept=false"""
        try:
            # Create another test friendship for rejection
            # First check if there are existing pending requests to avoid duplicate error
            admin_headers = self.get_auth_headers("admin")
            friends_response = self.session.get(f"{BASE_URL}/friends", headers=admin_headers)
            
            if friends_response.status_code == 200:
                pending_received = friends_response.json().get("pending_requests", {}).get("received", [])
                if pending_received:
                    # Use existing pending request
                    request_id = pending_received[0]["request_id"]
                    self.log_result(
                        "Create Test Friendship for Rejection",
                        True,
                        f"Using existing pending request (ID: {request_id})"
                    )
                else:
                    # Create new request
                    request_id = self.create_test_friendship()
                    if not request_id:
                        return False
            else:
                request_id = self.create_test_friendship()
                if not request_id:
                    return False
            
            response_data = {"request_id": request_id, "accept": False}
            
            response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_message = "Friend request declined"
                
                if data.get("message") == expected_message:
                    self.log_result(
                        "Friends Respond - Reject",
                        True,
                        f"Successfully rejected friend request: {data['message']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Friends Respond - Reject",
                        False,
                        f"Unexpected response message: {data.get('message')}",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Friends Respond - Reject",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result("Friends Respond - Reject", False, f"Exception: {str(e)}")
            return False

    def get_friend_id_from_friends_list(self, user_type: str) -> Optional[str]:
        """Get a friend ID from user's friends list"""
        try:
            headers = self.get_auth_headers(user_type)
            response = self.session.get(f"{BASE_URL}/friends", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get("friends", [])
                
                if friends:
                    return friends[0]["friend_id"]
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            return None

    def test_remove_friend_existing(self) -> bool:
        """Test DELETE /api/friends/{friend_id} with existing friend"""
        try:
            # First ensure we have a friendship to remove
            user_headers = self.get_auth_headers("user")
            
            # Get friend ID from user's friends list
            friend_id = self.get_friend_id_from_friends_list("user")
            
            if not friend_id:
                self.log_result(
                    "Remove Friend - Existing",
                    False,
                    "No friends found to remove (need accepted friendship first)"
                )
                return False
            
            response = self.session.delete(f"{BASE_URL}/friends/{friend_id}", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "Successfully removed" in data.get("message", ""):
                    self.log_result(
                        "Remove Friend - Existing",
                        True,
                        f"Successfully removed friend: {data['message']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Remove Friend - Existing",
                        False,
                        f"Unexpected response message: {data.get('message')}",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Remove Friend - Existing",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result("Remove Friend - Existing", False, f"Exception: {str(e)}")
            return False

    def test_remove_friend_nonexistent(self) -> bool:
        """Test DELETE /api/friends/{friend_id} with non-existent friend"""
        try:
            user_headers = self.get_auth_headers("user")
            fake_friend_id = "non-existent-friend-id-12345"
            
            response = self.session.delete(f"{BASE_URL}/friends/{fake_friend_id}", headers=user_headers)
            
            if response.status_code == 404:
                data = response.json()
                expected_detail = "Friendship not found"
                
                if data.get("detail") == expected_detail:
                    self.log_result(
                        "Remove Friend - Non-existent",
                        True,
                        f"Correctly returned 404 for non-existent friend: {data['detail']}"
                    )
                    return True
                else:
                    self.log_result(
                        "Remove Friend - Non-existent",
                        False,
                        f"Unexpected error message: {data.get('detail')}",
                        data
                    )
                    return False
            else:
                self.log_result(
                    "Remove Friend - Non-existent",
                    False,
                    f"Expected HTTP 404, got {response.status_code}: {response.text}",
                    response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                )
                return False
                
        except Exception as e:
            self.log_result("Remove Friend - Non-existent", False, f"Exception: {str(e)}")
            return False

    def test_notification_system(self) -> bool:
        """Test that notifications are sent when friends are removed"""
        try:
            # Get initial notification count for admin
            admin_headers = self.get_auth_headers("admin")
            initial_response = self.session.get(f"{BASE_URL}/notifications", headers=admin_headers)
            
            if initial_response.status_code != 200:
                self.log_result(
                    "Notification System Test",
                    False,
                    f"Could not get initial notifications: HTTP {initial_response.status_code}"
                )
                return False
            
            initial_count = len(initial_response.json())
            
            # Create and accept a friendship, then remove it
            request_id = self.create_test_friendship()
            if not request_id:
                return False
            
            # Accept the friendship
            if not self.test_friends_respond_accept(request_id):
                return False
            
            # Remove the friend (this should send notification)
            # Get admin ID from profile
            admin_profile = self.session.get(f"{BASE_URL}/profile", headers=admin_headers)
            admin_id = admin_profile.json()["user"]["id"]
            
            user_headers = self.get_auth_headers("user")
            remove_response = self.session.delete(f"{BASE_URL}/friends/{admin_id}", headers=user_headers)
            
            if remove_response.status_code != 200:
                self.log_result(
                    "Notification System Test",
                    False,
                    f"Could not remove friend: HTTP {remove_response.status_code}"
                )
                return False
            
            # Check if notification was sent to admin
            final_response = self.session.get(f"{BASE_URL}/notifications", headers=admin_headers)
            
            if final_response.status_code == 200:
                final_count = len(final_response.json())
                
                if final_count > initial_count:
                    # Look for friendship-related notification
                    notifications = final_response.json()
                    friendship_notifications = [
                        n for n in notifications 
                        if "friend" in n.get("message", "").lower() or "removed" in n.get("message", "").lower()
                    ]
                    
                    if friendship_notifications:
                        self.log_result(
                            "Notification System Test",
                            True,
                            f"Notification sent successfully - found {len(friendship_notifications)} friendship-related notifications"
                        )
                        return True
                    else:
                        self.log_result(
                            "Notification System Test",
                            False,
                            f"Notification count increased ({initial_count} → {final_count}) but no friendship-related notifications found"
                        )
                        return False
                else:
                    self.log_result(
                        "Notification System Test",
                        False,
                        f"No new notifications sent (count: {initial_count} → {final_count})"
                    )
                    return False
            else:
                self.log_result(
                    "Notification System Test",
                    False,
                    f"Could not get final notifications: HTTP {final_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Notification System Test", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run all friends management tests"""
        print("🎯 TOPKIT FRIENDS MANAGEMENT SYSTEM TESTING")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print(f"Test Users: {list(TEST_USERS.keys())}")
        print()
        
        # 1. Authentication Tests
        print("📋 PHASE 1: AUTHENTICATION TESTING")
        print("-" * 40)
        
        auth_success = True
        for user_type in TEST_USERS.keys():
            if not self.authenticate_user(user_type):
                auth_success = False
        
        if not auth_success:
            print("\n❌ AUTHENTICATION FAILED - Cannot proceed with friends testing")
            return
        
        print()
        
        # 2. Friends API Structure Tests
        print("📋 PHASE 2: FRIENDS API STRUCTURE TESTING")
        print("-" * 40)
        
        for user_type in ["user", "admin"]:
            self.test_friends_api_structure(user_type)
        
        print()
        
        # 3. Friends Response Testing
        print("📋 PHASE 3: FRIENDS RESPOND FUNCTIONALITY")
        print("-" * 40)
        
        # Create test friendship for acceptance
        request_id = self.create_test_friendship()
        if request_id:
            self.test_friends_respond_accept(request_id)
        
        # Test rejection
        self.test_friends_respond_reject()
        
        print()
        
        # 4. Remove Friend Testing
        print("📋 PHASE 4: REMOVE FRIEND FUNCTIONALITY")
        print("-" * 40)
        
        self.test_remove_friend_existing()
        self.test_remove_friend_nonexistent()
        
        print()
        
        # 5. Notification System Testing
        print("📋 PHASE 5: NOTIFICATION SYSTEM TESTING")
        print("-" * 40)
        
        self.test_notification_system()
        
        print()
        
        # Summary
        self.print_summary()

    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test"].split(" - ")[0] if " - " in result["test"] else "General"
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["success"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category breakdown
        for category, data in categories.items():
            total = data["passed"] + data["failed"]
            rate = (data["passed"] / total * 100) if total > 0 else 0
            status = "✅" if data["failed"] == 0 else "⚠️" if rate >= 50 else "❌"
            print(f"{status} {category}: {data['passed']}/{total} ({rate:.1f}%)")
        
        print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            print("-" * 30)
            for result in failed_results:
                print(f"• {result['test']}: {result['details']}")
        
        print()
        
        # Final verdict
        if success_rate >= 90:
            print("🎉 FRIENDS MANAGEMENT SYSTEM: EXCELLENT IMPLEMENTATION!")
        elif success_rate >= 75:
            print("✅ FRIENDS MANAGEMENT SYSTEM: GOOD IMPLEMENTATION WITH MINOR ISSUES")
        elif success_rate >= 50:
            print("⚠️ FRIENDS MANAGEMENT SYSTEM: NEEDS IMPROVEMENT")
        else:
            print("❌ FRIENDS MANAGEMENT SYSTEM: CRITICAL ISSUES IDENTIFIED")
        
        print(f"Overall Status: {success_rate:.1f}% SUCCESS RATE")

if __name__ == "__main__":
    tester = FriendsManagementTester()
    tester.run_comprehensive_test()