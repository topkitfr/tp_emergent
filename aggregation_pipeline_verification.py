#!/usr/bin/env python3
"""
AGGREGATION PIPELINE VERIFICATION - COMPREHENSIVE TEST
=====================================================

This test verifies that the aggregation pipeline fix is working correctly
by adding a new Jersey Release and checking if the enriched data appears.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-collect.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class AggregationPipelineVerifier:
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

    def get_available_jersey_releases(self):
        """Get available Jersey Releases from vestiaire"""
        print("🏪 GETTING AVAILABLE JERSEY RELEASES...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                jersey_releases = response.json()
                
                self.log_result(
                    "Get Available Jersey Releases", 
                    True, 
                    f"Found {len(jersey_releases)} Jersey Releases available"
                )
                
                # Show details of first few Jersey Releases
                if jersey_releases:
                    details = "Available Jersey Releases:\n"
                    for i, jr in enumerate(jersey_releases[:3]):
                        player_name = jr.get('player_name', 'Unknown')
                        jersey_id = jr.get('id')
                        master_jersey_info = jr.get('master_jersey_info', {})
                        season = master_jersey_info.get('season', 'Unknown')
                        details += f"   {i+1}. {player_name} ({season}) - ID: {jersey_id}\n"
                    
                    print(details)
                
                return jersey_releases
            else:
                self.log_result(
                    "Get Available Jersey Releases", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Get Available Jersey Releases", False, f"Exception: {str(e)}")
            return []

    def add_jersey_release_to_collection(self, jersey_release):
        """Add a Jersey Release to collection"""
        print("➕ ADDING JERSEY RELEASE TO COLLECTION...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Add Jersey Release", False, "No authentication token")
            return False, None
            
        try:
            jersey_id = jersey_release.get('id')
            player_name = jersey_release.get('player_name', 'Unknown')
            
            headers = {"Authorization": f"Bearer {self.user_token}"}
            collection_data = {
                "jersey_release_id": jersey_id,
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
                result = response.json()
                collection_id = result.get("collection_id")
                
                self.log_result(
                    "Add Jersey Release", 
                    True, 
                    f"Successfully added {player_name} to collection (ID: {collection_id})"
                )
                return True, collection_id
                
            elif response.status_code == 400 and "already in collection" in response.text.lower():
                self.log_result(
                    "Add Jersey Release", 
                    True, 
                    f"{player_name} already in collection (expected duplicate prevention)"
                )
                return True, None
            else:
                self.log_result(
                    "Add Jersey Release", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_result("Add Jersey Release", False, f"Exception: {str(e)}")
            return False, None

    def verify_aggregation_pipeline(self, target_jersey_id):
        """Verify that aggregation pipeline populates jersey_release and master_jersey"""
        print("🔍 VERIFYING AGGREGATION PIPELINE...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Verify Aggregation Pipeline", False, "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test owned collections
            owned_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if owned_response.status_code == 200:
                owned_collections = owned_response.json()
                
                # Find collection with target Jersey Release ID
                target_collection = None
                for collection in owned_collections:
                    if collection.get('jersey_release_id') == target_jersey_id:
                        target_collection = collection
                        break
                
                if target_collection:
                    jersey_release = target_collection.get('jersey_release', {})
                    master_jersey = target_collection.get('master_jersey', {})
                    
                    # Check if data is populated
                    jersey_release_populated = bool(jersey_release and jersey_release != {} and jersey_release is not None)
                    master_jersey_populated = bool(master_jersey and master_jersey != {} and master_jersey is not None)
                    
                    success = jersey_release_populated and master_jersey_populated
                    
                    details = f"Target Jersey Release ID: {target_jersey_id}\n"
                    details += f"   Jersey Release populated: {jersey_release_populated}\n"
                    details += f"   Master Jersey populated: {master_jersey_populated}\n"
                    
                    if jersey_release_populated:
                        details += f"   Player Name: {jersey_release.get('player_name', 'Missing')}\n"
                        details += f"   Jersey Release Keys: {list(jersey_release.keys())}\n"
                    
                    if master_jersey_populated:
                        details += f"   Season: {master_jersey.get('season', 'Missing')}\n"
                        details += f"   Jersey Type: {master_jersey.get('jersey_type', 'Missing')}\n"
                        details += f"   Master Jersey Keys: {list(master_jersey.keys())}\n"
                    
                    if not success:
                        details += f"   Raw jersey_release: {jersey_release}\n"
                        details += f"   Raw master_jersey: {master_jersey}"
                    
                    self.log_result("Verify Aggregation Pipeline", success, details)
                    return success
                else:
                    self.log_result(
                        "Verify Aggregation Pipeline", 
                        False, 
                        f"Collection with Jersey Release ID {target_jersey_id} not found in owned collections"
                    )
                    return False
            else:
                self.log_result(
                    "Verify Aggregation Pipeline", 
                    False, 
                    f"Failed to get owned collections: HTTP {owned_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Verify Aggregation Pipeline", False, f"Exception: {str(e)}")
            return False

    def test_wanted_collections_aggregation(self, target_jersey_id):
        """Test wanted collections aggregation pipeline"""
        print("🎯 TESTING WANTED COLLECTIONS AGGREGATION...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Test Wanted Collections", False, "No authentication token")
            return False
            
        try:
            # First add to wanted collection
            headers = {"Authorization": f"Bearer {self.user_token}"}
            collection_data = {
                "jersey_release_id": target_jersey_id,
                "collection_type": "wanted"
            }
            
            add_response = requests.post(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                headers=headers,
                json=collection_data
            )
            
            # Don't fail if already exists
            if add_response.status_code not in [201, 400]:
                self.log_result(
                    "Test Wanted Collections", 
                    False, 
                    f"Failed to add to wanted: HTTP {add_response.status_code}"
                )
                return False
            
            # Test wanted collections aggregation
            wanted_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", headers=headers)
            
            if wanted_response.status_code == 200:
                wanted_collections = wanted_response.json()
                
                # Find collection with target Jersey Release ID
                target_collection = None
                for collection in wanted_collections:
                    if collection.get('jersey_release_id') == target_jersey_id:
                        target_collection = collection
                        break
                
                if target_collection:
                    jersey_release = target_collection.get('jersey_release', {})
                    master_jersey = target_collection.get('master_jersey', {})
                    
                    jersey_release_populated = bool(jersey_release and jersey_release != {} and jersey_release is not None)
                    master_jersey_populated = bool(master_jersey and master_jersey != {} and master_jersey is not None)
                    
                    success = jersey_release_populated and master_jersey_populated
                    
                    details = f"Wanted collections aggregation test\n"
                    details += f"   Jersey Release populated: {jersey_release_populated}\n"
                    details += f"   Master Jersey populated: {master_jersey_populated}"
                    
                    self.log_result("Test Wanted Collections", success, details)
                    return success
                else:
                    self.log_result(
                        "Test Wanted Collections", 
                        False, 
                        f"Collection not found in wanted collections"
                    )
                    return False
            else:
                self.log_result(
                    "Test Wanted Collections", 
                    False, 
                    f"Failed to get wanted collections: HTTP {wanted_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_result("Test Wanted Collections", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive aggregation pipeline verification"""
        print("🚀 STARTING AGGREGATION PIPELINE VERIFICATION")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot continue")
            return False
        
        # Step 2: Get available Jersey Releases
        jersey_releases = self.get_available_jersey_releases()
        if not jersey_releases:
            print("❌ No Jersey Releases available - cannot test")
            return False
        
        # Step 3: Use first available Jersey Release for testing
        test_jersey_release = jersey_releases[0]
        test_jersey_id = test_jersey_release.get('id')
        
        # Step 4: Add Jersey Release to collection
        add_success, collection_id = self.add_jersey_release_to_collection(test_jersey_release)
        if not add_success:
            print("❌ Failed to add Jersey Release - cannot test aggregation")
            return False
        
        # Step 5: Verify aggregation pipeline for owned collections
        owned_aggregation_success = self.verify_aggregation_pipeline(test_jersey_id)
        
        # Step 6: Test wanted collections aggregation
        wanted_aggregation_success = self.test_wanted_collections_aggregation(test_jersey_id)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 AGGREGATION PIPELINE VERIFICATION SUMMARY")
        print("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                # Print details with proper indentation
                for line in result['details'].split('\n'):
                    if line.strip():
                        print(f"   {line}")
        
        print("\n" + "=" * 70)
        
        # Final assessment
        aggregation_working = owned_aggregation_success and wanted_aggregation_success
        
        if aggregation_working:
            print("🎉 AGGREGATION PIPELINE FIX VERIFICATION: SUCCESS!")
            print("✅ Jersey Release and Master Jersey data are properly populated")
            print("✅ Collections can now display enriched data in 'Ma Collection'")
            print("✅ Both owned and wanted collections show complete data")
        else:
            print("❌ AGGREGATION PIPELINE FIX VERIFICATION: FAILED!")
            if not owned_aggregation_success:
                print("❌ Owned collections aggregation not working")
            if not wanted_aggregation_success:
                print("❌ Wanted collections aggregation not working")
            print("❌ 'Ma Collection' page will still show incomplete data")
        
        return aggregation_working

if __name__ == "__main__":
    verifier = AggregationPipelineVerifier()
    success = verifier.run_comprehensive_test()
    sys.exit(0 if success else 1)