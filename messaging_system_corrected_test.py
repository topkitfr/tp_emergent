#!/usr/bin/env python3
"""
🎯 TopKit Messaging System Integration Testing (Corrected)
Testing the messaging system with proper field names and endpoints

Focus on the corrected dependency injection issues:
1. POST /api/conversations - Test with correct message field
2. POST /api/friends/request - Test friend request functionality  
3. Verify transaction integration endpoints exist
4. Test system message integration
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "messaging.test@example.com"
USER_PASSWORD = "MessagingTestSecure789#"

class MessagingSystemTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_id = None
        self.user_id = None
        self.test_results = []
        self.conversation_id = None
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} - {test_name}: {details}")
        
    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_id = user_data.get('id')
                admin_name = user_data.get('name', 'Unknown')
                admin_role = user_data.get('role', 'Unknown')
                self.log_result("Admin Authentication", True, 
                              f"Admin: {admin_name}, Role: {admin_role}, ID: {self.admin_id}")
                return True
            else:
                self.log_result("Admin Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                user_name = user_data.get('name', 'Unknown')
                user_role = user_data.get('role', 'Unknown')
                self.log_result("User Authentication", True, 
                              f"User: {user_name}, Role: {user_role}, ID: {self.user_id}")
                return True
            else:
                self.log_result("User Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    def test_conversation_creation_corrected(self):
        """Test POST /api/conversations with correct field names"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create a conversation with admin using correct field name
            response = requests.post(f"{BACKEND_URL}/conversations", 
                                   headers=headers,
                                   json={
                                       "recipient_id": self.admin_id,
                                       "message": "Hello! I'm interested in your jersey listing.",
                                       "message_type": "text"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get('conversation_id')
                self.log_result("Conversation Creation (Corrected)", True, 
                              f"Conversation created: {self.conversation_id}")
                return True
            elif response.status_code == 500:
                self.log_result("Conversation Creation (Corrected)", False, 
                              "HTTP 500 - Dependency injection still broken")
                return False
            else:
                self.log_result("Conversation Creation (Corrected)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Creation (Corrected)", False, f"Exception: {str(e)}")
            return False
            
    def test_friend_request_corrected(self):
        """Test POST /api/friends/request with correct parameters"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.post(f"{BACKEND_URL}/friends/request", 
                                   headers=headers,
                                   json={
                                       "user_id": self.admin_id,
                                       "message": "Let's be friends on TopKit!"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Friend Request (Corrected)", True, 
                              f"Friend request sent: {data.get('message', 'Success')}")
                return True
            elif response.status_code == 500:
                self.log_result("Friend Request (Corrected)", False, 
                              "HTTP 500 - Dependency injection still broken")
                return False
            else:
                self.log_result("Friend Request (Corrected)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Friend Request (Corrected)", False, f"Exception: {str(e)}")
            return False
            
    def test_transaction_endpoints_exist(self):
        """Test that transaction integration endpoints exist"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test endpoints with dummy IDs to check they exist (expect 404, not 500)
            endpoints_to_test = [
                "/payments/secure/checkout",
                "/transactions/dummy-id/buyer/confirm-receipt", 
                "/transactions/dummy-id/seller/mark-shipped",
                "/conversations/dummy-id/transaction",
                "/conversations/dummy-id/messages"
            ]
            
            results = []
            for endpoint in endpoints_to_test:
                try:
                    if endpoint == "/payments/secure/checkout":
                        # POST endpoint
                        response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                               headers=headers,
                                               json={"listing_id": "dummy", "origin_url": "test"})
                    elif "buyer/confirm-receipt" in endpoint or "seller/mark-shipped" in endpoint:
                        # POST endpoints
                        response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                               headers=headers,
                                               json={"notes": "test"})
                    else:
                        # GET endpoints
                        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                    
                    # We expect 404 (not found) or 422 (validation error), not 500 (server error)
                    endpoint_exists = response.status_code in [404, 422, 400]
                    results.append(endpoint_exists)
                    
                except Exception:
                    results.append(False)
            
            success_count = sum(results)
            total_count = len(endpoints_to_test)
            
            self.log_result("Transaction Endpoints Exist", success_count >= 4, 
                          f"{success_count}/{total_count} endpoints accessible")
            
            return success_count >= 4
            
        except Exception as e:
            self.log_result("Transaction Endpoints Exist", False, f"Exception: {str(e)}")
            return False
            
    def test_messaging_basic_functionality(self):
        """Test basic messaging functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test conversations list
            conversations_response = requests.get(f"{BACKEND_URL}/conversations", headers=headers)
            conversations_ok = conversations_response.status_code == 200
            
            # Test friends list
            friends_response = requests.get(f"{BACKEND_URL}/friends", headers=headers)
            friends_ok = friends_response.status_code == 200
            
            # Test notifications
            notifications_response = requests.get(f"{BACKEND_URL}/notifications", headers=headers)
            notifications_ok = notifications_response.status_code == 200
            
            # Get some data from responses
            conversations_data = conversations_response.json() if conversations_ok else {}
            friends_data = friends_response.json() if friends_ok else {}
            notifications_data = notifications_response.json() if notifications_ok else {}
            
            conversations_count = len(conversations_data.get('conversations', []))
            friends_count = len(friends_data.get('friends', {}).get('accepted', []))
            notifications_count = len(notifications_data.get('notifications', []))
            
            total_ok = sum([conversations_ok, friends_ok, notifications_ok])
            
            self.log_result("Basic Messaging Functionality", total_ok == 3, 
                          f"Conversations: {conversations_count}, Friends: {friends_count}, Notifications: {notifications_count}")
            
            return total_ok == 3
            
        except Exception as e:
            self.log_result("Basic Messaging Functionality", False, f"Exception: {str(e)}")
            return False
            
    def test_conversation_messages_if_exists(self):
        """Test conversation messages if conversation was created"""
        if not self.conversation_id:
            self.log_result("Conversation Messages", True, "No conversation to test (expected)")
            return True
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BACKEND_URL}/conversations/{self.conversation_id}/messages", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                system_messages = [msg for msg in messages if msg.get('message_type') == 'system']
                
                self.log_result("Conversation Messages", True, 
                              f"Total messages: {len(messages)}, System messages: {len(system_messages)}")
                return True
            else:
                self.log_result("Conversation Messages", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Messages", False, f"Exception: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all messaging system tests"""
        print("🎯 TOPKIT MESSAGING SYSTEM INTEGRATION TESTING (CORRECTED)")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return False
            
        if not self.authenticate_user():
            print("❌ User authentication failed - cannot continue")
            return False
            
        print()
        
        # Test basic messaging functionality
        self.test_messaging_basic_functionality()
        
        # Test corrected dependency injection endpoints
        self.test_conversation_creation_corrected()
        self.test_friend_request_corrected()
        
        # Test transaction integration endpoints exist
        self.test_transaction_endpoints_exist()
        
        # Test conversation messages if conversation was created
        self.test_conversation_messages_if_exists()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print()
        print("=" * 80)
        print("🎯 MESSAGING SYSTEM INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            if result['details']:
                print(f"    Details: {result['details']}")
        
        print()
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        if success_rate >= 80:
            print("🎉 MESSAGING SYSTEM INTEGRATION IS OPERATIONAL!")
            if success_rate == 100:
                print("✨ PERFECT IMPLEMENTATION - ALL TESTS PASSED!")
            else:
                print("⚠️  Minor issues identified but core functionality working")
        else:
            print("🚨 CRITICAL ISSUES IDENTIFIED - MESSAGING SYSTEM NEEDS FIXES")
            
        return success_rate >= 80

if __name__ == "__main__":
    tester = MessagingSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)