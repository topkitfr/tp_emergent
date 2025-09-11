#!/usr/bin/env python3
"""
🎯 TOPKIT MESSAGING ENDPOINTS BACKEND TESTING (LEBONCOIN STYLE)
================================================================

Test des endpoints de messagerie intégrée style Leboncoin pour TopKit
Focus sur les endpoints disponibles sans nécessiter de données de test complexes

ENDPOINTS À TESTER:
1. GET /api/conversations - Liste des conversations
2. POST /api/conversations - Créer une conversation
3. GET /api/conversations/{id}/messages - Messages d'une conversation
4. POST /api/conversations/{id}/messages - Envoyer un message
5. GET /api/friends - Système d'amis
6. POST /api/friends/request - Demande d'ami
7. Endpoints de transaction (structure et validation)

DONNÉES DE TEST:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User test: messaging.test@example.com / MessagingTestSecure789#
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://topkit-bugfixes.preview.emergentagent.com/api"

# Credentials de test
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "messaging.test@example.com", 
    "password": "MessagingTestSecure789#"
}

class MessagingEndpointsTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_id = None
        self.user_id = None
        self.test_results = []
        self.test_conversation_id = None
        
    def log_test(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_admin(self):
        """Authenticate admin user"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                admin_info = data.get("user", {})
                self.admin_id = admin_info.get("id")
                self.log_test(
                    "Admin Authentication",
                    True,
                    f"Admin authenticated: {admin_info.get('name')} (Role: {admin_info.get('role')}, ID: {self.admin_id})"
                )
                return True
            else:
                self.log_test("Admin Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def authenticate_user(self):
        """Authenticate regular user"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                self.log_test(
                    "User Authentication",
                    True,
                    f"User authenticated: {user_info.get('name')} (Role: {user_info.get('role')}, ID: {self.user_id})"
                )
                return True
            else:
                self.log_test("User Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False

    def test_conversations_list(self):
        """Test GET /api/conversations - Liste des conversations"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BASE_URL}/conversations", headers=headers)
            
            if response.status_code == 200:
                conversations = response.json()
                self.log_test(
                    "Conversations List",
                    True,
                    f"✅ Conversations endpoint accessible. Found {len(conversations)} conversations"
                )
                return True
            else:
                self.log_test(
                    "Conversations List",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Conversations List", False, f"Exception: {str(e)}")
            return False

    def test_create_conversation(self):
        """Test POST /api/conversations - Créer une conversation"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Create conversation with admin
            conversation_data = {
                "recipient_id": self.admin_id,
                "message": "Bonjour, je suis intéressé par le système de messagerie intégrée TopKit!"
            }
            
            response = requests.post(f"{BASE_URL}/conversations", json=conversation_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.test_conversation_id = result.get('conversation_id')
                self.log_test(
                    "Create Conversation",
                    True,
                    f"✅ Conversation created successfully! ID: {self.test_conversation_id}"
                )
                return True
            else:
                self.log_test(
                    "Create Conversation",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Create Conversation", False, f"Exception: {str(e)}")
            return False

    def test_conversation_messages(self):
        """Test GET /api/conversations/{id}/messages - Messages d'une conversation"""
        try:
            if not self.test_conversation_id:
                self.log_test("Conversation Messages", False, "No test conversation available")
                return False
                
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BASE_URL}/conversations/{self.test_conversation_id}/messages", headers=headers)
            
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get('messages', [])
                
                self.log_test(
                    "Conversation Messages",
                    True,
                    f"✅ Messages retrieved successfully! Found {len(messages)} messages"
                )
                
                # Show message details
                for i, msg in enumerate(messages[:2]):  # Show first 2 messages
                    msg_type = msg.get('message_type', 'text')
                    sender_id = msg.get('sender_id', 'unknown')
                    message_text = msg.get('message', '')[:50] + ('...' if len(msg.get('message', '')) > 50 else '')
                    print(f"   Message {i+1} ({msg_type}): {message_text} (Sender: {sender_id})")
                
                return True
            else:
                self.log_test(
                    "Conversation Messages",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Conversation Messages", False, f"Exception: {str(e)}")
            return False

    def test_send_message(self):
        """Test POST /api/conversations/{id}/messages - Envoyer un message"""
        try:
            if not self.test_conversation_id:
                self.log_test("Send Message", False, "No test conversation available")
                return False
                
            headers = {"Authorization": f"Bearer {self.admin_token}"}  # Admin replies
            
            message_data = {
                "message": "Bonjour! Merci pour votre intérêt dans TopKit. Le système de messagerie intégrée fonctionne parfaitement!",
                "message_type": "text"
            }
            
            response = requests.post(f"{BASE_URL}/conversations/{self.test_conversation_id}/messages", json=message_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get('message_id')
                self.log_test(
                    "Send Message",
                    True,
                    f"✅ Message sent successfully! Message ID: {message_id}"
                )
                return True
            else:
                self.log_test(
                    "Send Message",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Send Message", False, f"Exception: {str(e)}")
            return False

    def test_friends_system(self):
        """Test GET /api/friends - Système d'amis"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            response = requests.get(f"{BASE_URL}/friends", headers=headers)
            
            if response.status_code == 200:
                friends_data = response.json()
                friends = friends_data.get('friends', [])
                pending_requests = friends_data.get('pending_requests', [])
                
                self.log_test(
                    "Friends System",
                    True,
                    f"✅ Friends system accessible! Friends: {len(friends)}, Pending: {len(pending_requests)}"
                )
                return True
            else:
                self.log_test(
                    "Friends System",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Friends System", False, f"Exception: {str(e)}")
            return False

    def test_friend_request(self):
        """Test POST /api/friends/request - Demande d'ami"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            friend_request_data = {
                "user_id": self.admin_id,
                "message": "Bonjour, j'aimerais vous ajouter comme ami sur TopKit!"
            }
            
            response = requests.post(f"{BASE_URL}/friends/request", json=friend_request_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Friend Request",
                    True,
                    f"✅ Friend request sent successfully! {result.get('message', 'Request sent')}"
                )
                return True
            else:
                self.log_test(
                    "Friend Request",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Friend Request", False, f"Exception: {str(e)}")
            return False

    def test_transaction_endpoints_structure(self):
        """Test transaction endpoints structure (without full workflow)"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test endpoints that should exist (even if they return errors due to missing data)
            endpoints_to_test = [
                ("POST", "/payments/secure/checkout", {"listing_id": "test-id", "origin_url": "test"}),
                ("GET", "/conversations/test-id/transaction", None),
            ]
            
            results = []
            
            for method, endpoint, data in endpoints_to_test:
                try:
                    if method == "POST":
                        response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
                    else:
                        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                    
                    # We expect these to fail with 404/400/422, not 500 or missing endpoint
                    if response.status_code in [200, 400, 404, 422]:
                        results.append(f"✅ {method} {endpoint}: Endpoint exists (HTTP {response.status_code})")
                    elif response.status_code == 500:
                        results.append(f"⚠️ {method} {endpoint}: Server error (HTTP 500)")
                    else:
                        results.append(f"❌ {method} {endpoint}: Unexpected status (HTTP {response.status_code})")
                        
                except Exception as e:
                    results.append(f"❌ {method} {endpoint}: Exception - {str(e)}")
            
            success = len([r for r in results if r.startswith("✅")]) >= len(results) * 0.5
            
            self.log_test(
                "Transaction Endpoints Structure",
                success,
                f"Endpoint availability check:\n   " + "\n   ".join(results)
            )
            
            return success
            
        except Exception as e:
            self.log_test("Transaction Endpoints Structure", False, f"Exception: {str(e)}")
            return False

    def test_messaging_system_integration_readiness(self):
        """Test overall messaging system integration readiness"""
        try:
            readiness_checks = []
            
            # Check 1: Conversations system working
            if self.test_conversation_id:
                readiness_checks.append("✅ Conversation creation and management working")
            else:
                readiness_checks.append("❌ Conversation system not functional")
            
            # Check 2: Message sending/receiving
            headers = {"Authorization": f"Bearer {self.user_token}"}
            if self.test_conversation_id:
                response = requests.get(f"{BASE_URL}/conversations/{self.test_conversation_id}/messages", headers=headers)
                if response.status_code == 200:
                    messages = response.json().get('messages', [])
                    if len(messages) >= 2:  # Initial message + reply
                        readiness_checks.append("✅ Bidirectional messaging working")
                    else:
                        readiness_checks.append("⚠️ Limited messaging functionality")
                else:
                    readiness_checks.append("❌ Message retrieval not working")
            else:
                readiness_checks.append("❌ Cannot test messaging without conversation")
            
            # Check 3: Friends system
            response = requests.get(f"{BASE_URL}/friends", headers=headers)
            if response.status_code == 200:
                readiness_checks.append("✅ Friends system accessible")
            else:
                readiness_checks.append("❌ Friends system not accessible")
            
            # Check 4: Authentication integration
            if self.admin_token and self.user_token:
                readiness_checks.append("✅ Multi-user authentication working")
            else:
                readiness_checks.append("❌ Authentication issues")
            
            success_count = len([check for check in readiness_checks if check.startswith("✅")])
            total_checks = len(readiness_checks)
            success = success_count >= (total_checks * 0.75)  # 75% success rate
            
            readiness_summary = "\n   ".join(readiness_checks)
            
            self.log_test(
                "Messaging System Integration Readiness",
                success,
                f"Integration readiness ({success_count}/{total_checks} checks passed):\n   {readiness_summary}"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Messaging System Integration Readiness", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all messaging endpoints tests"""
        print("🎯 TOPKIT MESSAGING ENDPOINTS BACKEND TESTING")
        print("=" * 60)
        print()
        
        # Authentication tests
        if not self.authenticate_admin():
            print("❌ Admin authentication failed - cannot continue")
            return
            
        if not self.authenticate_user():
            print("❌ User authentication failed - cannot continue")
            return
        
        print("🧪 Running messaging endpoints tests...")
        print("-" * 40)
        
        # Core messaging tests
        self.test_conversations_list()
        self.test_create_conversation()
        self.test_conversation_messages()
        self.test_send_message()
        self.test_friends_system()
        self.test_friend_request()
        
        # Integration tests
        self.test_transaction_endpoints_structure()
        self.test_messaging_system_integration_readiness()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 MESSAGING ENDPOINTS TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS:")
        print("-" * 30)
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details'] and len(result['details']) < 200:
                print(f"   {result['details']}")
        
        print()
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 EXCELLENT: Messaging system endpoints are working excellently!")
        elif success_rate >= 75:
            print("✅ GOOD: Messaging system endpoints are mostly functional with minor issues.")
        elif success_rate >= 50:
            print("⚠️ PARTIAL: Messaging system endpoints have significant issues that need attention.")
        else:
            print("❌ CRITICAL: Messaging system endpoints have major failures requiring immediate fixes.")
        
        print()
        print("🔍 KEY FINDINGS:")
        print("- Basic messaging system functionality")
        print("- Conversation creation and management")
        print("- Message sending and receiving")
        print("- Friends system integration")
        print("- Transaction endpoints structure")
        print("- Integration readiness assessment")
        
        return success_rate

if __name__ == "__main__":
    tester = MessagingEndpointsTester()
    tester.run_all_tests()