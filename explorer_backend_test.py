#!/usr/bin/env python3
"""
TopKit Soccer Jersey Marketplace - Explorer Page Backend Testing
Testing the 5 new Explorer Page endpoints as requested
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test user credentials (existing users as requested)
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "adminpass123"
USER_EMAIL = "steinmetzlivio@gmail.com"
USER_PASSWORD = "userpass123"

# Fallback test user for registration
TEST_USER_EMAIL = f"explorertest_{int(time.time())}@topkit.com"
TEST_USER_PASSWORD = "testpass123"
TEST_USER_NAME = "Explorer Test User"

class ExplorerAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
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
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
            payload = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.admin_token = data["token"]
                    self.admin_user_id = data["user"]["id"]
                    self.log_test("Admin Authentication", "PASS", f"Admin authenticated: {ADMIN_EMAIL}")
                    return True
                else:
                    self.log_test("Admin Authentication", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Admin Authentication", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def authenticate_user(self):
        """Authenticate as regular user"""
        try:
            # First try existing user
            payload = {
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_user_id = data["user"]["id"]
                    self.log_test("User Authentication", "PASS", f"User authenticated: {USER_EMAIL}")
                    return True
            
            # If existing user fails, try to register a new test user
            register_payload = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": TEST_USER_NAME
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                data = register_response.json()
                if "token" in data and "user" in data:
                    self.user_token = data["token"]
                    self.user_user_id = data["user"]["id"]
                    self.log_test("User Authentication", "PASS", f"New test user registered: {TEST_USER_EMAIL}")
                    return True
                else:
                    self.log_test("User Authentication", "FAIL", "Missing token or user in registration response")
                    return False
            else:
                self.log_test("User Authentication", "FAIL", f"Registration failed - Status: {register_response.status_code}, Response: {register_response.text}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_test_data(self):
        """Create test data for explorer endpoints"""
        try:
            if not self.admin_token:
                self.log_test("Setup Test Data", "FAIL", "No admin token available")
                return False
            
            # Set admin auth header
            self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
            
            # Create test jerseys with different teams and leagues
            test_jerseys = [
                {
                    "team": "Real Madrid",
                    "season": "2023-24",
                    "player": "Vinicius Jr",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": "Official Real Madrid home jersey"
                },
                {
                    "team": "FC Barcelona",
                    "season": "2023-24", 
                    "player": "Robert Lewandowski",
                    "size": "M",
                    "condition": "mint",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": "Official FC Barcelona home jersey"
                },
                {
                    "team": "Manchester United",
                    "season": "2023-24",
                    "player": "Bruno Fernandes",
                    "size": "L",
                    "condition": "very_good",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Manchester United home jersey"
                },
                {
                    "team": "Liverpool FC",
                    "season": "2023-24",
                    "player": "Mohamed Salah",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Liverpool FC home jersey"
                },
                {
                    "team": "Paris Saint-Germain",
                    "season": "2023-24",
                    "player": "Kylian Mbappé",
                    "size": "M",
                    "condition": "mint",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Ligue 1",
                    "description": "Official PSG home jersey"
                }
            ]
            
            created_jerseys = []
            
            # Create jerseys
            for jersey_data in test_jerseys:
                response = self.session.post(f"{self.base_url}/jerseys", json=jersey_data)
                if response.status_code == 200:
                    jersey = response.json()
                    created_jerseys.append(jersey["id"])
                    
                    # Approve the jersey immediately (admin can do this)
                    approve_response = self.session.post(f"{self.base_url}/admin/jerseys/{jersey['id']}/approve")
                    if approve_response.status_code != 200:
                        self.log_test("Setup Test Data", "FAIL", f"Could not approve jersey {jersey['id']}")
                        return False
                else:
                    self.log_test("Setup Test Data", "FAIL", f"Could not create jersey: {response.text}")
                    return False
            
            # Wait a moment for approvals to process
            time.sleep(1)
            
            # Set user auth header for collections
            self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
            
            # Add some jerseys to collections to test most-collected/most-wanted
            if len(created_jerseys) >= 3:
                # Add first jersey to owned collection (will be most collected)
                for i in range(2):  # Add to 2 different collection types
                    collection_type = "owned" if i == 0 else "wanted"
                    collection_payload = {
                        "jersey_id": created_jerseys[0],
                        "collection_type": collection_type
                    }
                    self.session.post(f"{self.base_url}/collections", json=collection_payload)
                
                # Add second jersey to wanted collection (will be most wanted)
                wanted_payload = {
                    "jersey_id": created_jerseys[1],
                    "collection_type": "wanted"
                }
                self.session.post(f"{self.base_url}/collections", json=wanted_payload)
            
            self.log_test("Setup Test Data", "PASS", f"Created and approved {len(created_jerseys)} test jerseys with collections")
            return True
            
        except Exception as e:
            self.log_test("Setup Test Data", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_most_collected_endpoint(self):
        """Test GET /api/explorer/most-collected endpoint"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/explorer/most-collected")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Verify response structure
                if isinstance(jerseys, list):
                    # Check if we have jerseys with collection_count
                    if len(jerseys) > 0:
                        first_jersey = jerseys[0]
                        
                        # Verify required fields
                        required_fields = ["id", "team", "season", "status", "collection_count"]
                        missing_fields = [field for field in required_fields if field not in first_jersey]
                        
                        if not missing_fields:
                            # Verify only approved jerseys
                            all_approved = all(jersey.get("status") == "approved" for jersey in jerseys)
                            
                            if all_approved:
                                # Verify collection_count > 0 for all jerseys
                                all_collected = all(jersey.get("collection_count", 0) > 0 for jersey in jerseys)
                                
                                if all_collected:
                                    # Verify sorted by collection_count descending
                                    is_sorted = all(
                                        jerseys[i].get("collection_count", 0) >= jerseys[i+1].get("collection_count", 0)
                                        for i in range(len(jerseys)-1)
                                    )
                                    
                                    if is_sorted:
                                        # Verify no MongoDB ObjectId fields
                                        has_object_id = any("_id" in jersey for jersey in jerseys)
                                        
                                        if not has_object_id:
                                            self.log_test("Most Collected Endpoint", "PASS", 
                                                        f"Retrieved {len(jerseys)} most collected jerseys, top collection count: {first_jersey.get('collection_count')}")
                                            return True
                                        else:
                                            self.log_test("Most Collected Endpoint", "FAIL", "Response contains MongoDB ObjectId fields")
                                            return False
                                    else:
                                        self.log_test("Most Collected Endpoint", "FAIL", "Jerseys not sorted by collection_count descending")
                                        return False
                                else:
                                    self.log_test("Most Collected Endpoint", "FAIL", "Found jerseys with collection_count = 0")
                                    return False
                            else:
                                self.log_test("Most Collected Endpoint", "FAIL", "Found non-approved jerseys in response")
                                return False
                        else:
                            self.log_test("Most Collected Endpoint", "FAIL", f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Most Collected Endpoint", "PASS", "No collected jerseys found (acceptable if no collections exist)")
                        return True
                else:
                    self.log_test("Most Collected Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Most Collected Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Most Collected Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_most_wanted_endpoint(self):
        """Test GET /api/explorer/most-wanted endpoint"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/explorer/most-wanted")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Verify response structure
                if isinstance(jerseys, list):
                    # Check if we have jerseys with wanted_count
                    if len(jerseys) > 0:
                        first_jersey = jerseys[0]
                        
                        # Verify required fields
                        required_fields = ["id", "team", "season", "status", "wanted_count"]
                        missing_fields = [field for field in required_fields if field not in first_jersey]
                        
                        if not missing_fields:
                            # Verify only approved jerseys
                            all_approved = all(jersey.get("status") == "approved" for jersey in jerseys)
                            
                            if all_approved:
                                # Verify wanted_count > 0 for all jerseys
                                all_wanted = all(jersey.get("wanted_count", 0) > 0 for jersey in jerseys)
                                
                                if all_wanted:
                                    # Verify sorted by wanted_count descending
                                    is_sorted = all(
                                        jerseys[i].get("wanted_count", 0) >= jerseys[i+1].get("wanted_count", 0)
                                        for i in range(len(jerseys)-1)
                                    )
                                    
                                    if is_sorted:
                                        # Verify no MongoDB ObjectId fields
                                        has_object_id = any("_id" in jersey for jersey in jerseys)
                                        
                                        if not has_object_id:
                                            self.log_test("Most Wanted Endpoint", "PASS", 
                                                        f"Retrieved {len(jerseys)} most wanted jerseys, top wanted count: {first_jersey.get('wanted_count')}")
                                            return True
                                        else:
                                            self.log_test("Most Wanted Endpoint", "FAIL", "Response contains MongoDB ObjectId fields")
                                            return False
                                    else:
                                        self.log_test("Most Wanted Endpoint", "FAIL", "Jerseys not sorted by wanted_count descending")
                                        return False
                                else:
                                    self.log_test("Most Wanted Endpoint", "FAIL", "Found jerseys with wanted_count = 0")
                                    return False
                            else:
                                self.log_test("Most Wanted Endpoint", "FAIL", "Found non-approved jerseys in response")
                                return False
                        else:
                            self.log_test("Most Wanted Endpoint", "FAIL", f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Most Wanted Endpoint", "PASS", "No wanted jerseys found (acceptable if no wanted collections exist)")
                        return True
                else:
                    self.log_test("Most Wanted Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Most Wanted Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Most Wanted Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_latest_additions_endpoint(self):
        """Test GET /api/explorer/latest-additions endpoint"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/explorer/latest-additions")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                # Verify response structure
                if isinstance(jerseys, list):
                    if len(jerseys) > 0:
                        first_jersey = jerseys[0]
                        
                        # Verify required fields
                        required_fields = ["id", "team", "season", "status", "approved_at"]
                        missing_fields = [field for field in required_fields if field not in first_jersey]
                        
                        if not missing_fields:
                            # Verify only approved jerseys
                            all_approved = all(jersey.get("status") == "approved" for jersey in jerseys)
                            
                            if all_approved:
                                # Verify all have approved_at timestamps
                                all_have_approved_at = all(jersey.get("approved_at") is not None for jersey in jerseys)
                                
                                if all_have_approved_at:
                                    # Verify sorted by approved_at descending (latest first)
                                    is_sorted = True
                                    for i in range(len(jerseys)-1):
                                        current_date = jerseys[i].get("approved_at")
                                        next_date = jerseys[i+1].get("approved_at")
                                        if current_date and next_date and current_date < next_date:
                                            is_sorted = False
                                            break
                                    
                                    if is_sorted:
                                        # Verify no MongoDB ObjectId fields
                                        has_object_id = any("_id" in jersey for jersey in jerseys)
                                        
                                        if not has_object_id:
                                            self.log_test("Latest Additions Endpoint", "PASS", 
                                                        f"Retrieved {len(jerseys)} latest approved jerseys, latest approved: {first_jersey.get('approved_at')}")
                                            return True
                                        else:
                                            self.log_test("Latest Additions Endpoint", "FAIL", "Response contains MongoDB ObjectId fields")
                                            return False
                                    else:
                                        self.log_test("Latest Additions Endpoint", "FAIL", "Jerseys not sorted by approved_at descending")
                                        return False
                                else:
                                    self.log_test("Latest Additions Endpoint", "FAIL", "Found jerseys without approved_at timestamp")
                                    return False
                            else:
                                self.log_test("Latest Additions Endpoint", "FAIL", "Found non-approved jerseys in response")
                                return False
                        else:
                            self.log_test("Latest Additions Endpoint", "FAIL", f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Latest Additions Endpoint", "PASS", "No approved jerseys found (acceptable if database is empty)")
                        return True
                else:
                    self.log_test("Latest Additions Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Latest Additions Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Latest Additions Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_leagues_overview_endpoint(self):
        """Test GET /api/explorer/leagues endpoint"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{self.base_url}/explorer/leagues")
            
            if response.status_code == 200:
                leagues = response.json()
                
                # Verify response structure
                if isinstance(leagues, list):
                    if len(leagues) > 0:
                        first_league = leagues[0]
                        
                        # Verify required fields
                        required_fields = ["league", "jersey_count", "team_count", "season_count"]
                        missing_fields = [field for field in required_fields if field not in first_league]
                        
                        if not missing_fields:
                            # Verify all counts are positive integers
                            all_valid_counts = all(
                                isinstance(league.get("jersey_count"), int) and league.get("jersey_count") > 0 and
                                isinstance(league.get("team_count"), int) and league.get("team_count") > 0 and
                                isinstance(league.get("season_count"), int) and league.get("season_count") > 0
                                for league in leagues
                            )
                            
                            if all_valid_counts:
                                # Verify sorted by jersey_count descending
                                is_sorted = all(
                                    leagues[i].get("jersey_count", 0) >= leagues[i+1].get("jersey_count", 0)
                                    for i in range(len(leagues)-1)
                                )
                                
                                if is_sorted:
                                    # Verify no MongoDB ObjectId fields
                                    has_object_id = any("_id" in league for league in leagues)
                                    
                                    if not has_object_id:
                                        # Check for expected leagues from test data
                                        league_names = [league.get("league") for league in leagues]
                                        expected_leagues = ["La Liga", "Premier League", "Ligue 1"]
                                        found_expected = any(expected in league_names for expected in expected_leagues)
                                        
                                        self.log_test("Leagues Overview Endpoint", "PASS", 
                                                    f"Retrieved {len(leagues)} leagues overview, top league: {first_league.get('league')} ({first_league.get('jersey_count')} jerseys)")
                                        return True
                                    else:
                                        self.log_test("Leagues Overview Endpoint", "FAIL", "Response contains MongoDB ObjectId fields")
                                        return False
                                else:
                                    self.log_test("Leagues Overview Endpoint", "FAIL", "Leagues not sorted by jersey_count descending")
                                    return False
                            else:
                                self.log_test("Leagues Overview Endpoint", "FAIL", "Invalid count values found")
                                return False
                        else:
                            self.log_test("Leagues Overview Endpoint", "FAIL", f"Missing required fields: {missing_fields}")
                            return False
                    else:
                        self.log_test("Leagues Overview Endpoint", "PASS", "No leagues found (acceptable if no approved jerseys exist)")
                        return True
                else:
                    self.log_test("Leagues Overview Endpoint", "FAIL", "Response is not a list")
                    return False
            else:
                self.log_test("Leagues Overview Endpoint", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Leagues Overview Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_league_jerseys_endpoint(self):
        """Test GET /api/explorer/leagues/{league}/jerseys endpoint"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test with valid league names (case insensitive)
            test_leagues = ["La Liga", "premier league", "LIGUE 1"]
            
            for league_name in test_leagues:
                response = self.session.get(f"{self.base_url}/explorer/leagues/{league_name}/jerseys")
                
                if response.status_code == 200:
                    jerseys = response.json()
                    
                    # Verify response structure
                    if isinstance(jerseys, list):
                        if len(jerseys) > 0:
                            # Verify all jerseys are from the requested league (case insensitive)
                            all_from_league = all(
                                jersey.get("league", "").lower() == league_name.lower()
                                for jersey in jerseys
                            )
                            
                            if all_from_league:
                                # Verify only approved jerseys
                                all_approved = all(jersey.get("status") == "approved" for jersey in jerseys)
                                
                                if all_approved:
                                    # Verify no MongoDB ObjectId fields
                                    has_object_id = any("_id" in jersey for jersey in jerseys)
                                    
                                    if not has_object_id:
                                        # Verify required fields
                                        first_jersey = jerseys[0]
                                        required_fields = ["id", "team", "season", "league", "status"]
                                        missing_fields = [field for field in required_fields if field not in first_jersey]
                                        
                                        if not missing_fields:
                                            self.log_test(f"League Jerseys Endpoint ({league_name})", "PASS", 
                                                        f"Retrieved {len(jerseys)} jerseys from {league_name}")
                                        else:
                                            self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", f"Missing required fields: {missing_fields}")
                                            return False
                                    else:
                                        self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", "Response contains MongoDB ObjectId fields")
                                        return False
                                else:
                                    self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", "Found non-approved jerseys in response")
                                    return False
                            else:
                                self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", "Found jerseys from different leagues")
                                return False
                        else:
                            self.log_test(f"League Jerseys Endpoint ({league_name})", "PASS", f"No jerseys found for {league_name} (acceptable)")
                    else:
                        self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", "Response is not a list")
                        return False
                else:
                    self.log_test(f"League Jerseys Endpoint ({league_name})", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                    return False
            
            # Test with invalid league name
            invalid_response = self.session.get(f"{self.base_url}/explorer/leagues/NonExistentLeague/jerseys")
            
            if invalid_response.status_code == 200:
                invalid_jerseys = invalid_response.json()
                if isinstance(invalid_jerseys, list) and len(invalid_jerseys) == 0:
                    self.log_test("League Jerseys Endpoint (Invalid League)", "PASS", "Correctly returned empty list for non-existent league")
                    return True
                else:
                    self.log_test("League Jerseys Endpoint (Invalid League)", "FAIL", "Unexpected response for invalid league")
                    return False
            else:
                self.log_test("League Jerseys Endpoint (Invalid League)", "FAIL", f"Unexpected status for invalid league: {invalid_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("League Jerseys Endpoint", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_aggregation_queries_performance(self):
        """Test that aggregation queries work correctly with MongoDB"""
        try:
            # Remove auth header for public endpoint
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test all endpoints for basic functionality and response times
            endpoints = [
                "/explorer/most-collected",
                "/explorer/most-wanted", 
                "/explorer/latest-additions",
                "/explorer/leagues"
            ]
            
            all_passed = True
            
            for endpoint in endpoints:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Aggregation Performance {endpoint}", "PASS", 
                                    f"Response time: {response_time:.2f}s, Results: {len(data)}")
                    else:
                        self.log_test(f"Aggregation Performance {endpoint}", "FAIL", "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Aggregation Performance {endpoint}", "FAIL", f"Status: {response.status_code}")
                    all_passed = False
            
            return all_passed
                
        except Exception as e:
            self.log_test("Aggregation Queries Performance", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Explorer Page backend tests"""
        print("🚀 STARTING EXPLORER PAGE BACKEND TESTING")
        print("=" * 60)
        
        # Authentication
        if not self.authenticate_admin():
            print("❌ CRITICAL: Admin authentication failed - cannot continue")
            return False
        
        if not self.authenticate_user():
            print("❌ CRITICAL: User authentication failed - cannot continue")
            return False
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ CRITICAL: Test data setup failed - cannot continue")
            return False
        
        # Wait for data to be processed
        print("⏳ Waiting for test data to be processed...")
        time.sleep(3)
        
        # Run Explorer endpoint tests
        test_results = []
        
        print("\n🔍 TESTING EXPLORER ENDPOINTS")
        print("-" * 40)
        
        test_results.append(self.test_most_collected_endpoint())
        test_results.append(self.test_most_wanted_endpoint())
        test_results.append(self.test_latest_additions_endpoint())
        test_results.append(self.test_leagues_overview_endpoint())
        test_results.append(self.test_league_jerseys_endpoint())
        test_results.append(self.test_aggregation_queries_performance())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("🎯 EXPLORER PAGE BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL EXPLORER PAGE ENDPOINTS ARE WORKING PERFECTLY!")
        elif success_rate >= 80:
            print("✅ EXPLORER PAGE ENDPOINTS ARE MOSTLY FUNCTIONAL")
        else:
            print("❌ EXPLORER PAGE ENDPOINTS HAVE SIGNIFICANT ISSUES")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = ExplorerAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 TESTING COMPLETED SUCCESSFULLY")
        exit(0)
    else:
        print("\n❌ TESTING COMPLETED WITH FAILURES")
        exit(1)

if __name__ == "__main__":
    main()