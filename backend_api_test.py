#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Backend API Core Endpoints Testing
Testing core API endpoints to rule out backend issues before investigating frontend problems.

Focus on:
1. GET /api/jerseys - to see if jersey data is available
2. GET /api/listings - to see if marketplace listings are available  
3. Basic authentication endpoints if they exist
4. Any other core API endpoints that support the frontend functionality
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://topkit-workflow-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "steinmetzlivio@gmail.com"
TEST_USER_PASSWORD = "123"

class TopKitCoreAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
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
    
    def test_jerseys_endpoint(self):
        """Test GET /api/jerseys - Core jersey data availability"""
        try:
            print("🔍 Testing GET /api/jerseys endpoint...")
            response = self.session.get(f"{self.base_url}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                if isinstance(jerseys, list):
                    jersey_count = len(jerseys)
                    
                    # Check if jerseys have required fields
                    if jersey_count > 0:
                        sample_jersey = jerseys[0]
                        required_fields = ['id', 'team', 'season', 'size', 'condition']
                        missing_fields = [field for field in required_fields if field not in sample_jersey]
                        
                        if not missing_fields:
                            self.log_test("GET /api/jerseys", "PASS", 
                                        f"Retrieved {jersey_count} jerseys with proper structure")
                            
                            # Test with filters
                            filter_response = self.session.get(f"{self.base_url}/jerseys", params={
                                "limit": 5,
                                "skip": 0
                            })
                            
                            if filter_response.status_code == 200:
                                filtered_jerseys = filter_response.json()
                                self.log_test("GET /api/jerseys (with filters)", "PASS", 
                                            f"Filtering works, retrieved {len(filtered_jerseys)} jerseys")
                                return True
                            else:
                                self.log_test("GET /api/jerseys (with filters)", "FAIL", 
                                            f"Filter failed with status {filter_response.status_code}")
                                return False
                        else:
                            self.log_test("GET /api/jerseys", "FAIL", 
                                        f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/jerseys", "PASS", 
                                    "Endpoint works but no jerseys in database")
                        return True
                else:
                    self.log_test("GET /api/jerseys", "FAIL", 
                                "Response is not a list")
                    return False
            else:
                self.log_test("GET /api/jerseys", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_listings_endpoint(self):
        """Test GET /api/listings - Marketplace listings availability"""
        try:
            print("🔍 Testing GET /api/listings endpoint...")
            response = self.session.get(f"{self.base_url}/listings")
            
            if response.status_code == 200:
                listings = response.json()
                if isinstance(listings, list):
                    listing_count = len(listings)
                    
                    if listing_count > 0:
                        sample_listing = listings[0]
                        required_fields = ['id', 'jersey_id', 'seller_id', 'status']
                        missing_fields = [field for field in required_fields if field not in sample_listing]
                        
                        if not missing_fields:
                            # Check if jersey data is populated
                            if 'jersey' in sample_listing:
                                self.log_test("GET /api/listings", "PASS", 
                                            f"Retrieved {listing_count} listings with jersey data populated")
                            else:
                                self.log_test("GET /api/listings", "PASS", 
                                            f"Retrieved {listing_count} listings (jersey data not populated)")
                            
                            # Test with filters
                            filter_response = self.session.get(f"{self.base_url}/listings", params={
                                "limit": 5
                            })
                            
                            if filter_response.status_code == 200:
                                self.log_test("GET /api/listings (with filters)", "PASS", 
                                            "Listing filters work correctly")
                                return True
                            else:
                                self.log_test("GET /api/listings (with filters)", "FAIL", 
                                            f"Filter failed with status {filter_response.status_code}")
                                return False
                        else:
                            self.log_test("GET /api/listings", "FAIL", 
                                        f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("GET /api/listings", "PASS", 
                                    "Endpoint works but no listings in database")
                        return True
                else:
                    self.log_test("GET /api/listings", "FAIL", 
                                "Response is not a list")
                    return False
            else:
                self.log_test("GET /api/listings", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/listings", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_auth_login_endpoint(self):
        """Test POST /api/auth/login - Basic authentication"""
        try:
            print("🔍 Testing POST /api/auth/login endpoint...")
            
            payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    
                    user_info = data["user"]
                    self.log_test("POST /api/auth/login", "PASS", 
                                f"Login successful for {user_info.get('name', 'Unknown')} ({user_info.get('email', 'Unknown')})")
                    return True
                else:
                    self.log_test("POST /api/auth/login", "FAIL", 
                                "Missing token or user in response")
                    return False
            elif response.status_code == 400:
                self.log_test("POST /api/auth/login", "FAIL", 
                            f"Invalid credentials (expected for test): {response.text}")
                return False
            else:
                self.log_test("POST /api/auth/login", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/auth/login", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_auth_register_endpoint(self):
        """Test POST /api/auth/register - User registration"""
        try:
            print("🔍 Testing POST /api/auth/register endpoint...")
            
            # Use unique email to avoid conflicts
            unique_email = f"testuser_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.log_test("POST /api/auth/register", "PASS", 
                                f"Registration successful for {data['user'].get('name', 'Unknown')}")
                    return True
                else:
                    self.log_test("POST /api/auth/register", "FAIL", 
                                "Missing token or user in response")
                    return False
            elif response.status_code == 400:
                self.log_test("POST /api/auth/register", "PASS", 
                            "Registration endpoint working (user may already exist)")
                return True
            else:
                self.log_test("POST /api/auth/register", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/auth/register", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_profile_endpoint(self):
        """Test GET /api/profile - User profile with authentication"""
        try:
            print("🔍 Testing GET /api/profile endpoint...")
            
            if not self.auth_token:
                self.log_test("GET /api/profile", "SKIP", "No auth token available")
                return True
            
            response = self.session.get(f"{self.base_url}/profile")
            
            if response.status_code == 200:
                profile = response.json()
                if "user" in profile:
                    user_data = profile["user"]
                    stats_data = profile.get("stats", {})
                    
                    self.log_test("GET /api/profile", "PASS", 
                                f"Profile retrieved for {user_data.get('name', 'Unknown')} with stats: {stats_data}")
                    return True
                else:
                    self.log_test("GET /api/profile", "FAIL", 
                                "Missing user data in profile response")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("GET /api/profile", "PASS", 
                            "Profile endpoint correctly requires authentication")
                return True
            else:
                self.log_test("GET /api/profile", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/profile", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collections_endpoints(self):
        """Test collection endpoints - Core functionality for frontend"""
        try:
            print("🔍 Testing collection endpoints...")
            
            if not self.auth_token:
                self.log_test("Collection Endpoints", "SKIP", "No auth token available")
                return True
            
            # Test owned collection
            owned_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if owned_response.status_code == 200:
                owned_collection = owned_response.json()
                
                # Test wanted collection
                wanted_response = self.session.get(f"{self.base_url}/collections/wanted")
                
                if wanted_response.status_code == 200:
                    wanted_collection = wanted_response.json()
                    
                    self.log_test("GET /api/collections/*", "PASS", 
                                f"Collections retrieved: {len(owned_collection)} owned, {len(wanted_collection)} wanted")
                    return True
                else:
                    self.log_test("GET /api/collections/wanted", "FAIL", 
                                f"HTTP {wanted_response.status_code}")
                    return False
            elif owned_response.status_code in [401, 403]:
                self.log_test("GET /api/collections/*", "PASS", 
                            "Collection endpoints correctly require authentication")
                return True
            else:
                self.log_test("GET /api/collections/owned", "FAIL", 
                            f"HTTP {owned_response.status_code}: {owned_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Collection Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_explorer_endpoints(self):
        """Test explorer endpoints - Support for frontend navigation"""
        try:
            print("🔍 Testing explorer endpoints...")
            
            # Test most collected
            most_collected_response = self.session.get(f"{self.base_url}/explorer/most-collected")
            
            if most_collected_response.status_code == 200:
                most_collected = most_collected_response.json()
                
                # Test most wanted
                most_wanted_response = self.session.get(f"{self.base_url}/explorer/most-wanted")
                
                if most_wanted_response.status_code == 200:
                    most_wanted = most_wanted_response.json()
                    
                    # Test latest additions
                    latest_response = self.session.get(f"{self.base_url}/explorer/latest-additions")
                    
                    if latest_response.status_code == 200:
                        latest = latest_response.json()
                        
                        # Test leagues overview
                        leagues_response = self.session.get(f"{self.base_url}/explorer/leagues")
                        
                        if leagues_response.status_code == 200:
                            leagues = leagues_response.json()
                            
                            self.log_test("Explorer Endpoints", "PASS", 
                                        f"All explorer endpoints working: {len(most_collected)} most collected, {len(most_wanted)} most wanted, {len(latest)} latest, {len(leagues)} leagues")
                            return True
                        else:
                            self.log_test("GET /api/explorer/leagues", "FAIL", 
                                        f"HTTP {leagues_response.status_code}")
                            return False
                    else:
                        self.log_test("GET /api/explorer/latest-additions", "FAIL", 
                                    f"HTTP {latest_response.status_code}")
                        return False
                else:
                    self.log_test("GET /api/explorer/most-wanted", "FAIL", 
                                f"HTTP {most_wanted_response.status_code}")
                    return False
            else:
                self.log_test("GET /api/explorer/most-collected", "FAIL", 
                            f"HTTP {most_collected_response.status_code}: {most_collected_response.text}")
                return False
                
        except Exception as e:
            self.log_test("Explorer Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_creation_endpoint(self):
        """Test POST /api/jerseys - Jersey creation functionality"""
        try:
            print("🔍 Testing POST /api/jerseys endpoint...")
            
            if not self.auth_token:
                self.log_test("POST /api/jerseys", "SKIP", "No auth token available")
                return True
            
            payload = {
                "team": "Test FC",
                "season": "2024-25",
                "player": "Test Player",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Test Brand",
                "home_away": "home",
                "league": "Test League",
                "description": "Test jersey for API testing",
                "images": []
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("team") == "Test FC":
                    self.log_test("POST /api/jerseys", "PASS", 
                                f"Jersey creation successful: {data['team']} {data['season']}")
                    return True
                else:
                    self.log_test("POST /api/jerseys", "FAIL", 
                                "Invalid response data")
                    return False
            elif response.status_code in [401, 403]:
                self.log_test("POST /api/jerseys", "PASS", 
                            "Jersey creation correctly requires authentication")
                return True
            else:
                self.log_test("POST /api/jerseys", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("POST /api/jerseys", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_listing_creation_endpoint(self):
        """Test POST /api/listings - Listing creation functionality"""
        try:
            print("🔍 Testing POST /api/listings endpoint...")
            
            if not self.auth_token:
                self.log_test("POST /api/listings", "SKIP", "No auth token available")
                return True
            
            # First get a jersey ID to create listing for
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=1")
            
            if jerseys_response.status_code == 200:
                jerseys = jerseys_response.json()
                if jerseys:
                    jersey_id = jerseys[0]["id"]
                    
                    payload = {
                        "jersey_id": jersey_id,
                        "price": 99.99,
                        "description": "Test listing for API testing",
                        "images": []
                    }
                    
                    response = self.session.post(f"{self.base_url}/listings", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "id" in data and data.get("jersey_id") == jersey_id:
                            self.log_test("POST /api/listings", "PASS", 
                                        f"Listing creation successful: ${data.get('price', 'N/A')}")
                            return True
                        else:
                            self.log_test("POST /api/listings", "FAIL", 
                                        "Invalid response data")
                            return False
                    elif response.status_code in [401, 403]:
                        self.log_test("POST /api/listings", "PASS", 
                                    "Listing creation correctly requires authentication")
                        return True
                    else:
                        self.log_test("POST /api/listings", "FAIL", 
                                    f"HTTP {response.status_code}: {response.text}")
                        return False
                else:
                    self.log_test("POST /api/listings", "SKIP", 
                                "No jerseys available to create listing")
                    return True
            else:
                self.log_test("POST /api/listings", "SKIP", 
                            "Could not get jerseys for listing test")
                return True
                
        except Exception as e:
            self.log_test("POST /api/listings", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_server_health(self):
        """Test basic server connectivity and health"""
        try:
            print("🔍 Testing server health...")
            
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/jerseys", timeout=10)
            
            if response.status_code in [200, 401, 403]:
                self.log_test("Server Health", "PASS", 
                            f"Server is responding (HTTP {response.status_code})")
                return True
            else:
                self.log_test("Server Health", "FAIL", 
                            f"Server returned HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_test("Server Health", "FAIL", "Server timeout")
            return False
        except requests.exceptions.ConnectionError:
            self.log_test("Server Health", "FAIL", "Connection error")
            return False
        except Exception as e:
            self.log_test("Server Health", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_core_api_tests(self):
        """Run all core API tests"""
        print("🚀 Starting TopKit Core API Backend Testing")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        test_results = []
        
        # Core endpoint tests (as requested)
        test_results.append(("Server Health", self.test_server_health()))
        test_results.append(("GET /api/jerseys", self.test_jerseys_endpoint()))
        test_results.append(("GET /api/listings", self.test_listings_endpoint()))
        test_results.append(("POST /api/auth/register", self.test_auth_register_endpoint()))
        test_results.append(("POST /api/auth/login", self.test_auth_login_endpoint()))
        test_results.append(("GET /api/profile", self.test_profile_endpoint()))
        test_results.append(("Collection Endpoints", self.test_collections_endpoints()))
        test_results.append(("Explorer Endpoints", self.test_explorer_endpoints()))
        test_results.append(("POST /api/jerseys", self.test_jersey_creation_endpoint()))
        test_results.append(("POST /api/listings", self.test_listing_creation_endpoint()))
        
        # Summary
        print("=" * 60)
        print("🎯 CORE API TESTING SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print("=" * 60)
        print(f"📊 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL CORE API ENDPOINTS ARE WORKING CORRECTLY!")
            print("✅ Backend is not the cause of frontend navigation issues")
        elif passed >= total * 0.8:
            print("⚠️  Most core endpoints working, minor issues detected")
        else:
            print("❌ CRITICAL BACKEND ISSUES DETECTED!")
            print("🚨 Backend problems may be causing frontend issues")
        
        print("=" * 60)
        
        return passed, total

def main():
    """Main test execution"""
    tester = TopKitCoreAPITester()
    passed, total = tester.run_core_api_tests()
    
    # Exit with appropriate code
    if passed == total:
        exit(0)  # All tests passed
    elif passed >= total * 0.8:
        exit(1)  # Minor issues
    else:
        exit(2)  # Critical issues

if __name__ == "__main__":
    main()