#!/usr/bin/env python3

"""
My Collection Critical Bug Investigation Test
Testing the critical bug where jerseys are not appearing in collection despite confirmation message.

CRITICAL ISSUE REPORTED:
- User adds jersey to collection via "Add to My Collection" button
- Confirmation message appears after form submission
- Jersey does NOT appear in "My Collection" even after refreshing
- This suggests data is not being properly saved to database

BACKEND TESTING REQUIRED:
1. Test My Collection Endpoints (POST /api/my-collection, GET /api/my-collection)
2. Test Master Kit to Collection Workflow
3. Database Verification
4. Authentication Testing
5. Error Logging
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MyCollectionBugTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.test_master_kits = []  # Store created test master kits
        self.test_collection_items = []  # Store created collection items
        
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
        """Test admin authentication"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION")
        
        try:
            # Login with admin credentials
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                
                # Get user info from login response
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                user_role = user_data.get('role')
                user_name = user_data.get('name')
                
                if self.admin_token and self.admin_user_id:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    if user_role == 'admin':
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as {user_name} (admin). User ID: {self.admin_user_id}, Token length: {len(self.admin_token)}"
                        )
                        return True
                    else:
                        self.log_test(
                            "Admin Authentication", 
                            False, 
                            f"User authenticated but role is '{user_role}', not 'admin'"
                        )
                        return False
                else:
                    self.log_test(
                        "Admin Authentication", 
                        False, 
                        f"Missing token or user ID in response. Token: {bool(self.admin_token)}, User ID: {bool(self.admin_user_id)}"
                    )
                    return False
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_master_kit(self):
        """Create a test Master Kit for collection testing"""
        print("\n🏗️ CREATING TEST MASTER KIT")
        
        try:
            master_kit_data = {
                "club": "Test FC",
                "season": "2024-25",
                "kit_type": "home",
                "competition": "Test League",
                "model": "authentic",
                "brand": "Test Brand",
                "gender": "men",
                "front_photo": "test_photo.jpg"
            }
            
            response = self.session.post(f"{BACKEND_URL}/master-kits", json=master_kit_data)
            
            if response.status_code == 200:
                master_kit = response.json()
                master_kit_id = master_kit.get('id')
                topkit_reference = master_kit.get('topkit_reference')
                
                if master_kit_id:
                    self.test_master_kits.append(master_kit_id)
                    self.log_test(
                        "Test Master Kit Creation", 
                        True, 
                        f"Created Master Kit: {topkit_reference} (ID: {master_kit_id})"
                    )
                    return master_kit_id
                else:
                    self.log_test(
                        "Test Master Kit Creation", 
                        False, 
                        "Master Kit created but no ID returned"
                    )
                    return None
            else:
                self.log_test(
                    "Test Master Kit Creation", 
                    False, 
                    f"Failed to create Master Kit: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test("Test Master Kit Creation", False, f"Exception: {str(e)}")
            return None

    def test_master_kit_endpoints(self):
        """Test Master Kit endpoints to ensure they work"""
        print("\n🎯 TESTING MASTER KIT ENDPOINTS")
        
        try:
            # Test GET /api/master-kits
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                self.log_test(
                    "Master Kits List Endpoint", 
                    True, 
                    f"Retrieved {len(master_kits)} Master Kits"
                )
                
                # Test search functionality
                search_response = self.session.get(f"{BACKEND_URL}/master-kits/search?q=Test")
                if search_response.status_code == 200:
                    search_results = search_response.json()
                    self.log_test(
                        "Master Kits Search Endpoint", 
                        True, 
                        f"Search returned {len(search_results)} results"
                    )
                else:
                    self.log_test(
                        "Master Kits Search Endpoint", 
                        False, 
                        f"Search failed: {search_response.status_code}"
                    )
                
                return True
            else:
                self.log_test(
                    "Master Kits List Endpoint", 
                    False, 
                    f"Failed to get Master Kits: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Master Kit Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_add_to_collection_endpoint(self):
        """Test POST /api/my-collection endpoint - CRITICAL TEST"""
        print("\n🔥 TESTING ADD TO COLLECTION ENDPOINT (CRITICAL)")
        
        try:
            # First, ensure we have a Master Kit to add
            master_kit_id = None
            if self.test_master_kits:
                master_kit_id = self.test_master_kits[0]
            else:
                master_kit_id = self.create_test_master_kit()
            
            if not master_kit_id:
                self.log_test(
                    "Add to Collection - Setup", 
                    False, 
                    "No Master Kit available for testing"
                )
                return False
            
            # Test adding to "owned" collection
            collection_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "new_with_tags",
                "purchase_price": 89.99,
                "purchase_date": "2024-01-15",
                "personal_notes": "Test collection item for bug investigation"
            }
            
            print(f"   📤 Adding Master Kit {master_kit_id} to owned collection...")
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=collection_data)
            
            if response.status_code == 200:
                collection_item = response.json()
                collection_item_id = collection_item.get('id')
                
                if collection_item_id:
                    self.test_collection_items.append(collection_item_id)
                    
                    # Verify the response contains expected data
                    expected_fields = ['id', 'master_kit_id', 'collection_type', 'user_id', 'master_kit']
                    missing_fields = [field for field in expected_fields if field not in collection_item]
                    
                    if not missing_fields:
                        master_kit_info = collection_item.get('master_kit', {})
                        self.log_test(
                            "Add to Collection - POST Success", 
                            True, 
                            f"Successfully added to collection. ID: {collection_item_id}, Master Kit: {master_kit_info.get('topkit_reference', 'N/A')}"
                        )
                        
                        # Test adding to "wanted" collection (different type)
                        wanted_data = {
                            "master_kit_id": master_kit_id,
                            "collection_type": "wanted",
                            "personal_notes": "Test wanted item"
                        }
                        
                        wanted_response = self.session.post(f"{BACKEND_URL}/my-collection", json=wanted_data)
                        
                        if wanted_response.status_code == 200:
                            wanted_item = wanted_response.json()
                            wanted_item_id = wanted_item.get('id')
                            if wanted_item_id:
                                self.test_collection_items.append(wanted_item_id)
                                self.log_test(
                                    "Add to Collection - Wanted Type", 
                                    True, 
                                    f"Successfully added to wanted collection. ID: {wanted_item_id}"
                                )
                        else:
                            self.log_test(
                                "Add to Collection - Wanted Type", 
                                False, 
                                f"Failed to add to wanted: {wanted_response.status_code} - {wanted_response.text}"
                            )
                        
                        return True
                    else:
                        self.log_test(
                            "Add to Collection - Response Validation", 
                            False, 
                            f"Missing fields in response: {missing_fields}"
                        )
                        return False
                else:
                    self.log_test(
                        "Add to Collection - POST Success", 
                        False, 
                        "Collection item created but no ID returned"
                    )
                    return False
            else:
                self.log_test(
                    "Add to Collection - POST Success", 
                    False, 
                    f"Failed to add to collection: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Add to Collection Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_get_collection_endpoint(self):
        """Test GET /api/my-collection endpoint - CRITICAL TEST"""
        print("\n🔍 TESTING GET COLLECTION ENDPOINT (CRITICAL)")
        
        try:
            # Test getting all collection items
            response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if response.status_code == 200:
                collection_items = response.json()
                
                if isinstance(collection_items, list):
                    self.log_test(
                        "Get Collection - Basic Retrieval", 
                        True, 
                        f"Retrieved {len(collection_items)} collection items"
                    )
                    
                    # Verify our test items are in the collection
                    found_test_items = 0
                    for item in collection_items:
                        if item.get('id') in self.test_collection_items:
                            found_test_items += 1
                            
                            # Verify item structure
                            required_fields = ['id', 'master_kit_id', 'collection_type', 'user_id', 'master_kit']
                            missing_fields = [field for field in required_fields if field not in item]
                            
                            if not missing_fields:
                                master_kit = item.get('master_kit', {})
                                self.log_test(
                                    f"Collection Item Structure - {item.get('id')}", 
                                    True, 
                                    f"Item has all required fields. Master Kit: {master_kit.get('topkit_reference', 'N/A')}"
                                )
                            else:
                                self.log_test(
                                    f"Collection Item Structure - {item.get('id')}", 
                                    False, 
                                    f"Missing fields: {missing_fields}"
                                )
                    
                    if found_test_items > 0:
                        self.log_test(
                            "Get Collection - Test Items Found", 
                            True, 
                            f"Found {found_test_items}/{len(self.test_collection_items)} test items in collection"
                        )
                    else:
                        self.log_test(
                            "Get Collection - Test Items Found", 
                            False, 
                            "CRITICAL: None of our test items found in collection! This indicates the bug."
                        )
                    
                    # Test filtering by collection type
                    owned_response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=owned")
                    if owned_response.status_code == 200:
                        owned_items = owned_response.json()
                        self.log_test(
                            "Get Collection - Owned Filter", 
                            True, 
                            f"Retrieved {len(owned_items)} owned items"
                        )
                    
                    wanted_response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=wanted")
                    if wanted_response.status_code == 200:
                        wanted_items = wanted_response.json()
                        self.log_test(
                            "Get Collection - Wanted Filter", 
                            True, 
                            f"Retrieved {len(wanted_items)} wanted items"
                        )
                    
                    return True
                else:
                    self.log_test(
                        "Get Collection - Basic Retrieval", 
                        False, 
                        f"Expected list, got {type(collection_items)}"
                    )
                    return False
            else:
                self.log_test(
                    "Get Collection - Basic Retrieval", 
                    False, 
                    f"Failed to get collection: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Get Collection Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_database_persistence(self):
        """Test if data persists in database by making multiple requests"""
        print("\n💾 TESTING DATABASE PERSISTENCE")
        
        try:
            if not self.test_collection_items:
                self.log_test(
                    "Database Persistence", 
                    False, 
                    "No test collection items to verify persistence"
                )
                return False
            
            # Wait a moment and then check if items still exist
            import time
            time.sleep(2)
            
            # Make multiple requests to verify consistency
            for i in range(3):
                response = self.session.get(f"{BACKEND_URL}/my-collection")
                
                if response.status_code == 200:
                    collection_items = response.json()
                    found_items = [item for item in collection_items if item.get('id') in self.test_collection_items]
                    
                    self.log_test(
                        f"Database Persistence - Request {i+1}", 
                        len(found_items) > 0, 
                        f"Found {len(found_items)} test items in request {i+1}"
                    )
                else:
                    self.log_test(
                        f"Database Persistence - Request {i+1}", 
                        False, 
                        f"Request failed: {response.status_code}"
                    )
                
                time.sleep(1)
            
            return True
                
        except Exception as e:
            self.log_test("Database Persistence", False, f"Exception: {str(e)}")
            return False

    def test_duplicate_prevention(self):
        """Test duplicate prevention logic"""
        print("\n🚫 TESTING DUPLICATE PREVENTION")
        
        try:
            if not self.test_master_kits:
                self.log_test(
                    "Duplicate Prevention", 
                    False, 
                    "No test Master Kit available"
                )
                return False
            
            master_kit_id = self.test_master_kits[0]
            
            # Try to add the same Master Kit to the same collection type again
            duplicate_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "used"
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=duplicate_data)
            
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'already in your' in error_message.lower():
                    self.log_test(
                        "Duplicate Prevention", 
                        True, 
                        f"Correctly prevented duplicate: {error_message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Duplicate Prevention", 
                        False, 
                        f"Wrong error message: {error_message}"
                    )
                    return False
            else:
                self.log_test(
                    "Duplicate Prevention", 
                    False, 
                    f"Should have prevented duplicate, got: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Duplicate Prevention", False, f"Exception: {str(e)}")
            return False

    def test_collection_update_endpoint(self):
        """Test PUT /api/my-collection/{id} endpoint"""
        print("\n✏️ TESTING COLLECTION UPDATE ENDPOINT")
        
        try:
            if not self.test_collection_items:
                self.log_test(
                    "Collection Update", 
                    False, 
                    "No test collection items to update"
                )
                return False
            
            collection_item_id = self.test_collection_items[0]
            
            # Update the collection item
            update_data = {
                "personal_notes": "Updated notes for bug investigation",
                "purchase_price": 99.99,
                "condition": "very_good_condition"
            }
            
            response = self.session.put(f"{BACKEND_URL}/my-collection/{collection_item_id}", json=update_data)
            
            if response.status_code == 200:
                updated_item = response.json()
                
                # Verify the update was applied
                if (updated_item.get('personal_notes') == update_data['personal_notes'] and
                    updated_item.get('purchase_price') == update_data['purchase_price']):
                    self.log_test(
                        "Collection Update", 
                        True, 
                        f"Successfully updated collection item {collection_item_id}"
                    )
                    return True
                else:
                    self.log_test(
                        "Collection Update", 
                        False, 
                        "Update response doesn't reflect changes"
                    )
                    return False
            else:
                self.log_test(
                    "Collection Update", 
                    False, 
                    f"Failed to update: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Collection Update", False, f"Exception: {str(e)}")
            return False

    def test_collection_delete_endpoint(self):
        """Test DELETE /api/my-collection/{id} endpoint"""
        print("\n🗑️ TESTING COLLECTION DELETE ENDPOINT")
        
        try:
            if not self.test_collection_items:
                self.log_test(
                    "Collection Delete", 
                    False, 
                    "No test collection items to delete"
                )
                return False
            
            # Use the last item for deletion test
            collection_item_id = self.test_collection_items[-1]
            
            response = self.session.delete(f"{BACKEND_URL}/my-collection/{collection_item_id}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify the item is actually deleted
                verify_response = self.session.get(f"{BACKEND_URL}/my-collection")
                if verify_response.status_code == 200:
                    remaining_items = verify_response.json()
                    deleted_item_found = any(item.get('id') == collection_item_id for item in remaining_items)
                    
                    if not deleted_item_found:
                        self.log_test(
                            "Collection Delete", 
                            True, 
                            f"Successfully deleted collection item {collection_item_id}"
                        )
                        # Remove from our test list
                        self.test_collection_items.remove(collection_item_id)
                        return True
                    else:
                        self.log_test(
                            "Collection Delete", 
                            False, 
                            "Item still found in collection after deletion"
                        )
                        return False
                else:
                    self.log_test(
                        "Collection Delete", 
                        False, 
                        "Could not verify deletion"
                    )
                    return False
            else:
                self.log_test(
                    "Collection Delete", 
                    False, 
                    f"Failed to delete: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Collection Delete", False, f"Exception: {str(e)}")
            return False

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("\n⚠️ TESTING ERROR SCENARIOS")
        
        try:
            # Test adding non-existent Master Kit
            invalid_data = {
                "master_kit_id": "non-existent-id",
                "collection_type": "owned"
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=invalid_data)
            
            if response.status_code == 404:
                self.log_test(
                    "Error Handling - Invalid Master Kit", 
                    True, 
                    "Correctly returned 404 for non-existent Master Kit"
                )
            else:
                self.log_test(
                    "Error Handling - Invalid Master Kit", 
                    False, 
                    f"Expected 404, got {response.status_code}"
                )
            
            # Test invalid collection type
            invalid_type_data = {
                "master_kit_id": self.test_master_kits[0] if self.test_master_kits else "test",
                "collection_type": "invalid_type"
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=invalid_type_data)
            
            if response.status_code in [400, 422]:
                self.log_test(
                    "Error Handling - Invalid Collection Type", 
                    True, 
                    f"Correctly rejected invalid collection type: {response.status_code}"
                )
            else:
                self.log_test(
                    "Error Handling - Invalid Collection Type", 
                    False, 
                    f"Expected 400/422, got {response.status_code}"
                )
            
            return True
                
        except Exception as e:
            self.log_test("Error Scenarios", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all My Collection bug investigation tests"""
        print("🚀 STARTING MY COLLECTION CRITICAL BUG INVESTIGATION")
        print("=" * 80)
        
        # Test 1: Admin Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Master Kit Endpoints (prerequisite)
        self.test_master_kit_endpoints()
        
        # Test 3: Create Test Master Kit
        if not self.create_test_master_kit():
            print("\n❌ CRITICAL: Could not create test Master Kit. Cannot proceed with collection tests.")
            return False
        
        # Test 4: Add to Collection Endpoint (CRITICAL)
        self.test_add_to_collection_endpoint()
        
        # Test 5: Get Collection Endpoint (CRITICAL)
        self.test_get_collection_endpoint()
        
        # Test 6: Database Persistence
        self.test_database_persistence()
        
        # Test 7: Duplicate Prevention
        self.test_duplicate_prevention()
        
        # Test 8: Collection Update
        self.test_collection_update_endpoint()
        
        # Test 9: Collection Delete
        self.test_collection_delete_endpoint()
        
        # Test 10: Error Scenarios
        self.test_error_scenarios()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 MY COLLECTION CRITICAL BUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Critical issue analysis
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and any(keyword in result['test'].lower() for keyword in ['add to collection', 'get collection', 'test items found']):
                critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🔥 CRITICAL FAILURES DETECTED:")
            for failure in critical_failures:
                print(f"   • {failure['test']}: {failure['details']}")
            print(f"\n💡 ROOT CAUSE ANALYSIS:")
            print(f"   The critical bug appears to be in the collection save/retrieve workflow.")
            print(f"   Items may not be properly persisting to the database or user_id filtering may be incorrect.")
        
        if failed_tests > 0:
            print(f"\n❌ ALL FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        
        # Overall assessment
        if critical_failures:
            print(f"\n🚨 CRITICAL BUG CONFIRMED: The reported issue where jerseys don't appear in collection is REAL!")
            print(f"   Immediate investigation needed in the My Collection endpoints and database operations.")
        elif success_rate >= 90:
            print(f"\n🎉 EXCELLENT: My Collection system is working correctly - bug may be frontend-related.")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: My Collection system is mostly working with minor backend issues.")
        else:
            print(f"\n❌ CRITICAL: My Collection system has significant backend issues requiring immediate attention.")

def main():
    """Main test execution"""
    tester = MyCollectionBugTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🏁 BUG INVESTIGATION COMPLETED")
        else:
            print(f"\n💥 BUG INVESTIGATION FAILED - Critical authentication issue")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()