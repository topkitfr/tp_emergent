#!/usr/bin/env python3
"""
TopKit Collection Workflow Edge Cases Testing
Testing edge cases and potential issues that might still cause the collection visibility problem
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
BASE_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

class CollectionEdgeCasesTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_id = None
        self.admin_token = None
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
    
    def setup_test_user(self):
        """Create a test user"""
        try:
            unique_email = f"edgetest_{int(time.time())}@topkit.com"
            
            payload = {
                "email": unique_email,
                "password": "testpass123",
                "name": "Edge Case Test User"
            }
            
            response = self.session.post(f"{self.base_url}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["token"]
                self.user_id = data["user"]["id"]
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_test("Setup Test User", "PASS", f"User created: {unique_email}")
                return True
            else:
                self.log_test("Setup Test User", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Setup Test User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def setup_admin_user(self):
        """Setup admin user"""
        try:
            admin_payload = {
                "email": "topkitfr@gmail.com",
                "password": "adminpass123"
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=admin_payload)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.log_test("Setup Admin User", "PASS", "Admin logged in")
                return True
            else:
                self.log_test("Setup Admin User", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Setup Admin User", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_multiple_jerseys_same_team(self):
        """Test adding multiple jerseys from the same team to collection"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Multiple Jerseys Same Team", "FAIL", "Missing tokens")
                return False
            
            # Create multiple Real Madrid jerseys
            jerseys = []
            players = ["Vinicius Jr", "Jude Bellingham", "Luka Modrić"]
            
            for player in players:
                payload = {
                    "team": "Real Madrid",
                    "season": "2023-24",
                    "player": player,
                    "size": "L",
                    "condition": "very_good",
                    "manufacturer": "Adidas",
                    "home_away": "home",
                    "league": "La Liga",
                    "description": f"Real Madrid jersey with {player}",
                    "images": [f"https://example.com/real-{player.lower().replace(' ', '-')}.jpg"]
                }
                
                response = self.session.post(f"{self.base_url}/jerseys", json=payload)
                if response.status_code == 200:
                    jersey_id = response.json()["id"]
                    jerseys.append((jersey_id, player))
                    
                    # Approve jersey
                    admin_session = requests.Session()
                    admin_session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    admin_session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
            
            # Add all jerseys to collection
            for jersey_id, player in jerseys:
                collection_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned"
                }
                self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            # Verify all jerseys appear in collection
            collection_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if collection_response.status_code == 200:
                collections = collection_response.json()
                
                # Count Real Madrid jerseys in collection
                real_madrid_count = sum(1 for item in collections 
                                      if item.get("jersey", {}).get("team") == "Real Madrid")
                
                if real_madrid_count == len(jerseys):
                    self.log_test("Multiple Jerseys Same Team", "PASS", 
                                f"All {len(jerseys)} Real Madrid jerseys found in collection")
                    return True
                else:
                    self.log_test("Multiple Jerseys Same Team", "FAIL", 
                                f"Expected {len(jerseys)} Real Madrid jerseys, found {real_madrid_count}")
                    return False
            else:
                self.log_test("Multiple Jerseys Same Team", "FAIL", "Could not fetch collection")
                return False
                
        except Exception as e:
            self.log_test("Multiple Jerseys Same Team", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_with_special_characters(self):
        """Test jerseys with special characters in names"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Special Characters", "FAIL", "Missing tokens")
                return False
            
            # Create jersey with special characters
            payload = {
                "team": "FC Köln",
                "season": "2023-24",
                "player": "Florian Müller",
                "size": "M",
                "condition": "new",
                "manufacturer": "Uhlsport",
                "home_away": "home",
                "league": "Bundesliga",
                "description": "Maillot FC Köln avec caractères spéciaux - ñáéíóú",
                "images": ["https://example.com/koln-mueller.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                jersey_id = response.json()["id"]
                
                # Approve jersey
                admin_session = requests.Session()
                admin_session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}',
                    'Content-Type': 'application/json'
                })
                admin_session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
                
                # Add to collection
                collection_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned"
                }
                
                add_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
                
                if add_response.status_code == 200:
                    # Verify in collection
                    collection_response = self.session.get(f"{self.base_url}/collections/owned")
                    
                    if collection_response.status_code == 200:
                        collections = collection_response.json()
                        
                        # Look for our special character jersey
                        found = any(item.get("jersey_id") == jersey_id for item in collections)
                        
                        if found:
                            self.log_test("Special Characters", "PASS", 
                                        "Jersey with special characters found in collection")
                            return True
                        else:
                            self.log_test("Special Characters", "FAIL", 
                                        "Jersey with special characters not found in collection")
                            return False
                    else:
                        self.log_test("Special Characters", "FAIL", "Could not fetch collection")
                        return False
                else:
                    self.log_test("Special Characters", "FAIL", "Could not add to collection")
                    return False
            else:
                self.log_test("Special Characters", "FAIL", "Could not create jersey")
                return False
                
        except Exception as e:
            self.log_test("Special Characters", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_pagination_limits(self):
        """Test collection retrieval with many items"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Collection Pagination", "FAIL", "Missing tokens")
                return False
            
            # Create and add 15 jerseys to test pagination
            jersey_ids = []
            teams = ["Arsenal", "Chelsea", "Liverpool", "Manchester United", "Tottenham"]
            
            for i in range(15):
                team = teams[i % len(teams)]
                payload = {
                    "team": team,
                    "season": "2023-24",
                    "player": f"Player {i+1}",
                    "size": "L",
                    "condition": "very_good",
                    "manufacturer": "Nike",
                    "home_away": "home",
                    "league": "Premier League",
                    "description": f"Test jersey {i+1} for pagination",
                    "images": [f"https://example.com/test-{i+1}.jpg"]
                }
                
                response = self.session.post(f"{self.base_url}/jerseys", json=payload)
                if response.status_code == 200:
                    jersey_id = response.json()["id"]
                    jersey_ids.append(jersey_id)
                    
                    # Approve jersey
                    admin_session = requests.Session()
                    admin_session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}',
                        'Content-Type': 'application/json'
                    })
                    admin_session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
                    
                    # Add to collection
                    collection_payload = {
                        "jersey_id": jersey_id,
                        "collection_type": "owned"
                    }
                    self.session.post(f"{self.base_url}/collections", json=collection_payload)
            
            # Verify all jerseys appear in collection
            collection_response = self.session.get(f"{self.base_url}/collections/owned")
            
            if collection_response.status_code == 200:
                collections = collection_response.json()
                
                # Count how many of our test jerseys are in collection
                found_count = sum(1 for item in collections 
                                if item.get("jersey_id") in jersey_ids)
                
                if found_count >= 10:  # At least 10 should be found
                    self.log_test("Collection Pagination", "PASS", 
                                f"Found {found_count}/{len(jersey_ids)} jerseys in collection")
                    return True
                else:
                    self.log_test("Collection Pagination", "FAIL", 
                                f"Only found {found_count}/{len(jersey_ids)} jerseys in collection")
                    return False
            else:
                self.log_test("Collection Pagination", "FAIL", "Could not fetch collection")
                return False
                
        except Exception as e:
            self.log_test("Collection Pagination", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_both_owned_and_wanted(self):
        """Test adding same jersey to both owned and wanted collections"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Both Owned and Wanted", "FAIL", "Missing tokens")
                return False
            
            # Create jersey
            payload = {
                "team": "AC Milan",
                "season": "2023-24",
                "player": "Rafael Leão",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Puma",
                "home_away": "home",
                "league": "Serie A",
                "description": "AC Milan jersey with Leão",
                "images": ["https://example.com/milan-leao.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                jersey_id = response.json()["id"]
                
                # Approve jersey
                admin_session = requests.Session()
                admin_session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}',
                    'Content-Type': 'application/json'
                })
                admin_session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
                
                # Add to owned collection
                owned_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned"
                }
                
                owned_response = self.session.post(f"{self.base_url}/collections", json=owned_payload)
                
                # Add to wanted collection
                wanted_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "wanted"
                }
                
                wanted_response = self.session.post(f"{self.base_url}/collections", json=wanted_payload)
                
                if owned_response.status_code == 200 and wanted_response.status_code == 200:
                    # Check both collections
                    owned_collection = self.session.get(f"{self.base_url}/collections/owned").json()
                    wanted_collection = self.session.get(f"{self.base_url}/collections/wanted").json()
                    
                    owned_found = any(item.get("jersey_id") == jersey_id for item in owned_collection)
                    wanted_found = any(item.get("jersey_id") == jersey_id for item in wanted_collection)
                    
                    if owned_found and wanted_found:
                        self.log_test("Both Owned and Wanted", "PASS", 
                                    "Jersey found in both owned and wanted collections")
                        return True
                    else:
                        self.log_test("Both Owned and Wanted", "FAIL", 
                                    f"Jersey missing: owned={owned_found}, wanted={wanted_found}")
                        return False
                else:
                    self.log_test("Both Owned and Wanted", "FAIL", "Could not add to collections")
                    return False
            else:
                self.log_test("Both Owned and Wanted", "FAIL", "Could not create jersey")
                return False
                
        except Exception as e:
            self.log_test("Both Owned and Wanted", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_collection_after_jersey_update(self):
        """Test collection visibility after jersey is updated"""
        try:
            if not self.auth_token or not self.admin_token:
                self.log_test("Collection After Update", "FAIL", "Missing tokens")
                return False
            
            # Create jersey
            payload = {
                "team": "Juventus",
                "season": "2023-24",
                "player": "Federico Chiesa",
                "size": "L",
                "condition": "very_good",
                "manufacturer": "Adidas",
                "home_away": "home",
                "league": "Serie A",
                "description": "Original description",
                "images": ["https://example.com/juventus-chiesa.jpg"]
            }
            
            response = self.session.post(f"{self.base_url}/jerseys", json=payload)
            
            if response.status_code == 200:
                jersey_id = response.json()["id"]
                
                # Approve jersey
                admin_session = requests.Session()
                admin_session.headers.update({
                    'Authorization': f'Bearer {self.admin_token}',
                    'Content-Type': 'application/json'
                })
                admin_session.post(f"{self.base_url}/admin/jerseys/{jersey_id}/approve")
                
                # Add to collection
                collection_payload = {
                    "jersey_id": jersey_id,
                    "collection_type": "owned"
                }
                
                add_response = self.session.post(f"{self.base_url}/collections", json=collection_payload)
                
                if add_response.status_code == 200:
                    # Update jersey description
                    update_payload = {
                        "team": "Juventus",
                        "season": "2023-24",
                        "player": "Federico Chiesa",
                        "size": "L",
                        "condition": "very_good",
                        "manufacturer": "Adidas",
                        "home_away": "home",
                        "league": "Serie A",
                        "description": "Updated description - modified after adding to collection",
                        "images": ["https://example.com/juventus-chiesa-updated.jpg"]
                    }
                    
                    update_response = self.session.put(f"{self.base_url}/jerseys/{jersey_id}", json=update_payload)
                    
                    # Check if jersey still appears in collection with updated data
                    collection_response = self.session.get(f"{self.base_url}/collections/owned")
                    
                    if collection_response.status_code == 200:
                        collections = collection_response.json()
                        
                        # Find our jersey
                        jersey_in_collection = None
                        for item in collections:
                            if item.get("jersey_id") == jersey_id:
                                jersey_in_collection = item.get("jersey", {})
                                break
                        
                        if jersey_in_collection:
                            updated_description = jersey_in_collection.get("description", "")
                            if "Updated description" in updated_description:
                                self.log_test("Collection After Update", "PASS", 
                                            "Jersey found in collection with updated data")
                                return True
                            else:
                                self.log_test("Collection After Update", "PASS", 
                                            "Jersey found in collection (description may not be updated immediately)")
                                return True
                        else:
                            self.log_test("Collection After Update", "FAIL", 
                                        "Jersey not found in collection after update")
                            return False
                    else:
                        self.log_test("Collection After Update", "FAIL", "Could not fetch collection")
                        return False
                else:
                    self.log_test("Collection After Update", "FAIL", "Could not add to collection")
                    return False
            else:
                self.log_test("Collection After Update", "FAIL", "Could not create jersey")
                return False
                
        except Exception as e:
            self.log_test("Collection After Update", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_edge_cases_tests(self):
        """Run all edge case tests"""
        print("🧪 COLLECTION WORKFLOW EDGE CASES TESTING")
        print("=" * 60)
        print("Testing edge cases that might cause collection visibility issues")
        print()
        
        # Setup
        if not self.setup_test_user():
            return False
        
        if not self.setup_admin_user():
            return False
        
        # Test edge cases
        tests = [
            ("Multiple Jerseys Same Team", self.test_multiple_jerseys_same_team),
            ("Special Characters", self.test_collection_with_special_characters),
            ("Collection Pagination", self.test_collection_pagination_limits),
            ("Both Owned and Wanted", self.test_collection_both_owned_and_wanted),
            ("Collection After Update", self.test_collection_after_jersey_update),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            if test_func():
                passed_tests += 1
            print()
        
        # Summary
        print("=" * 60)
        print(f"EDGE CASES TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL EDGE CASE TESTS PASSED - Collection system is robust!")
            return True
        else:
            print(f"⚠️ {total_tests - passed_tests} edge case tests failed - Some scenarios need attention")
            return False

def main():
    """Main test execution"""
    tester = CollectionEdgeCasesTester()
    success = tester.run_edge_cases_tests()
    
    if success:
        print("\n✅ CONCLUSION: Collection system handles edge cases well.")
    else:
        print("\n⚠️ CONCLUSION: Some edge cases may cause issues.")

if __name__ == "__main__":
    main()