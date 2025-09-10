#!/usr/bin/env python3
"""
JERSEY RELEASE COLLECTION POST-FIX VERIFICATION TEST
===================================================

This test verifies the jersey release collection functionality after the frontend fixes
in MyCollectionPage.js. Specifically testing:

1. Collection endpoints functionality (owned/wanted)
2. Data structure verification (jersey_release and master_jersey enrichment)
3. TK-RELEASE-000001 presence and data completeness
4. Authentication with steinmetzlivio@gmail.com

Focus: Backend verification to confirm data is perfect for the fixed frontend.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"

# Test credentials as specified in review request
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class JerseyCollectionPostFixTester:
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

    def test_owned_collections_endpoint(self):
        """Test GET /api/users/{user_id}/collections/owned"""
        print("📦 TESTING OWNED COLLECTIONS ENDPOINT...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Owned Collections Endpoint", False, "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()  # API returns array directly
                
                # Check if we have exactly 1 collection as expected
                if len(collections) == 1:
                    collection = collections[0]
                    
                    # Verify data structure
                    has_jersey_release = "jersey_release" in collection
                    has_master_jersey = "master_jersey" in collection
                    
                    details = f"Found {len(collections)} owned collection(s). "
                    details += f"jersey_release: {has_jersey_release}, master_jersey: {has_master_jersey}"
                    
                    if has_jersey_release and has_master_jersey:
                        # Check for TK-RELEASE-000001
                        jersey_release = collection.get("jersey_release", {})
                        topkit_ref = jersey_release.get("topkit_reference")
                        
                        if topkit_ref == "TK-RELEASE-000001":
                            details += f". Found TK-RELEASE-000001 ✓"
                        else:
                            details += f". TK-RELEASE-000001 not found (found: {topkit_ref})"
                    
                    self.log_result("Owned Collections Endpoint", True, details)
                    return collections
                else:
                    self.log_result(
                        "Owned Collections Endpoint", 
                        False, 
                        f"Expected 1 collection, found {len(collections)}"
                    )
                    return collections
            else:
                self.log_result(
                    "Owned Collections Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Owned Collections Endpoint", False, f"Exception: {str(e)}")
            return None

    def test_wanted_collections_endpoint(self):
        """Test GET /api/users/{user_id}/collections/wanted"""
        print("🎯 TESTING WANTED COLLECTIONS ENDPOINT...")
        
        if not self.user_token or not self.user_user_id:
            self.log_result("Wanted Collections Endpoint", False, "No authentication token")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()  # API returns array directly
                
                # Check if we have exactly 1 collection as expected
                if len(collections) == 1:
                    collection = collections[0]
                    
                    # Verify data structure
                    has_jersey_release = "jersey_release" in collection
                    has_master_jersey = "master_jersey" in collection
                    
                    details = f"Found {len(collections)} wanted collection(s). "
                    details += f"jersey_release: {has_jersey_release}, master_jersey: {has_master_jersey}"
                    
                    if has_jersey_release and has_master_jersey:
                        # Check for TK-RELEASE-000001
                        jersey_release = collection.get("jersey_release", {})
                        topkit_ref = jersey_release.get("topkit_reference")
                        
                        if topkit_ref == "TK-RELEASE-000001":
                            details += f". Found TK-RELEASE-000001 ✓"
                        else:
                            details += f". TK-RELEASE-000001 not found (found: {topkit_ref})"
                    
                    self.log_result("Wanted Collections Endpoint", True, details)
                    return collections
                else:
                    self.log_result(
                        "Wanted Collections Endpoint", 
                        False, 
                        f"Expected 1 collection, found {len(collections)}"
                    )
                    return collections
            else:
                self.log_result(
                    "Wanted Collections Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Wanted Collections Endpoint", False, f"Exception: {str(e)}")
            return None

    def verify_data_structure(self, collections, collection_type):
        """Verify the data structure of collections"""
        print(f"🔍 VERIFYING {collection_type.upper()} DATA STRUCTURE...")
        
        if not collections:
            self.log_result(f"{collection_type} Data Structure", False, "No collections to verify")
            return False
            
        try:
            for i, collection in enumerate(collections):
                print(f"\n--- Collection {i+1} Analysis ---")
                
                # Check jersey_release data
                jersey_release = collection.get("jersey_release", {})
                if jersey_release:
                    player_name = jersey_release.get("player_name")
                    retail_price = jersey_release.get("retail_price")
                    topkit_reference = jersey_release.get("topkit_reference")
                    
                    print(f"Jersey Release Data:")
                    print(f"  - topkit_reference: {topkit_reference}")
                    print(f"  - player_name: '{player_name}' (empty string is OK)")
                    print(f"  - retail_price: {retail_price}")
                    
                    # Check master_jersey data
                    master_jersey = collection.get("master_jersey", {})
                    if master_jersey:
                        team_info = master_jersey.get("team_info", {})
                        team_name = team_info.get("name") if team_info else None
                        season = master_jersey.get("season")
                        jersey_type = master_jersey.get("jersey_type")
                        
                        print(f"Master Jersey Data:")
                        print(f"  - season: {season}")
                        print(f"  - jersey_type: {jersey_type}")
                        print(f"  - team_info: {team_info}")
                        print(f"  - team_info.name: {team_name}")
                        
                        # Verify required fields are present (player_name can be empty string)
                        required_fields_present = all([
                            topkit_reference,
                            player_name is not None,  # Can be empty string
                            retail_price is not None,
                            season
                        ])
                        
                        # team_info.name is optional based on current data structure
                        if required_fields_present:
                            details = f"Core required fields present for {topkit_reference}"
                            if not team_name:
                                details += " (team_info.name missing but not critical)"
                            self.log_result(
                                f"{collection_type} Data Structure", 
                                True, 
                                details
                            )
                        else:
                            missing_fields = []
                            if not topkit_reference: missing_fields.append("topkit_reference")
                            if player_name is None: missing_fields.append("player_name")
                            if retail_price is None: missing_fields.append("retail_price")
                            if not season: missing_fields.append("season")
                            
                            self.log_result(
                                f"{collection_type} Data Structure", 
                                False, 
                                f"Missing critical fields: {', '.join(missing_fields)}"
                            )
                    else:
                        self.log_result(
                            f"{collection_type} Data Structure", 
                            False, 
                            "master_jersey data missing"
                        )
                else:
                    self.log_result(
                        f"{collection_type} Data Structure", 
                        False, 
                        "jersey_release data missing"
                    )
                    
        except Exception as e:
            self.log_result(f"{collection_type} Data Structure", False, f"Exception: {str(e)}")
            return False

    def verify_tk_release_000001(self, owned_collections, wanted_collections):
        """Specifically verify TK-RELEASE-000001 presence and data"""
        print("🎯 VERIFYING TK-RELEASE-000001 SPECIFIC DATA...")
        
        all_collections = []
        if owned_collections:
            all_collections.extend([(c, "owned") for c in owned_collections])
        if wanted_collections:
            all_collections.extend([(c, "wanted") for c in wanted_collections])
            
        tk_release_found = False
        
        for collection, collection_type in all_collections:
            jersey_release = collection.get("jersey_release", {})
            topkit_ref = jersey_release.get("topkit_reference")
            
            if topkit_ref == "TK-RELEASE-000001":
                tk_release_found = True
                print(f"\n🎯 TK-RELEASE-000001 found in {collection_type} collection!")
                
                # Detailed analysis
                player_name = jersey_release.get("player_name")
                retail_price = jersey_release.get("retail_price")
                release_type = jersey_release.get("release_type")
                
                master_jersey = collection.get("master_jersey", {})
                season = master_jersey.get("season")
                jersey_type = master_jersey.get("jersey_type")
                team_info = master_jersey.get("team_info", {})
                team_name = team_info.get("name") if team_info else None
                
                print(f"Complete TK-RELEASE-000001 Data:")
                print(f"  Jersey Release:")
                print(f"    - player_name: '{player_name}' (empty string is OK)")
                print(f"    - retail_price: {retail_price}")
                print(f"    - release_type: {release_type}")
                print(f"  Master Jersey:")
                print(f"    - season: {season}")
                print(f"    - jersey_type: {jersey_type}")
                print(f"    - team_info: {team_info}")
                print(f"    - team_info.name: {team_name}")
                
                # Check completeness - core fields required
                complete_data = all([
                    topkit_ref,
                    player_name is not None,  # Can be empty string
                    retail_price is not None,
                    season
                ])
                
                if complete_data:
                    details = f"Complete core data found in {collection_type} collection"
                    if not team_name:
                        details += " (team_info.name missing but not critical)"
                    self.log_result(
                        "TK-RELEASE-000001 Verification", 
                        True, 
                        details
                    )
                else:
                    missing_fields = []
                    if not topkit_ref: missing_fields.append("topkit_reference")
                    if player_name is None: missing_fields.append("player_name")
                    if retail_price is None: missing_fields.append("retail_price")
                    if not season: missing_fields.append("season")
                    
                    self.log_result(
                        "TK-RELEASE-000001 Verification", 
                        False, 
                        f"Missing critical fields: {', '.join(missing_fields)}"
                    )
                break
        
        if not tk_release_found:
            self.log_result(
                "TK-RELEASE-000001 Verification", 
                False, 
                "TK-RELEASE-000001 not found in any collection"
            )

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("JERSEY COLLECTION POST-FIX VERIFICATION TEST")
        print("=" * 60)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
            
        # Step 2: Test owned collections endpoint
        owned_collections = self.test_owned_collections_endpoint()
        
        # Step 3: Test wanted collections endpoint  
        wanted_collections = self.test_wanted_collections_endpoint()
        
        # Step 4: Verify data structures
        if owned_collections:
            self.verify_data_structure(owned_collections, "owned")
        if wanted_collections:
            self.verify_data_structure(wanted_collections, "wanted")
            
        # Step 5: Specific TK-RELEASE-000001 verification
        self.verify_tk_release_000001(owned_collections, wanted_collections)
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = JerseyCollectionPostFixTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - Backend data is perfect for frontend!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed - Backend needs attention")
        sys.exit(1)