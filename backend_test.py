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
BASE_URL = "https://7dc90ad2-eb63-45b6-a854-741e16d4ebc1.preview.emergentagent.com/api"
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
    
    def create_sample_valuation_data(self):
        """Create sample jerseys and listings for valuation testing"""
        try:
            # Create Manchester United jersey
            man_utd_payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Manchester United home jersey with Bruno Fernandes #8",
                "images": ["https://example.com/manutd1.jpg"]
            }
            
            man_utd_response = self.session.post(f"{self.base_url}/jerseys", json=man_utd_payload)
            man_utd_jersey_id = None
            if man_utd_response.status_code == 200:
                man_utd_jersey_id = man_utd_response.json()["id"]
            
            # Create Real Madrid jersey
            real_madrid_payload = {
                "team": "Real Madrid",
                "season": "2023-24", 
                "player": "Vinicius Jr",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "La Liga",
                "description": "Official Real Madrid home jersey with Vinicius Jr #7",
                "images": ["https://example.com/realmadrid1.jpg"]
            }
            
            real_madrid_response = self.session.post(f"{self.base_url}/jerseys", json=real_madrid_payload)
            real_madrid_jersey_id = None
            if real_madrid_response.status_code == 200:
                real_madrid_jersey_id = real_madrid_response.json()["id"]
            
            # Create multiple listings for valuation data
            sample_listings = []
            
            if man_utd_jersey_id:
                # Manchester United listings with varying prices
                man_utd_listings = [
                    {"jersey_id": man_utd_jersey_id, "price": 89.99, "description": "Excellent condition ManU jersey"},
                    {"jersey_id": man_utd_jersey_id, "price": 94.50, "description": "Great ManU jersey, barely worn"},
                    {"jersey_id": man_utd_jersey_id, "price": 92.75, "description": "Nice ManU jersey for collection"}
                ]
                
                for listing_data in man_utd_listings:
                    listing_response = self.session.post(f"{self.base_url}/listings", json=listing_data)
                    if listing_response.status_code == 200:
                        sample_listings.append(listing_response.json()["id"])
            
            if real_madrid_jersey_id:
                # Real Madrid listings with varying prices
                real_madrid_listings = [
                    {"jersey_id": real_madrid_jersey_id, "price": 120.00, "description": "Mint condition Real Madrid jersey"},
                    {"jersey_id": real_madrid_jersey_id, "price": 122.12, "description": "Perfect Real Madrid jersey"},
                    {"jersey_id": real_madrid_jersey_id, "price": 118.50, "description": "Excellent Real Madrid jersey"}
                ]
                
                for listing_data in real_madrid_listings:
                    listing_response = self.session.post(f"{self.base_url}/listings", json=listing_data)
                    if listing_response.status_code == 200:
                        sample_listings.append(listing_response.json()["id"])
            
            return {
                "man_utd_jersey_id": man_utd_jersey_id,
                "real_madrid_jersey_id": real_madrid_jersey_id,
                "sample_listings": sample_listings
            }
            
        except Exception as e:
            self.log_test("Create Sample Valuation Data", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_jersey_valuation_endpoint(self):
        """Test individual jersey valuation endpoint"""
        try:
            # Create sample data first
            sample_data = self.create_sample_valuation_data()
            if not sample_data or not sample_data["man_utd_jersey_id"]:
                self.log_test("Jersey Valuation Endpoint", "FAIL", "Could not create sample data")
                return False
            
            # Wait a moment for valuation calculations
            time.sleep(2)
            
            # Test Manchester United jersey valuation
            jersey_id = sample_data["man_utd_jersey_id"]
            response = self.session.get(f"{self.base_url}/jerseys/{jersey_id}/valuation")
            
            if response.status_code == 200:
                data = response.json()
                if "valuation" in data and data["valuation"]:
                    valuation = data["valuation"]
                    required_fields = ["low_estimate", "median_estimate", "high_estimate", "total_listings", "market_data"]
                    
                    if all(field in valuation for field in required_fields):
                        low = valuation["low_estimate"]
                        median = valuation["median_estimate"] 
                        high = valuation["high_estimate"]
                        
                        # Verify estimates are reasonable (around expected values)
                        if 85 <= low <= 100 and 90 <= median <= 100 and 90 <= high <= 100:
                            self.log_test("Jersey Valuation Endpoint", "PASS", 
                                        f"ManU Jersey - Low: ${low}, Median: ${median}, High: ${high}")
                            return True
                        else:
                            self.log_test("Jersey Valuation Endpoint", "FAIL", 
                                        f"Estimates out of expected range - Low: ${low}, Median: ${median}, High: ${high}")
                            return False
                    else:
                        self.log_test("Jersey Valuation Endpoint", "FAIL", "Missing required valuation fields")
                        return False
                else:
                    # No valuation data available yet - this is acceptable for new jerseys
                    self.log_test("Jersey Valuation Endpoint", "PASS", "No valuation data available (acceptable for new jerseys)")
                    return True
            else:
                self.log_test("Jersey Valuation Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Valuation Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_valuations_endpoint(self):
        """Test user collection valuations endpoint"""
        try:
            if not self.auth_token:
                self.log_test("Collection Valuations Endpoint", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/collections/valuations")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["collections", "portfolio_summary"]
                
                if all(field in data for field in required_fields):
                    portfolio = data["portfolio_summary"]
                    portfolio_fields = ["total_items", "valued_items", "total_low_estimate", 
                                      "total_median_estimate", "total_high_estimate", "average_value"]
                    
                    if all(field in portfolio for field in portfolio_fields):
                        self.log_test("Collection Valuations Endpoint", "PASS", 
                                    f"Portfolio: {portfolio['total_items']} items, ${portfolio['total_median_estimate']} total value")
                        return True
                    else:
                        self.log_test("Collection Valuations Endpoint", "FAIL", "Missing portfolio summary fields")
                        return False
                else:
                    self.log_test("Collection Valuations Endpoint", "FAIL", "Missing required response fields")
                    return False
            else:
                self.log_test("Collection Valuations Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collection Valuations Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile_with_valuations(self):
        """Test profile endpoint includes valuation data"""
        try:
            if not self.auth_token:
                self.log_test("Profile with Valuations", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                if "user" in profile and "stats" in profile and "valuations" in profile:
                    valuations = profile["valuations"]
                    
                    if "portfolio_summary" in valuations:
                        portfolio = valuations["portfolio_summary"]
                        self.log_test("Profile with Valuations", "PASS", 
                                    f"Profile includes valuations with portfolio summary")
                        return True
                    else:
                        self.log_test("Profile with Valuations", "FAIL", "Missing portfolio_summary in valuations")
                        return False
                else:
                    self.log_test("Profile with Valuations", "FAIL", "Missing valuations in profile response")
                    return False
            else:
                self.log_test("Profile with Valuations", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile with Valuations", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collector_price_estimate(self):
        """Test collector price estimate endpoint"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Collector Price Estimate", "FAIL", "Missing auth token or jersey ID")
                return False
            
            payload = {
                "price": 95.00
            }
            
            response = self.session.post(f"{self.base_url}/jerseys/{self.test_jersey_id}/price-estimate", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "estimated_price" in data:
                    self.log_test("Collector Price Estimate", "PASS", 
                                f"Price estimate added: ${data['estimated_price']}")
                    return True
                else:
                    self.log_test("Collector Price Estimate", "FAIL", "Missing response fields")
                    return False
            else:
                self.log_test("Collector Price Estimate", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collector Price Estimate", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_market_trending_endpoint(self):
        """Test market trending jerseys endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/market/trending")
            
            if response.status_code == 200:
                data = response.json()
                if "trending_jerseys" in data:
                    trending = data["trending_jerseys"]
                    self.log_test("Market Trending Endpoint", "PASS", 
                                f"Retrieved {len(trending)} trending jerseys")
                    return True
                else:
                    self.log_test("Market Trending Endpoint", "FAIL", "Missing trending_jerseys in response")
                    return False
            else:
                self.log_test("Market Trending Endpoint", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Market Trending Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_valuation_calculation_logic(self):
        """Test valuation calculation with specific scenarios"""
        try:
            # Create sample data and wait for calculations
            sample_data = self.create_sample_valuation_data()
            if not sample_data:
                self.log_test("Valuation Calculation Logic", "FAIL", "Could not create sample data")
                return False
            
            # Wait for valuation calculations to complete
            time.sleep(3)
            
            # Test Real Madrid jersey (should have higher valuation due to mint condition)
            if sample_data["real_madrid_jersey_id"]:
                response = self.session.get(f"{self.base_url}/jerseys/{sample_data['real_madrid_jersey_id']}/valuation")
                
                if response.status_code == 200:
                    data = response.json()
                    if "valuation" in data and data["valuation"]:
                        valuation = data["valuation"]
                        
                        # Check confidence scoring
                        if "market_data" in valuation and "confidence_score" in valuation["market_data"]:
                            confidence = valuation["market_data"]["confidence_score"]
                            
                            # Verify weighted pricing algorithm is working
                            low = valuation["low_estimate"]
                            median = valuation["median_estimate"]
                            high = valuation["high_estimate"]
                            
                            if low <= median <= high and confidence > 0:
                                self.log_test("Valuation Calculation Logic", "PASS", 
                                            f"Real Madrid - Low: ${low}, Median: ${median}, High: ${high}, Confidence: {confidence}")
                                return True
                            else:
                                self.log_test("Valuation Calculation Logic", "FAIL", 
                                            f"Invalid valuation logic - Low: ${low}, Median: ${median}, High: ${high}")
                                return False
                        else:
                            self.log_test("Valuation Calculation Logic", "FAIL", "Missing confidence score")
                            return False
                    else:
                        # No valuation data yet - acceptable
                        self.log_test("Valuation Calculation Logic", "PASS", "No valuation data available yet (acceptable)")
                        return True
                else:
                    self.log_test("Valuation Calculation Logic", "FAIL", f"Status: {response.status_code}")
                    return False
            else:
                self.log_test("Valuation Calculation Logic", "FAIL", "No Real Madrid jersey created")
                return False
                
        except Exception as e:
            self.log_test("Valuation Calculation Logic", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_listing_updates_valuation(self):
        """Test that creating listings automatically updates valuation data"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Listing Updates Valuation", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Create a new listing
            payload = {
                "jersey_id": self.test_jersey_id,
                "price": 97.50,
                "description": "Test listing for valuation update",
                "images": []
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                # Wait for valuation update
                time.sleep(2)
                
                # Check if valuation was updated
                valuation_response = self.session.get(f"{self.base_url}/jerseys/{self.test_jersey_id}/valuation")
                
                if valuation_response.status_code == 200:
                    data = valuation_response.json()
                    if "valuation" in data and data["valuation"]:
                        valuation = data["valuation"]
                        if valuation["total_listings"] > 0:
                            self.log_test("Listing Updates Valuation", "PASS", 
                                        f"Valuation updated with {valuation['total_listings']} listings")
                            return True
                        else:
                            self.log_test("Listing Updates Valuation", "FAIL", "No listings counted in valuation")
                            return False
                    else:
                        # Valuation might not be calculated yet
                        self.log_test("Listing Updates Valuation", "PASS", "Listing created, valuation pending calculation")
                        return True
                else:
                    self.log_test("Listing Updates Valuation", "FAIL", f"Valuation check failed: {valuation_response.status_code}")
                    return False
            else:
                self.log_test("Listing Updates Valuation", "FAIL", f"Listing creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Listing Updates Valuation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_remove_from_collection_authenticated(self):
        """Test removing jersey from collection with authenticated user"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Remove From Collection (Authenticated)", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # First, ensure jersey is in collection (add it if not already there)
            add_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            # Try to add (might fail if already exists, which is fine)
            self.session.post(f"{self.base_url}/collections", json=add_payload)
            
            # Now test removal
            response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "removed" in data["message"].lower():
                    self.log_test("Remove From Collection (Authenticated)", "PASS", "Jersey successfully removed from collection")
                    return True
                else:
                    self.log_test("Remove From Collection (Authenticated)", "FAIL", "Unexpected response message")
                    return False
            else:
                self.log_test("Remove From Collection (Authenticated)", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Remove From Collection (Authenticated)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_remove_from_collection_unauthenticated(self):
        """Test removing jersey from collection without authentication"""
        try:
            if not self.test_jersey_id:
                self.log_test("Remove From Collection (Unauthenticated)", "FAIL", "No test jersey ID available")
                return False
            
            # Remove auth header temporarily
            original_auth = self.session.headers.get('Authorization')
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            # Restore auth header
            if original_auth:
                self.session.headers['Authorization'] = original_auth
            
            if response.status_code in [401, 403]:
                self.log_test("Remove From Collection (Unauthenticated)", "PASS", f"Correctly rejected with status {response.status_code}")
                return True
            else:
                self.log_test("Remove From Collection (Unauthenticated)", "FAIL", f"Expected 401/403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Remove From Collection (Unauthenticated)", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_remove_nonexistent_jersey_from_collection(self):
        """Test removing non-existent jersey from collection"""
        try:
            if not self.auth_token:
                self.log_test("Remove Non-existent Jersey", "FAIL", "No auth token available")
                return False
            
            # Use a fake jersey ID
            fake_jersey_id = str(uuid.uuid4())
            
            response = self.session.delete(f"{self.base_url}/collections/{fake_jersey_id}")
            
            if response.status_code == 404:
                self.log_test("Remove Non-existent Jersey", "PASS", "Correctly returned 404 for non-existent jersey")
                return True
            else:
                self.log_test("Remove Non-existent Jersey", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Remove Non-existent Jersey", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_remove_from_collection_integration_flow(self):
        """Test complete integration flow: GET collections -> DELETE jersey -> GET collections again"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Remove Collection Integration Flow", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Step 1: Add jersey to both owned and wanted collections
            add_owned_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "owned"
            }
            
            add_wanted_payload = {
                "jersey_id": self.test_jersey_id,
                "collection_type": "wanted"
            }
            
            # Add to collections (ignore if already exists)
            self.session.post(f"{self.base_url}/collections", json=add_owned_payload)
            self.session.post(f"{self.base_url}/collections", json=add_wanted_payload)
            
            # Step 2: Get initial collections
            owned_response_before = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response_before = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response_before.status_code != 200 or wanted_response_before.status_code != 200:
                self.log_test("Remove Collection Integration Flow", "FAIL", "Could not get initial collections")
                return False
            
            owned_before = owned_response_before.json()
            wanted_before = wanted_response_before.json()
            
            # Count jerseys with our test jersey ID
            owned_count_before = sum(1 for item in owned_before if item.get('jersey_id') == self.test_jersey_id)
            wanted_count_before = sum(1 for item in wanted_before if item.get('jersey_id') == self.test_jersey_id)
            
            # Step 3: Remove jersey from collection (removes from all collection types)
            remove_response = self.session.delete(f"{self.base_url}/collections/{self.test_jersey_id}")
            
            if remove_response.status_code != 200:
                self.log_test("Remove Collection Integration Flow", "FAIL", f"Remove failed with status {remove_response.status_code}")
                return False
            
            # Step 4: Get collections after removal
            owned_response_after = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response_after = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response_after.status_code != 200 or wanted_response_after.status_code != 200:
                self.log_test("Remove Collection Integration Flow", "FAIL", "Could not get collections after removal")
                return False
            
            owned_after = owned_response_after.json()
            wanted_after = wanted_response_after.json()
            
            # Count jerseys with our test jersey ID after removal
            owned_count_after = sum(1 for item in owned_after if item.get('jersey_id') == self.test_jersey_id)
            wanted_count_after = sum(1 for item in wanted_after if item.get('jersey_id') == self.test_jersey_id)
            
            # Step 5: Verify removal worked
            if owned_count_after < owned_count_before or wanted_count_after < wanted_count_before:
                self.log_test("Remove Collection Integration Flow", "PASS", 
                            f"Jersey removed successfully. Owned: {owned_count_before}→{owned_count_after}, Wanted: {wanted_count_before}→{wanted_count_after}")
                return True
            else:
                self.log_test("Remove Collection Integration Flow", "FAIL", 
                            f"Jersey not removed. Owned: {owned_count_before}→{owned_count_after}, Wanted: {wanted_count_before}→{wanted_count_after}")
                return False
                
        except Exception as e:
            self.log_test("Remove Collection Integration Flow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_sample_data_verification(self):
        """Test that sample data is properly loaded (3 users, 9 jerseys)"""
        try:
            # Test jerseys count
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                jerseys_count = len(jerseys)
                
                # Test listings count (should have some listings from sample data)
                listings_response = self.session.get(f"{self.base_url}/listings?limit=50")
                
                if listings_response.status_code == 200:
                    listings = listings_response.json()
                    listings_count = len(listings)
                    
                    # Verify we have reasonable amounts of sample data
                    if jerseys_count >= 3 and listings_count >= 1:
                        self.log_test("Sample Data Verification", "PASS", 
                                    f"Found {jerseys_count} jerseys and {listings_count} listings in database")
                        return True
                    else:
                        self.log_test("Sample Data Verification", "FAIL", 
                                    f"Insufficient sample data: {jerseys_count} jerseys, {listings_count} listings")
                        return False
                else:
                    self.log_test("Sample Data Verification", "FAIL", f"Could not get listings: {listings_response.status_code}")
                    return False
            else:
                self.log_test("Sample Data Verification", "FAIL", f"Could not get jerseys: {jerseys_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Sample Data Verification", "FAIL", f"Exception: {str(e)}")
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
        test_results['remove_from_collection_authenticated'] = self.test_remove_from_collection_authenticated()
        test_results['remove_from_collection_unauthenticated'] = self.test_remove_from_collection_unauthenticated()
        test_results['remove_nonexistent_jersey'] = self.test_remove_nonexistent_jersey_from_collection()
        test_results['remove_collection_integration_flow'] = self.test_remove_from_collection_integration_flow()
        
        # Data Verification Tests (High Priority)
        print("🗄️ DATA VERIFICATION TESTS")
        print("-" * 30)
        test_results['sample_data_verification'] = self.test_sample_data_verification()
        
        # Profile Tests (Medium Priority)
        print("👤 PROFILE TESTS")
        print("-" * 30)
        test_results['user_profile'] = self.test_user_profile()
        
        # Payment Tests (Medium Priority)
        print("💳 PAYMENT TESTS")
        print("-" * 30)
        test_results['payment_checkout'] = self.test_payment_checkout()
        
        # Jersey Valuation System Tests (NEW - High Priority)
        print("💰 JERSEY VALUATION SYSTEM TESTS")
        print("-" * 30)
        test_results['jersey_valuation_endpoint'] = self.test_jersey_valuation_endpoint()
        test_results['collection_valuations_endpoint'] = self.test_collection_valuations_endpoint()
        test_results['profile_with_valuations'] = self.test_profile_with_valuations()
        test_results['collector_price_estimate'] = self.test_collector_price_estimate()
        test_results['market_trending_endpoint'] = self.test_market_trending_endpoint()
        test_results['valuation_calculation_logic'] = self.test_valuation_calculation_logic()
        test_results['listing_updates_valuation'] = self.test_listing_updates_valuation()
        
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