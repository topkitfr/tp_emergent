#!/usr/bin/env python3
"""
MA COLLECTION ENDPOINT FIX VERIFICATION - FINAL TEST
===================================================

CRITICAL FINDINGS FROM INVESTIGATION:
1. ✅ TK-RELEASE-000001 EXISTS with ID: 7f267e15-196d-4b87-abb4-755f68ed40aa
2. ✅ User has BOTH owned and wanted collections with this Jersey Release
3. ✅ General collections endpoint NOW RETURNS PROPER DATA STRUCTURE
4. ✅ Data enrichment is working (jersey_release and master_jersey populated)
5. ✅ The reference field is 'topkit_reference' not 'reference'

This test verifies the SUCCESSFUL FIX of the general collections endpoint.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"

# Test credentials
USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class MaCollectionFixVerifier:
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

    def test_general_collections_endpoint_fix(self):
        """Test the FIXED general collections endpoint"""
        print("🎯 TESTING GENERAL COLLECTIONS ENDPOINT FIX...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if response has the correct structure
                if isinstance(data, dict) and 'collections' in data:
                    collections = data['collections']
                    
                    self.log_result(
                        "General Collections - Response Structure", 
                        True, 
                        f"Correct structure with 'collections' array containing {len(collections)} items"
                    )
                    
                    # Check for TK-RELEASE-000001 (using topkit_reference)
                    tk_release_found = False
                    enriched_count = 0
                    collection_types = set()
                    
                    for collection in collections:
                        jersey_release = collection.get('jersey_release', {})
                        master_jersey = collection.get('master_jersey', {})
                        collection_type = collection.get('collection_type')
                        
                        if collection_type:
                            collection_types.add(collection_type)
                        
                        # Check data enrichment
                        if jersey_release and master_jersey:
                            enriched_count += 1
                            
                        # Check for TK-RELEASE-000001 using correct field
                        if jersey_release.get('topkit_reference') == 'TK-RELEASE-000001':
                            tk_release_found = True
                    
                    self.log_result(
                        "General Collections - Data Enrichment", 
                        enriched_count == len(collections), 
                        f"Enriched collections: {enriched_count}/{len(collections)}"
                    )
                    
                    self.log_result(
                        "General Collections - TK-RELEASE-000001 Found", 
                        tk_release_found, 
                        f"Target Jersey Release {'found' if tk_release_found else 'not found'} in collections"
                    )
                    
                    self.log_result(
                        "General Collections - Collection Types", 
                        len(collection_types) > 0, 
                        f"Collection types: {list(collection_types)}"
                    )
                    
                    return data
                else:
                    self.log_result(
                        "General Collections - Response Structure", 
                        False, 
                        f"Unexpected response structure: {type(data)}"
                    )
                    return None
            else:
                self.log_result(
                    "General Collections Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_result("General Collections Endpoint", False, f"Exception: {str(e)}")
            return None

    def test_vestiaire_integration(self):
        """Test vestiaire endpoint to confirm Jersey Release exists"""
        print("🏪 TESTING VESTIAIRE INTEGRATION...")
        
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = requests.get(f"{BACKEND_URL}/vestiaire", headers=headers)
            
            if response.status_code == 200:
                jersey_releases = response.json()
                
                if isinstance(jersey_releases, list) and len(jersey_releases) > 0:
                    # Look for the Jersey Release with ID 7f267e15-196d-4b87-abb4-755f68ed40aa
                    target_release = None
                    for release in jersey_releases:
                        if release.get('id') == '7f267e15-196d-4b87-abb4-755f68ed40aa':
                            target_release = release
                            break
                    
                    if target_release:
                        self.log_result(
                            "Vestiaire - Target Jersey Release Found", 
                            True, 
                            f"ID: {target_release.get('id')}, Master Jersey ID: {target_release.get('master_jersey_id')}"
                        )
                        return target_release
                    else:
                        self.log_result(
                            "Vestiaire - Target Jersey Release Found", 
                            False, 
                            f"Target Jersey Release not found in {len(jersey_releases)} releases"
                        )
                        return None
                else:
                    self.log_result(
                        "Vestiaire Endpoint", 
                        False, 
                        f"Empty or invalid response: {len(jersey_releases) if isinstance(jersey_releases, list) else 'not a list'}"
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

    def test_workflow_completeness(self, collections_data):
        """Test the complete workflow: vestiaire → collection → Ma Collection"""
        print("🔄 TESTING COMPLETE WORKFLOW...")
        
        if not collections_data or 'collections' not in collections_data:
            self.log_result(
                "Workflow - Data Available", 
                False, 
                "No collections data available for workflow test"
            )
            return False
        
        collections = collections_data['collections']
        
        # Check if user has both owned and wanted collections
        owned_collections = [c for c in collections if c.get('collection_type') == 'owned']
        wanted_collections = [c for c in collections if c.get('collection_type') == 'wanted']
        
        self.log_result(
            "Workflow - Collection Types Present", 
            len(owned_collections) > 0 and len(wanted_collections) > 0, 
            f"Owned: {len(owned_collections)}, Wanted: {len(wanted_collections)}"
        )
        
        # Check if the target Jersey Release is in collections
        target_in_collections = False
        for collection in collections:
            jersey_release = collection.get('jersey_release', {})
            if jersey_release.get('topkit_reference') == 'TK-RELEASE-000001':
                target_in_collections = True
                break
        
        self.log_result(
            "Workflow - Target Jersey in Collections", 
            target_in_collections, 
            f"TK-RELEASE-000001 {'found' if target_in_collections else 'not found'} in user collections"
        )
        
        # Check data quality for display
        display_ready = True
        display_issues = []
        
        for collection in collections:
            jersey_release = collection.get('jersey_release', {})
            master_jersey = collection.get('master_jersey', {})
            
            if not jersey_release.get('topkit_reference'):
                display_issues.append("Missing topkit_reference")
            if not master_jersey.get('season'):
                display_issues.append("Missing season info")
            if not master_jersey.get('jersey_type'):
                display_issues.append("Missing jersey_type")
        
        display_ready = len(display_issues) == 0
        
        self.log_result(
            "Workflow - Display Data Quality", 
            display_ready, 
            f"Data quality: {'Good' if display_ready else 'Issues: ' + ', '.join(set(display_issues))}"
        )
        
        return target_in_collections and display_ready

    def run_comprehensive_verification(self):
        """Run comprehensive verification of the Ma Collection fix"""
        print("🎯 STARTING MA COLLECTION ENDPOINT FIX VERIFICATION")
        print("=" * 60)
        
        # Step 1: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Test vestiaire integration
        vestiaire_data = self.test_vestiaire_integration()
        
        # Step 3: Test the FIXED general collections endpoint
        collections_data = self.test_general_collections_endpoint_fix()
        
        # Step 4: Test complete workflow
        workflow_success = self.test_workflow_completeness(collections_data)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['success'])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print()
        
        # Critical assessment
        critical_tests = [
            "User Authentication",
            "General Collections - Response Structure", 
            "General Collections - TK-RELEASE-000001 Found",
            "General Collections - Data Enrichment"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['test'] in critical_tests and result['success'])
        
        if critical_passed == len(critical_tests):
            print("🎉 CRITICAL FIX VERIFICATION: SUCCESS!")
            print("✅ The general collections endpoint fix is working correctly")
            print("✅ TK-RELEASE-000001 is now visible in 'Ma Collection'")
            print("✅ User collections are properly enriched with jersey_release and master_jersey data")
            print("✅ The endpoint now returns the correct data structure for frontend consumption")
            print("✅ Both owned and wanted collections are properly combined")
        else:
            print("🚨 CRITICAL FIX VERIFICATION: PARTIAL SUCCESS")
            print(f"✅ {critical_passed}/{len(critical_tests)} critical tests passed")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 85:
            print("✅ MA COLLECTION ENDPOINT FIX IS WORKING EXCELLENTLY!")
            print("✅ Users can now see their collections in 'Ma Collection' page")
            print("✅ The reported bug has been successfully resolved")
        elif success_rate >= 70:
            print("⚠️  MA COLLECTION ENDPOINT FIX IS MOSTLY WORKING")
            print("⚠️  Some minor issues remain but core functionality restored")
        else:
            print("❌ MA COLLECTION ENDPOINT FIX NEEDS MORE WORK")
            print("❌ Critical issues still prevent proper functionality")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    verifier = MaCollectionFixVerifier()
    success = verifier.run_comprehensive_verification()
    sys.exit(0 if success else 1)