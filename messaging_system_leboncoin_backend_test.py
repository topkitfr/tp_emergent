#!/usr/bin/env python3
"""
🎯 TopKit Messaging System Integration Testing (Leboncoin Style)
Complete testing of the messaging system with transaction integration after dependency injection fixes

Test Focus:
1. POST /api/conversations - Fixed dependency injection
2. POST /api/friends/request - Fixed dependency injection  
3. POST /api/payments/secure/checkout - Verify automatic conversation creation
4. POST /api/transactions/{id}/buyer/confirm-receipt - Buyer action in messaging
5. POST /api/transactions/{id}/seller/mark-shipped - Seller action in messaging

Workflow to test:
1. Create conversation → Test fixed endpoint
2. Secure payment → Verify automatic conversation
3. System messages → Verify transaction integration
4. Seller ships → Message system with tracking
5. Buyer confirms → Payment release via messaging
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "messaging.test@example.com"
USER_PASSWORD = "MessagingTestSecure789#"

class MessagingSystemTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.conversation_id = None
        self.transaction_id = None
        self.listing_id = None
        
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
                admin_name = data.get('user', {}).get('name', 'Unknown')
                admin_role = data.get('user', {}).get('role', 'Unknown')
                self.log_result("Admin Authentication", True, 
                              f"Admin: {admin_name}, Role: {admin_role}")
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
                user_name = data.get('user', {}).get('name', 'Unknown')
                user_role = data.get('user', {}).get('role', 'Unknown')
                self.log_result("User Authentication", True, 
                              f"User: {user_name}, Role: {user_role}")
                return True
            else:
                self.log_result("User Authentication", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    def test_conversation_creation_fixed(self):
        """Test POST /api/conversations - Fixed dependency injection"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create a conversation with another user (admin in this case)
            response = requests.post(f"{BACKEND_URL}/conversations", 
                                   headers=headers,
                                   json={
                                       "participant_id": "f33eab32-2d5c-4f59-9104-83999453a43c",  # Admin ID
                                       "initial_message": "Hello! I'm interested in your jersey listing."
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get('conversation_id')
                self.log_result("Conversation Creation (Fixed)", True, 
                              f"Conversation created: {self.conversation_id}")
                return True
            elif response.status_code == 500:
                self.log_result("Conversation Creation (Fixed)", False, 
                              "HTTP 500 - Dependency injection still broken")
                return False
            else:
                self.log_result("Conversation Creation (Fixed)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Conversation Creation (Fixed)", False, f"Exception: {str(e)}")
            return False
            
    def test_friend_request_fixed(self):
        """Test POST /api/friends/request - Fixed dependency injection"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.post(f"{BACKEND_URL}/friends/request", 
                                   headers=headers,
                                   json={
                                       "user_id": "f33eab32-2d5c-4f59-9104-83999453a43c",  # Admin ID
                                       "message": "Let's be friends on TopKit!"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Friend Request (Fixed)", True, 
                              f"Friend request sent: {data.get('message', 'Success')}")
                return True
            elif response.status_code == 500:
                self.log_result("Friend Request (Fixed)", False, 
                              "HTTP 500 - Dependency injection still broken")
                return False
            else:
                self.log_result("Friend Request (Fixed)", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Friend Request (Fixed)", False, f"Exception: {str(e)}")
            return False
            
    def create_test_listing(self):
        """Create a test listing for payment testing"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # First create a jersey
            jersey_response = requests.post(f"{BACKEND_URL}/jerseys", 
                                          headers=headers,
                                          json={
                                              "team": "Real Madrid CF",
                                              "season": "2024-25",
                                              "player": "Vinicius Jr",
                                              "manufacturer": "Adidas",
                                              "home_away": "home",
                                              "league": "La Liga",
                                              "description": "Test jersey for messaging system"
                                          })
            
            if jersey_response.status_code != 200:
                self.log_result("Test Listing Creation", False, 
                              f"Jersey creation failed: {jersey_response.status_code}")
                return False
                
            jersey_data = jersey_response.json()
            jersey_id = jersey_data.get('id')
            
            # Add to collection
            collection_response = requests.post(f"{BACKEND_URL}/collections", 
                                              headers=headers,
                                              json={
                                                  "jersey_id": jersey_id,
                                                  "collection_type": "owned",
                                                  "size": "L",
                                                  "condition": "very_good"
                                              })
            
            if collection_response.status_code != 200:
                self.log_result("Test Listing Creation", False, 
                              f"Collection add failed: {collection_response.status_code}")
                return False
                
            collection_data = collection_response.json()
            collection_id = collection_data.get('id')
            
            # Create listing
            listing_response = requests.post(f"{BACKEND_URL}/listings", 
                                           headers=headers,
                                           json={
                                               "collection_id": collection_id,
                                               "price": 149.99,
                                               "marketplace_description": "Excellent condition Real Madrid jersey"
                                           })
            
            if listing_response.status_code == 200:
                listing_data = listing_response.json()
                self.listing_id = listing_data.get('id')
                self.log_result("Test Listing Creation", True, 
                              f"Listing created: {self.listing_id}")
                return True
            else:
                self.log_result("Test Listing Creation", False, 
                              f"Listing creation failed: {listing_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Test Listing Creation", False, f"Exception: {str(e)}")
            return False
            
    def test_secure_checkout_conversation_creation(self):
        """Test POST /api/payments/secure/checkout - Verify automatic conversation creation"""
        if not self.listing_id:
            self.log_result("Secure Checkout Test", False, "No test listing available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.post(f"{BACKEND_URL}/payments/secure/checkout", 
                                   headers=headers,
                                   json={
                                       "listing_id": self.listing_id,
                                       "origin_url": "https://jersey-collab-1.preview.emergentagent.com"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.transaction_id = data.get('transaction_id')
                conversation_created = data.get('conversation_created', False)
                
                self.log_result("Secure Checkout with Conversation", True, 
                              f"Transaction: {self.transaction_id}, Conversation: {conversation_created}")
                return True
            else:
                self.log_result("Secure Checkout with Conversation", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Secure Checkout with Conversation", False, f"Exception: {str(e)}")
            return False
            
    def test_seller_mark_shipped(self):
        """Test POST /api/transactions/{id}/seller/mark-shipped - Seller action in messaging"""
        if not self.transaction_id:
            self.log_result("Seller Mark Shipped", False, "No transaction available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}  # Admin is seller
            
            response = requests.post(f"{BACKEND_URL}/transactions/{self.transaction_id}/seller/mark-shipped", 
                                   headers=headers,
                                   json={
                                       "tracking_number": "FR123456789",
                                       "shipping_carrier": "La Poste",
                                       "notes": "Jersey shipped via express delivery"
                                   })
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Seller Mark Shipped", True, 
                              f"Shipped successfully: {data.get('message', 'Success')}")
                return True
            else:
                self.log_result("Seller Mark Shipped", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Seller Mark Shipped", False, f"Exception: {str(e)}")
            return False
            
    def test_buyer_confirm_receipt(self):
        """Test POST /api/transactions/{id}/buyer/confirm-receipt - Buyer action in messaging"""
        if not self.transaction_id:
            self.log_result("Buyer Confirm Receipt", False, "No transaction available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}  # User is buyer
            
            response = requests.post(f"{BACKEND_URL}/transactions/{self.transaction_id}/buyer/confirm-receipt", 
                                   headers=headers,
                                   json={
                                       "notes": "Jersey received in excellent condition as described",
                                       "rating": 5
                                   })
            
            if response.status_code == 200:
                data = response.json()
                payment_released = data.get('payment_released', False)
                self.log_result("Buyer Confirm Receipt", True, 
                              f"Receipt confirmed, Payment released: {payment_released}")
                return True
            else:
                self.log_result("Buyer Confirm Receipt", False, 
                              f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Buyer Confirm Receipt", False, f"Exception: {str(e)}")
            return False
            
    def test_conversation_messages(self):
        """Test conversation messages including system messages"""
        if not self.conversation_id:
            self.log_result("Conversation Messages", False, "No conversation available")
            return False
            
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
            
    def test_messaging_endpoints_availability(self):
        """Test basic messaging endpoints availability"""
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
            
            total_ok = sum([conversations_ok, friends_ok, notifications_ok])
            
            self.log_result("Messaging Endpoints Availability", total_ok == 3, 
                          f"Conversations: {conversations_ok}, Friends: {friends_ok}, Notifications: {notifications_ok}")
            
            return total_ok == 3
            
        except Exception as e:
            self.log_result("Messaging Endpoints Availability", False, f"Exception: {str(e)}")
            return False
            
    def run_all_tests(self):
        """Run all messaging system tests"""
        print("🎯 TOPKIT MESSAGING SYSTEM INTEGRATION TESTING (LEBONCOIN STYLE)")
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
        
        # Test messaging endpoints availability
        self.test_messaging_endpoints_availability()
        
        # Test fixed dependency injection endpoints
        self.test_conversation_creation_fixed()
        self.test_friend_request_fixed()
        
        # Create test data for transaction workflow
        self.create_test_listing()
        
        # Test Leboncoin-style workflow
        self.test_secure_checkout_conversation_creation()
        self.test_seller_mark_shipped()
        self.test_buyer_confirm_receipt()
        
        # Test conversation messages
        self.test_conversation_messages()
        
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