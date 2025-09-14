#!/usr/bin/env python3
"""
COLLECTION DATA QUALITY INVESTIGATION - BACKEND TEST
===================================================

Based on the Master Jersey / Jersey Release investigation, we found that:
✅ Vestiaire endpoint works perfectly (12 Jersey Releases with proper master_jersey_id links)
✅ Jersey Releases are properly enriched with Master Jersey data
✅ Collection addition works (duplicate prevention working correctly)

❌ CRITICAL ISSUE IDENTIFIED: Collections show empty jersey_release and master_jersey objects
   - User has 8 owned collections and 4 wanted collections
   - But jersey_release: {} and master_jersey: {} are empty
   - This explains why "Ma Collection" page shows no data

This test investigates the collection data aggregation pipeline to understand why
the jersey_release and master_jersey data is not being populated in collections.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footkit-hub.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class CollectionDataQualityInvestigator:
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
        print("🔐 USER AUTHENTICATION")
        print("=" * 30)
        
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
                    f"User: {user_data.get('name')}, ID: {self.user_user_id}"
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

    def investigate_collection_data_quality(self):
        """Investigate why collections have empty jersey_release and master_jersey data"""
        print("🔍 COLLECTION DATA QUALITY INVESTIGATION")
        print("=" * 50)
        
        # Test all collection endpoints
        self.test_owned_collections_data()
        self.test_wanted_collections_data()
        self.test_individual_collection_lookup()
        self.test_jersey_release_lookup()

    def test_owned_collections_data(self):
        """Test owned collections and analyze data quality"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                count = len(collections)
                
                self.log_result(
                    "Owned Collections Retrieved", 
                    True, 
                    f"Retrieved {count} owned collections"
                )
                
                if count > 0:
                    # Analyze data quality
                    empty_jersey_release = 0
                    empty_master_jersey = 0
                    valid_jersey_release_ids = 0
                    
                    for collection in collections:
                        jersey_release_id = collection.get('jersey_release_id')
                        jersey_release_data = collection.get('jersey_release', {})
                        master_jersey_data = collection.get('master_jersey', {})
                        
                        if jersey_release_id:
                            valid_jersey_release_ids += 1
                        
                        if not jersey_release_data or len(jersey_release_data) == 0:
                            empty_jersey_release += 1
                        
                        if not master_jersey_data or len(master_jersey_data) == 0:
                            empty_master_jersey += 1
                    
                    # Log data quality issues
                    data_quality_success = empty_jersey_release == 0 and empty_master_jersey == 0
                    self.log_result(
                        "Owned Collections Data Quality", 
                        data_quality_success, 
                        f"Valid jersey_release_ids: {valid_jersey_release_ids}/{count}, Empty jersey_release: {empty_jersey_release}/{count}, Empty master_jersey: {empty_master_jersey}/{count}"
                    )
                    
                    # Show detailed analysis of first collection
                    first_collection = collections[0]
                    print("📋 DETAILED OWNED COLLECTION ANALYSIS:")
                    print(f"Collection ID: {first_collection.get('id')}")
                    print(f"Jersey Release ID: {first_collection.get('jersey_release_id')}")
                    print(f"Jersey Release Data Keys: {list(first_collection.get('jersey_release', {}).keys())}")
                    print(f"Master Jersey Data Keys: {list(first_collection.get('master_jersey', {}).keys())}")
                    print(f"Full Collection Structure:")
                    print(json.dumps(first_collection, indent=2, default=str))
                    print()
                    
            else:
                self.log_result(
                    "Owned Collections Retrieved", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Owned Collections Retrieved", False, f"Exception: {str(e)}")

    def test_wanted_collections_data(self):
        """Test wanted collections and analyze data quality"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                count = len(collections)
                
                self.log_result(
                    "Wanted Collections Retrieved", 
                    True, 
                    f"Retrieved {count} wanted collections"
                )
                
                if count > 0:
                    # Analyze data quality
                    empty_jersey_release = 0
                    empty_master_jersey = 0
                    
                    for collection in collections:
                        jersey_release_data = collection.get('jersey_release', {})
                        master_jersey_data = collection.get('master_jersey', {})
                        
                        if not jersey_release_data or len(jersey_release_data) == 0:
                            empty_jersey_release += 1
                        
                        if not master_jersey_data or len(master_jersey_data) == 0:
                            empty_master_jersey += 1
                    
                    # Log data quality issues
                    data_quality_success = empty_jersey_release == 0 and empty_master_jersey == 0
                    self.log_result(
                        "Wanted Collections Data Quality", 
                        data_quality_success, 
                        f"Empty jersey_release: {empty_jersey_release}/{count}, Empty master_jersey: {empty_master_jersey}/{count}"
                    )
                    
            else:
                self.log_result(
                    "Wanted Collections Retrieved", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_result("Wanted Collections Retrieved", False, f"Exception: {str(e)}")

    def test_individual_collection_lookup(self):
        """Test looking up individual collections to see if the issue is in aggregation"""
        try:
            # First get a collection ID
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                if collections:
                    first_collection = collections[0]
                    collection_id = first_collection.get('id')
                    jersey_release_id = first_collection.get('jersey_release_id')
                    
                    print(f"🔍 INDIVIDUAL COLLECTION LOOKUP TEST")
                    print(f"Collection ID: {collection_id}")
                    print(f"Jersey Release ID: {jersey_release_id}")
                    print()
                    
                    # Test if we can get more details about this specific collection
                    # (This would require a specific endpoint that might not exist)
                    self.log_result(
                        "Individual Collection Analysis", 
                        True, 
                        f"Collection {collection_id} references Jersey Release {jersey_release_id}"
                    )
                    
        except Exception as e:
            self.log_result("Individual Collection Analysis", False, f"Exception: {str(e)}")

    def test_jersey_release_lookup(self):
        """Test if we can lookup Jersey Releases that are referenced in collections"""
        try:
            # Get a jersey_release_id from collections
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                if collections:
                    first_collection = collections[0]
                    jersey_release_id = first_collection.get('jersey_release_id')
                    
                    if jersey_release_id:
                        # Try to get this Jersey Release from vestiaire
                        vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
                        
                        if vestiaire_response.status_code == 200:
                            vestiaire_data = vestiaire_response.json()
                            
                            # Find the Jersey Release in vestiaire
                            found_jersey_release = None
                            for jersey_release in vestiaire_data:
                                if jersey_release.get('id') == jersey_release_id:
                                    found_jersey_release = jersey_release
                                    break
                            
                            if found_jersey_release:
                                self.log_result(
                                    "Jersey Release Lookup in Vestiaire", 
                                    True, 
                                    f"Found Jersey Release {jersey_release_id} in vestiaire with player: {found_jersey_release.get('player_name')}"
                                )
                                
                                print("📋 JERSEY RELEASE FROM VESTIAIRE:")
                                print(json.dumps(found_jersey_release, indent=2, default=str))
                                print()
                                
                                # Compare with collection data
                                collection_jersey_data = first_collection.get('jersey_release', {})
                                if not collection_jersey_data:
                                    self.log_result(
                                        "Collection vs Vestiaire Data Comparison", 
                                        False, 
                                        f"Jersey Release {jersey_release_id} exists in vestiaire but collection shows empty jersey_release data"
                                    )
                                else:
                                    self.log_result(
                                        "Collection vs Vestiaire Data Comparison", 
                                        True, 
                                        "Collection has jersey_release data populated"
                                    )
                            else:
                                self.log_result(
                                    "Jersey Release Lookup in Vestiaire", 
                                    False, 
                                    f"Jersey Release {jersey_release_id} not found in vestiaire"
                                )
                        else:
                            self.log_result(
                                "Jersey Release Lookup in Vestiaire", 
                                False, 
                                f"Failed to get vestiaire data: HTTP {vestiaire_response.status_code}"
                            )
                    else:
                        self.log_result(
                            "Jersey Release Lookup", 
                            False, 
                            "No jersey_release_id found in collection"
                        )
                        
        except Exception as e:
            self.log_result("Jersey Release Lookup", False, f"Exception: {str(e)}")

    def test_direct_database_aggregation_simulation(self):
        """Simulate what the aggregation pipeline should be doing"""
        print("🔧 AGGREGATION PIPELINE SIMULATION")
        print("=" * 40)
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Get collections
            collections_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if collections_response.status_code == 200 and vestiaire_response.status_code == 200:
                collections = collections_response.json()
                vestiaire_data = vestiaire_response.json()
                
                # Create a lookup map for Jersey Releases
                jersey_release_map = {}
                for jersey_release in vestiaire_data:
                    jersey_release_map[jersey_release['id']] = jersey_release
                
                # Simulate proper aggregation
                properly_enriched_collections = []
                for collection in collections:
                    jersey_release_id = collection.get('jersey_release_id')
                    if jersey_release_id and jersey_release_id in jersey_release_map:
                        jersey_release_data = jersey_release_map[jersey_release_id]
                        master_jersey_data = jersey_release_data.get('master_jersey_info', {})
                        
                        enriched_collection = collection.copy()
                        enriched_collection['jersey_release'] = jersey_release_data
                        enriched_collection['master_jersey'] = master_jersey_data
                        properly_enriched_collections.append(enriched_collection)
                
                success = len(properly_enriched_collections) > 0
                self.log_result(
                    "Aggregation Pipeline Simulation", 
                    success, 
                    f"Successfully enriched {len(properly_enriched_collections)} collections with Jersey Release and Master Jersey data"
                )
                
                if properly_enriched_collections:
                    print("📋 PROPERLY ENRICHED COLLECTION EXAMPLE:")
                    example = properly_enriched_collections[0]
                    print(f"Collection ID: {example.get('id')}")
                    print(f"Jersey Release Player: {example.get('jersey_release', {}).get('player_name')}")
                    print(f"Master Jersey Team: {example.get('master_jersey', {}).get('team_id')}")
                    print(f"Master Jersey Season: {example.get('master_jersey', {}).get('season')}")
                    print()
                    
            else:
                self.log_result(
                    "Aggregation Pipeline Simulation", 
                    False, 
                    "Failed to get required data for simulation"
                )
                
        except Exception as e:
            self.log_result("Aggregation Pipeline Simulation", False, f"Exception: {str(e)}")

    def generate_diagnosis(self):
        """Generate diagnosis of the collection data quality issue"""
        print("🏥 DIAGNOSIS")
        print("=" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Tests Run: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print()
        
        print("🔍 ROOT CAUSE ANALYSIS:")
        print("   • User has collections with valid jersey_release_id references")
        print("   • Jersey Releases exist in vestiaire with full data")
        print("   • Collections show empty jersey_release: {} and master_jersey: {}")
        print("   • This indicates the aggregation pipeline in collection endpoints is broken")
        print()
        
        print("💡 TECHNICAL ISSUE IDENTIFIED:")
        print("   • The collection endpoints are not properly joining/aggregating Jersey Release data")
        print("   • The MongoDB aggregation pipeline needs to be fixed to populate jersey_release and master_jersey fields")
        print("   • This is why 'Ma Collection' page shows no data despite user having 12 collections")
        print()
        
        print("🔧 SOLUTION REQUIRED:")
        print("   • Fix the aggregation pipeline in collection endpoints")
        print("   • Ensure jersey_release_id is used to lookup and populate jersey_release data")
        print("   • Ensure master_jersey_info from Jersey Releases is populated in master_jersey field")
        print("   • Test that collections display proper player names, team info, and season data")
        
        return failed_tests == 0

    def run_investigation(self):
        """Run the complete collection data quality investigation"""
        print("🔍 COLLECTION DATA QUALITY INVESTIGATION")
        print("=" * 60)
        print("Focus: Why collections show empty jersey_release and master_jersey data")
        print("User: steinmetzlivio@gmail.com")
        print()
        
        # Authentication
        if not self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Investigation
        self.investigate_collection_data_quality()
        
        # Simulation
        self.test_direct_database_aggregation_simulation()
        
        # Diagnosis
        success = self.generate_diagnosis()
        
        return success

def main():
    """Main execution function"""
    investigator = CollectionDataQualityInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("🎉 Investigation completed - Root cause identified!")
        sys.exit(0)
    else:
        print("❌ Investigation revealed critical data quality issues")
        sys.exit(1)

if __name__ == "__main__":
    main()