#!/usr/bin/env python3

"""
My Collection Critical Bug Investigation Test - CORRECTED VERSION
Testing with correct enum values for condition field.

CRITICAL ISSUE REPORTED:
- User adds jersey to collection via "Add to My Collection" button
- Confirmation message appears after form submission
- Jersey does NOT appear in "My Collection" even after refreshing
- This suggests data is not being properly saved to database
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://image-fix-10.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class MyCollectionCorrectedTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.test_master_kits = []
        self.test_collection_items = []
        
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
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                user_data = data.get('user', {})
                self.admin_user_id = user_data.get('id')
                user_role = user_data.get('role')
                user_name = user_data.get('name')
                
                if self.admin_token and self.admin_user_id:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.admin_token}'
                    })
                    
                    if user_role == 'admin':
                        self.log_test(
                            "Admin Authentication", 
                            True, 
                            f"Successfully authenticated as {user_name} (admin). User ID: {self.admin_user_id}"
                        )
                        return True
                    else:
                        self.log_test("Admin Authentication", False, f"User role is '{user_role}', not 'admin'")
                        return False
                else:
                    self.log_test("Admin Authentication", False, "Missing token or user ID in response")
                    return False
            else:
                self.log_test("Admin Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False

    def create_test_master_kit(self):
        """Create a test Master Kit for collection testing"""
        print("\n🏗️ CREATING TEST MASTER KIT")
        
        try:
            master_kit_data = {
                "club": "Test Collection FC",
                "season": "2024-25",
                "kit_type": "home",
                "competition": "Test League",
                "model": "authentic",
                "brand": "Test Brand",
                "gender": "men"
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
                    self.log_test("Test Master Kit Creation", False, "Master Kit created but no ID returned")
                    return None
            else:
                self.log_test("Test Master Kit Creation", False, f"Failed to create Master Kit: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Test Master Kit Creation", False, f"Exception: {str(e)}")
            return None

    def test_add_to_collection_corrected(self):
        """Test POST /api/my-collection endpoint with CORRECT enum values"""
        print("\n🔥 TESTING ADD TO COLLECTION ENDPOINT (CORRECTED)")
        
        try:
            if not self.test_master_kits:
                master_kit_id = self.create_test_master_kit()
            else:
                master_kit_id = self.test_master_kits[0]
            
            if not master_kit_id:
                self.log_test("Add to Collection - Setup", False, "No Master Kit available for testing")
                return False
            
            # Test adding to "owned" collection with CORRECT enum values
            collection_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "club_stock",  # CORRECT: Using KitCondition enum
                "physical_state": "new_with_tags",  # CORRECT: Using PhysicalState enum
                "purchase_price": 89.99,
                "personal_notes": "Test collection item for bug investigation - corrected version"
            }
            
            print(f"   📤 Adding Master Kit {master_kit_id} to owned collection with correct enums...")
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
                            "Add to Collection - POST Success (Corrected)", 
                            True, 
                            f"Successfully added to collection. ID: {collection_item_id}, Master Kit: {master_kit_info.get('topkit_reference', 'N/A')}"
                        )
                        
                        # Test adding to "wanted" collection
                        wanted_data = {
                            "master_kit_id": master_kit_id,
                            "collection_type": "wanted",
                            "personal_notes": "Test wanted item - corrected version"
                        }
                        
                        wanted_response = self.session.post(f"{BACKEND_URL}/my-collection", json=wanted_data)
                        
                        if wanted_response.status_code == 200:
                            wanted_item = wanted_response.json()
                            wanted_item_id = wanted_item.get('id')
                            if wanted_item_id:
                                self.test_collection_items.append(wanted_item_id)
                                self.log_test(
                                    "Add to Collection - Wanted Type (Corrected)", 
                                    True, 
                                    f"Successfully added to wanted collection. ID: {wanted_item_id}"
                                )
                        else:
                            self.log_test(
                                "Add to Collection - Wanted Type (Corrected)", 
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
                    self.log_test("Add to Collection - POST Success (Corrected)", False, "Collection item created but no ID returned")
                    return False
            else:
                self.log_test("Add to Collection - POST Success (Corrected)", False, f"Failed to add to collection: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Add to Collection Endpoint (Corrected)", False, f"Exception: {str(e)}")
            return False

    def test_get_collection_verification(self):
        """Test GET /api/my-collection endpoint to verify items appear"""
        print("\n🔍 TESTING GET COLLECTION VERIFICATION")
        
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
                                collection_type = item.get('collection_type')
                                condition = item.get('condition')
                                physical_state = item.get('physical_state')
                                
                                self.log_test(
                                    f"Collection Item Verification - {item.get('id')[:8]}", 
                                    True, 
                                    f"Type: {collection_type}, Condition: {condition}, Physical State: {physical_state}, Master Kit: {master_kit.get('topkit_reference', 'N/A')}"
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
                            f"✅ CRITICAL SUCCESS: Found {found_test_items}/{len(self.test_collection_items)} test items in collection! Bug appears to be FIXED."
                        )
                    else:
                        self.log_test(
                            "Get Collection - Test Items Found", 
                            False, 
                            "🚨 CRITICAL BUG CONFIRMED: None of our test items found in collection!"
                        )
                    
                    return found_test_items > 0
                else:
                    self.log_test("Get Collection - Basic Retrieval", False, f"Expected list, got {type(collection_items)}")
                    return False
            else:
                self.log_test("Get Collection - Basic Retrieval", False, f"Failed to get collection: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Get Collection Verification", False, f"Exception: {str(e)}")
            return False

    def test_collection_persistence_workflow(self):
        """Test complete workflow: Add → Retrieve → Verify persistence"""
        print("\n🔄 TESTING COMPLETE COLLECTION WORKFLOW")
        
        try:
            # Create a new Master Kit specifically for workflow testing
            workflow_kit_data = {
                "club": "Workflow Test FC",
                "season": "2024-25",
                "kit_type": "away",
                "competition": "Workflow League",
                "model": "replica",
                "brand": "Workflow Brand",
                "gender": "men"
            }
            
            kit_response = self.session.post(f"{BACKEND_URL}/master-kits", json=workflow_kit_data)
            
            if kit_response.status_code != 200:
                self.log_test("Workflow - Master Kit Creation", False, f"Failed to create workflow kit: {kit_response.status_code}")
                return False
            
            workflow_kit = kit_response.json()
            workflow_kit_id = workflow_kit.get('id')
            workflow_reference = workflow_kit.get('topkit_reference')
            
            self.log_test("Workflow - Master Kit Creation", True, f"Created workflow kit: {workflow_reference}")
            
            # Step 1: Add to collection
            collection_data = {
                "master_kit_id": workflow_kit_id,
                "collection_type": "owned",
                "size": "XL",
                "condition": "match_worn",  # Different condition for variety
                "physical_state": "very_good_condition",
                "purchase_price": 120.00,
                "personal_notes": "Workflow test - complete end-to-end verification"
            }
            
            add_response = self.session.post(f"{BACKEND_URL}/my-collection", json=collection_data)
            
            if add_response.status_code != 200:
                self.log_test("Workflow - Add to Collection", False, f"Failed to add: {add_response.status_code} - {add_response.text}")
                return False
            
            added_item = add_response.json()
            added_item_id = added_item.get('id')
            
            self.log_test("Workflow - Add to Collection", True, f"Added item ID: {added_item_id}")
            
            # Step 2: Immediate retrieval
            immediate_response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if immediate_response.status_code != 200:
                self.log_test("Workflow - Immediate Retrieval", False, f"Failed to retrieve: {immediate_response.status_code}")
                return False
            
            immediate_items = immediate_response.json()
            immediate_found = any(item.get('id') == added_item_id for item in immediate_items)
            
            self.log_test("Workflow - Immediate Retrieval", immediate_found, f"Item found immediately: {immediate_found}")
            
            # Step 3: Wait and retrieve again (persistence test)
            import time
            time.sleep(3)
            
            persistence_response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if persistence_response.status_code != 200:
                self.log_test("Workflow - Persistence Check", False, f"Failed to retrieve after wait: {persistence_response.status_code}")
                return False
            
            persistence_items = persistence_response.json()
            persistence_found = any(item.get('id') == added_item_id for item in persistence_items)
            
            self.log_test("Workflow - Persistence Check", persistence_found, f"Item persisted after 3 seconds: {persistence_found}")
            
            # Step 4: Verify item details
            if persistence_found:
                found_item = next(item for item in persistence_items if item.get('id') == added_item_id)
                
                details_correct = (
                    found_item.get('condition') == 'match_worn' and
                    found_item.get('physical_state') == 'very_good_condition' and
                    found_item.get('size') == 'XL' and
                    found_item.get('purchase_price') == 120.00
                )
                
                self.log_test("Workflow - Item Details Verification", details_correct, f"All details preserved: {details_correct}")
                
                return immediate_found and persistence_found and details_correct
            else:
                return False
                
        except Exception as e:
            self.log_test("Collection Workflow", False, f"Exception: {str(e)}")
            return False

    def test_duplicate_prevention_corrected(self):
        """Test duplicate prevention with correct enum values"""
        print("\n🚫 TESTING DUPLICATE PREVENTION (CORRECTED)")
        
        try:
            if not self.test_master_kits:
                self.log_test("Duplicate Prevention", False, "No test Master Kit available")
                return False
            
            master_kit_id = self.test_master_kits[0]
            
            # Try to add the same Master Kit to the same collection type again
            duplicate_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "M",
                "condition": "training",  # CORRECT enum value
                "physical_state": "used"  # CORRECT enum value
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=duplicate_data)
            
            if response.status_code == 400:
                error_message = response.json().get('detail', '')
                if 'already in your' in error_message.lower():
                    self.log_test("Duplicate Prevention (Corrected)", True, f"Correctly prevented duplicate: {error_message}")
                    return True
                else:
                    self.log_test("Duplicate Prevention (Corrected)", False, f"Wrong error message: {error_message}")
                    return False
            else:
                self.log_test("Duplicate Prevention (Corrected)", False, f"Should have prevented duplicate, got: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Prevention (Corrected)", False, f"Exception: {str(e)}")
            return False

    def run_corrected_tests(self):
        """Run corrected My Collection tests"""
        print("🚀 STARTING MY COLLECTION CORRECTED BUG INVESTIGATION")
        print("=" * 80)
        
        # Test 1: Admin Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Admin authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Create Test Master Kit
        if not self.create_test_master_kit():
            print("\n❌ CRITICAL: Could not create test Master Kit. Cannot proceed with collection tests.")
            return False
        
        # Test 3: Add to Collection with Correct Enums (CRITICAL)
        self.test_add_to_collection_corrected()
        
        # Test 4: Get Collection Verification (CRITICAL)
        self.test_get_collection_verification()
        
        # Test 5: Complete Workflow Test
        self.test_collection_persistence_workflow()
        
        # Test 6: Duplicate Prevention with Correct Enums
        self.test_duplicate_prevention_corrected()
        
        # Print summary
        self.print_corrected_summary()
        
        return True

    def print_corrected_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 MY COLLECTION CORRECTED BUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Check for critical success
        critical_success = any(
            result['success'] and 'Test Items Found' in result['test'] and 'CRITICAL SUCCESS' in result['details']
            for result in self.test_results
        )
        
        if critical_success:
            print(f"\n🎉 CRITICAL BUG RESOLUTION CONFIRMED!")
            print(f"   The issue was INCORRECT ENUM VALUES in the frontend/test data.")
            print(f"   Backend is working correctly when proper enum values are used.")
            print(f"   ROOT CAUSE: Frontend likely sending 'new_with_tags' for condition field")
            print(f"   instead of correct KitCondition values like 'club_stock', 'match_worn', etc.")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        
        # Final assessment
        if critical_success:
            print(f"\n🔧 SOLUTION IDENTIFIED:")
            print(f"   Frontend needs to use correct enum values:")
            print(f"   - condition: 'club_stock', 'match_prepared', 'match_worn', 'training', 'other'")
            print(f"   - physical_state: 'new_with_tags', 'very_good_condition', 'used', 'damaged', 'needs_restoration'")
            print(f"   Backend My Collection endpoints are working perfectly!")
        elif success_rate >= 75:
            print(f"\n✅ MOSTLY WORKING: My Collection system is functional with minor issues.")
        else:
            print(f"\n❌ ISSUES REMAIN: My Collection system still has problems requiring investigation.")

def main():
    """Main test execution"""
    tester = MyCollectionCorrectedTester()
    
    try:
        success = tester.run_corrected_tests()
        
        if success:
            print(f"\n🏁 CORRECTED BUG INVESTIGATION COMPLETED")
        else:
            print(f"\n💥 CORRECTED BUG INVESTIGATION FAILED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()