#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Backend API Testing
Tests all backend endpoints for authentication, jerseys, marketplace, collections, and payments
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://ce446aa3-3dc9-46b4-8a26-16c4f295a473.preview.emergentagent.com/api"
TEST_USER_EMAIL = "testuser@topkit.com"
TEST_USER_PASSWORD = "SecurePass123!"
TEST_USER_NAME = "Test User"

class TopKitAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
        self.test_listing_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def test_custom_auth_registration(self):
        """Test custom email/password registration"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"testuser_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Custom Auth Registration", "PASS", f"User registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Custom Auth Registration", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Custom Auth Registration", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Custom Auth Registration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_custom_auth_login(self):
        """Test custom email/password login"""
        try:
            # First register a user for login test
            unique_email = f"logintest_{int(time.time())}@topkit.com"
            
            # Register
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("Custom Auth Login (Setup)", "FAIL", "Could not register test user")
                return False
            
            # Now test login
            login_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.log_test("Custom Auth Login", "PASS", f"Login successful for user: {data['user']['email']}")
                    return True
                else:
                    self.log_test("Custom Auth Login", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Custom Auth Login", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Custom Auth Login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_google_oauth_redirect(self):
        """Test Google OAuth redirect endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/auth/google")
            
            if response.status_code == 200:
                # Should redirect to Google OAuth
                self.log_test("Google OAuth Redirect", "PASS", "Google OAuth redirect endpoint accessible")
                return True
            else:
                self.log_test("Google OAuth Redirect", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Google OAuth Redirect", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_emergent_auth_redirect(self):
        """Test Emergent auth redirect endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/auth/emergent/redirect")
            
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data:
                    self.log_test("Emergent Auth Redirect", "PASS", f"Auth URL: {data['auth_url']}")
                    return True
                else:
                    self.log_test("Emergent Auth Redirect", "FAIL", "Missing auth_url in response")
                    return False
            else:
                self.log_test("Emergent Auth Redirect", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Emergent Auth Redirect", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_create_jersey(self):
        """Test jersey creation"""
        try:
            if not self.auth_token:
                self.log_test("Create Jersey", "FAIL", "No auth token available")
                return False
            
            payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Manchester United home jersey with Bruno Fernandes #8",
                "images": ["https://example.com/jersey1.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_jersey_id = data["id"]
                    self.log_test("Create Jersey", "PASS", f"Jersey created with ID: {self.test_jersey_id}")
                    return True
                else:
                    self.log_test("Create Jersey", "FAIL", "Missing jersey ID in response")
                    return False
            else:
                self.log_test("Create Jersey", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_jerseys(self):
        """Test jersey retrieval with filters"""
        try:
            # Test basic get all jerseys
            response = self.session.get(f"{self.base_url}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                self.log_test("Get All Jerseys", "PASS", f"Retrieved {len(jerseys)} jerseys")
                
                # Test with filters
                filter_params = {
                    "team": "Manchester",
                    "season": "2023-24",
                    "size": "L",
                    "condition": "excellent",
                    "league": "Premier"
                }
                
                filter_response = self.session.get(f"{self.base_url}/jerseys", params=filter_params)
                
                if filter_response.status_code == 200:
                    filtered_jerseys = filter_response.json()
                    self.log_test("Get Jerseys with Filters", "PASS", f"Retrieved {len(filtered_jerseys)} filtered jerseys")
                    return True
                else:
                    self.log_test("Get Jerseys with Filters", "FAIL", f"Filter status: {filter_response.status_code}")
                    return False
            else:
                self.log_test("Get All Jerseys", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_specific_jersey(self):
        """Test getting a specific jersey by ID"""
        try:
            if not self.test_jersey_id:
                self.log_test("Get Specific Jersey", "FAIL", "No test jersey ID available")
                return False
            
            response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}")
            
            if response.status_code == 200:
                jersey = response.json()
                if jersey.get("id") == self.test_jersey_id:
                    self.log_test("Get Specific Jersey", "PASS", f"Retrieved jersey: {jersey.get('team')} {jersey.get('season')}")
                    return True
                else:
                    self.log_test("Get Specific Jersey", "FAIL", "Jersey ID mismatch")
                    return False
            else:
                self.log_test("Get Specific Jersey", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specific Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_create_listing(self):
        """Test marketplace listing creation"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Create Listing", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "jersey_id": self.test_jersey_id,
                "price": 89.99,
                "description": "Excellent condition Manchester United jersey, worn only once",
                "images": ["https://example.com/listing1.jpg", "https://example.com/listing2.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_listing_id = data["id"]
                    self.log_test("Create Listing", "PASS", f"Listing created with ID: {self.test_listing_id}")
                    return True
                else:
                    self.log_test("Create Listing", "FAIL", "Missing listing ID in response")
                    return False
            else:
                self.log_test("Create Listing", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Create Listing", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_listings(self):
        """Test marketplace listings retrieval with filters"""
        try:
            # Test basic get all listings
            response = self.session.get(f"{self.base_url}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                self.log_test("Get All Listings", "PASS", f"Retrieved {len(listings)} listings")
                
                # Test with filters
                filter_params = {
                    "team": "Manchester",
                    "season": "2023-24",
                    "min_price": 50.0,
                    "max_price": 150.0,
                    "condition": "excellent",
                    "size": "L"
                }
                
                filter_response = self.session.get(f"{self.base_url}/listings", params=filter_params)
                
                if filter_response.status_code == 200:
                    filtered_listings = filter_response.json()
                    self.log_test("Get Listings with Filters", "PASS", f"Retrieved {len(filtered_listings)} filtered listings")
                    return True
                else:
                    self.log_test("Get Listings with Filters", "FAIL", f"Filter status: {filter_response.status_code}")
                    return False
            else:
                self.log_test("Get All Listings", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Listings", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_specific_listing(self):
        """Test getting a specific listing with jersey and seller details"""
        try:
            if not self.test_listing_id:
                self.log_test("Get Specific Listing", "FAIL", "No test listing ID available")
                return False
            
            response = self.session.get(f"{self.base_url}/listings/{self.test_listing_id}")
            
            if response.status_code == 200:
                listing = response.json()
                if listing.get("id") == self.test_listing_id and "jersey" in listing and "seller" in listing:
                    self.log_test("Get Specific Listing", "PASS", f"Retrieved listing with jersey and seller details")
                    return True
                else:
                    self.log_test("Get Specific Listing", "FAIL", "Missing listing details or aggregated data")
                    return False
            else:
                self.log_test("Get Specific Listing", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get Specific Listing", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_add_to_collection(self):
        """Test adding jersey to user collection"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Add to Collection", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Test adding to "owned" collection
            payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                self.log_test("Add to Owned Collection", "PASS", "Jersey added to owned collection")
                
                # Test adding to "wanted" collection
                payload["collection_type"] = "wanted"
                wanted_response = self.session.post(f"{self.base_url}/collections", json=payload)
                
                if wanted_response.status_code == 200:
                    self.log_test("Add to Wanted Collection", "PASS", "Jersey added to wanted collection")
                    
                    # Test duplicate prevention
                    duplicate_response = self.session.post(f"{self.base_url}/collections", json=payload)
                    if duplicate_response.status_code == 400:
                        self.log_test("Duplicate Prevention", "PASS", "Duplicate collection entry prevented")
                        return True
                    else:
                        self.log_test("Duplicate Prevention", "FAIL", "Duplicate not prevented")
                        return False
                else:
                    self.log_test("Add to Wanted Collection", "FAIL", f"Status: {wanted_response.status_code}")
                    return False
            else:
                self.log_test("Add to Owned Collection", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add to Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_get_user_collections(self):
        """Test retrieving user collections"""
        try:
            if not self.auth_token:
                self.log_test("Get User Collections", "FAIL", "No auth token available")
                return False
            
            # Test getting owned collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code == 200:
                owned_collection = owned_response.json()
                self.log_test("Get Owned Collection", "PASS", f"Retrieved {len(owned_collection)} owned jerseys")
                
                # Test getting wanted collection
                wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
                
                if wanted_response.status_code == 200:
                    wanted_collection = wanted_response.json()
                    self.log_test("Get Wanted Collection", "PASS", f"Retrieved {len(wanted_collection)} wanted jerseys")
                    return True
                else:
                    self.log_test("Get Wanted Collection", "FAIL", f"Status: {wanted_response.status_code}")
                    return False
            else:
                self.log_test("Get Owned Collection", "FAIL", f"Status: {owned_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Get User Collections", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_profile(self):
        """Test user profile endpoint with stats"""
        try:
            if not self.auth_token:
                self.log_test("User Profile", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                if "user" in profile and "stats" in profile:
                    user_data = profile["user"]
                    stats_data = profile["stats"]
                    
                    required_user_fields = ["id", "email", "name", "provider", "created_at"]
                    required_stats_fields = ["owned_jerseys", "wanted_jerseys", "active_listings"]
                    
                    user_valid = all(field in user_data for field in required_user_fields)
                    stats_valid = all(field in stats_data for field in required_stats_fields)
                    
                    if user_valid and stats_valid:
                        self.log_test("User Profile", "PASS", f"Profile retrieved with stats: {stats_data}")
                        return True
                    else:
                        self.log_test("User Profile", "FAIL", "Missing required fields in profile or stats")
                        return False
                else:
                    self.log_test("User Profile", "FAIL", "Missing user or stats in response")
                    return False
            else:
                self.log_test("User Profile", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Profile", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_payment_checkout(self):
        """Test payment checkout endpoint"""
        try:
            if not self.auth_token or not self.test_listing_id:
                self.log_test("Payment Checkout", "FAIL", "Missing auth token or listing ID")
                return False
            
            payload = {
                "listing_id": self.test_listing_id,
                "origin_url": "https://topkit.com"
            }
            
            response = self.session.post(f"{self.base_url}/payments/checkout", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "checkout_url" in data and "session_id" in data:
                    self.log_test("Payment Checkout", "PASS", f"Checkout session created: {data['session_id']}")
                    return True
                else:
                    self.log_test("Payment Checkout", "FAIL", "Missing checkout_url or session_id")
                    return False
            else:
                self.log_test("Payment Checkout", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Payment Checkout", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jwt_token_validation(self):
        """Test JWT token validation for protected endpoints"""
        try:
            # Test with invalid token
            invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
            response = self.session.get(f"{self.base_url}/profile", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("JWT Token Validation (Invalid)", "PASS", "Invalid token correctly rejected")
                
                # Test with no token
                no_token_response = self.session.get(f"{self.base_url}/profile")
                
                if no_token_response.status_code == 403 or no_token_response.status_code == 401:
                    self.log_test("JWT Token Validation (Missing)", "PASS", "Missing token correctly rejected")
                    return True
                else:
                    self.log_test("JWT Token Validation (Missing)", "FAIL", f"Expected 401/403, got {no_token_response.status_code}")
                    return False
            else:
                self.log_test("JWT Token Validation (Invalid)", "FAIL", f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Validation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting TopKit Backend API Tests")
        print("=" * 50)
        
        test_results = {}
        
        # Authentication Tests (High Priority)
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        test_results['auth_register'] = self.test_custom_auth_registration()
        test_results['auth_login'] = self.test_custom_auth_login()
        test_results['google_oauth'] = self.test_google_oauth_redirect()
        test_results['emergent_auth'] = self.test_emergent_auth_redirect()
        test_results['jwt_validation'] = self.test_jwt_token_validation()
        
        # Jersey Database Tests (High Priority)
        print("⚽ JERSEY DATABASE TESTS")
        print("-" * 30)
        test_results['create_jersey'] = self.test_create_jersey()
        test_results['get_jerseys'] = self.test_get_jerseys()
        test_results['get_specific_jersey'] = self.test_get_specific_jersey()
        
        # Marketplace Tests (High Priority)
        print("🏪 MARKETPLACE TESTS")
        print("-" * 30)
        test_results['create_listing'] = self.test_create_listing()
        test_results['get_listings'] = self.test_get_listings()
        test_results['get_specific_listing'] = self.test_get_specific_listing()
        
        # Collections Tests (Medium Priority)
        print("📚 COLLECTIONS TESTS")
        print("-" * 30)
        test_results['add_to_collection'] = self.test_add_to_collection()
        test_results['get_collections'] = self.test_get_user_collections()
        
        # Profile Tests (Medium Priority)
        print("👤 PROFILE TESTS")
        print("-" * 30)
        test_results['user_profile'] = self.test_user_profile()
        
        # Payment Tests (Medium Priority)
        print("💳 PAYMENT TESTS")
        print("-" * 30)
        test_results['payment_checkout'] = self.test_payment_checkout()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        return test_results

if __name__ == "__main__":
    tester = TopKitAPITester()
    results = tester.run_all_tests()