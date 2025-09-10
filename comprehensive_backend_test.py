#!/usr/bin/env python3
"""
TopKit Comprehensive Backend Verification - Discogs Workflow & Security Assessment
Testing all critical backend functionality before Security Level 2 implementation
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials from review request
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "TopKit123!"

class TopKitTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = {
            "discogs_workflow": [],
            "authentication": [],
            "private_beta": [],
            "admin_moderation": [],
            "core_apis": [],
            "messaging": [],
            "marketplace": []
        }
        self.total_tests = 0
        self.passed_tests = 0
        
    def log_test(self, category, test_name, success, details=""):
        """Log test result"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results[category].append(result)
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, token=None, expected_status=None):
        """Make HTTP request with error handling"""
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return None, f"Unsupported method: {method}"
                
            if expected_status and response.status_code != expected_status:
                return None, f"Expected status {expected_status}, got {response.status_code}: {response.text}"
                
            return response, None
            
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
    
    def test_authentication_system(self):
        """Test authentication system stability"""
        print("\n🔐 TESTING AUTHENTICATION SYSTEM")
        
        # Test admin login
        response, error = self.make_request("POST", "/auth/login", {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if error or not response or response.status_code != 200:
            self.log_test("authentication", "Admin Login", False, 
                         error or f"Status: {response.status_code if response else 'No response'}")
            return False
        
        try:
            admin_data = response.json()
            self.admin_token = admin_data.get("token")
            admin_user = admin_data.get("user", {})
            self.admin_user_id = admin_user.get("id")
            
            if not self.admin_token:
                self.log_test("authentication", "Admin Login", False, "No token received")
                return False
                
            self.log_test("authentication", "Admin Login", True, 
                         f"Admin: {admin_user.get('name')}, Role: {admin_user.get('role')}")
        except Exception as e:
            self.log_test("authentication", "Admin Login", False, f"JSON parse error: {e}")
            return False
        
        # Test user login
        response, error = self.make_request("POST", "/auth/login", {
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        })
        
        if error or not response or response.status_code != 200:
            self.log_test("authentication", "User Login", False, 
                         error or f"Status: {response.status_code if response else 'No response'}")
        else:
            try:
                user_data = response.json()
                self.user_token = user_data.get("token")
                user_user = user_data.get("user", {})
                self.user_user_id = user_user.get("id")
                
                if self.user_token:
                    self.log_test("authentication", "User Login", True, 
                                 f"User: {user_user.get('name')}, Role: {user_user.get('role')}")
                else:
                    self.log_test("authentication", "User Login", False, "No token received")
            except Exception as e:
                self.log_test("authentication", "User Login", False, f"JSON parse error: {e}")
        
        # Test JWT token validation
        if self.admin_token:
            response, error = self.make_request("GET", "/profile", token=self.admin_token)
            success = not error and response and response.status_code == 200
            self.log_test("authentication", "JWT Token Validation", success, 
                         error or "Token validation successful")
        
        return self.admin_token is not None
    
    def test_discogs_workflow(self):
        """Test complete Discogs-style workflow"""
        print("\n🎯 TESTING DISCOGS-STYLE WORKFLOW")
        
        if not self.user_token:
            self.log_test("discogs_workflow", "Workflow Prerequisites", False, "User authentication required")
            return
        
        # Step 1: Jersey submission (without size/condition)
        jersey_data = {
            "team": "Real Madrid CF",
            "season": "2024-25",
            "player": "Vinicius Jr",
            "manufacturer": "Adidas",
            "home_away": "home",
            "league": "La Liga",
            "description": "Official Real Madrid home jersey 2024-25 season"
        }
        
        response, error = self.make_request("POST", "/jerseys", jersey_data, self.user_token)
        
        if error or not response or response.status_code != 200:
            self.log_test("discogs_workflow", "Jersey Submission", False, 
                         error or f"Status: {response.status_code}")
            return
        
        try:
            jersey_response = response.json()
            jersey_id = jersey_response.get("id")
            if not jersey_id:
                self.log_test("discogs_workflow", "Jersey Submission", False, "No jersey ID returned")
                return
            
            self.log_test("discogs_workflow", "Jersey Submission", True, 
                         f"Jersey ID: {jersey_id}, Status: {jersey_response.get('status')}")
        except Exception as e:
            self.log_test("discogs_workflow", "Jersey Submission", False, f"JSON parse error: {e}")
            return
        
        # Step 2: Admin approval
        if not self.admin_token:
            self.log_test("discogs_workflow", "Admin Approval", False, "Admin authentication required")
            return
        
        response, error = self.make_request("POST", f"/admin/jerseys/{jersey_id}/approve", 
                                          {}, self.admin_token)
        
        success = not error and response and response.status_code == 200
        self.log_test("discogs_workflow", "Admin Approval", success, 
                     error or "Jersey approved successfully")
        
        if not success:
            return
        
        # Step 3: Verify approved jerseys endpoint
        response, error = self.make_request("GET", "/jerseys/approved")
        
        if error or not response or response.status_code != 200:
            self.log_test("discogs_workflow", "Approved Jerseys Endpoint", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                approved_jerseys = response.json()
                found_jersey = any(j.get("id") == jersey_id for j in approved_jerseys)
                self.log_test("discogs_workflow", "Approved Jerseys Endpoint", found_jersey, 
                             f"Found {len(approved_jerseys)} approved jerseys, our jersey included: {found_jersey}")
            except Exception as e:
                self.log_test("discogs_workflow", "Approved Jerseys Endpoint", False, f"JSON parse error: {e}")
        
        # Step 4: Add to collection with size/condition
        collection_data = {
            "jersey_id": jersey_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "new",
            "personal_description": "Purchased from official store"
        }
        
        response, error = self.make_request("POST", "/collections", collection_data, self.user_token)
        
        if error or not response or response.status_code != 200:
            self.log_test("discogs_workflow", "Collection Addition", False, 
                         error or f"Status: {response.status_code}")
            return
        
        try:
            collection_response = response.json()
            collection_id = collection_response.get("id") or collection_response.get("collection_id")
            if not collection_id:
                self.log_test("discogs_workflow", "Collection Addition", False, 
                             f"No collection ID returned. Response: {collection_response}")
                return
            
            self.log_test("discogs_workflow", "Collection Addition", True, 
                         f"Collection ID: {collection_id}")
        except Exception as e:
            self.log_test("discogs_workflow", "Collection Addition", False, f"JSON parse error: {e}")
            return
        
        # Step 5: Verify my-owned collection endpoint
        response, error = self.make_request("GET", "/collections/my-owned", token=self.user_token)
        
        if error or not response or response.status_code != 200:
            self.log_test("discogs_workflow", "My Owned Collection", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                owned_items = response.json()
                found_item = any(item.get("id") == collection_id for item in owned_items)
                self.log_test("discogs_workflow", "My Owned Collection", found_item, 
                             f"Found {len(owned_items)} owned items, our item included: {found_item}")
            except Exception as e:
                self.log_test("discogs_workflow", "My Owned Collection", False, f"JSON parse error: {e}")
        
        # Step 6: Create listing from collection
        listing_data = {
            "collection_id": collection_id,
            "price": 89.99,
            "marketplace_description": "Excellent condition Real Madrid jersey, worn only once"
        }
        
        response, error = self.make_request("POST", "/listings", listing_data, self.user_token)
        
        success = not error and response and response.status_code == 200
        if success:
            try:
                listing_response = response.json()
                listing_id = listing_response.get("id")
                self.log_test("discogs_workflow", "Listing Creation", True, 
                             f"Listing ID: {listing_id}, Price: €{listing_response.get('price')}")
            except Exception as e:
                self.log_test("discogs_workflow", "Listing Creation", False, f"JSON parse error: {e}")
        else:
            self.log_test("discogs_workflow", "Listing Creation", False, 
                         error or f"Status: {response.status_code}")
    
    def test_private_beta_mode(self):
        """Test private beta mode functionality"""
        print("\n🔒 TESTING PRIVATE BETA MODE")
        
        # Test site mode endpoint
        response, error = self.make_request("GET", "/site/mode")
        
        if error or not response or response.status_code != 200:
            self.log_test("private_beta", "Site Mode Check", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                mode_data = response.json()
                current_mode = mode_data.get("mode")
                self.log_test("private_beta", "Site Mode Check", True, 
                             f"Current mode: {current_mode}")
            except Exception as e:
                self.log_test("private_beta", "Site Mode Check", False, f"JSON parse error: {e}")
        
        # Test access control
        response, error = self.make_request("GET", "/site/access-check", token=self.user_token)
        
        success = not error and response and response.status_code in [200, 403]
        self.log_test("private_beta", "Access Control", success, 
                     error or f"Access check returned status {response.status_code}")
        
        # Test beta request submission
        beta_request = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "message": "I would like to join the TopKit beta"
        }
        
        response, error = self.make_request("POST", "/beta/request-access", beta_request)
        
        success = not error and response and response.status_code == 200
        self.log_test("private_beta", "Beta Request Submission", success, 
                     error or "Beta request submitted successfully")
        
        # Test admin beta request management (if admin authenticated)
        if self.admin_token:
            response, error = self.make_request("GET", "/admin/beta/requests", token=self.admin_token)
            
            success = not error and response and response.status_code == 200
            if success:
                try:
                    requests_data = response.json()
                    self.log_test("private_beta", "Admin Beta Requests", True, 
                                 f"Found {len(requests_data)} beta requests")
                except Exception as e:
                    self.log_test("private_beta", "Admin Beta Requests", False, f"JSON parse error: {e}")
            else:
                self.log_test("private_beta", "Admin Beta Requests", False, 
                             error or f"Status: {response.status_code}")
    
    def test_admin_moderation(self):
        """Test admin moderation and notification systems"""
        print("\n👨‍💼 TESTING ADMIN MODERATION")
        
        if not self.admin_token:
            self.log_test("admin_moderation", "Admin Prerequisites", False, "Admin authentication required")
            return
        
        # Test pending jerseys retrieval
        response, error = self.make_request("GET", "/admin/jerseys/pending", token=self.admin_token)
        
        if error or not response or response.status_code != 200:
            self.log_test("admin_moderation", "Pending Jerseys", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                pending_jerseys = response.json()
                self.log_test("admin_moderation", "Pending Jerseys", True, 
                             f"Found {len(pending_jerseys)} pending jerseys")
            except Exception as e:
                self.log_test("admin_moderation", "Pending Jerseys", False, f"JSON parse error: {e}")
        
        # Test admin analytics
        response, error = self.make_request("GET", "/admin/traffic-stats", token=self.admin_token)
        
        success = not error and response and response.status_code == 200
        if success:
            try:
                stats = response.json()
                self.log_test("admin_moderation", "Admin Analytics", True, 
                             f"Users: {stats.get('total_users', 0)}, Jerseys: {stats.get('total_jerseys', 0)}")
            except Exception as e:
                self.log_test("admin_moderation", "Admin Analytics", False, f"JSON parse error: {e}")
        else:
            self.log_test("admin_moderation", "Admin Analytics", False, 
                         error or f"Status: {response.status_code}")
        
        # Test notification system (if user authenticated)
        if self.user_token:
            response, error = self.make_request("GET", "/notifications", token=self.user_token)
            
            success = not error and response and response.status_code == 200
            if success:
                try:
                    notifications = response.json()
                    self.log_test("admin_moderation", "Notification System", True, 
                                 f"Found {len(notifications)} notifications")
                except Exception as e:
                    self.log_test("admin_moderation", "Notification System", False, f"JSON parse error: {e}")
            else:
                self.log_test("admin_moderation", "Notification System", False, 
                             error or f"Status: {response.status_code}")
    
    def test_core_apis(self):
        """Test core API stability"""
        print("\n🔧 TESTING CORE API STABILITY")
        
        # Test jerseys endpoint
        response, error = self.make_request("GET", "/jerseys")
        
        if error or not response or response.status_code != 200:
            self.log_test("core_apis", "Jerseys API", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                jerseys = response.json()
                self.log_test("core_apis", "Jerseys API", True, 
                             f"Found {len(jerseys)} jerseys")
            except Exception as e:
                self.log_test("core_apis", "Jerseys API", False, f"JSON parse error: {e}")
        
        # Test marketplace catalog
        response, error = self.make_request("GET", "/marketplace/catalog")
        
        success = not error and response and response.status_code == 200
        if success:
            try:
                catalog = response.json()
                self.log_test("core_apis", "Marketplace Catalog", True, 
                             f"Found {len(catalog)} catalog items")
            except Exception as e:
                self.log_test("core_apis", "Marketplace Catalog", False, f"JSON parse error: {e}")
        else:
            self.log_test("core_apis", "Marketplace Catalog", False, 
                         error or f"Status: {response.status_code}")
        
        # Test user search (if user authenticated)
        if self.user_token:
            response, error = self.make_request("GET", "/users/search?q=test", token=self.user_token)
            
            success = not error and response and response.status_code == 200
            if success:
                try:
                    search_results = response.json()
                    self.log_test("core_apis", "User Search", True, 
                                 f"User search returned {len(search_results)} results")
                except Exception as e:
                    self.log_test("core_apis", "User Search", False, f"JSON parse error: {e}")
            else:
                self.log_test("core_apis", "User Search", False, 
                             error or f"Status: {response.status_code}")
    
    def test_messaging_system(self):
        """Test messaging system endpoints"""
        print("\n💬 TESTING MESSAGING SYSTEM")
        
        if not self.user_token:
            self.log_test("messaging", "Messaging Prerequisites", False, "User authentication required")
            return
        
        # Test conversations endpoint
        response, error = self.make_request("GET", "/conversations", token=self.user_token)
        
        success = not error and response and response.status_code == 200
        if success:
            try:
                conversations = response.json()
                self.log_test("messaging", "Conversations API", True, 
                             f"Found {len(conversations)} conversations")
            except Exception as e:
                self.log_test("messaging", "Conversations API", False, f"JSON parse error: {e}")
        else:
            self.log_test("messaging", "Conversations API", False, 
                         error or f"Status: {response.status_code}")
        
        # Test friends system
        response, error = self.make_request("GET", "/friends", token=self.user_token)
        
        success = not error and response and response.status_code == 200
        self.log_test("messaging", "Friends System", success, 
                     error or "Friends system functional")
    
    def test_marketplace_apis(self):
        """Test marketplace and collection APIs"""
        print("\n🛒 TESTING MARKETPLACE APIS")
        
        # Test listings endpoint
        response, error = self.make_request("GET", "/listings")
        
        if error or not response or response.status_code != 200:
            self.log_test("marketplace", "Listings API", False, 
                         error or f"Status: {response.status_code}")
        else:
            try:
                listings = response.json()
                self.log_test("marketplace", "Listings API", True, 
                             f"Found {len(listings)} active listings")
            except Exception as e:
                self.log_test("marketplace", "Listings API", False, f"JSON parse error: {e}")
        
        # Test user collections (if user authenticated)
        if self.user_token and self.user_user_id:
            response, error = self.make_request("GET", f"/users/{self.user_user_id}/collections", 
                                              token=self.user_token)
            
            success = not error and response and response.status_code == 200
            if success:
                try:
                    collections = response.json()
                    self.log_test("marketplace", "User Collections", True, 
                                 f"User has {len(collections)} collection items")
                except Exception as e:
                    self.log_test("marketplace", "User Collections", False, f"JSON parse error: {e}")
            else:
                self.log_test("marketplace", "User Collections", False, 
                             error or f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 STARTING TOPKIT COMPREHENSIVE BACKEND VERIFICATION")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test suites
        auth_success = self.test_authentication_system()
        
        if auth_success:
            self.test_discogs_workflow()
            self.test_private_beta_mode()
            self.test_admin_moderation()
            self.test_core_apis()
            self.test_messaging_system()
            self.test_marketplace_apis()
        else:
            print("\n❌ Authentication failed - skipping dependent tests")
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TESTING RESULTS SUMMARY")
        print("=" * 60)
        
        for category, results in self.test_results.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                rate = (passed / total * 100) if total > 0 else 0
                print(f"{category.upper().replace('_', ' ')}: {passed}/{total} ({rate:.1f}%)")
        
        print(f"\nOVERALL SUCCESS RATE: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        print(f"TEST DURATION: {duration:.2f} seconds")
        
        # Identify critical issues
        critical_failures = []
        for category, results in self.test_results.items():
            for result in results:
                if not result["success"] and category in ["authentication", "discogs_workflow"]:
                    critical_failures.append(f"{category}: {result['test']}")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   - {failure}")
        
        # Determine readiness for Security Level 2
        if success_rate >= 90 and not critical_failures:
            print(f"\n✅ SYSTEM READY FOR SECURITY LEVEL 2 IMPLEMENTATION")
        elif success_rate >= 80:
            print(f"\n⚠️  SYSTEM MOSTLY READY - MINOR ISSUES TO ADDRESS")
        else:
            print(f"\n❌ SYSTEM NOT READY - CRITICAL ISSUES MUST BE RESOLVED")
        
        return success_rate, critical_failures

if __name__ == "__main__":
    tester = TopKitTester()
    success_rate, critical_issues = tester.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 90 and not critical_issues:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Issues found