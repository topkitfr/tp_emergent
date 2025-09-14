#!/usr/bin/env python3
"""
TopKit Jersey Buttons Issue Testing
Focus: Testing why "Add to Owned/Wanted" buttons are not appearing on jersey cards
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://image-fix-10.preview.emergentagent.com/api"

class TopKitJerseyButtonsTester:
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
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        try:
            # Use unique email to avoid conflicts
            unique_email = f"jerseytest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "password123",
                "name": "Jersey Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_id = data["user"]["id"]
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log_test("Authentication Setup", "PASS", f"User registered with ID: {self.user_id}")
                    return True
                else:
                    self.log_test("Authentication Setup", "FAIL", "Missing token or user in response")
                    return False
            else:
                self.log_test("Authentication Setup", "FAIL", f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jerseys_database_content(self):
        """Test if there are jerseys in the database"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=50")
            
            if response.status_code == 200:
                jerseys = response.json()
                jersey_count = len(jerseys)
                
                if jersey_count == 0:
                    self.log_test("Jerseys Database Content", "FAIL", 
                                "❌ CRITICAL ISSUE: Database contains 0 jerseys! This explains why no jersey cards are showing on Browse Jerseys page.")
                    return False
                else:
                    self.log_test("Jerseys Database Content", "PASS", 
                                f"✅ Database contains {jersey_count} jerseys. Jersey data is available.")
                    
                    # Show sample jersey data
                    if jerseys:
                        sample_jersey = jerseys[0]
                        print(f"   Sample Jersey: {sample_jersey.get('team', 'N/A')} {sample_jersey.get('season', 'N/A')} - {sample_jersey.get('player', 'N/A')}")
                    
                    return True
            else:
                self.log_test("Jerseys Database Content", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jerseys Database Content", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_create_sample_jerseys(self):
        """Create sample jerseys if database is empty"""
        try:
            if not self.auth_token:
                self.log_test("Create Sample Jerseys", "FAIL", "No authentication token")
                return False
            
            sample_jerseys = [
                {
                    "team": "Manchester United",
                    "season": "2023-24",
                    "player": "Bruno Fernandes",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": "Official Manchester United home jersey with Bruno Fernandes #8",
                    "images": ["https://example.com/manutd-bruno.jpg"]
                },
                {
                    "team": "Real Madrid",
                    "season": "2023-24",
                    "player": "Vinicius Jr",
                    "size": "M",
                    "condition": "mint",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": "Official Real Madrid home jersey with Vinicius Jr #7",
                    "images": ["https://example.com/realmadrid-vini.jpg"]
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
                    "description": "Official Liverpool FC home jersey with Mohamed Salah #11",
                    "images": ["https://example.com/liverpool-salah.jpg"]
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
                    "description": "Official FC Barcelona home jersey with Lewandowski #9",
                    "images": ["https://example.com/barca-lewa.jpg"]
                },
                {
                    "team": "Paris Saint-Germain",
                    "season": "2023-24",
                    "player": "Kylian Mbappé",
                    "size": "L",
                    "condition": "excellent",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Ligue 1",
                    "description": "Official PSG home jersey with Kylian Mbappé #7",
                    "images": ["https://example.com/psg-mbappe.jpg"]
                }
            ]
            
            created_jerseys = []
            
            for jersey_data in sample_jerseys:
                response = self.session.post(f"{self.base_url}/jerseys", json=jersey_data)
                
                if response.status_code == 200:
                    jersey = response.json()
                    created_jerseys.append(jersey["id"])
                    print(f"   ✅ Created: {jersey_data['team']} {jersey_data['season']} - {jersey_data['player']}")
                else:
                    print(f"   ❌ Failed to create: {jersey_data['team']} - Status: {response.status_code}")
            
            if created_jerseys:
                self.log_test("Create Sample Jerseys", "PASS", 
                            f"Successfully created {len(created_jerseys)} sample jerseys for testing")
                return created_jerseys
            else:
                self.log_test("Create Sample Jerseys", "FAIL", "No jerseys were created")
                return []
                
        except Exception as e:
            self.log_test("Create Sample Jerseys", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_collections_endpoints(self):
        """Test collections endpoints (Add to Owned/Wanted functionality)"""
        try:
            if not self.auth_token:
                self.log_test("Collections Endpoints", "FAIL", "No authentication token")
                return False
            
            # First get a jersey to test with
            jerseys_response = self.session.get(f"{self.base_url}/jerseys?limit=1")
            
            if jerseys_response.status_code != 200:
                self.log_test("Collections Endpoints", "FAIL", "Could not get jerseys for testing")
                return False
            
            jerseys = jerseys_response.json()
            if not jerseys:
                self.log_test("Collections Endpoints", "FAIL", "No jerseys available for testing")
                return False
            
            test_jersey_id = jerseys[0]["id"]
            test_jersey_name = f"{jerseys[0].get('team', 'Unknown')} {jerseys[0].get('season', 'N/A')}"
            
            # Test adding to owned collection
            owned_payload = {
                "jersey_id": test_jersey_id,
                "collection_type": "owned"
            }
            
            owned_response = self.session.post(f"{self.base_url}/collections", json=owned_payload)
            
            if owned_response.status_code == 200:
                print(f"   ✅ Successfully added {test_jersey_name} to OWNED collection")
                
                # Test adding to wanted collection
                wanted_payload = {
                    "jersey_id": test_jersey_id,
                    "collection_type": "wanted"
                }
                
                wanted_response = self.session.post(f"{self.base_url}/collections", json=wanted_payload)
                
                if wanted_response.status_code == 200:
                    print(f"   ✅ Successfully added {test_jersey_name} to WANTED collection")
                    
                    # Test getting collections
                    owned_collection_response = self.session.get(f"{self.base_url}/collections/owned")
                    wanted_collection_response = self.session.get(f"{self.base_url}/collections/wanted")
                    
                    if owned_collection_response.status_code == 200 and wanted_collection_response.status_code == 200:
                        owned_collection = owned_collection_response.json()
                        wanted_collection = wanted_collection_response.json()
                        
                        self.log_test("Collections Endpoints", "PASS", 
                                    f"✅ Collections API working: {len(owned_collection)} owned, {len(wanted_collection)} wanted jerseys")
                        return True
                    else:
                        self.log_test("Collections Endpoints", "FAIL", "Could not retrieve collections")
                        return False
                else:
                    self.log_test("Collections Endpoints", "FAIL", f"Failed to add to wanted collection: {wanted_response.status_code}")
                    return False
            else:
                self.log_test("Collections Endpoints", "FAIL", f"Failed to add to owned collection: {owned_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Collections Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints"""
        try:
            # Test registration with new user
            unique_email = f"authtest_{int(time.time())}@topkit.com"
            
            register_payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Auth Test User"
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", json=register_payload)
            
            if register_response.status_code == 200:
                register_data = register_response.json()
                
                if "token" in register_data and "user" in register_data:
                    print(f"   ✅ Registration successful for {register_data['user']['email']}")
                    
                    # Test login
                    login_payload = {
                        "email": unique_email,
                        "password": "testpass123"
                    }
                    
                    login_response = self.session.post(f"{self.base_url}/auth/login", json=login_payload)
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        
                        if "token" in login_data and "user" in login_data:
                            print(f"   ✅ Login successful for {login_data['user']['email']}")
                            
                            # Test profile access with token
                            test_headers = {'Authorization': f'Bearer {login_data["token"]}'}
                            profile_response = self.session.get(f"{self.base_url}/profile", headers=test_headers)
                            
                            if profile_response.status_code == 200:
                                profile_data = profile_response.json()
                                
                                if "user" in profile_data and "stats" in profile_data:
                                    self.log_test("Authentication Endpoints", "PASS", 
                                                "✅ Authentication flow working: Register → Login → Profile access")
                                    return True
                                else:
                                    self.log_test("Authentication Endpoints", "FAIL", "Profile data incomplete")
                                    return False
                            else:
                                self.log_test("Authentication Endpoints", "FAIL", f"Profile access failed: {profile_response.status_code}")
                                return False
                        else:
                            self.log_test("Authentication Endpoints", "FAIL", "Login response missing token/user")
                            return False
                    else:
                        self.log_test("Authentication Endpoints", "FAIL", f"Login failed: {login_response.status_code}")
                        return False
                else:
                    self.log_test("Authentication Endpoints", "FAIL", "Registration response missing token/user")
                    return False
            else:
                self.log_test("Authentication Endpoints", "FAIL", f"Registration failed: {register_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Endpoints", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_jersey_card_data_structure(self):
        """Test that jersey data has all fields needed for frontend jersey cards"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys?limit=5")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                if not jerseys:
                    self.log_test("Jersey Card Data Structure", "FAIL", "No jerseys to test data structure")
                    return False
                
                # Check required fields for jersey cards
                required_fields = ["id", "team", "season", "player", "size", "condition", "manufacturer", "home_away", "league", "description"]
                
                all_jerseys_valid = True
                missing_fields_summary = {}
                
                for jersey in jerseys:
                    missing_fields = []
                    for field in required_fields:
                        if field not in jersey or jersey[field] is None:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        all_jerseys_valid = False
                        jersey_name = f"{jersey.get('team', 'Unknown')} {jersey.get('season', 'N/A')}"
                        missing_fields_summary[jersey_name] = missing_fields
                
                if all_jerseys_valid:
                    self.log_test("Jersey Card Data Structure", "PASS", 
                                f"✅ All {len(jerseys)} jerseys have complete data structure for frontend cards")
                    
                    # Show sample jersey structure
                    sample = jerseys[0]
                    print(f"   Sample Jersey Structure:")
                    print(f"   - Team: {sample.get('team')}")
                    print(f"   - Season: {sample.get('season')}")
                    print(f"   - Player: {sample.get('player')}")
                    print(f"   - Size: {sample.get('size')}")
                    print(f"   - Condition: {sample.get('condition')}")
                    print(f"   - League: {sample.get('league')}")
                    
                    return True
                else:
                    self.log_test("Jersey Card Data Structure", "FAIL", 
                                f"❌ Some jerseys missing required fields: {missing_fields_summary}")
                    return False
            else:
                self.log_test("Jersey Card Data Structure", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jersey Card Data Structure", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run comprehensive test to diagnose jersey buttons issue"""
        print("🔍 TOPKIT JERSEY BUTTONS ISSUE DIAGNOSIS")
        print("=" * 60)
        print("Testing why 'Add to Owned/Wanted' buttons are not appearing on jersey cards")
        print()
        
        # Test 1: Check if jerseys exist in database
        print("📊 STEP 1: Checking Jersey Database Content")
        jerseys_exist = self.test_jerseys_database_content()
        
        # If no jerseys, create sample data
        if not jerseys_exist:
            print("\n🔧 STEP 1.1: Creating Sample Jersey Data")
            self.setup_authentication()
            created_jerseys = self.test_create_sample_jerseys()
            
            if created_jerseys:
                print("\n📊 STEP 1.2: Re-checking Jersey Database Content")
                self.test_jerseys_database_content()
        
        print("\n🔐 STEP 2: Testing Authentication System")
        auth_working = self.test_authentication_endpoints()
        
        print("\n📋 STEP 3: Testing Collections Functionality")
        if not self.auth_token:
            self.setup_authentication()
        collections_working = self.test_collections_endpoints()
        
        print("\n📄 STEP 4: Testing Jersey Card Data Structure")
        data_structure_valid = self.test_jersey_card_data_structure()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSIS SUMMARY")
        print("=" * 60)
        
        if jerseys_exist:
            print("✅ Jersey Data: Database contains jerseys - data available for frontend")
        else:
            print("❌ Jersey Data: Database was empty - this would cause 0 jersey cards to display")
        
        if auth_working:
            print("✅ Authentication: Working correctly - users can register/login")
        else:
            print("❌ Authentication: Issues detected - may prevent button functionality")
        
        if collections_working:
            print("✅ Collections API: Working correctly - Add to Owned/Wanted functionality available")
        else:
            print("❌ Collections API: Issues detected - buttons may not work even if visible")
        
        if data_structure_valid:
            print("✅ Data Structure: Jersey data complete - frontend should render cards properly")
        else:
            print("❌ Data Structure: Missing fields - may cause rendering issues")
        
        print("\n🔍 ROOT CAUSE ANALYSIS:")
        if not jerseys_exist:
            print("❌ PRIMARY ISSUE: Empty jersey database explains why Browse Jerseys page shows 0 cards")
            print("   → No jersey cards = No 'Add to Owned/Wanted' buttons visible")
            print("   → Solution: Populate database with jersey data")
        elif not auth_working:
            print("❌ SECONDARY ISSUE: Authentication problems may prevent button functionality")
            print("   → Users need to be logged in to see collection buttons")
        elif not collections_working:
            print("❌ SECONDARY ISSUE: Collections API problems prevent button functionality")
            print("   → Buttons may be visible but not functional")
        else:
            print("✅ Backend systems appear functional - issue may be frontend-specific")
            print("   → Check frontend jersey card rendering and button visibility logic")

if __name__ == "__main__":
    tester = TopKitJerseyButtonsTester()
    tester.run_comprehensive_test()