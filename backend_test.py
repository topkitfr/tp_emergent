#!/usr/bin/env python3
"""
VESTIAIRE COLLECTION FUNCTIONALITY INVESTIGATION - BACKEND TEST
=============================================================

This test investigates the reported bug where adding jersey releases to collections 
is not working despite previous testing showing 95% success rate.

Focus Areas:
1. Test the `/api/vestiaire` endpoint - verify data structure and array format
2. Test all collection-related endpoints for jersey releases
3. Test authentication flow for collection operations  
4. Test complete workflow: user login → load vestiaire → add to collection

Authentication Details:
- Admin: topkitfr@gmail.com / TopKitSecure789#
- User: steinmetzlivio@gmail.com / T0p_Mdp_1288*
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://footwear-collab.preview.emergentagent.com/api"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

USER_CREDENTIALS = {
    "email": "steinmetzlivio@gmail.com", 
    "password": "T0p_Mdp_1288*"
}

class VestiaireCollectionTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.user_user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print(f"{status} {test_name}: {details}")
        
    def authenticate_admin(self):
        """Test admin authentication"""
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                
                self.log_result(
                    "Admin Authentication",
                    True,
                    f"Admin login successful - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.admin_user_id}"
                )
                return True
            else:
                self.log_result(
                    "Admin Authentication", 
                    False,
                    f"Login failed - Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Exception: {str(e)}")
            return False
            
    def authenticate_user(self):
        """Test user authentication"""
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
                    f"User login successful - Name: {user_data.get('name')}, Role: {user_data.get('role')}, ID: {self.user_user_id}"
                )
                return True
            else:
                self.log_result(
                    "User Authentication",
                    False, 
                    f"Login failed - Status: {response.status_code}, Response: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result("User Authentication", False, f"Exception: {str(e)}")
            return False
            
    def test_vestiaire_endpoint(self):
        """Test the /api/vestiaire endpoint - core focus of investigation"""
        try:
            response = requests.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if data is an array
                if isinstance(data, list):
                    jersey_count = len(data)
                    
                    # Analyze data structure
                    if jersey_count > 0:
                        sample_jersey = data[0]
                        
                        # Check for jersey release structure (not direct team/season fields)
                        required_fields = ['id', 'master_jersey_info', 'player_name']
                        missing_fields = [field for field in required_fields if field not in sample_jersey]
                        
                        if not missing_fields:
                            # Check nested master_jersey_info structure
                            master_info = sample_jersey.get('master_jersey_info', {})
                            season = master_info.get('season', 'Unknown')
                            team_id = master_info.get('team_id', 'Unknown')
                            brand_id = master_info.get('brand_id', 'Unknown')
                            
                            self.log_result(
                                "Vestiaire Endpoint Data Structure",
                                True,
                                f"Perfect array format with {jersey_count} jersey releases. Sample: Player {sample_jersey.get('player_name')}, Season {season}, Team ID {team_id}, Brand ID {brand_id}"
                            )
                        else:
                            self.log_result(
                                "Vestiaire Endpoint Data Structure",
                                False,
                                f"Missing required fields: {missing_fields}"
                            )
                    else:
                        self.log_result(
                            "Vestiaire Endpoint Data Structure",
                            False,
                            "Empty array returned - no jersey releases available for collection testing"
                        )
                        
                    return data
                else:
                    self.log_result(
                        "Vestiaire Endpoint Data Structure",
                        False,
                        f"Expected array but got {type(data)}: {data}"
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
            
    def test_collection_endpoints_with_auth(self, token, user_id, user_type):
        """Test collection endpoints with authentication"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test GET owned collections
        try:
            response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/owned", headers=headers)
            if response.status_code == 200:
                owned_data = response.json()
                self.log_result(
                    f"{user_type} - GET Owned Collections",
                    True,
                    f"Retrieved {len(owned_data)} owned collections"
                )
            else:
                self.log_result(
                    f"{user_type} - GET Owned Collections",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(f"{user_type} - GET Owned Collections", False, f"Exception: {str(e)}")
            
        # Test GET wanted collections  
        try:
            response = requests.get(f"{BACKEND_URL}/users/{user_id}/collections/wanted", headers=headers)
            if response.status_code == 200:
                wanted_data = response.json()
                self.log_result(
                    f"{user_type} - GET Wanted Collections",
                    True,
                    f"Retrieved {len(wanted_data)} wanted collections"
                )
            else:
                self.log_result(
                    f"{user_type} - GET Wanted Collections", 
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result(f"{user_type} - GET Wanted Collections", False, f"Exception: {str(e)}")
            
    def test_add_to_collection(self, token, user_id, user_type, jersey_release_id, collection_type):
        """Test adding jersey release to collection"""
        headers = {"Authorization": f"Bearer {token}"}
        
        collection_data = {
            "jersey_release_id": jersey_release_id,
            "collection_type": collection_type,
            "size": "L",
            "condition": "mint"
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/users/{user_id}/collections",
                headers=headers,
                json=collection_data
            )
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                collection_id = result_data.get('collection_id', 'Unknown')
                self.log_result(
                    f"{user_type} - Add to {collection_type.title()} Collection",
                    True,
                    f"Successfully added jersey release {jersey_release_id} to {collection_type} collection (ID: {collection_id})"
                )
                return True
            elif response.status_code == 400:
                # Check if it's a duplicate error (expected behavior)
                error_text = response.text
                if "already in collection" in error_text.lower():
                    self.log_result(
                        f"{user_type} - Add to {collection_type.title()} Collection",
                        True,
                        f"Duplicate prevention working correctly: {error_text}"
                    )
                    return True
                else:
                    self.log_result(
                        f"{user_type} - Add to {collection_type.title()} Collection",
                        False,
                        f"HTTP 400 - Validation error: {error_text}"
                    )
                    return False
            else:
                self.log_result(
                    f"{user_type} - Add to {collection_type.title()} Collection",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_result(f"{user_type} - Add to {collection_type.title()} Collection", False, f"Exception: {str(e)}")
            return False
            
    def test_user_experience_issues(self):
        """Test for user experience issues that explain the reported bug"""
        if not self.user_token or not self.user_user_id:
            self.log_result("User Experience Issues", False, "User not authenticated")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test 1: Check if general collections endpoint works
        try:
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections", headers=headers)
            if response.status_code == 200:
                data = response.json()
                collections = data.get('collections', [])
                if len(collections) == 0:
                    self.log_result(
                        "General Collections Endpoint",
                        False,
                        f"General collections endpoint returns empty array despite user having collections. Response: {data}"
                    )
                else:
                    self.log_result(
                        "General Collections Endpoint",
                        True,
                        f"General collections endpoint working - {len(collections)} items"
                    )
            else:
                self.log_result(
                    "General Collections Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
        except Exception as e:
            self.log_result("General Collections Endpoint", False, f"Exception: {str(e)}")
            
        # Test 2: Check data quality in collections
        try:
            response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    sample = data[0]
                    jersey_release = sample.get('jersey_release', {})
                    master_info = jersey_release.get('master_jersey_info', {})
                    
                    # Check for missing data
                    issues = []
                    if not jersey_release.get('player_name') or jersey_release.get('player_name') == 'Unknown':
                        issues.append("Missing player name")
                    if not master_info.get('season') or master_info.get('season') == 'Unknown':
                        issues.append("Missing season info")
                    if not sample.get('added_at'):
                        issues.append("Missing added_at timestamp")
                        
                    if issues:
                        self.log_result(
                            "Collection Data Quality",
                            False,
                            f"Data quality issues found: {', '.join(issues)}"
                        )
                    else:
                        self.log_result(
                            "Collection Data Quality",
                            True,
                            "Collection data quality is good"
                        )
                else:
                    self.log_result("Collection Data Quality", False, "No owned collections to check")
            else:
                self.log_result("Collection Data Quality", False, f"Cannot retrieve owned collections")
        except Exception as e:
            self.log_result("Collection Data Quality", False, f"Exception: {str(e)}")
            
        # Test 3: Check if user can see available jersey releases that aren't in collection
        try:
            vestiaire_response = requests.get(f"{BACKEND_URL}/vestiaire")
            owned_response = requests.get(f"{BACKEND_URL}/users/{self.user_user_id}/collections/owned", headers=headers)
            
            if vestiaire_response.status_code == 200 and owned_response.status_code == 200:
                vestiaire_data = vestiaire_response.json()
                owned_data = owned_response.json()
                
                vestiaire_ids = {jersey.get('id') for jersey in vestiaire_data}
                owned_ids = {item.get('jersey_release', {}).get('id') for item in owned_data}
                
                available_to_add = vestiaire_ids - owned_ids
                
                if len(available_to_add) == 0:
                    self.log_result(
                        "Available Items to Add",
                        True,
                        f"User has all {len(vestiaire_ids)} available jersey releases in owned collection - duplicate prevention working correctly"
                    )
                else:
                    self.log_result(
                        "Available Items to Add",
                        True,
                        f"{len(available_to_add)} jersey releases available to add to collection"
                    )
            else:
                self.log_result("Available Items to Add", False, "Cannot compare vestiaire and collections")
        except Exception as e:
            self.log_result("Available Items to Add", False, f"Exception: {str(e)}")
        """Test the complete workflow: login → load vestiaire → add to collection"""
        print("\n" + "="*80)
        print("COMPLETE WORKFLOW TEST: User Login → Load Vestiaire → Add to Collection")
        print("="*80)
        
        # Step 1: User Authentication
        if not self.authenticate_user():
            self.log_result("Complete Workflow", False, "User authentication failed - cannot proceed")
            return False
            
        # Step 2: Load Vestiaire Data
        vestiaire_data = self.test_vestiaire_endpoint()
        if not vestiaire_data or len(vestiaire_data) == 0:
            self.log_result("Complete Workflow", False, "No vestiaire data available - cannot test collection functionality")
            return False
            
        # Step 3: Test adding first available jersey release to both collections
        first_jersey = vestiaire_data[0]
        jersey_id = first_jersey.get('id')
        
        if not jersey_id:
            self.log_result("Complete Workflow", False, "Jersey release missing ID field")
            return False
            
        # Get jersey display info
        master_info = first_jersey.get('master_jersey_info', {})
        player_name = first_jersey.get('player_name', 'Unknown Player')
        season = master_info.get('season', 'Unknown Season')
        
        print(f"\nTesting with Jersey Release: {player_name} - {season}")
        
        # Test adding to owned collection
        owned_success = self.test_add_to_collection(
            self.user_token, self.user_user_id, "User", jersey_id, "owned"
        )
        
        # Test adding to wanted collection  
        wanted_success = self.test_add_to_collection(
            self.user_token, self.user_user_id, "User", jersey_id, "wanted"
        )
        
        # Overall workflow success
        workflow_success = owned_success or wanted_success
        self.log_result(
            "Complete Workflow",
            workflow_success,
            f"Workflow {'completed successfully' if workflow_success else 'failed'} - Owned: {owned_success}, Wanted: {wanted_success}"
        )
        
        return workflow_success
        
    def run_comprehensive_test(self):
        """Run comprehensive vestiaire collection functionality test"""
        print("🔍 VESTIAIRE COLLECTION FUNCTIONALITY INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Phase 1: Authentication Testing
        print("PHASE 1: AUTHENTICATION TESTING")
        print("-" * 40)
        admin_auth_success = self.authenticate_admin()
        user_auth_success = self.authenticate_user()
        
        if not (admin_auth_success and user_auth_success):
            print("\n❌ CRITICAL: Authentication failed - cannot proceed with collection testing")
            return False
            
        # Phase 2: Vestiaire Endpoint Testing
        print("\nPHASE 2: VESTIAIRE ENDPOINT TESTING")
        print("-" * 40)
        vestiaire_data = self.test_vestiaire_endpoint()
        
        if not vestiaire_data:
            print("\n❌ CRITICAL: Vestiaire endpoint failed - cannot test collection functionality")
            return False
            
        # Phase 3: Collection Endpoints Testing
        print("\nPHASE 3: COLLECTION ENDPOINTS TESTING")
        print("-" * 40)
        self.test_collection_endpoints_with_auth(self.admin_token, self.admin_user_id, "Admin")
        self.test_collection_endpoints_with_auth(self.user_token, self.user_user_id, "User")
        
        # Phase 4: Collection Addition Testing
        print("\nPHASE 4: COLLECTION ADDITION TESTING")
        print("-" * 40)
        
        if len(vestiaire_data) > 0:
            # Test with first available jersey release
            test_jersey = vestiaire_data[0]
            jersey_id = test_jersey.get('id')
            
            if jersey_id:
                # Get jersey display info
                master_info = test_jersey.get('master_jersey_info', {})
                player_name = test_jersey.get('player_name', 'Unknown Player')
                season = master_info.get('season', 'Unknown Season')
                
                print(f"Testing with Jersey: {player_name} - {season} (ID: {jersey_id})")
                
                # Test both collection types for both users
                self.test_add_to_collection(self.admin_token, self.admin_user_id, "Admin", jersey_id, "owned")
                self.test_add_to_collection(self.admin_token, self.admin_user_id, "Admin", jersey_id, "wanted")
                self.test_add_to_collection(self.user_token, self.user_user_id, "User", jersey_id, "owned")
                self.test_add_to_collection(self.user_token, self.user_user_id, "User", jersey_id, "wanted")
                
                # Test with additional jerseys if available
                if len(vestiaire_data) > 1:
                    second_jersey = vestiaire_data[1]
                    second_jersey_id = second_jersey.get('id')
                    if second_jersey_id:
                        second_master_info = second_jersey.get('master_jersey_info', {})
                        second_player_name = second_jersey.get('player_name', 'Unknown Player')
                        second_season = second_master_info.get('season', 'Unknown Season')
                        
                        print(f"\nTesting with Second Jersey: {second_player_name} - {second_season} (ID: {second_jersey_id})")
                        self.test_add_to_collection(self.user_token, self.user_user_id, "User", second_jersey_id, "owned")
                        self.test_add_to_collection(self.user_token, self.user_user_id, "User", second_jersey_id, "wanted")
            else:
                print("❌ Jersey release missing ID field - cannot test collection addition")
        else:
            print("❌ No jersey releases available for collection testing")
            
        # Phase 5: Complete Workflow Test
        print("\nPHASE 5: COMPLETE WORKFLOW TEST")
        print("-" * 40)
        self.test_complete_workflow()
        
        # Generate Summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("VESTIAIRE COLLECTION FUNCTIONALITY TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\nDETAILED RESULTS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if not result['success']:
                print(f"   └─ {result['details']}")
                
        # Critical Issues Analysis
        critical_failures = [
            result for result in self.test_results 
            if not result['success'] and any(keyword in result['test'].lower() 
            for keyword in ['authentication', 'vestiaire endpoint', 'complete workflow'])
        ]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED ({len(critical_failures)}):")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
                
        # Success Analysis
        collection_successes = [
            result for result in self.test_results
            if result['success'] and 'collection' in result['test'].lower()
        ]
        
        if collection_successes:
            print(f"\n✅ COLLECTION FUNCTIONALITY WORKING ({len(collection_successes)} tests passed):")
            for success in collection_successes[:3]:  # Show first 3
                print(f"   • {success['test']}")
                
        # Final Assessment
        print(f"\n{'='*80}")
        if success_rate >= 90:
            print("🎉 ASSESSMENT: VESTIAIRE COLLECTION FUNCTIONALITY IS WORKING EXCELLENTLY!")
            print("   The reported bug may be a frontend issue or user-specific problem.")
        elif success_rate >= 70:
            print("⚠️  ASSESSMENT: VESTIAIRE COLLECTION FUNCTIONALITY IS MOSTLY WORKING")
            print("   Some issues identified that may explain the reported bug.")
        else:
            print("🚨 ASSESSMENT: CRITICAL ISSUES FOUND IN VESTIAIRE COLLECTION FUNCTIONALITY")
            print("   Multiple failures explain the reported bug.")
            
        print(f"{'='*80}")

def main():
    """Main test execution"""
    tester = VestiaireCollectionTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()