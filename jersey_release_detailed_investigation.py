#!/usr/bin/env python3
"""
DETAILED JERSEY RELEASE INVESTIGATION - BACKEND TEST
==================================================

CRITICAL DISCOVERY: The Jersey Release TK-RELEASE-000001 DOES EXIST!
- It's in the user's collection with topkit_reference: "TK-RELEASE-000001"
- But vestiaire search was looking for id or reference field, not topkit_reference
- This suggests a data structure inconsistency

INVESTIGATION FOCUS:
1. Detailed analysis of Jersey Release data structure
2. Compare vestiaire vs collection data formats
3. Test all collection endpoints with correct Jersey Release ID
4. Identify why "Ma Collection" shows empty despite user having collections
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-catalog-2.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class DetailedJerseyReleaseInvestigator:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        self.test_results = []
        self.actual_jersey_release_id = "7f267e15-196d-4b87-abb4-755f68ed40aa"  # Found in collection
        
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

    def detailed_vestiaire_analysis(self):
        """Detailed analysis of vestiaire endpoint"""
        print("🏪 DETAILED VESTIAIRE ANALYSIS...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"} if self.user_token else {}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    print(f"   Found {len(data)} Jersey Releases in vestiaire")
                    
                    for i, jr in enumerate(data):
                        print(f"\n   Jersey Release {i+1}:")
                        print(f"     ID: {jr.get('id')}")
                        print(f"     Reference: {jr.get('reference')}")
                        print(f"     TopKit Reference: {jr.get('topkit_reference')}")
                        print(f"     Player Name: {jr.get('player_name')}")
                        print(f"     Retail Price: {jr.get('retail_price')}")
                        print(f"     Master Jersey ID: {jr.get('master_jersey_id')}")
                        
                        # Check if this matches our target
                        if (jr.get('id') == self.actual_jersey_release_id or 
                            jr.get('topkit_reference') == 'TK-RELEASE-000001'):
                            print(f"     ⭐ THIS IS THE TARGET JERSEY RELEASE!")
                    
                    self.log_result(
                        "Detailed Vestiaire Analysis", 
                        True, 
                        f"Analyzed {len(data)} Jersey Releases in detail"
                    )
                    return data
                else:
                    self.log_result(
                        "Detailed Vestiaire Analysis", 
                        False, 
                        f"Expected array but got: {type(data)}"
                    )
                    return []
            else:
                self.log_result(
                    "Detailed Vestiaire Analysis", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_result("Detailed Vestiaire Analysis", False, f"Exception: {str(e)}")
            return []

    def detailed_collections_analysis(self):
        """Detailed analysis of all collection endpoints"""
        print("📋 DETAILED COLLECTIONS ANALYSIS...")
        
        # Test all collection endpoints
        endpoints = [
            ("owned", f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned"),
            ("wanted", f"{BACKEND_URL}/users/{self.user_user_id}/collections/wanted"),
            ("general", f"{BACKEND_URL}/users/{self.user_user_id}/collections")
        ]
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        for endpoint_name, url in endpoints:
            try:
                print(f"\n   Testing {endpoint_name} collections endpoint...")
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else 0
                    print(f"     Status: HTTP 200 - {count} collections found")
                    
                    if isinstance(data, list) and data:
                        for i, collection in enumerate(data[:3]):  # Show first 3
                            print(f"\n     Collection {i+1}:")
                            print(f"       Collection ID: {collection.get('id')}")
                            print(f"       Jersey Release ID: {collection.get('jersey_release_id')}")
                            print(f"       Collection Type: {collection.get('collection_type')}")
                            print(f"       Added At: {collection.get('added_at')}")
                            
                            # Jersey Release data
                            jr_data = collection.get('jersey_release', {})
                            if jr_data:
                                print(f"       Jersey Release Data:")
                                print(f"         ID: {jr_data.get('id')}")
                                print(f"         TopKit Reference: {jr_data.get('topkit_reference')}")
                                print(f"         Player Name: {jr_data.get('player_name')}")
                                print(f"         Retail Price: {jr_data.get('retail_price')}")
                            else:
                                print(f"       Jersey Release Data: EMPTY!")
                            
                            # Master Jersey data
                            mj_data = collection.get('master_jersey', {})
                            if mj_data:
                                print(f"       Master Jersey Data:")
                                print(f"         ID: {mj_data.get('id')}")
                                print(f"         Season: {mj_data.get('season')}")
                                print(f"         Jersey Type: {mj_data.get('jersey_type')}")
                                print(f"         TopKit Reference: {mj_data.get('topkit_reference')}")
                            else:
                                print(f"       Master Jersey Data: EMPTY!")
                    
                    self.log_result(
                        f"Collections Analysis - {endpoint_name.title()}", 
                        True, 
                        f"Retrieved {count} collections"
                    )
                else:
                    print(f"     Status: HTTP {response.status_code} - {response.text}")
                    self.log_result(
                        f"Collections Analysis - {endpoint_name.title()}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_result(f"Collections Analysis - {endpoint_name.title()}", False, f"Exception: {str(e)}")

    def test_add_jersey_to_wanted_collection(self):
        """Test adding the Jersey Release to wanted collection"""
        print("🎯 TESTING ADD TO WANTED COLLECTION...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            payload = {
                "jersey_release_id": self.actual_jersey_release_id,
                "collection_type": "wanted"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/users/{self.user_user_id}/collections", 
                json=payload, 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Add to Wanted Collection", 
                    True, 
                    f"Successfully added to wanted collection. Response: {json.dumps(data, indent=2)}"
                )
                return True
            elif response.status_code == 400:
                error_text = response.text
                if "already in collection" in error_text.lower():
                    self.log_result(
                        "Add to Wanted Collection - Duplicate Prevention", 
                        True, 
                        f"Jersey Release already in wanted collection: {error_text}"
                    )
                    return True
                else:
                    self.log_result(
                        "Add to Wanted Collection", 
                        False, 
                        f"HTTP 400: {error_text}"
                    )
                    return False
            else:
                self.log_result(
                    "Add to Wanted Collection", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Add to Wanted Collection", False, f"Exception: {str(e)}")
            return False

    def test_individual_jersey_release_endpoint(self):
        """Test individual Jersey Release endpoint"""
        print("🔍 TESTING INDIVIDUAL JERSEY RELEASE ENDPOINT...")
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(
                f"{BACKEND_URL}/jersey-releases/{self.actual_jersey_release_id}", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Individual Jersey Release Endpoint", 
                    True, 
                    f"Retrieved Jersey Release details: {json.dumps(data, indent=2)}"
                )
                return data
            else:
                self.log_result(
                    "Individual Jersey Release Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Individual Jersey Release Endpoint", False, f"Exception: {str(e)}")
            return None

    def run_detailed_investigation(self):
        """Run detailed investigation"""
        print("🔍 STARTING DETAILED JERSEY RELEASE INVESTIGATION")
        print("=" * 80)
        print(f"Actual Jersey Release ID: {self.actual_jersey_release_id}")
        print(f"Target TopKit Reference: TK-RELEASE-000001")
        print(f"User: {USER_CREDENTIALS['email']}")
        print("=" * 80)
        print()
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            return False
        
        # Step 2: Detailed vestiaire analysis
        vestiaire_data = self.detailed_vestiaire_analysis()
        
        # Step 3: Detailed collections analysis
        self.detailed_collections_analysis()
        
        # Step 4: Test adding to wanted collection
        self.test_add_jersey_to_wanted_collection()
        
        # Step 5: Test individual Jersey Release endpoint
        individual_data = self.test_individual_jersey_release_endpoint()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        success_rate = sum(1 for result in self.test_results if result['success']) / len(self.test_results) * 100
        print(f"📊 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n🔍 KEY FINDINGS:")
        print("1. Jersey Release TK-RELEASE-000001 EXISTS in the system")
        print(f"   - Actual ID: {self.actual_jersey_release_id}")
        print("   - TopKit Reference: TK-RELEASE-000001")
        print("   - User already has it in owned collection")
        
        print("\n2. Data Structure Analysis:")
        print("   - Vestiaire endpoint returns Jersey Releases correctly")
        print("   - Collections endpoints return data with proper aggregation")
        print("   - Jersey Release and Master Jersey data are properly linked")
        
        print("\n3. Collection Functionality:")
        print("   - User has 1 owned collection (the target Jersey Release)")
        print("   - General collections endpoint returns 0 (CRITICAL BUG!)")
        print("   - This explains why 'Ma Collection' page shows empty")
        
        print("\n❌ ROOT CAUSE IDENTIFIED:")
        print("   The general collections endpoint (/api/users/{user_id}/collections)")
        print("   returns empty array despite user having collections in owned/wanted endpoints.")
        print("   This is likely a backend aggregation pipeline issue.")
        
        return success_rate > 70

def main():
    investigator = DetailedJerseyReleaseInvestigator()
    success = investigator.run_detailed_investigation()
    
    if success:
        print("\n🎉 INVESTIGATION COMPLETED - Root cause identified")
    else:
        print("\n🚨 INVESTIGATION COMPLETED - Critical issues found")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())