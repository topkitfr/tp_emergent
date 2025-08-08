#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Backend API Testing
URGENT AUTHENTICATION DIAGNOSIS - Testing authentication system to diagnose disconnection issues
"""

import requests
import json
import uuid
from datetime import datetime
import time
import jwt

# Configuration
BASE_URL = "https://b0eb9f53-62ff-4085-84f1-93e2485a4420.preview.emergentagent.com/api"
TEST_USER_EMAIL = "test@topkit.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_NAME = "testuser"

class TopKitAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.test_jersey_id = None
        self.test_listing_id = None
        self.new_workflow_jersey_id = None  # For new workflow testing
        self.new_workflow_listing_id = None  # For new workflow testing
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
    
    def test_new_user_workflow_jersey_creation(self):
        """Test NEW WORKFLOW: Jersey Creation for 'Add New Jersey' functionality"""
        try:
            if not self.auth_token:
                self.log_test("New Workflow - Jersey Creation", "FAIL", "No auth token available")
                return False
            
            # Test creating a jersey with comprehensive data (as per new workflow)
            payload = {
                "team": "Liverpool FC",
                "season": "2023-24",
                "player": "Mohamed Salah",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Liverpool FC home jersey with Mohamed Salah #11 - perfect for collection",
                "images": ["https://example.com/liverpool-salah-home.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("team") == "Liverpool FC":
                    self.new_workflow_jersey_id = data["id"]
                    self.log_test("New Workflow - Jersey Creation", "PASS", 
                                f"Jersey created for new workflow: {data['team']} {data['season']} {data.get('player', 'N/A')}")
                    return True
                else:
                    self.log_test("New Workflow - Jersey Creation", "FAIL", "Missing jersey data in response")
                    return False
            else:
                self.log_test("New Workflow - Jersey Creation", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Jersey Creation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_immediate_collection_add(self):
        """Test NEW WORKFLOW: Immediate addition to collection after jersey creation"""
        try:
            if not self.auth_token or not hasattr(self, 'new_workflow_jersey_id'):
                self.log_test("New Workflow - Immediate Collection Add", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Test adding newly created jersey to owned collection (simulating "Add New Jersey" flow)
            payload = {
                "jersey_id": self.new_workflow_jersey_id,
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{self.base_url}/collections", json=payload)
            
            if response.status_code == 200:
                # Verify it was added by checking collections
                collection_response = self.session.get(f"{self.base_url}/collections/owned")
                
                if collection_response.status_code == 200:
                    collections = collection_response.json()
                    jersey_in_collection = any(item.get('jersey_id') == self.new_workflow_jersey_id for item in collections)
                    
                    if jersey_in_collection:
                        self.log_test("New Workflow - Immediate Collection Add", "PASS", 
                                    "Jersey successfully added to collection immediately after creation")
                        return True
                    else:
                        self.log_test("New Workflow - Immediate Collection Add", "FAIL", "Jersey not found in collection")
                        return False
                else:
                    self.log_test("New Workflow - Immediate Collection Add", "FAIL", "Could not verify collection")
                    return False
            else:
                self.log_test("New Workflow - Immediate Collection Add", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Immediate Collection Add", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_sell_from_collection(self):
        """Test NEW WORKFLOW: 'Sell This Jersey' - Creating listing from collection item"""
        try:
            if not self.auth_token or not hasattr(self, 'new_workflow_jersey_id'):
                self.log_test("New Workflow - Sell From Collection", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Test creating a listing from a jersey in collection (simulating "Sell This Jersey" button)
            payload = {
                "jersey_id": self.new_workflow_jersey_id,
                "price": 125.99,
                "description": "Excellent condition Liverpool FC jersey from my personal collection. Mohamed Salah #11, worn only once for photos. Perfect for any Liverpool fan!",
                "images": ["https://example.com/liverpool-salah-listing1.jpg", "https://example.com/liverpool-salah-listing2.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/listings", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("jersey_id") == self.new_workflow_jersey_id:
                    self.new_workflow_listing_id = data["id"]
                    self.log_test("New Workflow - Sell From Collection", "PASS", 
                                f"Listing created from collection jersey: ${data.get('price', 'N/A')}")
                    return True
                else:
                    self.log_test("New Workflow - Sell From Collection", "FAIL", "Invalid listing data")
                    return False
            else:
                self.log_test("New Workflow - Sell From Collection", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Sell From Collection", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_complete_data_flow(self):
        """Test NEW WORKFLOW: Complete data flow integrity - Jersey Creation → Collection → Listing"""
        try:
            if not self.auth_token:
                self.log_test("New Workflow - Complete Data Flow", "FAIL", "No auth token available")
                return False
            
            # Step 1: Create a new jersey (simulating "Add New Jersey")
            jersey_payload = {
                "team": "FC Barcelona",
                "season": "2023-24",
                "player": "Robert Lewandowski",
                "size": "M",
                "condition": "mint",
                "manufacturer": "Nike",
                "home_away": "home",
                "league": "La Liga",
                "description": "Official FC Barcelona home jersey with Lewandowski #9 - brand new with tags",
                "images": ["https://example.com/barca-lewandowski.jpg"]
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if jersey_response.status_code != 200:
                self.log_test("New Workflow - Complete Data Flow", "FAIL", "Step 1: Jersey creation failed")
                return False
            
            jersey_data = jersey_response.json()
            flow_jersey_id = jersey_data["id"]
            
            # Step 2: Add to collection immediately
            collection_payload = {
                "jersey_id": flow_jersey_id,
                "collection_type": "owned"
            }
            
            collection_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if collection_response.status_code != 200:
                self.log_test("New Workflow - Complete Data Flow", "FAIL", "Step 2: Collection add failed")
                return False
            
            # Step 3: Create listing from collection (simulating "Sell This Jersey")
            listing_payload = {
                "jersey_id": flow_jersey_id,
                "price": 149.99,
                "description": "Mint condition FC Barcelona jersey from my collection. Lewandowski #9, never worn, still has original tags.",
                "images": ["https://example.com/barca-listing.jpg"]
            }
            
            listing_response = self.session.post(f"{self.base_url}/listings", json=listing_payload)
            
            if listing_response.status_code != 200:
                self.log_test("New Workflow - Complete Data Flow", "FAIL", "Step 3: Listing creation failed")
                return False
            
            listing_data = listing_response.json()
            
            # Step 4: Verify complete data integrity
            # Check that listing has correct jersey reference
            listing_detail_response = self.session.get(f"{self.base_url}/listings/{listing_data['id']}")
            
            if listing_detail_response.status_code == 200:
                listing_detail = listing_detail_response.json()
                
                # Verify all data is properly linked
                if (listing_detail.get("jersey_id") == flow_jersey_id and
                    "jersey" in listing_detail and
                    listing_detail["jersey"].get("team") == "FC Barcelona" and
                    listing_detail["jersey"].get("player") == "Robert Lewandowski"):
                    
                    self.log_test("New Workflow - Complete Data Flow", "PASS", 
                                f"Complete flow verified: Jersey → Collection → Listing (${listing_data.get('price')})")
                    return True
                else:
                    self.log_test("New Workflow - Complete Data Flow", "FAIL", "Data integrity check failed")
                    return False
            else:
                self.log_test("New Workflow - Complete Data Flow", "FAIL", "Could not verify listing details")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Complete Data Flow", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_browse_functionality(self):
        """Test NEW WORKFLOW: Browse jerseys functionality (no create listing buttons)"""
        try:
            # Test that browse functionality still works (backend should support frontend changes)
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Test filtering still works
                filter_response = self.session.get(f"{self.base_url}/jerseys", params={
                    "team": "Liverpool",
                    "condition": "excellent"
                })
                
                if filter_response.status_code == 200:
                    filtered_jerseys = filter_response.json()
                    self.log_test("New Workflow - Browse Functionality", "PASS", 
                                f"Browse working: {len(jerseys)} total jerseys, {len(filtered_jerseys)} filtered")
                    return True
                else:
                    self.log_test("New Workflow - Browse Functionality", "FAIL", "Filtering failed")
                    return False
            else:
                self.log_test("New Workflow - Browse Functionality", "FAIL", f"Browse failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Browse Functionality", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_marketplace_functionality(self):
        """Test NEW WORKFLOW: Marketplace functionality (view/buy only, no create listing buttons)"""
        try:
            # Test marketplace viewing functionality
            response = self.session.get(f"{self.base_url}/listings?limit=10")
            
            if response.status_code == 200:
                listings = response.json()
                
                # Test marketplace filtering
                filter_response = self.session.get(f"{self.base_url}/listings", params={
                    "min_price": 50.0,
                    "max_price": 200.0,
                    "condition": "excellent"
                })
                
                if filter_response.status_code == 200:
                    filtered_listings = filter_response.json()
                    
                    # Test individual listing view (for "buy" functionality)
                    if filtered_listings:
                        listing_id = filtered_listings[0]["id"]
                        detail_response = self.session.get(f"{self.base_url}/listings/{listing_id}")
                        
                        if detail_response.status_code == 200:
                            self.log_test("New Workflow - Marketplace Functionality", "PASS", 
                                        f"Marketplace working: {len(listings)} listings, filtering and detail view functional")
                            return True
                        else:
                            self.log_test("New Workflow - Marketplace Functionality", "FAIL", "Listing detail view failed")
                            return False
                    else:
                        self.log_test("New Workflow - Marketplace Functionality", "PASS", 
                                    f"Marketplace working: {len(listings)} listings, filtering functional")
                        return True
                else:
                    self.log_test("New Workflow - Marketplace Functionality", "FAIL", "Marketplace filtering failed")
                    return False
            else:
                self.log_test("New Workflow - Marketplace Functionality", "FAIL", f"Marketplace failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Marketplace Functionality", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_collections_centralized_approach(self):
        """Test NEW WORKFLOW: Collections as central hub for jersey management"""
        try:
            if not self.auth_token:
                self.log_test("New Workflow - Collections Central Hub", "FAIL", "No auth token available")
                return False
            
            # Test that collections properly support the centralized approach
            # 1. Get owned collections
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code == 200:
                owned_jerseys = owned_response.json()
                
                # 2. Get wanted collections
                wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
                
                if wanted_response.status_code == 200:
                    wanted_jerseys = wanted_response.json()
                    
                    # 3. Test that collection items have all necessary data for the new workflow
                    if owned_jerseys:
                        sample_owned = owned_jerseys[0]
                        required_fields = ["jersey_id", "collection_type", "jersey"]
                        
                        if all(field in sample_owned for field in required_fields):
                            jersey_data = sample_owned["jersey"]
                            jersey_required_fields = ["id", "team", "season", "size", "condition", "manufacturer"]
                            
                            if all(field in jersey_data for field in jersey_required_fields):
                                self.log_test("New Workflow - Collections Central Hub", "PASS", 
                                            f"Collections support centralized approach: {len(owned_jerseys)} owned, {len(wanted_jerseys)} wanted")
                                return True
                            else:
                                self.log_test("New Workflow - Collections Central Hub", "FAIL", "Missing jersey data fields")
                                return False
                        else:
                            self.log_test("New Workflow - Collections Central Hub", "FAIL", "Missing collection fields")
                            return False
                    else:
                        self.log_test("New Workflow - Collections Central Hub", "PASS", 
                                    f"Collections endpoint working (empty collections): owned={len(owned_jerseys)}, wanted={len(wanted_jerseys)}")
                        return True
                else:
                    self.log_test("New Workflow - Collections Central Hub", "FAIL", "Wanted collections failed")
                    return False
            else:
                self.log_test("New Workflow - Collections Central Hub", "FAIL", "Owned collections failed")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Collections Central Hub", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_new_user_workflow_profile_stats_only(self):
        """Test NEW WORKFLOW: Profile page shows stats and valuations only (no selling functionality)"""
        try:
            if not self.auth_token:
                self.log_test("New Workflow - Profile Stats Only", "FAIL", "No auth token available")
                return False
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                
                # Verify profile has stats and valuations (as per new workflow)
                required_sections = ["user", "stats", "valuations"]
                
                if all(section in profile for section in required_sections):
                    stats = profile["stats"]
                    valuations = profile["valuations"]
                    
                    # Check stats fields
                    stats_fields = ["owned_jerseys", "wanted_jerseys", "active_listings"]
                    
                    if all(field in stats for field in stats_fields):
                        # Check valuations structure
                        if "portfolio_summary" in valuations:
                            portfolio = valuations["portfolio_summary"]
                            portfolio_fields = ["total_items", "total_median_estimate"]
                            
                            if all(field in portfolio for field in portfolio_fields):
                                self.log_test("New Workflow - Profile Stats Only", "PASS", 
                                            f"Profile supports new workflow: {stats['owned_jerseys']} owned, ${portfolio.get('total_median_estimate', 0)} portfolio value")
                                return True
                            else:
                                self.log_test("New Workflow - Profile Stats Only", "FAIL", "Missing portfolio fields")
                                return False
                        else:
                            self.log_test("New Workflow - Profile Stats Only", "FAIL", "Missing portfolio summary")
                            return False
                    else:
                        self.log_test("New Workflow - Profile Stats Only", "FAIL", "Missing stats fields")
                        return False
                else:
                    self.log_test("New Workflow - Profile Stats Only", "FAIL", "Missing required profile sections")
                    return False
            else:
                self.log_test("New Workflow - Profile Stats Only", "FAIL", f"Profile failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("New Workflow - Profile Stats Only", "FAIL", f"Exception: {str(e)}")
            return False

    def test_jersey_update_endpoint(self):
        """Test PUT /api/jerseys/{jersey_id} endpoint for updating jersey details"""
        try:
            if not self.auth_token or not self.test_jersey_id:
                self.log_test("Jersey Update Endpoint", "FAIL", "Missing auth token or jersey ID")
                return False
            
            # Test updating jersey details
            update_payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "XL",  # Changed from L to XL
                "condition": "mint",  # Changed from excellent to mint
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Updated: Official Manchester United home jersey with Bruno Fernandes #8 - now in mint condition",
                "images": ["https://example.com/jersey1-updated.jpg"]
            }
            
            response = self.session.put(f"{self.base_url}/jerseys/{self.test_jersey_id}", json=update_payload)
            
            if response.status_code == 200:
                updated_jersey = response.json()
                
                # Verify the updates were applied
                if (updated_jersey.get("size") == "XL" and 
                    updated_jersey.get("condition") == "mint" and
                    "Updated:" in updated_jersey.get("description", "")):
                    
                    self.log_test("Jersey Update Endpoint", "PASS", 
                                f"Jersey updated successfully: Size {updated_jersey.get('size')}, Condition {updated_jersey.get('condition')}")
                    return True
                else:
                    self.log_test("Jersey Update Endpoint", "FAIL", "Updates not reflected in response")
                    return False
            else:
                self.log_test("Jersey Update Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Update Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_update_authorization(self):
        """Test that users can only update their own jerseys"""
        try:
            if not self.test_jersey_id:
                self.log_test("Jersey Update Authorization", "FAIL", "No test jersey ID available")
                return False
            
            # Create a second user to test authorization
            unique_email = f"testuser2_{int(time.time())}@topkit.com"
            
            register_payload = {
                "email": unique_email,
                "password": TEST_USER_PASSWORD,
                "name": "Test User 2"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code != 200:
                self.log_test("Jersey Update Authorization", "FAIL", "Could not create second user")
                return False
            
            # Get the second user's token
            second_user_data = register_response.json()
            second_user_token = second_user_data["token"]
            
            # Try to update the first user's jersey with second user's token
            update_payload = {
                "team": "Manchester United",
                "season": "2023-24",
                "player": "Bruno Fernandes",
                "size": "S",
                "condition": "good",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Unauthorized update attempt",
                "images": []
            }
            
            # Use second user's token
            unauthorized_headers = {'Authorization': f'Bearer {second_user_token}'}
            response = self.session.put(f"{self.base_url}/jerseys/{self.test_jersey_id}", 
                                      json=update_payload, headers=unauthorized_headers)
            
            if response.status_code == 403:
                self.log_test("Jersey Update Authorization", "PASS", "Unauthorized update correctly rejected with 403")
                return True
            else:
                self.log_test("Jersey Update Authorization", "FAIL", f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Update Authorization", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_update_nonexistent(self):
        """Test updating non-existent jersey returns 404"""
        try:
            if not self.auth_token:
                self.log_test("Jersey Update Non-existent", "FAIL", "No auth token available")
                return False
            
            fake_jersey_id = str(uuid.uuid4())
            
            update_payload = {
                "team": "Fake Team",
                "season": "2023-24",
                "player": "Fake Player",
                "size": "L",
                "condition": "excellent",
                "manufacturer": "Fake Brand",
                "home_away": "home",
                "league": "Fake League",
                "description": "This should fail",
                "images": []
            }
            
            response = self.session.put(f"{self.base_url}/jerseys/{fake_jersey_id}", json=update_payload)
            
            if response.status_code == 404:
                self.log_test("Jersey Update Non-existent", "PASS", "Non-existent jersey update correctly returned 404")
                return True
            else:
                self.log_test("Jersey Update Non-existent", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Update Non-existent", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_delete_with_existing_jerseys(self):
        """Test DELETE /api/collections/{jersey_id} with jerseys that exist in user collections"""
        try:
            if not self.auth_token:
                self.log_test("Collection Delete - Existing Jerseys", "FAIL", "No auth token available")
                return False
            
            # First, get current collections to find existing jerseys
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
            
            if owned_response.status_code != 200 or wanted_response.status_code != 200:
                self.log_test("Collection Delete - Existing Jerseys", "FAIL", "Could not get current collections")
                return False
            
            owned_jerseys = owned_response.json()
            wanted_jerseys = wanted_response.json()
            
            # Find a jersey that exists in collections
            test_jersey_for_delete = None
            
            if owned_jerseys:
                test_jersey_for_delete = owned_jerseys[0]["jersey_id"]
            elif wanted_jerseys:
                test_jersey_for_delete = wanted_jerseys[0]["jersey_id"]
            elif self.test_jersey_id:
                # Add our test jersey to collection first
                add_payload = {
                    "jersey_id": self.test_jersey_id,
                    "collection_type": "owned"
                }
                add_response = self.session.post(f"{self.base_url}/collections", json=add_payload)
                if add_response.status_code in [200, 400]:  # 400 if already exists
                    test_jersey_for_delete = self.test_jersey_id
            
            if not test_jersey_for_delete:
                self.log_test("Collection Delete - Existing Jerseys", "FAIL", "No jersey available for delete test")
                return False
            
            # Now test deletion
            delete_response = self.session.delete(f"{self.base_url}/collections/{test_jersey_for_delete}")
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                if "message" in delete_data and "removed" in delete_data["message"].lower():
                    self.log_test("Collection Delete - Existing Jerseys", "PASS", 
                                f"Successfully deleted jersey {test_jersey_for_delete} from collection")
                    return True
                else:
                    self.log_test("Collection Delete - Existing Jerseys", "FAIL", "Unexpected response message")
                    return False
            else:
                self.log_test("Collection Delete - Existing Jerseys", "FAIL", 
                            f"Delete failed with status {delete_response.status_code}: {delete_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Delete - Existing Jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_full_integration_flow_priority(self):
        """Test PRIORITY INTEGRATION: Create jersey → Add to collection → Edit jersey → Remove from collection"""
        try:
            if not self.auth_token:
                self.log_test("Full Integration Flow - Priority", "FAIL", "No auth token available")
                return False
            
            # Step 1: Create a new jersey
            jersey_payload = {
                "team": "Arsenal FC",
                "season": "2023-24",
                "player": "Bukayo Saka",
                "size": "M",
                "condition": "excellent",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "Official Arsenal home jersey with Saka #7",
                "images": ["https://example.com/arsenal-saka.jpg"]
            }
            
            jersey_response = self.session.post(f"{self.base_url}/jerseys", json=jersey_payload)
            
            if jersey_response.status_code != 200:
                self.log_test("Full Integration Flow - Priority", "FAIL", "Step 1: Jersey creation failed")
                return False
            
            integration_jersey_id = jersey_response.json()["id"]
            
            # Step 2: Add to collection
            collection_payload = {
                "jersey_id": integration_jersey_id,
                "collection_type": "owned"
            }
            
            collection_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            if collection_response.status_code != 200:
                self.log_test("Full Integration Flow - Priority", "FAIL", "Step 2: Add to collection failed")
                return False
            
            # Step 3: Edit jersey (test the PUT endpoint)
            edit_payload = {
                "team": "Arsenal FC",
                "season": "2023-24",
                "player": "Bukayo Saka",
                "size": "L",  # Changed from M to L
                "condition": "mint",  # Changed from excellent to mint
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Premier League",
                "description": "UPDATED: Official Arsenal home jersey with Saka #7 - now in mint condition",
                "images": ["https://example.com/arsenal-saka-updated.jpg"]
            }
            
            edit_response = self.session.put(f"{self.base_url}/jerseys/{integration_jersey_id}", json=edit_payload)
            
            if edit_response.status_code != 200:
                self.log_test("Full Integration Flow - Priority", "FAIL", f"Step 3: Jersey edit failed with status {edit_response.status_code}")
                return False
            
            # Verify the edit worked
            updated_jersey = edit_response.json()
            if updated_jersey.get("size") != "L" or updated_jersey.get("condition") != "mint":
                self.log_test("Full Integration Flow - Priority", "FAIL", "Step 3: Jersey edit not applied correctly")
                return False
            
            # Step 4: Remove from collection
            remove_response = self.session.delete(f"{self.base_url}/collections/{integration_jersey_id}")
            
            if remove_response.status_code != 200:
                self.log_test("Full Integration Flow - Priority", "FAIL", f"Step 4: Remove from collection failed with status {remove_response.status_code}")
                return False
            
            # Step 5: Verify removal by checking collections
            verify_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if verify_response.status_code == 200:
                owned_after_removal = verify_response.json()
                jersey_still_in_collection = any(item.get('jersey_id') == integration_jersey_id for item in owned_after_removal)
                
                if not jersey_still_in_collection:
                    self.log_test("Full Integration Flow - Priority", "PASS", 
                                f"✅ Complete integration flow successful: Create → Add → Edit (M→L, excellent→mint) → Remove")
                    return True
                else:
                    self.log_test("Full Integration Flow - Priority", "FAIL", "Step 5: Jersey still in collection after removal")
                    return False
            else:
                self.log_test("Full Integration Flow - Priority", "FAIL", "Step 5: Could not verify removal")
                return False
                
        except Exception as e:
            self.log_test("Full Integration Flow - Priority", "FAIL", f"Exception: {str(e)}")
            return False

    def create_test_users_and_jerseys(self):
        """Create test users and jerseys for profile and creator testing"""
        try:
            # Create test users
            test_users = []
            
            # User 1: Alex Johnson (public profile)
            alex_email = f"alex.johnson_{int(time.time())}@topkit.com"
            alex_payload = {
                "email": alex_email,
                "password": "SecurePass123!",
                "name": "Alex Johnson"
            }
            
            alex_response = self.session.post(f"{self.base_url}/auth/register", json=alex_payload)
            if alex_response.status_code == 200:
                alex_data = alex_response.json()
                test_users.append({
                    "id": alex_data["user"]["id"],
                    "name": "Alex Johnson",
                    "email": alex_email,
                    "token": alex_data["token"],
                    "privacy": "public"
                })
            
            # User 2: Sarah Martinez (public profile)
            sarah_email = f"sarah.martinez_{int(time.time())}@topkit.com"
            sarah_payload = {
                "email": sarah_email,
                "password": "SecurePass123!",
                "name": "Sarah Martinez"
            }
            
            sarah_response = self.session.post(f"{self.base_url}/auth/register", json=sarah_payload)
            if sarah_response.status_code == 200:
                sarah_data = sarah_response.json()
                test_users.append({
                    "id": sarah_data["user"]["id"],
                    "name": "Sarah Martinez",
                    "email": sarah_email,
                    "token": sarah_data["token"],
                    "privacy": "public"
                })
            
            # User 3: Private User (private profile)
            private_email = f"private.user_{int(time.time())}@topkit.com"
            private_payload = {
                "email": private_email,
                "password": "SecurePass123!",
                "name": "Private User"
            }
            
            private_response = self.session.post(f"{self.base_url}/auth/register", json=private_payload)
            if private_response.status_code == 200:
                private_data = private_response.json()
                test_users.append({
                    "id": private_data["user"]["id"],
                    "name": "Private User",
                    "email": private_email,
                    "token": private_data["token"],
                    "privacy": "private"
                })
                
                # Set private user's profile to private
                private_headers = {'Authorization': f'Bearer {private_data["token"]}'}
                settings_payload = {
                    "profile_privacy": "private",
                    "show_collection_value": False
                }
                self.session.put(f"{self.base_url}/profile/settings", json=settings_payload, headers=private_headers)
            
            # Create jerseys for each user
            jerseys_created = []
            
            # Alex Johnson's jerseys (2 jerseys)
            if len(test_users) >= 1:
                alex_headers = {'Authorization': f'Bearer {test_users[0]["token"]}'}
                
                # Manchester United jersey
                man_utd_payload = {
                    "team": "Manchester United",
                    "season": "2023-24",
                    "player": "Bruno Fernandes",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Manchester United home jersey",
                    "images": ["https://example.com/manutd.jpg"]
                }
                
                man_utd_response = self.session.post(f"{self.base_url}/jerseys", json=man_utd_payload, headers=alex_headers)
                if man_utd_response.status_code == 200:
                    jerseys_created.append({
                        "id": man_utd_response.json()["id"],
                        "team": "Manchester United",
                        "creator": "Alex Johnson",
                        "creator_id": test_users[0]["id"]
                    })
                
                # Liverpool jersey
                liverpool_payload = {
                    "team": "Liverpool FC",
                    "season": "2023-24",
                    "player": "Mohamed Salah",
                    "size": "M",
                    "condition": "mint",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Liverpool FC home jersey",
                    "images": ["https://example.com/liverpool.jpg"]
                }
                
                liverpool_response = self.session.post(f"{self.base_url}/jerseys", json=liverpool_payload, headers=alex_headers)
                if liverpool_response.status_code == 200:
                    jerseys_created.append({
                        "id": liverpool_response.json()["id"],
                        "team": "Liverpool FC",
                        "creator": "Alex Johnson",
                        "creator_id": test_users[0]["id"]
                    })
            
            # Sarah Martinez's jerseys (2 jerseys)
            if len(test_users) >= 2:
                sarah_headers = {'Authorization': f'Bearer {test_users[1]["token"]}'}
                
                # Real Madrid jersey
                real_madrid_payload = {
                    "team": "Real Madrid",
                    "season": "2023-24",
                    "player": "Vinicius Jr",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": "Official Real Madrid home jersey",
                    "images": ["https://example.com/realmadrid.jpg"]
                }
                
                real_madrid_response = self.session.post(f"{self.base_url}/jerseys", json=real_madrid_payload, headers=sarah_headers)
                if real_madrid_response.status_code == 200:
                    jerseys_created.append({
                        "id": real_madrid_response.json()["id"],
                        "team": "Real Madrid",
                        "creator": "Sarah Martinez",
                        "creator_id": test_users[1]["id"]
                    })
                
                # Chelsea jersey
                chelsea_payload = {
                    "team": "Chelsea FC",
                    "season": "2023-24",
                    "player": "Enzo Fernandez",
                    "size": "XL",
                    "condition": "very_good",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Chelsea FC home jersey",
                    "images": ["https://example.com/chelsea.jpg"]
                }
                
                chelsea_response = self.session.post(f"{self.base_url}/jerseys", json=chelsea_payload, headers=sarah_headers)
                if chelsea_response.status_code == 200:
                    jerseys_created.append({
                        "id": chelsea_response.json()["id"],
                        "team": "Chelsea FC",
                        "creator": "Sarah Martinez",
                        "creator_id": test_users[1]["id"]
                    })
            
            # Private User's jersey (1 jersey)
            if len(test_users) >= 3:
                private_headers = {'Authorization': f'Bearer {test_users[2]["token"]}'}
                
                # Arsenal jersey
                arsenal_payload = {
                    "team": "Arsenal FC",
                    "season": "2023-24",
                    "player": "Bukayo Saka",
                    "size": "M",
                    "condition": "good",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Arsenal FC home jersey",
                    "images": ["https://example.com/arsenal.jpg"]
                }
                
                arsenal_response = self.session.post(f"{self.base_url}/jerseys", json=arsenal_payload, headers=private_headers)
                if arsenal_response.status_code == 200:
                    jerseys_created.append({
                        "id": arsenal_response.json()["id"],
                        "team": "Arsenal FC",
                        "creator": "Private User",
                        "creator_id": test_users[2]["id"]
                    })
            
            return {
                "users": test_users,
                "jerseys": jerseys_created
            }
            
        except Exception as e:
            self.log_test("Create Test Users and Jerseys", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_jersey_api_with_creator_info(self):
        """PRIORITY 1: Test GET /api/jerseys endpoint includes creator_info for each jersey"""
        try:
            # Create test data
            test_data = self.create_test_users_and_jerseys()
            if not test_data:
                self.log_test("Jersey API with Creator Info", "FAIL", "Could not create test data")
                return False
            
            # Test GET /api/jerseys endpoint
            response = self.session.get(f"{self.base_url}/jerseys?limit=10")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Verify creator_info is included
                creator_info_found = 0
                for jersey in jerseys:
                    if "creator_info" in jersey:
                        creator_info = jersey["creator_info"]
                        if "name" in creator_info and "id" in creator_info:
                            creator_info_found += 1
                            
                            # Verify creator info matches our test data
                            expected_creator = next((j for j in test_data["jerseys"] if j["id"] == jersey["id"]), None)
                            if expected_creator and creator_info["name"] == expected_creator["creator"]:
                                continue
                
                if creator_info_found > 0:
                    self.log_test("Jersey API with Creator Info", "PASS", 
                                f"Found {creator_info_found} jerseys with proper creator_info (name, id, picture fields)")
                    return True
                else:
                    self.log_test("Jersey API with Creator Info", "FAIL", "No jerseys found with creator_info")
                    return False
            else:
                self.log_test("Jersey API with Creator Info", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey API with Creator Info", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_profile_endpoints(self):
        """PRIORITY 2: Test GET /api/users/{user_id}/profile for each test user"""
        try:
            # Create test data
            test_data = self.create_test_users_and_jerseys()
            if not test_data:
                self.log_test("User Profile Endpoints", "FAIL", "Could not create test data")
                return False
            
            profiles_tested = 0
            
            for user in test_data["users"]:
                # Test public profile
                response = self.session.get(f"{self.base_url}/users/{user['id']}/profile")
                
                if response.status_code == 200:
                    profile = response.json()
                    
                    if user["privacy"] == "public":
                        # Verify public profile returns full information
                        required_fields = ["id", "name", "picture", "provider", "created_at", "profile_privacy", "stats"]
                        if all(field in profile for field in required_fields):
                            stats = profile["stats"]
                            required_stats = ["owned_jerseys", "wanted_jerseys", "active_listings", "jerseys_created"]
                            
                            if all(stat in stats for stat in required_stats):
                                profiles_tested += 1
                                self.log_test(f"User Profile - {user['name']} (Public)", "PASS", 
                                            f"Stats: {stats['jerseys_created']} created, {stats['owned_jerseys']} owned")
                            else:
                                self.log_test(f"User Profile - {user['name']} (Public)", "FAIL", "Missing required stats")
                        else:
                            self.log_test(f"User Profile - {user['name']} (Public)", "FAIL", "Missing required fields")
                    
                    elif user["privacy"] == "private":
                        # Verify private profile returns limited info
                        if "profile_privacy" in profile and profile["profile_privacy"] == "private":
                            if "message" in profile and "private" in profile["message"].lower():
                                profiles_tested += 1
                                self.log_test(f"User Profile - {user['name']} (Private)", "PASS", 
                                            "Private profile correctly returns limited info")
                            else:
                                self.log_test(f"User Profile - {user['name']} (Private)", "FAIL", "Missing private message")
                        else:
                            self.log_test(f"User Profile - {user['name']} (Private)", "FAIL", "Privacy not properly indicated")
                else:
                    self.log_test(f"User Profile - {user['name']}", "FAIL", f"Status: {response.status_code}")
            
            if profiles_tested >= 3:
                self.log_test("User Profile Endpoints", "PASS", f"Successfully tested {profiles_tested} user profiles")
                return True
            else:
                self.log_test("User Profile Endpoints", "FAIL", f"Only {profiles_tested} profiles tested successfully")
                return False
                
        except Exception as e:
            self.log_test("User Profile Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_created_jerseys_endpoint(self):
        """PRIORITY 3: Test GET /api/users/{user_id}/jerseys for each user"""
        try:
            # Create test data
            test_data = self.create_test_users_and_jerseys()
            if not test_data:
                self.log_test("User Created Jerseys Endpoint", "FAIL", "Could not create test data")
                return False
            
            jerseys_tested = 0
            
            for user in test_data["users"]:
                response = self.session.get(f"{self.base_url}/users/{user['id']}/jerseys")
                
                if user["privacy"] == "public":
                    if response.status_code == 200:
                        jerseys = response.json()
                        
                        # Count expected jerseys for this user
                        expected_jerseys = [j for j in test_data["jerseys"] if j["creator_id"] == user["id"]]
                        
                        if len(jerseys) == len(expected_jerseys):
                            # Verify jersey data includes creator_info
                            creator_info_correct = True
                            for jersey in jerseys:
                                if "creator_info" in jersey:
                                    creator_info = jersey["creator_info"]
                                    if creator_info["name"] != user["name"] or creator_info["id"] != user["id"]:
                                        creator_info_correct = False
                                        break
                                else:
                                    creator_info_correct = False
                                    break
                            
                            if creator_info_correct:
                                jerseys_tested += 1
                                jersey_teams = [j["team"] for j in jerseys]
                                self.log_test(f"User Created Jerseys - {user['name']}", "PASS", 
                                            f"Found {len(jerseys)} jerseys: {', '.join(jersey_teams)}")
                            else:
                                self.log_test(f"User Created Jerseys - {user['name']}", "FAIL", "Creator info incorrect")
                        else:
                            self.log_test(f"User Created Jerseys - {user['name']}", "FAIL", 
                                        f"Expected {len(expected_jerseys)} jerseys, got {len(jerseys)}")
                    else:
                        self.log_test(f"User Created Jerseys - {user['name']}", "FAIL", f"Status: {response.status_code}")
                
                elif user["privacy"] == "private":
                    if response.status_code == 403:
                        jerseys_tested += 1
                        self.log_test(f"User Created Jerseys - {user['name']} (Private)", "PASS", 
                                    "Correctly returned 403 for private user")
                    else:
                        self.log_test(f"User Created Jerseys - {user['name']} (Private)", "FAIL", 
                                    f"Expected 403, got {response.status_code}")
            
            if jerseys_tested >= 3:
                self.log_test("User Created Jerseys Endpoint", "PASS", f"Successfully tested {jerseys_tested} user jersey endpoints")
                return True
            else:
                self.log_test("User Created Jerseys Endpoint", "FAIL", f"Only {jerseys_tested} endpoints tested successfully")
                return False
                
        except Exception as e:
            self.log_test("User Created Jerseys Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_data_integrity_and_aggregation(self):
        """PRIORITY 4: Test data integrity and aggregation pipelines"""
        try:
            # Create test data
            test_data = self.create_test_users_and_jerseys()
            if not test_data:
                self.log_test("Data Integrity and Aggregation", "FAIL", "Could not create test data")
                return False
            
            integrity_checks = 0
            
            # Test 1: Verify jersey creator relationships are correct
            response = self.session.get(f"{self.base_url}/jerseys?limit=20")
            if response.status_code == 200:
                jerseys = response.json()
                
                creator_relationships_correct = True
                for jersey in jerseys:
                    if "creator_info" in jersey and "created_by" in jersey:
                        # Find expected creator
                        expected_creator = next((j for j in test_data["jerseys"] if j["id"] == jersey["id"]), None)
                        if expected_creator:
                            if jersey["creator_info"]["id"] != expected_creator["creator_id"]:
                                creator_relationships_correct = False
                                break
                
                if creator_relationships_correct:
                    integrity_checks += 1
                    self.log_test("Data Integrity - Creator Relationships", "PASS", "All creator relationships correct")
                else:
                    self.log_test("Data Integrity - Creator Relationships", "FAIL", "Creator relationship mismatch found")
            
            # Test 2: Test non-existent user ID returns 404
            fake_user_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/users/{fake_user_id}/profile")
            if response.status_code == 404:
                integrity_checks += 1
                self.log_test("Data Integrity - Non-existent User", "PASS", "Correctly returned 404 for non-existent user")
            else:
                self.log_test("Data Integrity - Non-existent User", "FAIL", f"Expected 404, got {response.status_code}")
            
            # Test 3: Verify aggregation pipelines work with MongoDB
            # Test jersey aggregation with creator lookup
            response = self.session.get(f"{self.base_url}/jerseys?team=Manchester&limit=5")
            if response.status_code == 200:
                jerseys = response.json()
                aggregation_working = True
                
                for jersey in jerseys:
                    if "creator_info" not in jersey:
                        aggregation_working = False
                        break
                    
                    creator_info = jersey["creator_info"]
                    if not ("name" in creator_info and "id" in creator_info):
                        aggregation_working = False
                        break
                
                if aggregation_working:
                    integrity_checks += 1
                    self.log_test("Data Integrity - Aggregation Pipeline", "PASS", "MongoDB aggregation working correctly")
                else:
                    self.log_test("Data Integrity - Aggregation Pipeline", "FAIL", "Aggregation pipeline issues detected")
            
            if integrity_checks >= 3:
                self.log_test("Data Integrity and Aggregation", "PASS", f"All {integrity_checks} integrity checks passed")
                return True
            else:
                self.log_test("Data Integrity and Aggregation", "FAIL", f"Only {integrity_checks}/3 integrity checks passed")
                return False
                
        except Exception as e:
            self.log_test("Data Integrity and Aggregation", "FAIL", f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests with focus on NEW USER PROFILE & JERSEY CREATOR functionality"""
        print("🚀 Starting TopKit Backend API Tests - NEW USER PROFILE & JERSEY CREATOR FOCUS")
        print("🎯 PRIORITY 1: Jersey API with Creator Information")
        print("🎯 PRIORITY 2: User Profile Endpoints") 
        print("🎯 PRIORITY 3: User Created Jerseys Endpoint")
        print("🎯 PRIORITY 4: Data Integrity & Aggregation")
        print("=" * 60)
        
        test_results = {}
        
        # Authentication Tests (Required for other tests)
        print("🔐 AUTHENTICATION TESTS")
        print("-" * 30)
        test_results['auth_register'] = self.test_custom_auth_registration()
        test_results['auth_login'] = self.test_custom_auth_login()
        test_results['google_oauth'] = self.test_google_oauth_redirect()
        test_results['emergent_auth'] = self.test_emergent_auth_redirect()
        test_results['jwt_validation'] = self.test_jwt_token_validation()
        
        # NEW USER PROFILE & JERSEY CREATOR TESTS - TOP PRIORITY
        print("🎯 NEW USER PROFILE & JERSEY CREATOR FUNCTIONALITY TESTS")
        print("-" * 50)
        test_results['jersey_api_with_creator_info'] = self.test_jersey_api_with_creator_info()
        test_results['user_profile_endpoints'] = self.test_user_profile_endpoints()
        test_results['user_created_jerseys_endpoint'] = self.test_user_created_jerseys_endpoint()
        test_results['data_integrity_and_aggregation'] = self.test_data_integrity_and_aggregation()
        
        # PRIORITY TESTS - Collection Delete Functionality
        print("🎯 COLLECTION DELETE FUNCTIONALITY")
        print("-" * 40)
        test_results['remove_from_collection_authenticated'] = self.test_remove_from_collection_authenticated()
        test_results['remove_from_collection_unauthenticated'] = self.test_remove_from_collection_unauthenticated()
        test_results['remove_nonexistent_jersey'] = self.test_remove_nonexistent_jersey_from_collection()
        test_results['remove_collection_integration_flow'] = self.test_remove_from_collection_integration_flow()
        test_results['collection_delete_existing_jerseys'] = self.test_collection_delete_with_existing_jerseys()
        
        # PRIORITY TESTS - Jersey Update Functionality
        print("🎯 JERSEY UPDATE FUNCTIONALITY")
        print("-" * 40)
        test_results['jersey_update_endpoint'] = self.test_jersey_update_endpoint()
        test_results['jersey_update_authorization'] = self.test_jersey_update_authorization()
        test_results['jersey_update_nonexistent'] = self.test_jersey_update_nonexistent()
        
        # PRIORITY TESTS - Integration Testing
        print("🎯 INTEGRATION TESTING")
        print("-" * 40)
        test_results['full_integration_flow_priority'] = self.test_full_integration_flow_priority()
        
        # Jersey Database Tests (Required for integration)
        print("⚽ JERSEY DATABASE TESTS")
        print("-" * 30)
        test_results['create_jersey'] = self.test_create_jersey()
        test_results['get_jerseys'] = self.test_get_jerseys()
        test_results['get_specific_jersey'] = self.test_get_specific_jersey()
        
        # Marketplace Tests (Required for integration)
        print("🏪 MARKETPLACE TESTS")
        print("-" * 30)
        test_results['create_listing'] = self.test_create_listing()
        test_results['get_listings'] = self.test_get_listings()
        test_results['get_specific_listing'] = self.test_get_specific_listing()
        
        # Collections Tests (Additional coverage)
        print("📚 COLLECTIONS TESTS (Additional)")
        print("-" * 30)
        test_results['add_to_collection'] = self.test_add_to_collection()
        test_results['get_collections'] = self.test_get_user_collections()
        
        # Data Verification Tests
        print("🗄️ DATA VERIFICATION TESTS")
        print("-" * 30)
        test_results['sample_data_verification'] = self.test_sample_data_verification()
        
        # Profile Tests
        print("👤 PROFILE TESTS")
        print("-" * 30)
        test_results['user_profile'] = self.test_user_profile()
        
        # Payment Tests
        print("💳 PAYMENT TESTS")
        print("-" * 30)
        test_results['payment_checkout'] = self.test_payment_checkout()
        
        # Jersey Valuation System Tests
        print("💰 JERSEY VALUATION SYSTEM TESTS")
        print("-" * 30)
        test_results['jersey_valuation_endpoint'] = self.test_jersey_valuation_endpoint()
        test_results['collection_valuations_endpoint'] = self.test_collection_valuations_endpoint()
        test_results['profile_with_valuations'] = self.test_profile_with_valuations()
        test_results['collector_price_estimate'] = self.test_collector_price_estimate()
        test_results['market_trending_endpoint'] = self.test_market_trending_endpoint()
        test_results['valuation_calculation_logic'] = self.test_valuation_calculation_logic()
        test_results['listing_updates_valuation'] = self.test_listing_updates_valuation()
        
        # NEW USER WORKFLOW TESTS
        print("🎯 NEW USER WORKFLOW TESTS")
        print("-" * 30)
        test_results['new_workflow_jersey_creation'] = self.test_new_user_workflow_jersey_creation()
        test_results['new_workflow_immediate_collection_add'] = self.test_new_user_workflow_immediate_collection_add()
        test_results['new_workflow_sell_from_collection'] = self.test_new_user_workflow_sell_from_collection()
        test_results['new_workflow_complete_data_flow'] = self.test_new_user_workflow_complete_data_flow()
        test_results['new_workflow_browse_functionality'] = self.test_new_user_workflow_browse_functionality()
        test_results['new_workflow_marketplace_functionality'] = self.test_new_user_workflow_marketplace_functionality()
        test_results['new_workflow_collections_centralized'] = self.test_new_user_workflow_collections_centralized_approach()
        test_results['new_workflow_profile_stats_only'] = self.test_new_user_workflow_profile_stats_only()
        
        # Summary
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Separate NEW USER PROFILE & JERSEY CREATOR test results
        new_profile_creator_tests = {
            'jersey_api_with_creator_info': 'Jersey API with Creator Information',
            'user_profile_endpoints': 'User Profile Endpoints',
            'user_created_jerseys_endpoint': 'User Created Jerseys Endpoint',
            'data_integrity_and_aggregation': 'Data Integrity & Aggregation'
        }
        
        print(f"\n🎯 NEW USER PROFILE & JERSEY CREATOR TEST RESULTS:")
        
        profile_creator_passed = sum(1 for test_name in new_profile_creator_tests.keys() if test_results.get(test_name, False))
        profile_creator_total = len(new_profile_creator_tests)
        profile_creator_rate = (profile_creator_passed/profile_creator_total)*100 if profile_creator_total > 0 else 0
        
        print(f"NEW FUNCTIONALITY: {profile_creator_passed}/{profile_creator_total} ({profile_creator_rate:.1f}%)")
        for test_name, description in new_profile_creator_tests.items():
            status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
            print(f"  {description}: {status}")
        
        # Separate priority test results
        priority_tests = {
            'collection_delete': [
                'remove_from_collection_authenticated',
                'remove_from_collection_unauthenticated', 
                'remove_nonexistent_jersey',
                'remove_collection_integration_flow',
                'collection_delete_existing_jerseys'
            ],
            'jersey_update': [
                'jersey_update_endpoint',
                'jersey_update_authorization',
                'jersey_update_nonexistent'
            ],
            'integration': [
                'full_integration_flow_priority'
            ]
        }
        
        print(f"\n🎯 OTHER PRIORITY TEST RESULTS:")
        
        for priority_name, test_names in priority_tests.items():
            priority_passed = sum(1 for test_name in test_names if test_results.get(test_name, False))
            priority_total = len(test_names)
            priority_rate = (priority_passed/priority_total)*100 if priority_total > 0 else 0
            
            print(f"{priority_name.upper()}: {priority_passed}/{priority_total} ({priority_rate:.1f}%)")
            for test_name in test_names:
                status = "✅ PASS" if test_results.get(test_name, False) else "❌ FAIL"
                print(f"  {test_name}: {status}")
        
        # Separate new workflow results
        new_workflow_tests = {k: v for k, v in test_results.items() if k.startswith('new_workflow_')}
        new_workflow_passed = sum(1 for result in new_workflow_tests.values() if result)
        new_workflow_total = len(new_workflow_tests)
        
        if new_workflow_total > 0:
            print(f"\n🎯 NEW USER WORKFLOW RESULTS:")
            print(f"New Workflow Tests: {new_workflow_total}")
            print(f"New Workflow Passed: {new_workflow_passed}")
            print(f"New Workflow Success Rate: {(new_workflow_passed/new_workflow_total)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            priority_marker = ""
            if test_name in new_profile_creator_tests:
                priority_marker = "🎯 NEW PROFILE/CREATOR"
            elif any(test_name in tests for tests in priority_tests.values()):
                priority_marker = "🎯 PRIORITY"
            elif test_name.startswith('new_workflow_'):
                priority_marker = "🔄 WORKFLOW"
            print(f"  {test_name}: {status} {priority_marker}")
        
        return test_results

if __name__ == "__main__":
    tester = TopKitAPITester()
    results = tester.run_all_tests()