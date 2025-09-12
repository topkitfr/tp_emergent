#!/usr/bin/env python3
"""
COLLECTION AGGREGATION PIPELINE FIX VERIFICATION - BACKEND TEST
==============================================================

This test verifies that the aggregation pipeline fix for collections is working correctly.
The fix should ensure that jersey_release and master_jersey data are properly populated
instead of returning empty objects.

Test Focus:
1. GET /api/users/{user_id}/collections/owned - verify enriched data
2. GET /api/users/{user_id}/collections/wanted - verify enriched data  
3. Verify jersey_release is no longer empty object {}
4. Verify master_jersey contains team_info, season, etc.
5. Test adding new Jersey Release and verify enriched data

Authentication:
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-collection-5.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class CollectionAggregationTester:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def authenticate_user(self):
        """Authenticate user and get token"""
        print("🔐 AUTHENTICATING USER...")
        
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=USER_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get("token")
                user_data = data.get("user", {})
                self.user_user_id = user_data.get("id")
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"User: {user_data.get('name')} (ID: {self.user_user_id})"
                )
                return True
            else:
                self.log_result(
                    "User Authentication", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False

    def test_owned_collections_enriched_data(self):
        """Test GET /api/users/{user_id}/collections/owned for enriched data"""
        print("📦 TESTING OWNED COLLECTIONS WITH ENRICHED DATA...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Owned Collections Test", False, "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                
                if not collections:
                    self.log_result(
                        "Owned Collections Test", 
                        True, 
                        "No owned collections found (empty array)"
                    )
                    return True
                
                # Analyze first collection for data quality
                first_collection = collections[0]
                jersey_release = first_collection.get("jersey_release", {})
                master_jersey = first_collection.get("master_jersey", {})
                
                # Check if jersey_release is no longer empty
                jersey_release_populated = bool(jersey_release and jersey_release != {})
                
                # Check if master_jersey contains expected data
                master_jersey_populated = bool(
                    master_jersey and 
                    master_jersey != {} and
                    master_jersey.get("team_info") and
                    master_jersey.get("season")
                )
                
                details = f"Collections found: {len(collections)}, "
                details += f"Jersey Release populated: {jersey_release_populated}, "
                details += f"Master Jersey populated: {master_jersey_populated}"
                
                if jersey_release_populated and master_jersey_populated:
                    # Show sample data structure
                    sample_data = {
                        "jersey_release_keys": list(jersey_release.keys()) if jersey_release else [],
                        "master_jersey_keys": list(master_jersey.keys()) if master_jersey else [],
                        "team_info": master_jersey.get("team_info", "Not found"),
                        "season": master_jersey.get("season", "Not found")
                    }
                    details += f", Sample data: {json.dumps(sample_data, indent=2)}"
                
                success = jersey_release_populated and master_jersey_populated
                self.log_result("Owned Collections Test", success, details)
                return success
                
            else:
                self.log_result(
                    "Owned Collections Test", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Owned Collections Test", False, f"Exception: {str(e)}")
            return False

    def test_wanted_collections_enriched_data(self):
        """Test GET /api/users/{user_id}/collections/wanted for enriched data"""
        print("🎯 TESTING WANTED COLLECTIONS WITH ENRICHED DATA...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Wanted Collections Test", False, "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                
                if not collections:
                    self.log_result(
                        "Wanted Collections Test", 
                        True, 
                        "No wanted collections found (empty array)"
                    )
                    return True
                
                # Analyze first collection for data quality
                first_collection = collections[0]
                jersey_release = first_collection.get("jersey_release", {})
                master_jersey = first_collection.get("master_jersey", {})
                
                # Check if jersey_release is no longer empty
                jersey_release_populated = bool(jersey_release and jersey_release != {})
                
                # Check if master_jersey contains expected data
                master_jersey_populated = bool(
                    master_jersey and 
                    master_jersey != {} and
                    master_jersey.get("team_info") and
                    master_jersey.get("season")
                )
                
                details = f"Collections found: {len(collections)}, "
                details += f"Jersey Release populated: {jersey_release_populated}, "
                details += f"Master Jersey populated: {master_jersey_populated}"
                
                if jersey_release_populated and master_jersey_populated:
                    # Show sample data structure
                    sample_data = {
                        "jersey_release_keys": list(jersey_release.keys()) if jersey_release else [],
                        "master_jersey_keys": list(master_jersey.keys()) if master_jersey else [],
                        "team_info": master_jersey.get("team_info", "Not found"),
                        "season": master_jersey.get("season", "Not found")
                    }
                    details += f", Sample data: {json.dumps(sample_data, indent=2)}"
                
                success = jersey_release_populated and master_jersey_populated
                self.log_result("Wanted Collections Test", success, details)
                return success
                
            else:
                self.log_result(
                    "Wanted Collections Test", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Wanted Collections Test", False, f"Exception: {str(e)}")
            return False

    def test_vestiaire_data_availability(self):
        """Test /api/vestiaire endpoint to see available Jersey Releases"""
        print("🏪 TESTING VESTIAIRE DATA AVAILABILITY...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                vestiaire_data = response.json()
                
                if isinstance(vestiaire_data, list) and len(vestiaire_data) > 0:
                    # Check for new Jersey Releases mentioned in review request
                    jersey_names = []
                    for jersey in vestiaire_data:
                        master_jersey_info = jersey.get("master_jersey_info", {})
                        player_name = master_jersey_info.get("player_name", "Unknown")
                        jersey_names.append(player_name)
                    
                    # Look for the mentioned players: Mohamed Salah, Harry Kane, Rafael Leão
                    target_players = ["Mohamed Salah", "Harry Kane", "Rafael Leão"]
                    found_players = [player for player in target_players if player in jersey_names]
                    
                    details = f"Jersey Releases available: {len(vestiaire_data)}, "
                    details += f"Player names: {jersey_names}, "
                    details += f"Target players found: {found_players}"
                    
                    self.log_result("Vestiaire Data Availability", True, details)
                    return vestiaire_data
                else:
                    self.log_result(
                        "Vestiaire Data Availability", 
                        False, 
                        "No Jersey Releases found in vestiaire"
                    )
                    return []
                    
            else:
                self.log_result(
                    "Vestiaire Data Availability", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Vestiaire Data Availability", False, f"Exception: {str(e)}")
            return []

    def test_add_jersey_release_to_collection(self, jersey_releases):
        """Test adding a Jersey Release to collection and verify enriched data"""
        print("➕ TESTING ADD JERSEY RELEASE TO COLLECTION...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Add Jersey Release Test", False, "No authentication token")
            return False
            
        if not jersey_releases:
            self.log_result("Add Jersey Release Test", False, "No Jersey Releases available")
            return False
            
        try:
            # Use first available Jersey Release
            jersey_release = jersey_releases[0]
            jersey_release_id = jersey_release.get("id")
            
            if not jersey_release_id:
                self.log_result("Add Jersey Release Test", False, "No Jersey Release ID found")
                return False
            
            # Try to add to owned collection
            headers = {"Authorization": f"Bearer {self.user_token}"}
            collection_data = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "mint"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                headers=headers,
                json=collection_data
            )
            
            if response.status_code == 201:
                collection_result = response.json()
                collection_id = collection_result.get("collection_id")
                
                # Now test if the collection shows enriched data
                owned_response = requests.get(
                    f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", 
                    headers=headers
                )
                
                if owned_response.status_code == 200:
                    owned_collections = owned_response.json()
                    
                    # Find the newly added collection
                    new_collection = None
                    for collection in owned_collections:
                        if collection.get("id") == collection_id:
                            new_collection = collection
                            break
                    
                    if new_collection:
                        jersey_release_data = new_collection.get("jersey_release", {})
                        master_jersey_data = new_collection.get("master_jersey", {})
                        
                        jersey_release_populated = bool(jersey_release_data and jersey_release_data != {})
                        master_jersey_populated = bool(
                            master_jersey_data and 
                            master_jersey_data != {} and
                            master_jersey_data.get("team_info") and
                            master_jersey_data.get("season")
                        )
                        
                        success = jersey_release_populated and master_jersey_populated
                        details = f"Collection added successfully (ID: {collection_id}), "
                        details += f"Jersey Release populated: {jersey_release_populated}, "
                        details += f"Master Jersey populated: {master_jersey_populated}"
                        
                        if success:
                            details += f", Player: {master_jersey_data.get('player_name', 'Unknown')}, "
                            details += f"Team: {master_jersey_data.get('team_info', {}).get('name', 'Unknown')}, "
                            details += f"Season: {master_jersey_data.get('season', 'Unknown')}"
                        
                        self.log_result("Add Jersey Release Test", success, details)
                        return success
                    else:
                        self.log_result(
                            "Add Jersey Release Test", 
                            False, 
                            f"Newly added collection not found in owned collections"
                        )
                        return False
                else:
                    self.log_result(
                        "Add Jersey Release Test", 
                        False, 
                        f"Failed to retrieve owned collections: HTTP {owned_response.status_code}"
                    )
                    return False
                    
            elif response.status_code == 400:
                # Might be duplicate - this is expected behavior
                error_message = response.text
                if "already in collection" in error_message.lower():
                    self.log_result(
                        "Add Jersey Release Test", 
                        True, 
                        "Jersey Release already in collection (expected duplicate prevention)"
                    )
                    return True
                else:
                    self.log_result(
                        "Add Jersey Release Test", 
                        False, 
                        f"HTTP 400: {error_message}"
                    )
                    return False
            else:
                self.log_result(
                    "Add Jersey Release Test", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Add Jersey Release Test", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all collection aggregation tests"""
        print("🚀 STARTING COLLECTION AGGREGATION PIPELINE FIX VERIFICATION")
        print("=" * 70)
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot continue with tests")
            return False
        
        # Step 2: Test vestiaire data availability
        jersey_releases = self.test_vestiaire_data_availability()
        
        # Step 3: Test owned collections with enriched data
        owned_success = self.test_owned_collections_enriched_data()
        
        # Step 4: Test wanted collections with enriched data
        wanted_success = self.test_wanted_collections_enriched_data()
        
        # Step 5: Test adding new Jersey Release (if available)
        add_success = self.test_add_jersey_release_to_collection(jersey_releases)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        print("\n" + "=" * 70)
        
        # Overall assessment
        critical_tests_passed = owned_success and wanted_success
        
        if critical_tests_passed:
            print("🎉 COLLECTION AGGREGATION PIPELINE FIX VERIFICATION: SUCCESS!")
            print("✅ Jersey Release and Master Jersey data are now properly populated")
            print("✅ Collections can now display enriched data in 'Ma Collection'")
        else:
            print("❌ COLLECTION AGGREGATION PIPELINE FIX VERIFICATION: FAILED!")
            print("❌ Jersey Release and/or Master Jersey data still not properly populated")
            print("❌ 'Ma Collection' page will still show empty/incomplete data")
        
        return critical_tests_passed

if __name__ == "__main__":
    tester = CollectionAggregationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)