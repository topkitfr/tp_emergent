#!/usr/bin/env python3

"""
TopKit Friends System and Messaging System API Testing
=====================================================

This script tests the newly implemented Friends System and Messaging System API endpoints:

Friends System:
1. POST /api/users/search - Search for users to add as friends
2. POST /api/friends/request - Send friend requests  
3. POST /api/friends/respond - Accept/decline friend requests
4. GET /api/friends - Get friends list and pending requests

Messaging System:
5. POST /api/conversations - Create conversations and send messages
6. GET /api/conversations - Get user's conversations list
7. GET /api/conversations/{id}/messages - Get messages from specific conversation
8. POST /api/conversations/send - Send messages with real-time notification support
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://football-jersey-db.preview.emergentagent.com/api"

class TopKitFriendsMessagingTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.test_users = {}
        self.auth_tokens = {}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def create_test_users(self) -> bool:
        """Create test users for friends and messaging testing"""
        print("🔧 Creating test users for Friends & Messaging testing...")
        
        test_users_data = [
            {
                "name": "Alice Johnson",
                "email": "alice.johnson@test.com",
                "password": "testpass123"
            },
            {
                "name": "Bob Smith", 
                "email": "bob.smith@test.com",
                "password": "testpass123"
            },
            {
                "name": "Charlie Brown",
                "email": "charlie.brown@test.com", 
                "password": "testpass123"
            }
        ]
        
        for user_data in test_users_data:
            try:
                # Try to register user
                response = self.session.post(
                    f"{self.backend_url}/auth/register",
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 201 or response.status_code == 200:
                    data = response.json()
                    user_id = data["user"]["id"]
                    token = data["token"]
                    
                    self.test_users[user_data["name"]] = {
                        "id": user_id,
                        "email": user_data["email"],
                        "name": user_data["name"]
                    }
                    self.auth_tokens[user_data["name"]] = token
                    
                    print(f"✅ Created user: {user_data['name']} (ID: {user_id})")
                    
                elif response.status_code == 400 and "already exists" in response.text:
                    # User exists, try to login
                    login_response = self.session.post(
                        f"{self.backend_url}/auth/login",
                        json={
                            "email": user_data["email"],
                            "password": user_data["password"]
                        },
                        timeout=10
                    )
                    
                    if login_response.status_code == 200:
                        data = login_response.json()
                        user_id = data["user"]["id"]
                        token = data["token"]
                        
                        self.test_users[user_data["name"]] = {
                            "id": user_id,
                            "email": user_data["email"],
                            "name": user_data["name"]
                        }
                        self.auth_tokens[user_data["name"]] = token
                        
                        print(f"✅ Logged in existing user: {user_data['name']} (ID: {user_id})")
                    else:
                        print(f"❌ Failed to login existing user: {user_data['name']}")
                        return False
                else:
                    print(f"❌ Failed to create user {user_data['name']}: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error creating user {user_data['name']}: {str(e)}")
                return False
        
        print(f"✅ Successfully set up {len(self.test_users)} test users")
        return len(self.test_users) >= 3

    def get_auth_headers(self, user_name: str) -> Dict[str, str]:
        """Get authorization headers for a user"""
        token = self.auth_tokens.get(user_name)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    def test_user_search(self) -> bool:
        """Test GET /api/users/search - Search for users to add as friends"""
        print("🔍 Testing User Search API...")
        
        try:
            # Test 1: Search for users as Alice
            alice_headers = self.get_auth_headers("Alice Johnson")
            
            response = self.session.get(
                f"{self.backend_url}/users/search",
                params={"query": "Bob", "limit": 10},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                
                # Check if Bob is in search results
                bob_found = any(user.get("name") == "Bob Smith" for user in users)
                
                if bob_found:
                    self.log_test(
                        "User Search - Find Bob",
                        True,
                        f"Found {len(users)} users, Bob Smith included",
                        users
                    )
                else:
                    self.log_test(
                        "User Search - Find Bob",
                        False,
                        f"Bob Smith not found in search results",
                        users
                    )
                    return False
            else:
                self.log_test(
                    "User Search - Find Bob",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Search with email
            response = self.session.get(
                f"{self.backend_url}/users/search",
                params={"query": "charlie.brown", "limit": 10},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                charlie_found = any("charlie.brown" in user.get("email", "").lower() for user in users)
                
                self.log_test(
                    "User Search - Find by Email",
                    charlie_found,
                    f"Found {len(users)} users, Charlie found by email: {charlie_found}",
                    users
                )
            else:
                self.log_test(
                    "User Search - Find by Email",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 3: Search with short query (should return empty)
            response = self.session.get(
                f"{self.backend_url}/users/search",
                params={"query": "B", "limit": 10},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                users = response.json()
                self.log_test(
                    "User Search - Short Query",
                    len(users) == 0,
                    f"Short query returned {len(users)} users (should be 0)",
                    users
                )
            else:
                self.log_test(
                    "User Search - Short Query",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test("User Search", False, f"Exception: {str(e)}")
            return False

    def test_friend_requests(self) -> bool:
        """Test POST /api/friends/request - Send friend requests"""
        print("👥 Testing Friend Request API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_id = self.test_users["Bob Smith"]["id"]
            charlie_id = self.test_users["Charlie Brown"]["id"]
            
            # Test 1: Alice sends friend request to Bob
            response = self.session.post(
                f"{self.backend_url}/friends/request",
                json={"user_id": bob_id, "message": "Hi Bob! Let's be friends!"},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Friend Request - Alice to Bob",
                    True,
                    f"Friend request sent successfully: {data.get('message')}",
                    data
                )
                
                # Store request ID for later use
                self.alice_to_bob_request_id = data.get("request_id")
            else:
                self.log_test(
                    "Friend Request - Alice to Bob",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Alice sends friend request to Charlie
            response = self.session.post(
                f"{self.backend_url}/friends/request",
                json={"user_id": charlie_id},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Friend Request - Alice to Charlie",
                    True,
                    f"Friend request sent successfully: {data.get('message')}",
                    data
                )
                
                # Store request ID for later use
                self.alice_to_charlie_request_id = data.get("request_id")
            else:
                self.log_test(
                    "Friend Request - Alice to Charlie",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 3: Try to send duplicate request (should fail)
            response = self.session.post(
                f"{self.backend_url}/friends/request",
                json={"user_id": bob_id},
                headers=alice_headers,
                timeout=10
            )
            
            self.log_test(
                "Friend Request - Duplicate Prevention",
                response.status_code == 400,
                f"Duplicate request correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 400 else None
            )
            
            # Test 4: Try to send friend request to self (should fail)
            alice_id = self.test_users["Alice Johnson"]["id"]
            response = self.session.post(
                f"{self.backend_url}/friends/request",
                json={"user_id": alice_id},
                headers=alice_headers,
                timeout=10
            )
            
            self.log_test(
                "Friend Request - Self Request Prevention",
                response.status_code == 400,
                f"Self friend request correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 400 else None
            )
            
            return True
            
        except Exception as e:
            self.log_test("Friend Request", False, f"Exception: {str(e)}")
            return False

    def test_friend_responses(self) -> bool:
        """Test POST /api/friends/respond - Accept/decline friend requests"""
        print("✅ Testing Friend Response API...")
        
        try:
            bob_headers = self.get_auth_headers("Bob Smith")
            charlie_headers = self.get_auth_headers("Charlie Brown")
            
            # Test 1: Bob accepts Alice's friend request
            if hasattr(self, 'alice_to_bob_request_id'):
                response = self.session.post(
                    f"{self.backend_url}/friends/respond",
                    json={
                        "request_id": self.alice_to_bob_request_id,
                        "accept": True
                    },
                    headers=bob_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Friend Response - Bob Accepts Alice",
                        True,
                        f"Friend request accepted: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Friend Response - Bob Accepts Alice",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            else:
                self.log_test(
                    "Friend Response - Bob Accepts Alice",
                    False,
                    "No request ID available from previous test"
                )
                return False
            
            # Test 2: Charlie declines Alice's friend request
            if hasattr(self, 'alice_to_charlie_request_id'):
                response = self.session.post(
                    f"{self.backend_url}/friends/respond",
                    json={
                        "request_id": self.alice_to_charlie_request_id,
                        "accept": False
                    },
                    headers=charlie_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Friend Response - Charlie Declines Alice",
                        True,
                        f"Friend request declined: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Friend Response - Charlie Declines Alice",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            else:
                self.log_test(
                    "Friend Response - Charlie Declines Alice",
                    False,
                    "No request ID available from previous test"
                )
                return False
            
            # Test 3: Try to respond to non-existent request (should fail)
            response = self.session.post(
                f"{self.backend_url}/friends/respond",
                json={
                    "request_id": "non-existent-id",
                    "accept": True
                },
                headers=bob_headers,
                timeout=10
            )
            
            self.log_test(
                "Friend Response - Invalid Request ID",
                response.status_code == 404,
                f"Invalid request ID correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 404 else None
            )
            
            return True
            
        except Exception as e:
            self.log_test("Friend Response", False, f"Exception: {str(e)}")
            return False

    def test_friends_list(self) -> bool:
        """Test GET /api/friends - Get friends list and pending requests"""
        print("📋 Testing Friends List API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_headers = self.get_auth_headers("Bob Smith")
            
            # Test 1: Get Alice's friends list (should have Bob as friend)
            response = self.session.get(
                f"{self.backend_url}/friends",
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                friends = data.get("friends", [])
                pending_received = data.get("pending_requests", {}).get("received", [])
                pending_sent = data.get("pending_requests", {}).get("sent", [])
                stats = data.get("stats", {})
                
                # Check if Bob is in Alice's friends list
                bob_is_friend = any(friend.get("name") == "Bob Smith" for friend in friends)
                
                self.log_test(
                    "Friends List - Alice's Friends",
                    bob_is_friend,
                    f"Alice has {len(friends)} friends, Bob is friend: {bob_is_friend}. Stats: {stats}",
                    data
                )
                
                if not bob_is_friend:
                    return False
                    
            else:
                self.log_test(
                    "Friends List - Alice's Friends",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Get Bob's friends list (should have Alice as friend)
            response = self.session.get(
                f"{self.backend_url}/friends",
                headers=bob_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                friends = data.get("friends", [])
                stats = data.get("stats", {})
                
                # Check if Alice is in Bob's friends list
                alice_is_friend = any(friend.get("name") == "Alice Johnson" for friend in friends)
                
                self.log_test(
                    "Friends List - Bob's Friends",
                    alice_is_friend,
                    f"Bob has {len(friends)} friends, Alice is friend: {alice_is_friend}. Stats: {stats}",
                    data
                )
                
                if not alice_is_friend:
                    return False
                    
            else:
                self.log_test(
                    "Friends List - Bob's Friends",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Friends List", False, f"Exception: {str(e)}")
            return False

    def test_create_conversation(self) -> bool:
        """Test POST /api/conversations - Create conversations and send messages"""
        print("💬 Testing Create Conversation API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_id = self.test_users["Bob Smith"]["id"]
            
            # Test 1: Alice creates conversation with Bob
            response = self.session.post(
                f"{self.backend_url}/conversations",
                json={
                    "recipient_id": bob_id,
                    "message": "Hi Bob! How are you doing?",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                message_id = data.get("message_id")
                
                self.log_test(
                    "Create Conversation - Alice to Bob",
                    True,
                    f"Conversation created successfully. ID: {conversation_id}, Message ID: {message_id}",
                    data
                )
                
                # Store conversation ID for later tests
                self.alice_bob_conversation_id = conversation_id
                
            else:
                self.log_test(
                    "Create Conversation - Alice to Bob",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Add another message to existing conversation
            if hasattr(self, 'alice_bob_conversation_id'):
                response = self.session.post(
                    f"{self.backend_url}/conversations",
                    json={
                        "conversation_id": self.alice_bob_conversation_id,
                        "message": "I hope we can chat more often!",
                        "message_type": "text"
                    },
                    headers=alice_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Create Conversation - Add Message to Existing",
                        True,
                        f"Message added to existing conversation: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Create Conversation - Add Message to Existing",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Test 3: Try to create conversation with non-existent user (should fail)
            response = self.session.post(
                f"{self.backend_url}/conversations",
                json={
                    "recipient_id": "non-existent-user-id",
                    "message": "Hello!",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            self.log_test(
                "Create Conversation - Invalid Recipient",
                response.status_code == 404,
                f"Invalid recipient correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 404 else None
            )
            
            return True
            
        except Exception as e:
            self.log_test("Create Conversation", False, f"Exception: {str(e)}")
            return False

    def test_get_conversations(self) -> bool:
        """Test GET /api/conversations - Get user's conversations list"""
        print("📝 Testing Get Conversations API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_headers = self.get_auth_headers("Bob Smith")
            
            # Test 1: Get Alice's conversations
            response = self.session.get(
                f"{self.backend_url}/conversations",
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
                
                # Check if conversation with Bob exists
                bob_conversation = None
                for conv in conversations:
                    if conv.get("other_user", {}).get("name") == "Bob Smith":
                        bob_conversation = conv
                        break
                
                self.log_test(
                    "Get Conversations - Alice's List",
                    bob_conversation is not None,
                    f"Alice has {len(conversations)} conversations, conversation with Bob found: {bob_conversation is not None}",
                    conversations
                )
                
                if bob_conversation is None:
                    return False
                    
            else:
                self.log_test(
                    "Get Conversations - Alice's List",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Get Bob's conversations
            response = self.session.get(
                f"{self.backend_url}/conversations",
                headers=bob_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
                
                # Check if conversation with Alice exists
                alice_conversation = None
                for conv in conversations:
                    if conv.get("other_user", {}).get("name") == "Alice Johnson":
                        alice_conversation = conv
                        break
                
                self.log_test(
                    "Get Conversations - Bob's List",
                    alice_conversation is not None,
                    f"Bob has {len(conversations)} conversations, conversation with Alice found: {alice_conversation is not None}",
                    conversations
                )
                
                if alice_conversation is None:
                    return False
                    
            else:
                self.log_test(
                    "Get Conversations - Bob's List",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Get Conversations", False, f"Exception: {str(e)}")
            return False

    def test_get_conversation_messages(self) -> bool:
        """Test GET /api/conversations/{id}/messages - Get messages from specific conversation"""
        print("📨 Testing Get Conversation Messages API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_headers = self.get_auth_headers("Bob Smith")
            
            if not hasattr(self, 'alice_bob_conversation_id'):
                self.log_test(
                    "Get Conversation Messages",
                    False,
                    "No conversation ID available from previous tests"
                )
                return False
            
            # Test 1: Alice gets messages from conversation with Bob
            response = self.session.get(
                f"{self.backend_url}/conversations/{self.alice_bob_conversation_id}/messages",
                params={"limit": 50, "skip": 0},
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                conversation_id = data.get("conversation_id")
                total = data.get("total", 0)
                
                # Check if messages exist and have correct structure
                has_messages = len(messages) > 0
                correct_structure = True
                
                for msg in messages:
                    if not all(key in msg for key in ["id", "sender_id", "message", "created_at", "sent_by_me"]):
                        correct_structure = False
                        break
                
                self.log_test(
                    "Get Conversation Messages - Alice View",
                    has_messages and correct_structure,
                    f"Found {len(messages)} messages, correct structure: {correct_structure}, total: {total}",
                    data
                )
                
                if not (has_messages and correct_structure):
                    return False
                    
            else:
                self.log_test(
                    "Get Conversation Messages - Alice View",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Bob gets messages from same conversation
            response = self.session.get(
                f"{self.backend_url}/conversations/{self.alice_bob_conversation_id}/messages",
                params={"limit": 50, "skip": 0},
                headers=bob_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                # Check if Bob sees the same messages but with different "sent_by_me" values
                has_messages = len(messages) > 0
                
                self.log_test(
                    "Get Conversation Messages - Bob View",
                    has_messages,
                    f"Bob found {len(messages)} messages in same conversation",
                    data
                )
                
                if not has_messages:
                    return False
                    
            else:
                self.log_test(
                    "Get Conversation Messages - Bob View",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 3: Try to access conversation without authorization (should fail)
            charlie_headers = self.get_auth_headers("Charlie Brown")
            response = self.session.get(
                f"{self.backend_url}/conversations/{self.alice_bob_conversation_id}/messages",
                headers=charlie_headers,
                timeout=10
            )
            
            self.log_test(
                "Get Conversation Messages - Unauthorized Access",
                response.status_code == 403,
                f"Unauthorized access correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 403 else None
            )
            
            return True
            
        except Exception as e:
            self.log_test("Get Conversation Messages", False, f"Exception: {str(e)}")
            return False

    def test_send_message_realtime(self) -> bool:
        """Test POST /api/conversations/send - Send messages with real-time notification support"""
        print("⚡ Testing Send Message with Real-time Notifications API...")
        
        try:
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_headers = self.get_auth_headers("Bob Smith")
            bob_id = self.test_users["Bob Smith"]["id"]
            
            # Test 1: Alice sends message to Bob using real-time endpoint
            response = self.session.post(
                f"{self.backend_url}/conversations/send",
                json={
                    "recipient_id": bob_id,
                    "message": "This is a real-time message test!",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                message_id = data.get("message_id")
                real_time_sent = data.get("real_time_sent", False)
                
                self.log_test(
                    "Send Message Real-time - New Message",
                    True,
                    f"Message sent successfully. Conversation: {conversation_id}, Message: {message_id}, Real-time: {real_time_sent}",
                    data
                )
                
                # Store conversation ID for next test
                self.realtime_conversation_id = conversation_id
                
            else:
                self.log_test(
                    "Send Message Real-time - New Message",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            # Test 2: Bob replies using existing conversation ID
            if hasattr(self, 'realtime_conversation_id'):
                response = self.session.post(
                    f"{self.backend_url}/conversations/send",
                    json={
                        "conversation_id": self.realtime_conversation_id,
                        "message": "Thanks Alice! Real-time messaging is working great!",
                        "message_type": "text"
                    },
                    headers=bob_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Send Message Real-time - Reply to Existing",
                        True,
                        f"Reply sent successfully: {data.get('message')}",
                        data
                    )
                else:
                    self.log_test(
                        "Send Message Real-time - Reply to Existing",
                        False,
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
            
            # Test 3: Try to send message to non-existent conversation (should fail)
            response = self.session.post(
                f"{self.backend_url}/conversations/send",
                json={
                    "conversation_id": "non-existent-conversation-id",
                    "message": "This should fail",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            self.log_test(
                "Send Message Real-time - Invalid Conversation",
                response.status_code == 404,
                f"Invalid conversation ID correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 404 else None
            )
            
            # Test 4: Try to send message without recipient_id or conversation_id (should fail)
            response = self.session.post(
                f"{self.backend_url}/conversations/send",
                json={
                    "message": "This should fail - no recipient or conversation",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            self.log_test(
                "Send Message Real-time - Missing Required Fields",
                response.status_code == 400,
                f"Missing required fields correctly rejected: HTTP {response.status_code}",
                response.json() if response.status_code == 400 else None
            )
            
            return True
            
        except Exception as e:
            self.log_test("Send Message Real-time", False, f"Exception: {str(e)}")
            return False

    def test_complete_workflow(self) -> bool:
        """Test complete friends and messaging workflow"""
        print("🔄 Testing Complete Friends & Messaging Workflow...")
        
        try:
            # This test verifies the complete user journey:
            # 1. Search for users
            # 2. Send friend requests
            # 3. Accept friend requests
            # 4. Start messaging
            # 5. Continue conversation
            
            alice_headers = self.get_auth_headers("Alice Johnson")
            bob_headers = self.get_auth_headers("Bob Smith")
            
            # Verify Alice and Bob are friends
            response = self.session.get(
                f"{self.backend_url}/friends",
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                friends = data.get("friends", [])
                bob_is_friend = any(friend.get("name") == "Bob Smith" for friend in friends)
                
                if not bob_is_friend:
                    self.log_test(
                        "Complete Workflow - Friendship Verification",
                        False,
                        "Alice and Bob are not friends - workflow incomplete"
                    )
                    return False
            else:
                self.log_test(
                    "Complete Workflow - Friendship Verification",
                    False,
                    f"Failed to get friends list: HTTP {response.status_code}"
                )
                return False
            
            # Verify they have active conversations
            response = self.session.get(
                f"{self.backend_url}/conversations",
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                conversations = response.json()
                bob_conversation = any(
                    conv.get("other_user", {}).get("name") == "Bob Smith" 
                    for conv in conversations
                )
                
                if not bob_conversation:
                    self.log_test(
                        "Complete Workflow - Conversation Verification",
                        False,
                        "Alice and Bob don't have active conversations - workflow incomplete"
                    )
                    return False
            else:
                self.log_test(
                    "Complete Workflow - Conversation Verification",
                    False,
                    f"Failed to get conversations: HTTP {response.status_code}"
                )
                return False
            
            # Send a final test message to confirm everything works
            bob_id = self.test_users["Bob Smith"]["id"]
            response = self.session.post(
                f"{self.backend_url}/conversations/send",
                json={
                    "recipient_id": bob_id,
                    "message": "🎉 Complete workflow test successful! Friends and messaging system is working perfectly!",
                    "message_type": "text"
                },
                headers=alice_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test(
                    "Complete Workflow - Final Message Test",
                    True,
                    "Complete friends and messaging workflow verified successfully!"
                )
                return True
            else:
                self.log_test(
                    "Complete Workflow - Final Message Test",
                    False,
                    f"Final message test failed: HTTP {response.status_code}"
                )
                return False
            
        except Exception as e:
            self.log_test("Complete Workflow", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all Friends System and Messaging System tests"""
        print("🚀 Starting TopKit Friends System and Messaging System API Testing")
        print("=" * 80)
        
        # Setup phase
        if not self.create_test_users():
            print("❌ Failed to create test users. Aborting tests.")
            return False
        
        print("\n" + "=" * 80)
        print("🧪 Running Friends System Tests")
        print("=" * 80)
        
        # Friends System Tests
        tests_passed = 0
        total_tests = 8
        
        if self.test_user_search():
            tests_passed += 1
        
        if self.test_friend_requests():
            tests_passed += 1
        
        if self.test_friend_responses():
            tests_passed += 1
        
        if self.test_friends_list():
            tests_passed += 1
        
        print("\n" + "=" * 80)
        print("💬 Running Messaging System Tests")
        print("=" * 80)
        
        if self.test_create_conversation():
            tests_passed += 1
        
        if self.test_get_conversations():
            tests_passed += 1
        
        if self.test_get_conversation_messages():
            tests_passed += 1
        
        if self.test_send_message_realtime():
            tests_passed += 1
        
        print("\n" + "=" * 80)
        print("🔄 Running Complete Workflow Test")
        print("=" * 80)
        
        # Complete workflow test doesn't count towards main test count
        workflow_success = self.test_complete_workflow()
        
        # Print final results
        print("\n" + "=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        
        success_rate = (tests_passed / total_tests) * 100
        
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"🔄 Complete Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
        
        # Print detailed results
        print(f"\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"  {status_icon} {result['test']}")
            if result["details"]:
                print(f"      {result['details']}")
        
        print(f"\n🎯 Overall Status: {'✅ ALL SYSTEMS OPERATIONAL' if tests_passed == total_tests and workflow_success else '❌ ISSUES DETECTED'}")
        
        return tests_passed == total_tests and workflow_success

if __name__ == "__main__":
    tester = TopKitFriendsMessagingTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All Friends System and Messaging System API endpoints are working correctly!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the detailed results above.")
        exit(1)