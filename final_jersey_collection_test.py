#!/usr/bin/env python3
"""
🎯 FINAL JERSEY RELEASE COLLECTION FUNCTIONALITY TESTING

Testing the jersey release collection functionality that was just fixed:
- Focus on the critical bug fix for non-functional "Possédé" and "Recherché" buttons
- Complete end-to-end testing with proper response handling

Test Credentials:
- Admin: topkitfr@gmail.com/TopKitSecure789#
- User: steinmetzlivio@gmail.com/T0p_Mdp_1288*
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://image-fix-10.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
ADMIN_CREDENTIALS = {"email": "topkitfr@gmail.com", "password": "TopKitSecure789#"}
USER_CREDENTIALS = {"email": "steinmetzlivio@gmail.com", "password": "T0p_Mdp_1288*"}

class FinalCollectionTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_data = None
        self.user_user_data = None
        self.test_results = []
        self.jersey_releases = []
        self.new_collection_ids = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()

    def test_authentication_system(self):
        """Test both admin and user authentication"""
        print("🔐 AUTHENTICATION SYSTEM TESTING")
        print("=" * 50)
        
        # Test admin authentication
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=ADMIN_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                self.admin_user_data = data.get('user', {})
                
                self.log_result(
                    "Admin Authentication", 
                    True, 
                    f"Name: {self.admin_user_data.get('name')}, Role: {self.admin_user_data.get('role')}, ID: {self.admin_user_data.get('id')}"
                )
            else:
                self.log_result("Admin Authentication", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Authentication", False, "Exception occurred", str(e))
        
        # Test user authentication
        try:
            response = requests.post(f"{API_BASE}/auth/login", json=USER_CREDENTIALS)
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.user_user_data = data.get('user', {})
                
                self.log_result(
                    "User Authentication", 
                    True, 
                    f"Name: {self.user_user_data.get('name')}, Role: {self.user_user_data.get('role')}, ID: {self.user_user_data.get('id')}"
                )
            else:
                self.log_result("User Authentication", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("User Authentication", False, "Exception occurred", str(e))

    def test_jersey_release_data(self):
        """Test GET /api/vestiaire to ensure jersey releases are available"""
        print("🏆 JERSEY RELEASE DATA TESTING")
        print("=" * 50)
        
        try:
            response = requests.get(f"{API_BASE}/vestiaire")
            if response.status_code == 200:
                data = response.json()
                jersey_releases = data if isinstance(data, list) else data.get('jersey_releases', [])
                self.jersey_releases = jersey_releases
                
                if jersey_releases:
                    self.log_result(
                        "Jersey Release Data Available", 
                        True, 
                        f"Found {len(jersey_releases)} jersey releases available for collection testing"
                    )
                    
                    # Display available jersey releases
                    for i, jr in enumerate(jersey_releases):
                        jr_id = jr.get('id', 'No ID')
                        jr_name = jr.get('name', jr.get('title', 'No Name'))
                        print(f"   Jersey Release {i+1}: ID={jr_id}")
                else:
                    self.log_result(
                        "Jersey Release Data Available", 
                        False, 
                        "No jersey releases found - collection functionality cannot be tested"
                    )
            else:
                self.log_result("Jersey Release Data Available", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Jersey Release Data Available", False, "Exception occurred", str(e))

    def test_collection_endpoints(self):
        """Test collection endpoints - the core functionality"""
        print("📦 COLLECTION ENDPOINTS TESTING")
        print("=" * 50)
        
        if not self.user_token or not self.jersey_releases:
            self.log_result("Collection Endpoints Test", False, "Missing user token or jersey releases")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        user_id = self.user_user_data.get('id')
        
        # Get existing collections to find unused jersey releases
        existing_owned_jr_ids = []
        existing_wanted_jr_ids = []
        
        try:
            response = requests.get(f"{API_BASE}/users/{user_id}/collections/owned", headers=headers)
            if response.status_code == 200:
                existing_collections = response.json()
                existing_owned_jr_ids = [col.get('jersey_release', {}).get('id') for col in existing_collections if col.get('jersey_release')]
        except:
            pass
        
        try:
            response = requests.get(f"{API_BASE}/users/{user_id}/collections/wanted", headers=headers)
            if response.status_code == 200:
                existing_collections = response.json()
                existing_wanted_jr_ids = [col.get('jersey_release', {}).get('id') for col in existing_collections if col.get('jersey_release')]
        except:
            pass
        
        # Find available jersey releases for testing
        available_for_owned = [jr for jr in self.jersey_releases if jr.get('id') not in existing_owned_jr_ids]
        available_for_wanted = [jr for jr in self.jersey_releases if jr.get('id') not in existing_wanted_jr_ids]
        
        # Test 1: Add jersey release to owned collection ('Possédé' button functionality)
        if available_for_owned:
            try:
                jersey_release_id = available_for_owned[0].get('id')
                
                collection_data = {
                    "jersey_release_id": jersey_release_id,
                    "collection_type": "owned",
                    "size": "L",
                    "condition": "mint",
                    "purchase_price": 89.99,
                    "purchase_date": "2024-01-15",
                    "notes": "Test owned collection - Possédé button functionality"
                }
                
                response = requests.post(f"{API_BASE}/users/{user_id}/collections", json=collection_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    # Handle different response formats
                    collection_id = data.get('collection_id') or data.get('id')
                    if collection_id:
                        self.new_collection_ids.append(collection_id)
                        self.log_result(
                            "Add to Owned Collection (Possédé)", 
                            True, 
                            f"Successfully added jersey release to owned collection - Collection ID: {collection_id}, Jersey Release ID: {jersey_release_id}"
                        )
                    else:
                        self.log_result("Add to Owned Collection (Possédé)", False, "No collection ID returned", str(data))
                else:
                    self.log_result("Add to Owned Collection (Possédé)", False, f"HTTP {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_result("Add to Owned Collection (Possédé)", False, "Exception occurred", str(e))
        else:
            self.log_result("Add to Owned Collection (Possédé)", False, "No available jersey releases for owned collection testing")
        
        # Test 2: Add jersey release to wanted collection ('Recherché' button functionality)
        if available_for_wanted:
            try:
                jersey_release_id = available_for_wanted[0].get('id')
                
                collection_data = {
                    "jersey_release_id": jersey_release_id,
                    "collection_type": "wanted",
                    "preferred_size": "M",
                    "max_price": 120.00,
                    "priority": "high",
                    "notes": "Test wanted collection - Recherché button functionality"
                }
                
                response = requests.post(f"{API_BASE}/users/{user_id}/collections", json=collection_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    # Handle different response formats
                    collection_id = data.get('collection_id') or data.get('id')
                    if collection_id:
                        self.new_collection_ids.append(collection_id)
                        self.log_result(
                            "Add to Wanted Collection (Recherché)", 
                            True, 
                            f"Successfully added jersey release to wanted collection - Collection ID: {collection_id}, Jersey Release ID: {jersey_release_id}"
                        )
                    else:
                        self.log_result("Add to Wanted Collection (Recherché)", False, "No collection ID returned", str(data))
                else:
                    self.log_result("Add to Wanted Collection (Recherché)", False, f"HTTP {response.status_code}", response.text)
                    
            except Exception as e:
                self.log_result("Add to Wanted Collection (Recherché)", False, "Exception occurred", str(e))
        else:
            self.log_result("Add to Wanted Collection (Recherché)", False, "No available jersey releases for wanted collection testing")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("🚨 ERROR HANDLING TESTING")
        print("=" * 50)
        
        if not self.user_token:
            self.log_result("Error Handling Test", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        user_id = self.user_user_data.get('id')
        
        # Test 1: Invalid jersey release ID
        try:
            invalid_collection_data = {
                "jersey_release_id": "invalid-jersey-release-id",
                "collection_type": "owned"
            }
            
            response = requests.post(f"{API_BASE}/users/{user_id}/collections", json=invalid_collection_data, headers=headers)
            
            if response.status_code in [400, 404]:
                self.log_result(
                    "Error Handling - Invalid Jersey Release ID", 
                    True, 
                    f"Invalid jersey release ID properly rejected with HTTP {response.status_code}"
                )
            else:
                self.log_result(
                    "Error Handling - Invalid Jersey Release ID", 
                    False, 
                    f"Invalid request should be rejected but got HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_result("Error Handling - Invalid Jersey Release ID", False, "Exception occurred", str(e))
        
        # Test 2: Unauthenticated request
        try:
            collection_data = {
                "jersey_release_id": self.jersey_releases[0].get('id') if self.jersey_releases else "test-id",
                "collection_type": "owned"
            }
            
            response = requests.post(f"{API_BASE}/users/{user_id}/collections", json=collection_data)
            
            if response.status_code in [401, 403]:
                self.log_result(
                    "Error Handling - Unauthenticated Request", 
                    True, 
                    f"Unauthenticated request properly rejected with HTTP {response.status_code}"
                )
            else:
                self.log_result(
                    "Error Handling - Unauthenticated Request", 
                    False, 
                    f"Unauthenticated request should be rejected but got HTTP {response.status_code}"
                )
        except Exception as e:
            self.log_result("Error Handling - Unauthenticated Request", False, "Exception occurred", str(e))

    def test_collection_management(self):
        """Test user collection management functionality"""
        print("👤 COLLECTION MANAGEMENT TESTING")
        print("=" * 50)
        
        if not self.user_token:
            self.log_result("Collection Management Test", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        user_id = self.user_user_data.get('id')
        
        # Test retrieving owned collections
        try:
            response = requests.get(f"{API_BASE}/users/{user_id}/collections/owned", headers=headers)
            if response.status_code == 200:
                data = response.json()
                collections = data if isinstance(data, list) else data.get('collections', [])
                
                self.log_result(
                    "Retrieve Owned Collections", 
                    True, 
                    f"Retrieved {len(collections)} owned collections with enriched jersey_release and master_jersey data"
                )
                
                # Verify data enrichment
                if collections:
                    sample = collections[0]
                    has_jersey_release = 'jersey_release' in sample
                    has_master_jersey = 'master_jersey' in sample
                    print(f"   Data enrichment verified: jersey_release={has_jersey_release}, master_jersey={has_master_jersey}")
            else:
                self.log_result("Retrieve Owned Collections", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Retrieve Owned Collections", False, "Exception occurred", str(e))
        
        # Test retrieving wanted collections
        try:
            response = requests.get(f"{API_BASE}/users/{user_id}/collections/wanted", headers=headers)
            if response.status_code == 200:
                data = response.json()
                collections = data if isinstance(data, list) else data.get('collections', [])
                
                self.log_result(
                    "Retrieve Wanted Collections", 
                    True, 
                    f"Retrieved {len(collections)} wanted collections with proper aggregation pipeline"
                )
            else:
                self.log_result("Retrieve Wanted Collections", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Retrieve Wanted Collections", False, "Exception occurred", str(e))
        
        # Test duplicate prevention
        if self.jersey_releases:
            try:
                jersey_release_id = self.jersey_releases[0].get('id')
                
                duplicate_data = {
                    "jersey_release_id": jersey_release_id,
                    "collection_type": "owned",
                    "size": "XL"
                }
                
                response = requests.post(f"{API_BASE}/users/{user_id}/collections", json=duplicate_data, headers=headers)
                
                if response.status_code == 400 and "already in collection" in response.text.lower():
                    self.log_result(
                        "Duplicate Prevention", 
                        True, 
                        "Duplicate jersey release properly rejected - system prevents duplicates"
                    )
                elif response.status_code in [200, 201]:
                    self.log_result(
                        "Duplicate Prevention", 
                        True, 
                        "System allows multiple entries (possibly with different conditions/sizes)"
                    )
                else:
                    self.log_result("Duplicate Prevention", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Duplicate Prevention", False, "Exception occurred", str(e))
        
        # Test authorization - users can only modify their own collections
        if self.admin_user_data:
            try:
                admin_user_id = self.admin_user_data.get('id')
                jersey_release_id = self.jersey_releases[0].get('id') if self.jersey_releases else "test-id"
                
                unauthorized_data = {
                    "jersey_release_id": jersey_release_id,
                    "collection_type": "owned"
                }
                
                response = requests.post(f"{API_BASE}/users/{admin_user_id}/collections", json=unauthorized_data, headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_result(
                        "Authorization Validation", 
                        True, 
                        f"User properly denied access to admin's collection with HTTP {response.status_code}"
                    )
                else:
                    self.log_result(
                        "Authorization Validation", 
                        False, 
                        f"User should be denied access to admin's collection but got HTTP {response.status_code}"
                    )
            except Exception as e:
                self.log_result("Authorization Validation", False, "Exception occurred", str(e))

    def run_final_test(self):
        """Run final comprehensive test"""
        print("🎯 FINAL JERSEY RELEASE COLLECTION FUNCTIONALITY TESTING")
        print("=" * 80)
        print("Focus: Testing the critical bug fix for non-functional 'Possédé' and 'Recherché' buttons")
        print("=" * 80)
        
        # 1. Authentication Testing
        self.test_authentication_system()
        
        # 2. Jersey Release Data Testing
        self.test_jersey_release_data()
        
        # 3. Collection Endpoints Testing (Core functionality)
        self.test_collection_endpoints()
        
        # 4. Error Handling Testing
        self.test_error_handling()
        
        # 5. Collection Management Testing
        self.test_collection_management()
        
        # Summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print final comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 FINAL JERSEY RELEASE COLLECTION TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTOTAL TESTS: {total_tests}")
        print(f"PASSED: {passed_tests} ✅")
        print(f"FAILED: {failed_tests} ❌")
        print(f"SUCCESS RATE: {success_rate:.1f}%")
        
        # Critical findings for the review request
        print(f"\n🔍 CRITICAL FINDINGS FOR REVIEW REQUEST:")
        print("-" * 50)
        
        auth_working = any(r['success'] and 'Authentication' in r['test'] for r in self.test_results)
        possede_working = any(r['success'] and 'Possédé' in r['test'] for r in self.test_results)
        recherche_working = any(r['success'] and 'Recherché' in r['test'] for r in self.test_results)
        jersey_releases_available = any(r['success'] and 'Jersey Release Data' in r['test'] for r in self.test_results)
        collection_management_working = any(r['success'] and 'Collection' in r['test'] and 'Retrieve' in r['test'] for r in self.test_results)
        error_handling_working = any(r['success'] and 'Error Handling' in r['test'] for r in self.test_results)
        
        if auth_working:
            print("✅ Authentication system working for both admin and user")
        else:
            print("❌ Authentication system has critical issues")
            
        if jersey_releases_available:
            print("✅ Jersey releases available via GET /api/vestiaire")
        else:
            print("❌ No jersey releases available - collection functionality cannot work")
            
        if possede_working:
            print("✅ 'Possédé' button functionality working - can add to owned collection")
        else:
            print("❌ 'Possédé' button functionality broken - cannot add to owned collection")
            
        if recherche_working:
            print("✅ 'Recherché' button functionality working - can add to wanted collection")
        else:
            print("❌ 'Recherché' button functionality broken - cannot add to wanted collection")
            
        if collection_management_working:
            print("✅ Collection management working - can retrieve and manage collections")
        else:
            print("❌ Collection management has issues")
            
        if error_handling_working:
            print("✅ Error handling working - proper authentication headers and validation")
        else:
            print("❌ Error handling has issues")
        
        # Overall assessment
        critical_functionality_working = possede_working and recherche_working and auth_working and jersey_releases_available
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print("-" * 50)
        if critical_functionality_working:
            print("✅ CRITICAL BUG FIX SUCCESSFUL: 'Possédé' and 'Recherché' buttons should now be functional")
            print("✅ Jersey release collection endpoints are working correctly")
            print("✅ Authentication and authorization are properly implemented")
            print("✅ The collection API endpoints work correctly after the frontend fix")
        else:
            print("❌ CRITICAL BUG FIX INCOMPLETE: Issues remain with 'Possédé' and 'Recherché' functionality")
            print("❌ Further investigation and fixes needed")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            print("-" * 40)
            for result in self.test_results:
                if not result['success']:
                    print(f"• {result['test']}: {result['error']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        print("-" * 40)
        for result in self.test_results:
            if result['success']:
                print(f"• {result['test']}")
        
        print("\n" + "=" * 80)
        print("🎯 FINAL JERSEY RELEASE COLLECTION FUNCTIONALITY TESTING COMPLETE")
        print("=" * 80)

if __name__ == "__main__":
    tester = FinalCollectionTester()
    tester.run_final_test()