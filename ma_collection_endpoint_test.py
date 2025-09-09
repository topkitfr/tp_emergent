#!/usr/bin/env python3
"""
MA COLLECTION ENDPOINT FIX VERIFICATION - BACKEND TEST
=====================================================

This test verifies the critical fix for the general collections endpoint 
that was causing "Ma Collection" to display empty despite user having collections.

CRITICAL TEST OBJECTIVES:
1. Test corrected `/api/users/{user_id}/collections` endpoint
2. Verify it returns Jersey Release TK-RELEASE-000001 for steinmetzlivio@gmail.com
3. Confirm data enrichment (jersey_release and master_jersey data)
4. Test complete workflow: vestiaire → collection → "Ma Collection"

Authentication:
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jersey-tracker.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class MaCollectionEndpointTester:
    def __init__(self):
        self.user_token = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
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
                self.user_token = data.get('token')
                user_data = data.get('user', {})
                self.user_user_id = user_data.get('id')
                
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

    def test_vestiaire_endpoint(self):
        """Test vestiaire endpoint to verify Jersey Release TK-RELEASE-000001 exists"""
        print("🏪 TESTING VESTIAIRE ENDPOINT...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                jersey_releases = response.json()
                
                # Look for TK-RELEASE-000001
                target_release = None
                for release in jersey_releases:
                    if release.get('reference') == 'TK-RELEASE-000001':
                        target_release = release
                        break
                
                if target_release:
                    self.log_result(
                        "Vestiaire - TK-RELEASE-000001 Found", 
                        True, 
                        f"ID: {target_release.get('id')}, Player: {target_release.get('player_name', 'Unknown')}"
                    )
                    return target_release
                else:
                    self.log_result(
                        "Vestiaire - TK-RELEASE-000001 Found", 
                        False, 
                        f"TK-RELEASE-000001 not found in {len(jersey_releases)} releases"
                    )
                    return None
            else:
                self.log_result(
                    "Vestiaire Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("Vestiaire Endpoint", False, f"Exception: {str(e)}")
            return None

    def test_general_collections_endpoint(self):
        """Test the CRITICAL general collections endpoint that was fixed"""
        print("📋 TESTING GENERAL COLLECTIONS ENDPOINT (THE CRITICAL FIX)...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                collections = response.json()
                
                if isinstance(collections, list) and len(collections) > 0:
                    # Check for TK-RELEASE-000001 in collections
                    tk_release_found = False
                    enriched_data_count = 0
                    
                    for collection in collections:
                        jersey_release = collection.get('jersey_release', {})
                        master_jersey = collection.get('master_jersey', {})
                        
                        # Check if data is enriched (not empty objects)
                        if jersey_release and len(jersey_release) > 0:
                            enriched_data_count += 1
                            
                        # Check for TK-RELEASE-000001
                        if jersey_release.get('reference') == 'TK-RELEASE-000001':
                            tk_release_found = True
                    
                    success = len(collections) > 0 and enriched_data_count > 0
                    details = f"Collections: {len(collections)}, Enriched: {enriched_data_count}, TK-RELEASE-000001: {'Found' if tk_release_found else 'Not Found'}"
                    
                    self.log_result("General Collections Endpoint - Data Retrieved", success, details)
                    
                    if tk_release_found:
                        self.log_result("General Collections - TK-RELEASE-000001 Present", True, "Target Jersey Release found in user's collections")
                    else:
                        self.log_result("General Collections - TK-RELEASE-000001 Present", False, "Target Jersey Release not found in collections")
                    
                    return collections
                else:
                    self.log_result(
                        "General Collections Endpoint", 
                        False, 
                        f"Empty collections array returned (length: {len(collections) if isinstance(collections, list) else 'not a list'})"
                    )
                    return []
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

    def test_specific_collections_endpoints(self):
        """Test specific owned and wanted collections endpoints for comparison"""
        print("📊 TESTING SPECIFIC COLLECTIONS ENDPOINTS...")
        
        results = {}
        
        for collection_type in ['owned', 'wanted']:
            try:
                headers = {"Authorization": f"Bearer {self.user_token}"}
                response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/{collection_type}", headers=headers)
                
                if response.status_code == 200:
                    collections = response.json()
                    results[collection_type] = collections
                    
                    tk_release_found = any(
                        c.get('jersey_release', {}).get('reference') == 'TK-RELEASE-000001' 
                        for c in collections
                    )
                    
                    self.log_result(
                        f"Specific Collections - {collection_type.title()}", 
                        True, 
                        f"Count: {len(collections)}, TK-RELEASE-000001: {'Found' if tk_release_found else 'Not Found'}"
                    )
                else:
                    self.log_result(
                        f"Specific Collections - {collection_type.title()}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    results[collection_type] = []
                    
            except Exception as e:
                self.log_result(f"Specific Collections - {collection_type.title()}", False, f"Exception: {str(e)}")
                results[collection_type] = []
        
        return results

    def test_data_consistency(self, general_collections, specific_collections):
        """Test data consistency between general and specific endpoints"""
        print("🔍 TESTING DATA CONSISTENCY...")
        
        # Calculate expected total from specific endpoints
        owned_count = len(specific_collections.get('owned', []))
        wanted_count = len(specific_collections.get('wanted', []))
        expected_total = owned_count + wanted_count
        
        # Get actual total from general endpoint
        actual_total = len(general_collections)
        
        consistency_check = actual_total == expected_total
        
        self.log_result(
            "Data Consistency Check", 
            consistency_check, 
            f"Expected: {expected_total} (Owned: {owned_count}, Wanted: {wanted_count}), Actual: {actual_total}"
        )
        
        # Check if general endpoint properly combines both types
        if general_collections:
            collection_types = set(c.get('collection_type') for c in general_collections)
            has_both_types = 'owned' in collection_types and 'wanted' in collection_types
            
            self.log_result(
                "Collection Types Combination", 
                has_both_types or len(collection_types) > 0, 
                f"Types found: {list(collection_types)}"
            )

    def run_comprehensive_test(self):
        """Run comprehensive test of the Ma Collection endpoint fix"""
        print("🎯 STARTING MA COLLECTION ENDPOINT FIX VERIFICATION")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test vestiaire to confirm TK-RELEASE-000001 exists
        target_release = self.test_vestiaire_endpoint()
        
        # Step 3: Test the CRITICAL general collections endpoint
        general_collections = self.test_general_collections_endpoint()
        
        # Step 4: Test specific collections endpoints for comparison
        specific_collections = self.test_specific_collections_endpoints()
        
        # Step 5: Test data consistency
        self.test_data_consistency(general_collections, specific_collections)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Critical assessment
        critical_tests = [
            "User Authentication",
            "General Collections Endpoint - Data Retrieved", 
            "General Collections - TK-RELEASE-000001 Present"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print("🎉 CRITICAL FIX VERIFICATION: SUCCESS!")
            print("✅ The general collections endpoint fix is working correctly")
            print("✅ TK-RELEASE-000001 is now visible in 'Ma Collection'")
            print("✅ User can see their collections with proper data enrichment")
        else:
            print("🚨 CRITICAL FIX VERIFICATION: FAILED!")
            print("❌ The general collections endpoint still has issues")
            print("❌ 'Ma Collection' may still appear empty to users")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = MaCollectionEndpointTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)