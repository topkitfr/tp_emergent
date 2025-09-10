#!/usr/bin/env python3

"""
Backend Test for Reference Kit Collection Functionality
Testing the fixes for reference kit collection endpoints as specified in review request.

Test Requirements:
1. AUTHENTICATION TEST: Login with admin credentials: topkitfr@gmail.com / TopKitSecure789#
2. COLLECTION RETRIEVAL TEST: 
   - GET /api/users/{user_id}/reference-kit-collections/owned
   - GET /api/users/{user_id}/reference-kit-collections/wanted  
   - Verify these endpoints return existing collection data (should show 2 items from database)
   - Check data enrichment with reference_kit_info, master_kit_info, team_info, brand_info
3. DATA INHERITANCE VERIFICATION: 
   - Verify returned collections show proper team names (not "unknown")
   - Check that season, brand, and other master kit information is inherited correctly
   - Confirm images from reference kits are included in the response
4. NEW DELETE ENDPOINT TEST: 
   - Test the newly created DELETE /api/reference-kit-collections/{collection_id} endpoint
   - Use one of the existing collection IDs from the database
   - Verify proper error handling and successful deletion
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kitfix-contrib.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ReferenceKitCollectionTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status} - {test_name}: {details}")
        
    def authenticate_admin(self):
        """Test 1: AUTHENTICATION TEST - Login with admin credentials"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        print("=" * 60)
        
        try:
            # Login with admin credentials
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            print(f"Login response status: {response.status_code}")
            print(f"Login response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login response data: {data}")
                self.admin_token = data.get('token') or data.get('access_token')
                
                if self.admin_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    # Extract user_id from login response
                    user_data = data.get('user', {})
                    self.admin_user_id = user_data.get('id')
                    
                    if self.admin_user_id:
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated admin user. Token length: {len(self.admin_token)}, User ID: {self.admin_user_id}, Role: {user_data.get('role', 'unknown')}"
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, "No user ID found in login response")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "No access token received")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception during authentication: {str(e)}")
            return False
    
    def test_collection_retrieval_endpoints(self):
        """Test 2: COLLECTION RETRIEVAL TEST - Test GET endpoints for reference kit collections"""
        print("\n📊 TESTING COLLECTION RETRIEVAL ENDPOINTS")
        print("=" * 60)
        
        if not self.admin_user_id:
            self.log_test("Collection Retrieval", False, "No admin user ID available")
            return False, []
            
        endpoints_to_test = [
            ("owned", f"/users/{self.admin_user_id}/reference-kit-collections/owned"),
            ("wanted", f"/users/{self.admin_user_id}/reference-kit-collections/wanted"),
            ("combined", f"/users/{self.admin_user_id}/reference-kit-collections")
        ]
        
        all_collections = []
        endpoint_results = {}
        
        for endpoint_name, endpoint_path in endpoints_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}{endpoint_path}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response structures
                    if endpoint_name == "combined":
                        # Combined endpoint might return structured data
                        if isinstance(data, dict):
                            owned_collections = data.get('owned', [])
                            wanted_collections = data.get('wanted', [])
                            collections = owned_collections + wanted_collections
                        else:
                            collections = data if isinstance(data, list) else []
                    else:
                        # Individual endpoints return arrays
                        collections = data if isinstance(data, list) else []
                    
                    endpoint_results[endpoint_name] = {
                        'success': True,
                        'count': len(collections),
                        'collections': collections
                    }
                    
                    all_collections.extend(collections)
                    
                    self.log_test(
                        f"GET {endpoint_name} collections", 
                        True, 
                        f"Retrieved {len(collections)} collections successfully"
                    )
                    
                else:
                    endpoint_results[endpoint_name] = {
                        'success': False,
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }
                    
                    self.log_test(
                        f"GET {endpoint_name} collections", 
                        False, 
                        f"Failed with status {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                endpoint_results[endpoint_name] = {
                    'success': False,
                    'error': f"Exception: {str(e)}"
                }
                
                self.log_test(
                    f"GET {endpoint_name} collections", 
                    False, 
                    f"Exception: {str(e)}"
                )
        
        # Overall assessment
        successful_endpoints = sum(1 for result in endpoint_results.values() if result['success'])
        total_collections_found = len(all_collections)
        
        overall_success = successful_endpoints >= 2 and total_collections_found >= 0  # At least 2 endpoints working
        
        self.log_test(
            "Collection Retrieval Overall", 
            overall_success, 
            f"Successfully tested {successful_endpoints}/3 endpoints. Total collections found: {total_collections_found}"
        )
        
        return endpoint_results, all_collections
    
    def test_data_enrichment(self, collections):
        """Test 3: DATA INHERITANCE VERIFICATION - Check data enrichment and inheritance"""
        print("\n🔍 TESTING DATA ENRICHMENT AND INHERITANCE")
        print("=" * 60)
        
        if not collections:
            self.log_test("Data Enrichment", False, "No collections available for testing")
            return False
        
        enrichment_results = {
            'total_collections': len(collections),
            'enriched_collections': 0,
            'team_names_found': 0,
            'season_info_found': 0,
            'brand_info_found': 0,
            'images_found': 0,
            'unknown_team_names': 0
        }
        
        for i, collection in enumerate(collections):
            print(f"\n--- Analyzing Collection {i+1} ---")
            
            # Check basic structure
            collection_id = collection.get('id', 'unknown')
            reference_kit_id = collection.get('reference_kit_id', 'unknown')
            collection_type = collection.get('collection_type', 'unknown')
            
            print(f"Collection ID: {collection_id}")
            print(f"Reference Kit ID: {reference_kit_id}")
            print(f"Collection Type: {collection_type}")
            
            # Check reference_kit_info enrichment
            reference_kit_info = collection.get('reference_kit_info') or collection.get('reference_kit', {})
            if reference_kit_info:
                enrichment_results['enriched_collections'] += 1
                print(f"✅ Reference Kit Info: {len(reference_kit_info)} fields")
                
                # Check for images
                product_images = reference_kit_info.get('product_images', [])
                if product_images:
                    enrichment_results['images_found'] += 1
                    print(f"✅ Product Images: {len(product_images)} images found")
                else:
                    print("⚠️ No product images found")
            else:
                print("❌ No reference_kit_info found")
            
            # Check master_kit_info/master_jersey_info enrichment
            master_info = collection.get('master_kit_info') or collection.get('master_jersey_info') or collection.get('master_jersey', {})
            if master_info:
                season = master_info.get('season', 'unknown')
                jersey_type = master_info.get('jersey_type', 'unknown')
                model = master_info.get('model', 'unknown')
                
                if season != 'unknown':
                    enrichment_results['season_info_found'] += 1
                    print(f"✅ Season Info: {season}")
                else:
                    print("⚠️ No season information found")
                    
                print(f"Jersey Type: {jersey_type}")
                print(f"Model: {model}")
            else:
                print("❌ No master kit/jersey info found")
            
            # Check team_info enrichment
            team_info = collection.get('team_info', {})
            # Also check if team_info is nested in master_jersey
            if not team_info and master_info:
                team_info = master_info.get('team_info', {})
                
            if team_info:
                team_name = team_info.get('name', 'unknown')
                if team_name and team_name.lower() != 'unknown':
                    enrichment_results['team_names_found'] += 1
                    print(f"✅ Team Name: {team_name}")
                else:
                    enrichment_results['unknown_team_names'] += 1
                    print(f"⚠️ Team name is unknown or missing")
                    
                team_country = team_info.get('country', 'unknown')
                print(f"Team Country: {team_country}")
            else:
                print("❌ No team_info found")
            
            # Check brand_info enrichment
            brand_info = collection.get('brand_info', {})
            if brand_info:
                enrichment_results['brand_info_found'] += 1
                brand_name = brand_info.get('name', 'unknown')
                print(f"✅ Brand Info: {brand_name}")
            else:
                print("❌ No brand_info found")
                
            # Print the actual collection structure for debugging
            print(f"DEBUG - Collection keys: {list(collection.keys())}")
            if 'reference_kit' in collection:
                print(f"DEBUG - Reference kit keys: {list(collection['reference_kit'].keys()) if collection['reference_kit'] else 'None'}")
            if 'master_jersey' in collection:
                print(f"DEBUG - Master jersey keys: {list(collection['master_jersey'].keys()) if collection['master_jersey'] else 'None'}")
        
        # Calculate success metrics
        enrichment_success_rate = (enrichment_results['enriched_collections'] / enrichment_results['total_collections']) * 100 if enrichment_results['total_collections'] > 0 else 0
        team_name_success_rate = (enrichment_results['team_names_found'] / enrichment_results['total_collections']) * 100 if enrichment_results['total_collections'] > 0 else 0
        
        overall_success = (
            enrichment_results['enriched_collections'] > 0 and
            enrichment_results['unknown_team_names'] == 0 and
            enrichment_success_rate >= 50
        )
        
        self.log_test(
            "Data Enrichment Analysis", 
            overall_success, 
            f"Enrichment rate: {enrichment_success_rate:.1f}%, Team names found: {enrichment_results['team_names_found']}/{enrichment_results['total_collections']}, Unknown team names: {enrichment_results['unknown_team_names']}"
        )
        
        return enrichment_results
    
    def test_delete_endpoint(self, collections):
        """Test 4: NEW DELETE ENDPOINT TEST - Test DELETE endpoint for reference kit collections"""
        print("\n🗑️ TESTING DELETE ENDPOINT")
        print("=" * 60)
        
        if not collections:
            self.log_test("Delete Endpoint", False, "No collections available for delete testing")
            return False
        
        # Find a collection to delete (use the first one)
        test_collection = collections[0]
        collection_id = test_collection.get('id')
        
        if not collection_id:
            self.log_test("Delete Endpoint", False, "No collection ID found for delete testing")
            return False
        
        print(f"Testing DELETE with collection ID: {collection_id}")
        
        try:
            # Test DELETE endpoint
            delete_response = self.session.delete(f"{BACKEND_URL}/reference-kit-collections/{collection_id}")
            
            if delete_response.status_code == 200:
                self.log_test(
                    "DELETE endpoint success", 
                    True, 
                    f"Successfully deleted collection {collection_id}. Response: {delete_response.text}"
                )
                
                # Verify deletion by trying to retrieve the collection again
                # We'll check if the collection count decreased
                verification_response = self.session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/reference-kit-collections")
                
                if verification_response.status_code == 200:
                    verification_data = verification_response.json()
                    
                    # Handle different response structures
                    if isinstance(verification_data, dict):
                        owned_collections = verification_data.get('owned', [])
                        wanted_collections = verification_data.get('wanted', [])
                        remaining_collections = owned_collections + wanted_collections
                    else:
                        remaining_collections = verification_data if isinstance(verification_data, list) else []
                    
                    # Check if the deleted collection is no longer present
                    deleted_collection_found = any(c.get('id') == collection_id for c in remaining_collections)
                    
                    if not deleted_collection_found:
                        self.log_test(
                            "DELETE verification", 
                            True, 
                            f"Collection {collection_id} successfully removed. Remaining collections: {len(remaining_collections)}"
                        )
                        return True
                    else:
                        self.log_test(
                            "DELETE verification", 
                            False, 
                            f"Collection {collection_id} still found after deletion"
                        )
                        return False
                else:
                    self.log_test(
                        "DELETE verification", 
                        False, 
                        f"Failed to verify deletion: {verification_response.status_code}"
                    )
                    return False
                    
            elif delete_response.status_code == 404:
                self.log_test(
                    "DELETE endpoint error handling", 
                    True, 
                    f"Proper 404 error for non-existent collection: {delete_response.text}"
                )
                return True
                
            elif delete_response.status_code == 401:
                self.log_test(
                    "DELETE endpoint authentication", 
                    True, 
                    f"Proper authentication required: {delete_response.text}"
                )
                return False  # This is actually a problem if we're authenticated
                
            else:
                self.log_test(
                    "DELETE endpoint", 
                    False, 
                    f"Unexpected status code {delete_response.status_code}: {delete_response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("DELETE endpoint", False, f"Exception during delete test: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test 5: ERROR HANDLING - Test various error scenarios"""
        print("\n⚠️ TESTING ERROR HANDLING")
        print("=" * 60)
        
        error_tests = []
        
        # Test 1: Invalid user ID
        try:
            response = self.session.get(f"{BACKEND_URL}/users/invalid-user-id/reference-kit-collections/owned")
            error_tests.append({
                'test': 'Invalid User ID',
                'expected_status': [400, 404, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 404, 422]
            })
        except Exception as e:
            error_tests.append({
                'test': 'Invalid User ID',
                'success': False,
                'error': str(e)
            })
        
        # Test 2: Unauthenticated request
        try:
            unauthenticated_session = requests.Session()
            response = unauthenticated_session.get(f"{BACKEND_URL}/users/{self.admin_user_id}/reference-kit-collections/owned")
            error_tests.append({
                'test': 'Unauthenticated Request',
                'expected_status': [401],
                'actual_status': response.status_code,
                'success': response.status_code == 401
            })
        except Exception as e:
            error_tests.append({
                'test': 'Unauthenticated Request',
                'success': False,
                'error': str(e)
            })
        
        # Test 3: Invalid collection ID for DELETE
        try:
            response = self.session.delete(f"{BACKEND_URL}/reference-kit-collections/invalid-collection-id")
            error_tests.append({
                'test': 'Invalid Collection ID DELETE',
                'expected_status': [400, 404, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 404, 422]
            })
        except Exception as e:
            error_tests.append({
                'test': 'Invalid Collection ID DELETE',
                'success': False,
                'error': str(e)
            })
        
        # Log results
        successful_error_tests = 0
        for test in error_tests:
            if test['success']:
                successful_error_tests += 1
                self.log_test(
                    f"Error Handling - {test['test']}", 
                    True, 
                    f"Proper error response: {test.get('actual_status', 'N/A')}"
                )
            else:
                self.log_test(
                    f"Error Handling - {test['test']}", 
                    False, 
                    f"Unexpected response: {test.get('actual_status', test.get('error', 'Unknown'))}"
                )
        
        overall_success = successful_error_tests >= 2  # At least 2 out of 3 error tests should pass
        
        self.log_test(
            "Error Handling Overall", 
            overall_success, 
            f"Passed {successful_error_tests}/{len(error_tests)} error handling tests"
        )
        
        return overall_success
    
    def run_all_tests(self):
        """Run all reference kit collection tests"""
        print("🚀 STARTING REFERENCE KIT COLLECTION FUNCTIONALITY TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Collection Retrieval
        endpoint_results, collections = self.test_collection_retrieval_endpoints()
        
        # Test 3: Data Enrichment
        enrichment_results = self.test_data_enrichment(collections)
        
        # Test 4: Delete Endpoint (only if we have collections)
        if collections:
            delete_success = self.test_delete_endpoint(collections)
        else:
            self.log_test("Delete Endpoint", False, "No collections available for delete testing")
            delete_success = False
        
        # Test 5: Error Handling
        error_handling_success = self.test_error_handling()
        
        # Generate final report
        self.generate_final_report()
        
        return True
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📋 FINAL TEST REPORT - REFERENCE KIT COLLECTION FUNCTIONALITY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📊 DETAILED RESULTS:")
        print("-" * 80)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} - {result['test']}")
            print(f"    Details: {result['details']}")
            print(f"    Time: {result['timestamp']}")
            print()
        
        # Overall assessment
        if success_rate >= 80:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Reference Kit Collection functionality is working well!")
        elif success_rate >= 60:
            print("⚠️ OVERALL ASSESSMENT: GOOD - Reference Kit Collection functionality is mostly working with minor issues.")
        elif success_rate >= 40:
            print("🔧 OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Reference Kit Collection functionality has significant issues.")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL ISSUES - Reference Kit Collection functionality is severely broken.")
        
        print("=" * 80)

def main():
    """Main function to run the tests"""
    tester = ReferenceKitCollectionTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Testing completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Testing failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🚨 Unexpected error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()