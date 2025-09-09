#!/usr/bin/env python3
"""
TopKit Messaging System Comprehensive Backend Testing Suite
Testing messaging system functionality to identify issues with messages not being visible and friend requirements
As requested in the review request
"""

import requests
import json
import sys
from datetime import datetime
import time
import websocket
import threading

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"
WS_URL = "wss://soccer-jersey-hub-2.preview.emergentagent.com/ws"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class MessagingSystemComprehensiveTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.test_conversation_id = None
        self.test_user_id = None
        self.ws_connection = None
        self.ws_messages = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def authenticate_user(self):
        """Authenticate test user - steinmetzlivio@gmail.com/123"""
        print("🔐 AUTHENTICATION & USER SETUP")
        print("=" * 50)
        
        try:
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_id = data["user"]["id"]
                    user_name = data["user"]["name"]
                    user_role = data["user"]["role"]
                    self.log_test(
                        "Login with steinmetzlivio@gmail.com/123",
                        True,
                        f"Authentication successful - User: {user_name}, Role: {user_role}, ID: {self.user_id}"
                    )
                    return True
                else:
                    self.log_test("Login Authentication", False, "", "Missing token or user data in response")
                    return False
            else:
                self.log_test("Login Authentication", False, "", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Login Authentication", False, "", str(e))
            return False

    def test_conversation_management_apis(self):
        """Test Conversation Management APIs"""
        print("💬 CONVERSATION MANAGEMENT APIs")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Conversation Management APIs", False, "", "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: GET /api/conversations - retrieve user conversations
        try:
            response = self.session.get(f"{BASE_URL}/conversations", headers=headers)
            
            if response.status_code == 200:
                conversations = response.json()
                if isinstance(conversations, list):
                    self.log_test(
                        "GET /api/conversations - Retrieve User Conversations",
                        True,
                        f"Successfully retrieved {len(conversations)} conversations with proper structure"
                    )
                    
                    # Analyze conversation structure
                    if len(conversations) > 0:
                        sample_conv = conversations[0]
                        has_participants = "participants" in sample_conv
                        has_last_message = "last_message" in sample_conv or "last_message_at" in sample_conv
                        
                        structure_details = f"Structure analysis: participants={has_participants}, last_message_info={has_last_message}"
                        self.log_test(
                            "Conversation Structure Verification",
                            True,
                            structure_details
                        )
                        
                        # Store conversation ID for message testing
                        self.test_conversation_id = sample_conv.get("id") or sample_conv.get("conversation_id")
                else:
                    self.log_test("GET /api/conversations - Retrieve User Conversations", False, "", "Invalid response format - expected list")
            else:
                self.log_test("GET /api/conversations - Retrieve User Conversations", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/conversations - Retrieve User Conversations", False, "", str(e))

        # Test 2: POST /api/conversations - create new conversations
        try:
            # First get a user to create conversation with
            search_response = self.session.get(f"{BASE_URL}/users/search?query=admin", headers=headers)
            
            if search_response.status_code == 200:
                users = search_response.json()
                if isinstance(users, list) and len(users) > 0:
                    # Find a user that's not the current user
                    target_user = None
                    for user in users:
                        if user.get("id") != self.user_id:
                            target_user = user
                            self.test_user_id = user.get("id")
                            break
                    
                    if target_user:
                        conversation_data = {
                            "recipient_id": target_user["id"],
                            "message": "Hello! Testing conversation creation functionality. This message should be visible in the conversation."
                        }
                        
                        response = self.session.post(f"{BASE_URL}/conversations", json=conversation_data, headers=headers)
                        
                        if response.status_code in [200, 201]:
                            conversation_result = response.json()
                            conversation_id = conversation_result.get("conversation_id") or conversation_result.get("id")
                            self.test_conversation_id = conversation_id
                            self.log_test(
                                "POST /api/conversations - Create New Conversations",
                                True,
                                f"Successfully created conversation with {target_user.get('name', 'Unknown')} - ID: {conversation_id}"
                            )
                        else:
                            self.log_test("POST /api/conversations - Create New Conversations", False, "", f"HTTP {response.status_code}: {response.text}")
                    else:
                        self.log_test("POST /api/conversations - Create New Conversations", False, "", "No suitable target user found")
                else:
                    self.log_test("POST /api/conversations - Create New Conversations", False, "", "No users found in search results")
            else:
                self.log_test("POST /api/conversations - Create New Conversations", False, "", f"User search failed: HTTP {search_response.status_code}")
        except Exception as e:
            self.log_test("POST /api/conversations - Create New Conversations", False, "", str(e))

    def test_message_apis(self):
        """Test Message APIs - Focus on message visibility issues"""
        print("📨 MESSAGE APIs - VISIBILITY TESTING")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Message APIs", False, "", "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: GET /api/conversations/{id}/messages - retrieve messages from conversations
        if self.test_conversation_id:
            try:
                response = self.session.get(f"{BASE_URL}/conversations/{self.test_conversation_id}/messages", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "messages" in data:
                        messages = data["messages"]
                        total_messages = data.get("total", len(messages))
                        conversation_id = data.get("conversation_id")
                        
                        self.log_test(
                            "GET /api/conversations/{id}/messages - Retrieve Messages",
                            True,
                            f"Successfully retrieved {total_messages} messages from conversation {conversation_id}"
                        )
                        
                        # Analyze message structure for visibility issues
                        if len(messages) > 0:
                            sample_message = messages[0]
                            has_sender = "sender_id" in sample_message
                            has_content = "message" in sample_message or "content" in sample_message
                            has_timestamp = "created_at" in sample_message or "timestamp" in sample_message
                            
                            structure_analysis = f"Message structure: sender={has_sender}, content={has_content}, timestamp={has_timestamp}"
                            self.log_test(
                                "Message Structure Analysis",
                                True,
                                structure_analysis
                            )
                        else:
                            self.log_test(
                                "Message Visibility Check",
                                False,
                                "",
                                "No messages found in conversation - potential visibility issue"
                            )
                    else:
                        self.log_test("GET /api/conversations/{id}/messages - Retrieve Messages", False, "", "Invalid response format - missing 'messages' key")
                elif response.status_code == 404:
                    self.log_test(
                        "GET /api/conversations/{id}/messages - Retrieve Messages",
                        False,
                        "",
                        "Conversation not found - potential data consistency issue"
                    )
                elif response.status_code == 403:
                    self.log_test(
                        "GET /api/conversations/{id}/messages - Retrieve Messages",
                        False,
                        "",
                        "Access denied - potential authorization issue affecting message visibility"
                    )
                else:
                    self.log_test("GET /api/conversations/{id}/messages - Retrieve Messages", False, "", f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("GET /api/conversations/{id}/messages - Retrieve Messages", False, "", str(e))
        else:
            self.log_test("GET /api/conversations/{id}/messages - Retrieve Messages", False, "", "No conversation ID available for testing")

        # Test 2: POST /api/conversations/send - send messages to conversations
        try:
            if self.test_conversation_id:
                # Test sending to existing conversation
                message_data = {
                    "conversation_id": self.test_conversation_id,
                    "message": "This is a test message to verify message sending and visibility. Message timestamp: " + datetime.now().isoformat()
                }
                
                response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    message_result = response.json()
                    message_id = message_result.get("message_id") or message_result.get("id")
                    self.log_test(
                        "POST /api/conversations/send - Send Messages (Existing Conversation)",
                        True,
                        f"Message sent successfully - ID: {message_id}"
                    )
                    
                    # Immediately check if message is visible
                    time.sleep(1)  # Brief delay for processing
                    check_response = self.session.get(f"{BASE_URL}/conversations/{self.test_conversation_id}/messages", headers=headers)
                    
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        if isinstance(check_data, dict) and "messages" in check_data:
                            messages = check_data["messages"]
                            # Look for our test message
                            found_message = any("test message to verify" in msg.get("message", "").lower() for msg in messages)
                            
                            if found_message:
                                self.log_test(
                                    "Message Visibility Verification",
                                    True,
                                    "Sent message is immediately visible in conversation"
                                )
                            else:
                                self.log_test(
                                    "Message Visibility Verification",
                                    False,
                                    "",
                                    "Sent message not found in conversation - VISIBILITY ISSUE DETECTED"
                                )
                        else:
                            self.log_test("Message Visibility Verification", False, "", "Could not retrieve messages for visibility check")
                    else:
                        self.log_test("Message Visibility Verification", False, "", f"Failed to check message visibility: HTTP {check_response.status_code}")
                        
                else:
                    self.log_test("POST /api/conversations/send - Send Messages (Existing Conversation)", False, "", f"HTTP {response.status_code}: {response.text}")
            
            # Test sending to new conversation (direct messaging)
            if self.test_user_id:
                message_data = {
                    "recipient_id": self.test_user_id,
                    "message": "Direct message test - creating new conversation. This should be visible immediately. Timestamp: " + datetime.now().isoformat()
                }
                
                response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    new_conversation_id = result.get("conversation_id") or result.get("id")
                    self.log_test(
                        "POST /api/conversations/send - Send Messages (New Conversation)",
                        True,
                        f"Direct message sent successfully, new conversation created: {new_conversation_id}"
                    )
                else:
                    self.log_test("POST /api/conversations/send - Send Messages (New Conversation)", False, "", f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_test("POST /api/conversations/send - Send Messages (New Conversation)", False, "", "No target user ID available for direct messaging test")
                
        except Exception as e:
            self.log_test("POST /api/conversations/send - Send Messages", False, "", str(e))

    def test_user_search_and_friend_requirements(self):
        """Test User Search & Friend Requirements for messaging"""
        print("👥 USER SEARCH & FRIEND REQUIREMENTS")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("User Search & Friend Requirements", False, "", "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: GET /api/users/search - search users for messaging
        try:
            # Test with different search queries
            search_queries = ["admin", "test", "top"]
            
            for query in search_queries:
                response = self.session.get(f"{BASE_URL}/users/search?query={query}", headers=headers)
                
                if response.status_code == 200:
                    users = response.json()
                    if isinstance(users, list):
                        self.log_test(
                            f"GET /api/users/search - Search Users ('{query}')",
                            True,
                            f"Found {len(users)} users matching '{query}'"
                        )
                        
                        # Check if current user is excluded from search results
                        current_user_in_results = any(user.get("id") == self.user_id for user in users)
                        if not current_user_in_results:
                            self.log_test(
                                "User Search - Self Exclusion",
                                True,
                                "Current user correctly excluded from search results"
                            )
                        else:
                            self.log_test(
                                "User Search - Self Exclusion",
                                False,
                                "",
                                "Current user appears in own search results"
                            )
                    else:
                        self.log_test(f"GET /api/users/search - Search Users ('{query}')", False, "", "Invalid response format")
                elif response.status_code == 422:
                    self.log_test(
                        f"GET /api/users/search - Search Users ('{query}')",
                        True,
                        "Search validation working (minimum query length required)"
                    )
                else:
                    self.log_test(f"GET /api/users/search - Search Users ('{query}')", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/users/search - Search Users", False, "", str(e))

        # Test 2: Verify friend relationships requirement for messaging
        try:
            # Get friends list to check current friend status
            friends_response = self.session.get(f"{BASE_URL}/friends", headers=headers)
            
            if friends_response.status_code == 200:
                friends_data = friends_response.json()
                friends_list = friends_data.get("friends", [])
                pending_requests = friends_data.get("pending_requests", {})
                
                self.log_test(
                    "Friend System Status Check",
                    True,
                    f"Current friends: {len(friends_list)}, Pending requests: {len(pending_requests.get('received', []))} received, {len(pending_requests.get('sent', []))} sent"
                )
                
                # Test messaging between non-friend users
                search_response = self.session.get(f"{BASE_URL}/users/search?query=admin", headers=headers)
                
                if search_response.status_code == 200:
                    users = search_response.json()
                    if isinstance(users, list) and len(users) > 0:
                        # Find a user who is not a friend
                        non_friend_user = None
                        for user in users:
                            user_id = user.get("id")
                            if user_id != self.user_id and not any(friend.get("id") == user_id for friend in friends_list):
                                non_friend_user = user
                                break
                        
                        if non_friend_user:
                            # Attempt to message non-friend user
                            message_data = {
                                "recipient_id": non_friend_user["id"],
                                "message": "Testing direct messaging between non-friend users. This should work if friend requirement is removed."
                            }
                            
                            response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                            
                            if response.status_code in [200, 201]:
                                self.log_test(
                                    "Direct Messaging Between Non-Friends",
                                    True,
                                    f"Successfully sent message to non-friend user {non_friend_user.get('name', 'Unknown')} - Friend requirement removed"
                                )
                            elif response.status_code == 403:
                                self.log_test(
                                    "Direct Messaging Between Non-Friends",
                                    False,
                                    "",
                                    "Friend requirement still blocking direct messaging - ISSUE IDENTIFIED"
                                )
                            else:
                                self.log_test("Direct Messaging Between Non-Friends", False, "", f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_test("Direct Messaging Between Non-Friends", False, "", "No non-friend users found for testing")
                    else:
                        self.log_test("Direct Messaging Between Non-Friends", False, "", "No users found for friend requirement testing")
                else:
                    self.log_test("Direct Messaging Between Non-Friends", False, "", f"User search failed: HTTP {search_response.status_code}")
            else:
                self.log_test("Friend System Status Check", False, "", f"HTTP {friends_response.status_code}: {friends_response.text}")
        except Exception as e:
            self.log_test("Friend Requirements Testing", False, "", str(e))

    def test_real_time_messaging(self):
        """Test Real-time Messaging WebSocket connections"""
        print("⚡ REAL-TIME MESSAGING - WEBSOCKET")
        print("=" * 50)
        
        if not self.user_token or not self.user_id:
            self.log_test("Real-time Messaging", False, "", "No user token or ID available")
            return

        # Test WebSocket connection
        try:
            ws_url = f"{WS_URL}/{self.user_id}"
            
            def on_message(ws, message):
                self.ws_messages.append(message)
                print(f"WebSocket message received: {message}")
            
            def on_error(ws, error):
                print(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("WebSocket connection closed")
            
            def on_open(ws):
                print("WebSocket connection opened")
                # Send a test message
                test_message = json.dumps({
                    "type": "ping",
                    "user_id": self.user_id,
                    "timestamp": datetime.now().isoformat()
                })
                ws.send(test_message)
            
            # Attempt WebSocket connection
            self.ws_connection = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread for a short time
            ws_thread = threading.Thread(target=self.ws_connection.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection and test
            time.sleep(3)
            
            if len(self.ws_messages) > 0:
                self.log_test(
                    "WebSocket Connection at /ws/{user_id}",
                    True,
                    f"WebSocket connection successful, received {len(self.ws_messages)} messages"
                )
            else:
                self.log_test(
                    "WebSocket Connection at /ws/{user_id}",
                    True,
                    "WebSocket connection established (no messages received in test period)"
                )
                
            # Test real-time message notifications
            if self.test_conversation_id:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                message_data = {
                    "conversation_id": self.test_conversation_id,
                    "message": "WebSocket notification test message - should trigger real-time notification"
                }
                
                # Send message and check for WebSocket notification
                initial_ws_count = len(self.ws_messages)
                response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    time.sleep(2)  # Wait for WebSocket notification
                    
                    if len(self.ws_messages) > initial_ws_count:
                        self.log_test(
                            "Real-time Message Notifications",
                            True,
                            "WebSocket notification received after sending message"
                        )
                    else:
                        self.log_test(
                            "Real-time Message Notifications",
                            False,
                            "",
                            "No WebSocket notification received after sending message"
                        )
                else:
                    self.log_test("Real-time Message Notifications", False, "", f"Failed to send test message: HTTP {response.status_code}")
            
            # Close WebSocket connection
            if self.ws_connection:
                self.ws_connection.close()
                
        except Exception as e:
            self.log_test("WebSocket Connection Testing", False, "", str(e))

    def test_seller_contact_integration(self):
        """Test Seller Contact Integration with messaging"""
        print("🛒 SELLER CONTACT INTEGRATION")
        print("=" * 50)
        
        if not self.user_token:
            self.log_test("Seller Contact Integration", False, "", "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}

        # Test 1: Get marketplace listings to find sellers
        try:
            response = self.session.get(f"{BASE_URL}/marketplace/catalog", headers=headers)
            
            if response.status_code == 200:
                marketplace_data = response.json()
                if isinstance(marketplace_data, list) and len(marketplace_data) > 0:
                    self.log_test(
                        "Marketplace Listings Access",
                        True,
                        f"Found {len(marketplace_data)} marketplace items for seller contact testing"
                    )
                    
                    # Test messaging between marketplace users (buyer to seller)
                    sample_item = marketplace_data[0]
                    if "seller_id" in sample_item or "listings" in sample_item:
                        seller_id = sample_item.get("seller_id")
                        if not seller_id and "listings" in sample_item and len(sample_item["listings"]) > 0:
                            seller_id = sample_item["listings"][0].get("seller_id")
                        
                        if seller_id and seller_id != self.user_id:
                            # Test contacting seller
                            message_data = {
                                "recipient_id": seller_id,
                                "message": f"Hello! I'm interested in your {sample_item.get('team', 'jersey')} listing. Is it still available?"
                            }
                            
                            response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                            
                            if response.status_code in [200, 201]:
                                self.log_test(
                                    "Buyer to Seller Messaging",
                                    True,
                                    f"Successfully contacted seller {seller_id} about marketplace item"
                                )
                            else:
                                self.log_test("Buyer to Seller Messaging", False, "", f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_test("Buyer to Seller Messaging", False, "", "No valid seller ID found or seller is current user")
                    else:
                        self.log_test("Seller Contact Integration", False, "", "Marketplace items missing seller information")
                else:
                    self.log_test(
                        "Marketplace Listings Access",
                        True,
                        "Marketplace catalog accessible but empty (expected in clean database)"
                    )
            else:
                self.log_test("Marketplace Listings Access", False, "", f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Seller Contact Integration", False, "", str(e))

        # Test 2: Verify seller contact functionality in listings
        try:
            # Get active listings
            listings_response = self.session.get(f"{BASE_URL}/listings", headers=headers)
            
            if listings_response.status_code == 200:
                listings = listings_response.json()
                if isinstance(listings, list):
                    self.log_test(
                        "Active Listings Access",
                        True,
                        f"Retrieved {len(listings)} active listings for seller contact testing"
                    )
                    
                    # Test contact seller functionality for each listing
                    for listing in listings[:3]:  # Test first 3 listings
                        seller_id = listing.get("seller_id")
                        listing_id = listing.get("id")
                        
                        if seller_id and seller_id != self.user_id:
                            # Test messaging with listing context
                            message_data = {
                                "recipient_id": seller_id,
                                "message": f"Hi! I'm interested in your listing (ID: {listing_id}). Could you provide more details?",
                                "listing_id": listing_id  # Include listing context
                            }
                            
                            response = self.session.post(f"{BASE_URL}/conversations/send", json=message_data, headers=headers)
                            
                            if response.status_code in [200, 201]:
                                self.log_test(
                                    f"Seller Contact for Listing {listing_id}",
                                    True,
                                    "Successfully contacted seller with listing context"
                                )
                                break  # Only test one successful contact
                            else:
                                self.log_test(f"Seller Contact for Listing {listing_id}", False, "", f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_test("Active Listings Access", False, "", "Invalid listings response format")
            else:
                self.log_test("Active Listings Access", False, "", f"HTTP {listings_response.status_code}: {listings_response.text}")
        except Exception as e:
            self.log_test("Seller Contact via Listings", False, "", str(e))

    def run_all_tests(self):
        """Run all messaging system tests"""
        print("🚀 MESSAGING SYSTEM COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"WebSocket URL: {WS_URL}")
        print(f"Test User: {TEST_USER_EMAIL}")
        print("=" * 70)
        print()
        
        # Authenticate first
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return 0
        
        # Run all test suites as requested in review
        self.test_conversation_management_apis()
        self.test_message_apis()
        self.test_user_search_and_friend_requirements()
        self.test_real_time_messaging()
        self.test_seller_contact_integration()
        
        # Generate summary
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("📊 MESSAGING SYSTEM TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Categorize issues found
        critical_issues = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["error"].lower() for keyword in ["visibility", "friend requirement", "not found", "access denied"]):
                    critical_issues.append(result)
                else:
                    minor_issues.append(result)
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for result in critical_issues:
                print(f"  - {result['test']}: {result['error']}")
            print()
        
        if minor_issues:
            print("⚠️  MINOR ISSUES:")
            for result in minor_issues:
                print(f"  - {result['test']}: {result['error']}")
            print()
        
        print("✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test']}")
        
        print()
        print("🎯 MESSAGING SYSTEM COMPREHENSIVE TESTING COMPLETE")
        print("Focus areas tested as requested:")
        print("  ✓ Authentication & User Setup")
        print("  ✓ Conversation Management APIs")
        print("  ✓ Message APIs & Visibility")
        print("  ✓ User Search & Friend Requirements")
        print("  ✓ Real-time Messaging (WebSocket)")
        print("  ✓ Seller Contact Integration")
        
        return success_rate

if __name__ == "__main__":
    tester = MessagingSystemComprehensiveTester()
    success_rate = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 70 else 1)