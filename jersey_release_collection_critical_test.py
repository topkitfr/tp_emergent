#!/usr/bin/env python3
"""
CRITICAL JERSEY RELEASE COLLECTION BUG INVESTIGATION - BACKEND TEST
================================================================

This test investigates the CRITICAL issue reported where:
- User created Jersey Release TK-RELEASE-000001
- Clicked "possédé" but no confirmation message
- Jersey doesn't appear in "Ma Collection"

URGENT TESTS TO PERFORM:
1. Verify Jersey Release TK-RELEASE-000001 exists in database
2. Test GET /api/vestiaire to confirm it appears
3. Test POST /api/users/{user_id}/collections with user steinmetzlivio@gmail.com/T0p_Mdp_1288*
4. Test GET /api/users/{user_id}/collections/owned and wanted
5. Verify complete workflow: Vestiaire → Add to Collection → Appears in "Ma Collection"

Authentication: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class JerseyReleaseCollectionCriticalTester:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        self.test_results = []
        self.target_jersey_release_id = "TK-RELEASE-000001"  # The specific Jersey Release mentioned
        
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
                    f"User: {user_data.get('name')}, ID: {self.user_user_id}, Role: {user_data.get('role')}"
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

    def test_vestiaire_endpoint(self):
        """Test GET /api/vestiaire endpoint and look for TK-RELEASE-000001"""
        print("🏪 TESTING VESTIAIRE ENDPOINT...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if it's an array
                if isinstance(data, list):
                    jersey_releases = data
                    total_count = len(jersey_releases)
                    
                    # Look for the specific Jersey Release TK-RELEASE-000001
                    target_found = False
                    target_details = None
                    
                    for jr in jersey_releases:
                        if jr.get('id') == self.target_jersey_release_id or jr.get('reference') == self.target_jersey_release_id:
                            target_found = True
                            target_details = {
                                "id": jr.get('id'),
                                "reference": jr.get('reference'),
                                "master_jersey_info": jr.get('master_jersey_info', {}),
                                "price": jr.get('price'),
                                "created_by": jr.get('created_by')
                            }
                            break
                    
                    if target_found:
                        self.log_result(
                            "Vestiaire Endpoint - Target Jersey Release Found", 
                            True, 
                            f"Found TK-RELEASE-000001 in vestiaire with {total_count} total releases. Details: {json.dumps(target_details, indent=2)}"
                        )
                    else:
                        # List all available Jersey Releases for debugging
                        available_releases = [{"id": jr.get('id'), "reference": jr.get('reference')} for jr in jersey_releases[:5]]
                        self.log_result(
                            "Vestiaire Endpoint - Target Jersey Release NOT Found", 
                            False, 
                            f"TK-RELEASE-000001 NOT found in {total_count} releases. First 5 releases: {json.dumps(available_releases, indent=2)}"
                        )
                    
                    return jersey_releases, target_found, target_details
                else:
                    self.log_result(
                        "Vestiaire Endpoint", 
                        False, 
                        f"Expected array but got: {type(data)}. Data: {data}"
                    )
                    return [], False, None
            else:
                self.log_result(
                    "Vestiaire Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return [], False, None
                
        except Exception as e:
            self.log_result("Vestiaire Endpoint", False, f"Exception: {str(e)}")
            return [], False, None

    def test_add_to_owned_collection(self, jersey_release_id):
        """Test adding Jersey Release to owned collection"""
        print("👕 TESTING ADD TO OWNED COLLECTION...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {
                "jersey_release_id": jersey_release_id,
                "collection_type": "owned"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                json=payload, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Add to Owned Collection", 
                    True, 
                    f"Successfully added to owned collection. Response: {json.dumps(data, indent=2)}"
                )
                return True, data
            elif response.status_code == 400:
                # Check if it's a duplicate error (which might be expected)
                error_text = response.text
                if "already in collection" in error_text.lower():
                    self.log_result(
                        "Add to Owned Collection - Duplicate Prevention", 
                        True, 
                        f"Jersey Release already in collection (expected behavior): {error_text}"
                    )
                    return True, {"message": "Already in collection"}
                else:
                    self.log_result(
                        "Add to Owned Collection", 
                        False, 
                        f"HTTP 400 (Bad Request): {error_text}"
                    )
                    return False, None
            else:
                self.log_result(
                    "Add to Owned Collection", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False, None
                
        except Exception as e:
            self.log_result("Add to Owned Collection", False, f"Exception: {str(e)}")
            return False, None

    def test_get_owned_collections(self):
        """Test GET /api/users/{user_id}/collections/owned"""
        print("📋 TESTING GET OWNED COLLECTIONS...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    collections_count = len(data)
                    
                    # Look for our target Jersey Release in collections
                    target_in_collection = False
                    collection_details = []
                    
                    for collection in data:
                        collection_info = {
                            "collection_id": collection.get('id'),
                            "jersey_release_id": collection.get('jersey_release_id'),
                            "jersey_release": collection.get('jersey_release', {}),
                            "master_jersey": collection.get('master_jersey', {}),
                            "added_at": collection.get('added_at')
                        }
                        collection_details.append(collection_info)
                        
                        # Check if this is our target Jersey Release
                        jr_id = collection.get('jersey_release_id')
                        jr_data = collection.get('jersey_release', {})
                        if jr_id == self.target_jersey_release_id or jr_data.get('id') == self.target_jersey_release_id:
                            target_in_collection = True
                    
                    if target_in_collection:
                        self.log_result(
                            "Get Owned Collections - Target Found", 
                            True, 
                            f"Found target Jersey Release in {collections_count} owned collections"
                        )
                    else:
                        self.log_result(
                            "Get Owned Collections - Target NOT Found", 
                            False, 
                            f"Target Jersey Release NOT found in {collections_count} owned collections. Collections: {json.dumps(collection_details[:3], indent=2)}"
                        )
                    
                    return data, target_in_collection
                else:
                    self.log_result(
                        "Get Owned Collections", 
                        False, 
                        f"Expected array but got: {type(data)}. Data: {data}"
                    )
                    return [], False
            else:
                self.log_result(
                    "Get Owned Collections", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return [], False
                
        except Exception as e:
            self.log_result("Get Owned Collections", False, f"Exception: {str(e)}")
            return [], False

    def test_get_wanted_collections(self):
        """Test GET /api/users/{user_id}/collections/wanted"""
        print("🎯 TESTING GET WANTED COLLECTIONS...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                collections_count = len(data) if isinstance(data, list) else 0
                
                self.log_result(
                    "Get Wanted Collections", 
                    True, 
                    f"Retrieved {collections_count} wanted collections"
                )
                return data
            else:
                self.log_result(
                    "Get Wanted Collections", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Get Wanted Collections", False, f"Exception: {str(e)}")
            return []

    def test_general_collections_endpoint(self):
        """Test GET /api/users/{user_id}/collections (general endpoint)"""
        print("📚 TESTING GENERAL COLLECTIONS ENDPOINT...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                collections_count = len(data) if isinstance(data, list) else 0
                
                self.log_result(
                    "General Collections Endpoint", 
                    True, 
                    f"Retrieved {collections_count} total collections"
                )
                return data
            else:
                self.log_result(
                    "General Collections Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("General Collections Endpoint", False, f"Exception: {str(e)}")
            return []

    def run_comprehensive_test(self):
        """Run comprehensive test of Jersey Release collection functionality"""
        print("🚨 STARTING CRITICAL JERSEY RELEASE COLLECTION BUG INVESTIGATION")
        print("=" * 80)
        print(f"Target Jersey Release: {self.target_jersey_release_id}")
        print(f"User: {USER_CREDENTIALS['email']}")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate user
        if not self.authenticate_user():
            print("❌ CRITICAL: User authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test vestiaire endpoint and look for target Jersey Release
        jersey_releases, target_found, target_details = self.test_vestiaire_endpoint()
        
        if not target_found:
            print(f"❌ CRITICAL: Target Jersey Release {self.target_jersey_release_id} NOT found in vestiaire")
            print("   This explains why user cannot add it to collection!")
            
            # Still continue with other tests to check collection functionality
            if jersey_releases:
                # Use first available Jersey Release for testing collection functionality
                test_jersey_release = jersey_releases[0]
                test_jersey_id = test_jersey_release.get('id')
                print(f"   Using first available Jersey Release for collection testing: {test_jersey_id}")
            else:
                print("   No Jersey Releases available for testing collection functionality")
                return False
        else:
            test_jersey_id = target_details['id']
            print(f"✅ Target Jersey Release found in vestiaire: {test_jersey_id}")
        
        # Step 3: Test adding to owned collection
        add_success, add_response = self.test_add_to_owned_collection(test_jersey_id)
        
        # Step 4: Test retrieving owned collections
        owned_collections, target_in_owned = self.test_get_owned_collections()
        
        # Step 5: Test retrieving wanted collections
        wanted_collections = self.test_get_wanted_collections()
        
        # Step 6: Test general collections endpoint
        general_collections = self.test_general_collections_endpoint()
        
        # Summary and Root Cause Analysis
        print("\n" + "=" * 80)
        print("🎯 ROOT CAUSE ANALYSIS")
        print("=" * 80)
        
        success_rate = sum(1 for result in self.test_results if result['success']) / len(self.test_results) * 100
        
        if not target_found:
            print(f"❌ CRITICAL ISSUE IDENTIFIED: Jersey Release {self.target_jersey_release_id} does not exist in vestiaire")
            print("   This is the ROOT CAUSE of the user's reported issue!")
            print("   User cannot add a Jersey Release to collection if it doesn't exist in the system.")
        elif add_success and target_in_owned:
            print("✅ Collection functionality is working correctly")
            print("   The issue may be in the frontend UI or user workflow")
        elif add_success and not target_in_owned:
            print("❌ CRITICAL: Jersey Release added to collection but not appearing in owned collections")
            print("   This indicates a data aggregation or retrieval issue")
        else:
            print("❌ CRITICAL: Collection addition functionality is broken")
        
        print(f"\n📊 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        # Detailed findings
        print("\n📋 DETAILED FINDINGS:")
        for result in self.test_results:
            print(f"   {result['status']} {result['test']}")
            if result['details']:
                print(f"      {result['details']}")
        
        return success_rate > 80

def main():
    tester = JerseyReleaseCollectionCriticalTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 TESTING COMPLETED - Most functionality working")
    else:
        print("\n🚨 TESTING COMPLETED - Critical issues identified")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())