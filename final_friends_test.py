#!/usr/bin/env python3
"""
TopKit Friends Management System - Final Comprehensive Test
==========================================================

Testing the newly implemented friends management features as requested:
1. GET /api/friends - Complete structure with friends, pending_requests, stats
2. POST /api/friends/respond - Accept/reject friend requests with current_user fix  
3. DELETE /api/friends/{friend_id} - Remove friends with notification system
4. Authentication with steinmetzlivio@gmail.com/123 or topkitfr@gmail.com/adminpass123

This test focuses on the core functionality and handles edge cases properly.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://kit-collection-5.preview.emergentagent.com/api"
TEST_USERS = {
    "user": {"email": "friendstest@example.com", "password": "SecurePass789!"},
    "admin": {"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"}
}

class FinalFriendsTest:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
        self.results = []
        
    def log(self, test: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {"test": test, "success": success, "details": details, "data": data}
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test}: {details}")
        
    def authenticate(self, user_type: str) -> bool:
        """Authenticate and store token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=TEST_USERS[user_type])
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data["token"]
                user_info = data["user"]
                self.log(f"Auth {user_type}", True, f"{user_info['name']} ({user_info['role']})")
                return True
            else:
                self.log(f"Auth {user_type}", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log(f"Auth {user_type}", False, f"Exception: {str(e)}")
            return False
    
    def get_headers(self, user_type: str) -> Dict[str, str]:
        """Get auth headers"""
        return {"Authorization": f"Bearer {self.tokens[user_type]}"}
    
    def test_friends_api_structure(self) -> bool:
        """Test GET /api/friends returns complete structure"""
        try:
            headers = self.get_headers("user")
            response = self.session.get(f"{BASE_URL}/friends", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required structure
                required = ["friends", "pending_requests", "stats"]
                missing = [k for k in required if k not in data]
                if missing:
                    self.log("Friends API Structure", False, f"Missing keys: {missing}")
                    return False
                
                # Check pending_requests structure
                pr = data["pending_requests"]
                if not isinstance(pr, dict) or "received" not in pr or "sent" not in pr:
                    self.log("Friends API Structure", False, "Invalid pending_requests structure")
                    return False
                
                # Check stats structure
                stats = data["stats"]
                required_stats = ["total_friends", "pending_received", "pending_sent"]
                missing_stats = [k for k in required_stats if k not in stats]
                if missing_stats:
                    self.log("Friends API Structure", False, f"Missing stats: {missing_stats}")
                    return False
                
                self.log("Friends API Structure", True, 
                        f"Complete structure - {stats['total_friends']} friends, "
                        f"{stats['pending_received']} received, {stats['pending_sent']} sent")
                return True
            else:
                self.log("Friends API Structure", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log("Friends API Structure", False, f"Exception: {str(e)}")
            return False
    
    def create_fresh_friendship(self) -> Optional[str]:
        """Create a new friendship for testing"""
        try:
            # Get admin ID
            admin_headers = self.get_headers("admin")
            admin_profile = self.session.get(f"{BASE_URL}/profile", headers=admin_headers)
            if admin_profile.status_code != 200:
                return None
            admin_id = admin_profile.json()["user"]["id"]
            
            # Check if friendship already exists
            user_headers = self.get_headers("user")
            friends_response = self.session.get(f"{BASE_URL}/friends", headers=user_headers)
            if friends_response.status_code == 200:
                friends_data = friends_response.json()
                
                # Check if already friends
                for friend in friends_data.get("friends", []):
                    if friend["friend_id"] == admin_id:
                        # Remove existing friendship first
                        self.session.delete(f"{BASE_URL}/friends/{admin_id}", headers=user_headers)
                        break
                
                # Check if pending request exists
                for req in friends_data.get("pending_requests", {}).get("sent", []):
                    if req["addressee_id"] == admin_id:
                        # Request already exists, return its ID
                        return req["request_id"]
            
            # Send new friend request
            friend_request_data = {"user_id": admin_id, "message": "Test friend request"}
            response = self.session.post(f"{BASE_URL}/friends/request", json=friend_request_data, headers=user_headers)
            
            if response.status_code == 200:
                return response.json()["request_id"]
            else:
                return None
                
        except Exception as e:
            return None
    
    def test_friends_respond_accept(self) -> bool:
        """Test POST /api/friends/respond with accept=true"""
        try:
            # Create friendship request
            request_id = self.create_fresh_friendship()
            if not request_id:
                self.log("Friends Respond Accept", False, "Could not create test friendship")
                return False
            
            # Accept the request as admin
            admin_headers = self.get_headers("admin")
            response_data = {"request_id": request_id, "accept": True}
            response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Friend request accepted":
                    self.log("Friends Respond Accept", True, "Successfully accepted friend request")
                    return True
                else:
                    self.log("Friends Respond Accept", False, f"Unexpected message: {data.get('message')}")
                    return False
            else:
                self.log("Friends Respond Accept", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log("Friends Respond Accept", False, f"Exception: {str(e)}")
            return False
    
    def test_friends_respond_reject(self) -> bool:
        """Test POST /api/friends/respond with accept=false"""
        try:
            # Create another friendship request
            request_id = self.create_fresh_friendship()
            if not request_id:
                self.log("Friends Respond Reject", False, "Could not create test friendship")
                return False
            
            # Reject the request as admin
            admin_headers = self.get_headers("admin")
            response_data = {"request_id": request_id, "accept": False}
            response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Friend request declined":
                    self.log("Friends Respond Reject", True, "Successfully rejected friend request")
                    return True
                else:
                    self.log("Friends Respond Reject", False, f"Unexpected message: {data.get('message')}")
                    return False
            else:
                self.log("Friends Respond Reject", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log("Friends Respond Reject", False, f"Exception: {str(e)}")
            return False
    
    def test_remove_friend_existing(self) -> bool:
        """Test DELETE /api/friends/{friend_id} with existing friend"""
        try:
            # First ensure we have a friendship
            request_id = self.create_fresh_friendship()
            if not request_id:
                self.log("Remove Friend Setup", False, "Could not create friendship")
                return False
            
            # Accept the friendship
            admin_headers = self.get_headers("admin")
            response_data = {"request_id": request_id, "accept": True}
            accept_response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            
            if accept_response.status_code != 200:
                self.log("Remove Friend Setup", False, "Could not accept friendship")
                return False
            
            # Get admin ID for removal
            admin_profile = self.session.get(f"{BASE_URL}/profile", headers=admin_headers)
            admin_id = admin_profile.json()["user"]["id"]
            
            # Remove the friend
            user_headers = self.get_headers("user")
            response = self.session.delete(f"{BASE_URL}/friends/{admin_id}", headers=user_headers)
            
            if response.status_code == 200:
                data = response.json()
                if "Successfully removed" in data.get("message", ""):
                    self.log("Remove Friend Existing", True, f"Successfully removed friend: {data['message']}")
                    return True
                else:
                    self.log("Remove Friend Existing", False, f"Unexpected message: {data.get('message')}")
                    return False
            else:
                self.log("Remove Friend Existing", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log("Remove Friend Existing", False, f"Exception: {str(e)}")
            return False
    
    def test_remove_friend_nonexistent(self) -> bool:
        """Test DELETE /api/friends/{friend_id} with non-existent friend"""
        try:
            user_headers = self.get_headers("user")
            fake_friend_id = "non-existent-friend-id-12345"
            response = self.session.delete(f"{BASE_URL}/friends/{fake_friend_id}", headers=user_headers)
            
            if response.status_code == 404:
                data = response.json()
                if data.get("detail") == "Friendship not found":
                    self.log("Remove Friend Nonexistent", True, "Correctly returned 404 for non-existent friend")
                    return True
                else:
                    self.log("Remove Friend Nonexistent", False, f"Unexpected error: {data.get('detail')}")
                    return False
            else:
                self.log("Remove Friend Nonexistent", False, f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log("Remove Friend Nonexistent", False, f"Exception: {str(e)}")
            return False
    
    def test_notification_creation(self) -> bool:
        """Test that notifications are created when friends are removed"""
        try:
            # Get initial notification count
            admin_headers = self.get_headers("admin")
            initial_response = self.session.get(f"{BASE_URL}/notifications", headers=admin_headers)
            if initial_response.status_code != 200:
                self.log("Notification Test", False, "Could not get initial notifications")
                return False
            
            initial_count = len(initial_response.json())
            
            # Create and accept friendship, then remove it
            request_id = self.create_fresh_friendship()
            if not request_id:
                self.log("Notification Test", False, "Could not create friendship for notification test")
                return False
            
            # Accept friendship
            response_data = {"request_id": request_id, "accept": True}
            accept_response = self.session.post(f"{BASE_URL}/friends/respond", json=response_data, headers=admin_headers)
            if accept_response.status_code != 200:
                self.log("Notification Test", False, "Could not accept friendship for notification test")
                return False
            
            # Get admin ID and remove friend
            admin_profile = self.session.get(f"{BASE_URL}/profile", headers=admin_headers)
            admin_id = admin_profile.json()["user"]["id"]
            
            user_headers = self.get_headers("user")
            remove_response = self.session.delete(f"{BASE_URL}/friends/{admin_id}", headers=user_headers)
            if remove_response.status_code != 200:
                self.log("Notification Test", False, "Could not remove friend for notification test")
                return False
            
            # Check for new notifications
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
                        self.log("Notification Creation", True, 
                                f"Notification sent successfully - found {len(friendship_notifications)} friendship notifications")
                        return True
                    else:
                        self.log("Notification Creation", False, 
                                f"Notification count increased but no friendship notifications found")
                        return False
                else:
                    self.log("Notification Creation", False, 
                            f"No new notifications sent (count: {initial_count} → {final_count})")
                    return False
            else:
                self.log("Notification Creation", False, "Could not get final notifications")
                return False
                
        except Exception as e:
            self.log("Notification Creation", False, f"Exception: {str(e)}")
            return False
    
    def run_test(self):
        """Run comprehensive friends management test"""
        print("🎯 TOPKIT FRIENDS MANAGEMENT SYSTEM - FINAL TEST")
        print("=" * 60)
        print(f"Backend URL: {BASE_URL}")
        print()
        
        # Authentication
        print("📋 AUTHENTICATION")
        print("-" * 30)
        if not self.authenticate("user") or not self.authenticate("admin"):
            print("❌ Authentication failed - cannot proceed")
            return
        print()
        
        # Core API Tests
        print("📋 FRIENDS API TESTING")
        print("-" * 30)
        self.test_friends_api_structure()
        print()
        
        print("📋 FRIENDS RESPOND TESTING")
        print("-" * 30)
        self.test_friends_respond_accept()
        self.test_friends_respond_reject()
        print()
        
        print("📋 REMOVE FRIEND TESTING")
        print("-" * 30)
        self.test_remove_friend_existing()
        self.test_remove_friend_nonexistent()
        print()
        
        print("📋 NOTIFICATION SYSTEM TESTING")
        print("-" * 30)
        self.test_notification_creation()
        print()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        total = len(self.results)
        passed = len([r for r in self.results if r["success"]])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {failed} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
            print()
        
        # Final verdict
        if success_rate >= 90:
            print("🎉 FRIENDS MANAGEMENT SYSTEM: EXCELLENT - PRODUCTION READY!")
        elif success_rate >= 75:
            print("✅ FRIENDS MANAGEMENT SYSTEM: GOOD - MINOR ISSUES ONLY")
        elif success_rate >= 50:
            print("⚠️ FRIENDS MANAGEMENT SYSTEM: NEEDS IMPROVEMENT")
        else:
            print("❌ FRIENDS MANAGEMENT SYSTEM: CRITICAL ISSUES")
        
        print(f"Overall Status: {success_rate:.1f}% SUCCESS RATE")
        
        # Specific findings for the review request
        print()
        print("🔍 REVIEW REQUEST FINDINGS:")
        print("-" * 40)
        
        api_structure_passed = any(r["success"] for r in self.results if "Friends API Structure" in r["test"])
        respond_accept_passed = any(r["success"] for r in self.results if "Friends Respond Accept" in r["test"])
        respond_reject_passed = any(r["success"] for r in self.results if "Friends Respond Reject" in r["test"])
        remove_friend_passed = any(r["success"] for r in self.results if "Remove Friend Existing" in r["test"])
        notification_passed = any(r["success"] for r in self.results if "Notification Creation" in r["test"])
        
        print(f"✅ GET /api/friends structure: {'WORKING' if api_structure_passed else 'FAILED'}")
        print(f"✅ POST /api/friends/respond (accept): {'WORKING' if respond_accept_passed else 'FAILED'}")
        print(f"✅ POST /api/friends/respond (reject): {'WORKING' if respond_reject_passed else 'FAILED'}")
        print(f"✅ DELETE /api/friends/{{friend_id}}: {'WORKING' if remove_friend_passed else 'FAILED'}")
        print(f"✅ Notification system: {'WORKING' if notification_passed else 'NEEDS VERIFICATION'}")

if __name__ == "__main__":
    tester = FinalFriendsTest()
    tester.run_test()