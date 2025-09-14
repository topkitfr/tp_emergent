#!/usr/bin/env python3
"""
RAPID TEST: Verify Backend Returns Empty List and Database is Clean
Focus: Check for phantom data as requested by user
"""

import requests
import json
import time

# Configuration
BASE_URL = "https://kit-fixes.preview.emergentagent.com/api"

class RapidEmptyDatabaseTester:
    def __init__(self):
        self.base_url = BASE_URL
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
    
    def test_get_jerseys_empty_list(self):
        """PRIORITY 1: Test GET /api/jerseys returns empty list []"""
        try:
            response = self.session.get(f"{self.base_url}/jerseys")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                if isinstance(jerseys, list):
                    if len(jerseys) == 0:
                        self.log_test("GET /api/jerseys Returns Empty List", "PASS", 
                                    "✅ API correctly returns empty list []")
                        return True
                    else:
                        self.log_test("GET /api/jerseys Returns Empty List", "FAIL", 
                                    f"❌ PHANTOM DATA DETECTED: Found {len(jerseys)} jerseys when expecting 0")
                        
                        # Show details of phantom data
                        print("   🔍 PHANTOM DATA DETAILS:")
                        for i, jersey in enumerate(jerseys[:5]):  # Show first 5
                            team = jersey.get('team', 'Unknown')
                            season = jersey.get('season', 'Unknown')
                            player = jersey.get('player', 'No player')
                            created_by = jersey.get('created_by', 'Unknown')
                            print(f"      {i+1}. {team} {season} - {player} (Created by: {created_by})")
                        
                        if len(jerseys) > 5:
                            print(f"      ... and {len(jerseys) - 5} more jerseys")
                        print()
                        return False
                else:
                    self.log_test("GET /api/jerseys Returns Empty List", "FAIL", 
                                f"❌ API returned non-list response: {type(jerseys)}")
                    return False
            else:
                self.log_test("GET /api/jerseys Returns Empty List", "FAIL", 
                            f"❌ API request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/jerseys Returns Empty List", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def test_database_collections_empty(self):
        """PRIORITY 2: Test database collections are empty"""
        try:
            # Test multiple endpoints to check for data
            endpoints_to_check = [
                ("/jerseys", "Jerseys"),
                ("/listings", "Listings"), 
                ("/market/trending", "Market Trending")
            ]
            
            all_empty = True
            phantom_data_found = []
            
            for endpoint, name in endpoints_to_check:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response formats
                    if endpoint == "/market/trending":
                        items = data.get("trending_jerseys", [])
                    else:
                        items = data if isinstance(data, list) else []
                    
                    if len(items) > 0:
                        all_empty = False
                        phantom_data_found.append(f"{name}: {len(items)} items")
                        
                        # Show sample data for jerseys
                        if endpoint == "/jerseys" and len(items) > 0:
                            print(f"   🔍 SAMPLE {name.upper()} DATA:")
                            for i, item in enumerate(items[:3]):
                                team = item.get('team', 'Unknown')
                                season = item.get('season', 'Unknown')
                                created_by = item.get('created_by', 'Unknown')
                                print(f"      {i+1}. {team} {season} (Created by: {created_by})")
                            if len(items) > 3:
                                print(f"      ... and {len(items) - 3} more items")
                            print()
                else:
                    print(f"   ⚠️ Could not check {name} (Status: {response.status_code})")
            
            if all_empty:
                self.log_test("Database Collections Empty Check", "PASS", 
                            "✅ All checked collections are empty - no phantom data")
                return True
            else:
                self.log_test("Database Collections Empty Check", "FAIL", 
                            f"❌ PHANTOM DATA DETECTED in: {', '.join(phantom_data_found)}")
                return False
                
        except Exception as e:
            self.log_test("Database Collections Empty Check", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def test_specific_phantom_data_search(self):
        """PRIORITY 3: Search for specific phantom data mentioned in test_result.md"""
        try:
            phantom_indicators = [
                ("Alex Johnson", "User name from previous tests"),
                ("2021-22", "Old season data"),
                ("Manchester United", "Frequently mentioned team"),
                ("Bruno Fernandes", "Frequently mentioned player")
            ]
            
            phantom_found = []
            
            # Check jerseys for phantom data
            response = self.session.get(f"{self.base_url}/jerseys?limit=100")
            
            if response.status_code == 200:
                jerseys = response.json()
                
                for jersey in jerseys:
                    jersey_str = json.dumps(jersey).lower()
                    
                    for indicator, description in phantom_indicators:
                        if indicator.lower() in jersey_str:
                            phantom_found.append(f"{indicator} found in jersey: {jersey.get('team', 'Unknown')} {jersey.get('season', 'Unknown')}")
            
            if len(phantom_found) == 0:
                self.log_test("Specific Phantom Data Search", "PASS", 
                            "✅ No specific phantom data indicators found")
                return True
            else:
                self.log_test("Specific Phantom Data Search", "FAIL", 
                            f"❌ PHANTOM DATA INDICATORS FOUND:")
                for phantom in phantom_found:
                    print(f"      • {phantom}")
                print()
                return False
                
        except Exception as e:
            self.log_test("Specific Phantom Data Search", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def test_backend_service_status(self):
        """PRIORITY 4: Verify backend service is responding correctly"""
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url.replace('/api', '')}")
            
            if response.status_code in [200, 404]:  # 404 is expected for root
                self.log_test("Backend Service Status", "PASS", 
                            f"✅ Backend service responding (Status: {response.status_code})")
                return True
            else:
                self.log_test("Backend Service Status", "FAIL", 
                            f"❌ Backend service issue (Status: {response.status_code})")
                return False
                
        except Exception as e:
            self.log_test("Backend Service Status", "FAIL", f"❌ Exception: {str(e)}")
            return False
    
    def run_rapid_tests(self):
        """Run all rapid tests focused on empty database verification"""
        print("🎯 RAPID EMPTY DATABASE VERIFICATION TEST")
        print("=" * 60)
        print("Focus: Verify backend returns empty list and no phantom data exists")
        print()
        
        test_results = []
        
        # Priority 1: Check GET /api/jerseys returns empty list
        print("🔍 PRIORITY 1: Testing GET /api/jerseys endpoint")
        test_results.append(self.test_get_jerseys_empty_list())
        
        # Priority 2: Check database collections are empty
        print("🔍 PRIORITY 2: Testing database collections")
        test_results.append(self.test_database_collections_empty())
        
        # Priority 3: Search for specific phantom data
        print("🔍 PRIORITY 3: Searching for specific phantom data")
        test_results.append(self.test_specific_phantom_data_search())
        
        # Priority 4: Verify backend service status
        print("🔍 PRIORITY 4: Backend service status check")
        test_results.append(self.test_backend_service_status())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("=" * 60)
        print(f"🎯 RAPID TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ RESULT: Database is clean - no phantom data detected")
            print("✅ Backend correctly returns empty list []")
        else:
            print("❌ RESULT: Phantom data detected - database cleanup needed")
            print("❌ Backend may be returning ghost data")
        
        print("=" * 60)
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = RapidEmptyDatabaseTester()
    success = tester.run_rapid_tests()
    exit(0 if success else 1)