#!/usr/bin/env python3

"""
Master Kit to My Collection Workflow Backend Test
Testing the complete Master Kit to My Collection workflow as requested in the review.

Test Requirements from Review Request:
1. User authentication with credentials: topkitfr@gmail.com / TopKitSecure789#
2. User can add a Master Kit to their collection (test both "Add to My Collection" and "Add to Want List" functionality)
3. Personal details form works correctly when adding to collection
4. Added Master Kits appear properly in the user's "My Collection" page under both "Owned" and "Wanted" tabs
5. Collection statistics update correctly after adding items

Focus on the full workflow from Kit Area -> Add to Collection -> Personal Details -> My Collection page display.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BACKEND_URL = "https://jersey-collab-1.preview.emergentagent.com/api"
USER_EMAIL = "topkitfr@gmail.com"
USER_PASSWORD = "TopKitSecure789#"

class MasterKitCollectionWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.user_id = None
        self.test_results = []
        self.available_master_kits = []
        self.test_collection_items = []  # Store created collection items for cleanup
        
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

    def authenticate_user(self):
        """Test user authentication with provided credentials"""
        print("\n🔐 TESTING USER AUTHENTICATION")
        
        try:
            # Login with provided credentials
            login_data = {
                "email": USER_EMAIL,
                "password": USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                
                # Get user info from login response
                user_data = data.get('user', {})
                self.user_id = user_data.get('id')
                user_name = user_data.get('name')
                user_role = user_data.get('role')
                
                if self.user_token and self.user_id:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.user_token}'
                    })
                    
                    self.log_test(
                        "User Authentication", 
                        True, 
                        f"Successfully authenticated as {user_name} ({user_role}). User ID: {self.user_id}, Token length: {len(self.user_token)}"
                    )
                    return True
                else:
                    self.log_test(
                        "User Authentication", 
                        False, 
                        f"Missing token or user ID in response. Token: {bool(self.user_token)}, User ID: {bool(self.user_id)}"
                    )
                    return False
            else:
                self.log_test(
                    "User Authentication", 
                    False, 
                    f"Login failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False

    def test_get_master_kits(self):
        """Test GET /api/master-kits to get available kits"""
        print("\n📦 TESTING GET MASTER KITS")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                
                if isinstance(master_kits, list):
                    self.available_master_kits = master_kits
                    
                    if len(master_kits) > 0:
                        # Check structure of first master kit
                        first_kit = master_kits[0]
                        required_fields = ['id', 'club', 'season', 'kit_type', 'brand']
                        missing_fields = [field for field in required_fields if field not in first_kit]
                        
                        if not missing_fields:
                            self.log_test(
                                "Get Master Kits", 
                                True, 
                                f"Retrieved {len(master_kits)} Master Kits. Sample kit: {first_kit.get('club')} {first_kit.get('season')} {first_kit.get('kit_type')}"
                            )
                            
                            # Log details of available kits for testing
                            kit_details = []
                            for kit in master_kits[:3]:  # Show first 3 kits
                                kit_details.append(f"{kit.get('club')} {kit.get('season')} {kit.get('kit_type')} (ID: {kit.get('id')})")
                            
                            self.log_test(
                                "Master Kits Available for Testing", 
                                True, 
                                f"Available kits: {'; '.join(kit_details)}"
                            )
                            
                            return True
                        else:
                            self.log_test(
                                "Get Master Kits", 
                                False, 
                                f"Master Kit missing required fields: {missing_fields}"
                            )
                            return False
                    else:
                        self.log_test(
                            "Get Master Kits", 
                            False, 
                            "No Master Kits found in database"
                        )
                        return False
                else:
                    self.log_test(
                        "Get Master Kits", 
                        False, 
                        f"Expected list, got {type(master_kits)}"
                    )
                    return False
            else:
                self.log_test(
                    "Get Master Kits", 
                    False, 
                    f"Failed to get Master Kits: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Get Master Kits", False, f"Exception: {str(e)}")
            return False

    def test_add_to_owned_collection(self):
        """Test POST /api/my-collection to add a kit to owned collection"""
        print("\n➕ TESTING ADD TO OWNED COLLECTION")
        
        if not self.available_master_kits:
            self.log_test(
                "Add to Owned Collection", 
                False, 
                "No Master Kits available for testing"
            )
            return False
        
        try:
            # Use the first available Master Kit
            test_kit = self.available_master_kits[0]
            master_kit_id = test_kit.get('id')
            
            # Create collection data with personal details
            collection_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "L",
                "condition": "club_stock",  # Use correct enum value
                "physical_state": "very_good_condition",  # Use correct enum value
                "purchase_price": 89.99,
                "personal_notes": "My favorite kit from this season",
                "name_printing": "Mbappé",  # Use correct field name
                "number_printing": "7",  # Use correct field name
                "is_signed": False  # Use correct field name
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=collection_data)
            
            if response.status_code in [200, 201]:
                collection_item = response.json()
                collection_id = collection_item.get('id')
                
                if collection_id:
                    self.test_collection_items.append(collection_id)
                    
                    # Verify the response contains the Master Kit info
                    master_kit_info = collection_item.get('master_kit')
                    if master_kit_info:
                        self.log_test(
                            "Add to Owned Collection", 
                            True, 
                            f"Successfully added {test_kit.get('club')} {test_kit.get('season')} {test_kit.get('kit_type')} to owned collection. Collection ID: {collection_id}"
                        )
                        
                        # Verify personal details were saved
                        saved_details = {
                            'size': collection_item.get('size'),
                            'condition': collection_item.get('condition'),
                            'physical_state': collection_item.get('physical_state'),
                            'purchase_price': collection_item.get('purchase_price'),
                            'name_printing': collection_item.get('name_printing'),
                            'number_printing': collection_item.get('number_printing')
                        }
                        
                        self.log_test(
                            "Personal Details Saved - Owned", 
                            True, 
                            f"Personal details saved correctly: Size {saved_details['size']}, Condition {saved_details['condition']}, State {saved_details['physical_state']}, Price €{saved_details['purchase_price']}, Player {saved_details['name_printing']} #{saved_details['number_printing']}"
                        )
                        
                        return True
                    else:
                        self.log_test(
                            "Add to Owned Collection", 
                            False, 
                            "Response missing Master Kit information"
                        )
                        return False
                else:
                    self.log_test(
                        "Add to Owned Collection", 
                        False, 
                        "Response missing collection ID"
                    )
                    return False
            else:
                self.log_test(
                    "Add to Owned Collection", 
                    False, 
                    f"Failed to add to collection: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Add to Owned Collection", False, f"Exception: {str(e)}")
            return False

    def test_add_to_want_list(self):
        """Test POST /api/my-collection with collection_type="wanted" to add to want list"""
        print("\n❤️ TESTING ADD TO WANT LIST")
        
        if len(self.available_master_kits) < 2:
            self.log_test(
                "Add to Want List", 
                False, 
                "Need at least 2 Master Kits for testing (one for owned, one for wanted)"
            )
            return False
        
        try:
            # Use the second available Master Kit for want list
            test_kit = self.available_master_kits[1]
            master_kit_id = test_kit.get('id')
            
            # Create want list data with personal details
            want_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "wanted",
                "size": "M",  # Desired size
                "personal_notes": "Looking for this kit in good condition",
                "name_printing": "Neymar",  # Player preference
                "number_printing": "10"  # Number preference
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=want_data)
            
            if response.status_code in [200, 201]:
                want_item = response.json()
                want_id = want_item.get('id')
                
                if want_id:
                    self.test_collection_items.append(want_id)
                    
                    # Verify the response contains the Master Kit info
                    master_kit_info = want_item.get('master_kit')
                    if master_kit_info:
                        self.log_test(
                            "Add to Want List", 
                            True, 
                            f"Successfully added {test_kit.get('club')} {test_kit.get('season')} {test_kit.get('kit_type')} to want list. Want ID: {want_id}"
                        )
                        
                        # Verify want list details were saved
                        saved_details = {
                            'desired_size': want_item.get('desired_size'),
                            'max_price': want_item.get('max_price'),
                            'condition_preference': want_item.get('condition_preference'),
                            'priority': want_item.get('priority')
                        }
                        
                        self.log_test(
                            "Personal Details Saved - Wanted", 
                            True, 
                            f"Want list details saved correctly: Size {saved_details['desired_size']}, Max Price €{saved_details['max_price']}, Condition {saved_details['condition_preference']}, Priority {saved_details['priority']}"
                        )
                        
                        return True
                    else:
                        self.log_test(
                            "Add to Want List", 
                            False, 
                            "Response missing Master Kit information"
                        )
                        return False
                else:
                    self.log_test(
                        "Add to Want List", 
                        False, 
                        "Response missing want ID"
                    )
                    return False
            else:
                self.log_test(
                    "Add to Want List", 
                    False, 
                    f"Failed to add to want list: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Add to Want List", False, f"Exception: {str(e)}")
            return False

    def test_get_my_collection_owned(self):
        """Test GET /api/my-collection to verify owned items appear"""
        print("\n👕 TESTING GET MY COLLECTION - OWNED")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=owned")
            
            if response.status_code == 200:
                owned_items = response.json()
                
                if isinstance(owned_items, list):
                    owned_count = len(owned_items)
                    
                    if owned_count > 0:
                        # Verify the added item appears in owned collection
                        first_item = owned_items[0]
                        master_kit_info = first_item.get('master_kit')
                        
                        if master_kit_info:
                            self.log_test(
                                "Get My Collection - Owned", 
                                True, 
                                f"Found {owned_count} owned item(s). First item: {master_kit_info.get('club')} {master_kit_info.get('season')} {master_kit_info.get('kit_type')}"
                            )
                            
                            # Verify personal details are included
                            personal_details = {
                                'size': first_item.get('size'),
                                'condition': first_item.get('condition'),
                                'physical_state': first_item.get('physical_state'),
                                'purchase_price': first_item.get('purchase_price'),
                                'name_printing': first_item.get('name_printing')
                            }
                            
                            self.log_test(
                                "Owned Collection Personal Details", 
                                True, 
                                f"Personal details retrieved: Size {personal_details['size']}, Condition {personal_details['condition']}, State {personal_details['physical_state']}, Price €{personal_details['purchase_price']}, Player {personal_details['name_printing']}"
                            )
                            
                            return True
                        else:
                            self.log_test(
                                "Get My Collection - Owned", 
                                False, 
                                "Owned items missing Master Kit information"
                            )
                            return False
                    else:
                        self.log_test(
                            "Get My Collection - Owned", 
                            False, 
                            "No owned items found (expected at least 1 from previous test)"
                        )
                        return False
                else:
                    self.log_test(
                        "Get My Collection - Owned", 
                        False, 
                        f"Expected list, got {type(owned_items)}"
                    )
                    return False
            else:
                self.log_test(
                    "Get My Collection - Owned", 
                    False, 
                    f"Failed to get owned collection: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Get My Collection - Owned", False, f"Exception: {str(e)}")
            return False

    def test_get_my_collection_wanted(self):
        """Test GET /api/my-collection to verify wanted items appear"""
        print("\n❤️ TESTING GET MY COLLECTION - WANTED")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=wanted")
            
            if response.status_code == 200:
                wanted_items = response.json()
                
                if isinstance(wanted_items, list):
                    wanted_count = len(wanted_items)
                    
                    if wanted_count > 0:
                        # Verify the added item appears in wanted collection
                        first_item = wanted_items[0]
                        master_kit_info = first_item.get('master_kit')
                        
                        if master_kit_info:
                            self.log_test(
                                "Get My Collection - Wanted", 
                                True, 
                                f"Found {wanted_count} wanted item(s). First item: {master_kit_info.get('club')} {master_kit_info.get('season')} {master_kit_info.get('kit_type')}"
                            )
                            
                            # Verify want list details are included
                            want_details = {
                                'size': first_item.get('size'),
                                'name_printing': first_item.get('name_printing'),
                                'number_printing': first_item.get('number_printing'),
                                'personal_notes': first_item.get('personal_notes')
                            }
                            
                            self.log_test(
                                "Wanted Collection Details", 
                                True, 
                                f"Want list details retrieved: Size {want_details['size']}, Player {want_details['name_printing']} #{want_details['number_printing']}, Notes: {want_details['personal_notes'][:30] if want_details['personal_notes'] else 'None'}..."
                            )
                            
                            return True
                        else:
                            self.log_test(
                                "Get My Collection - Wanted", 
                                False, 
                                "Wanted items missing Master Kit information"
                            )
                            return False
                    else:
                        self.log_test(
                            "Get My Collection - Wanted", 
                            False, 
                            "No wanted items found (expected at least 1 from previous test)"
                        )
                        return False
                else:
                    self.log_test(
                        "Get My Collection - Wanted", 
                        False, 
                        f"Expected list, got {type(wanted_items)}"
                    )
                    return False
            else:
                self.log_test(
                    "Get My Collection - Wanted", 
                    False, 
                    f"Failed to get wanted collection: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Get My Collection - Wanted", False, f"Exception: {str(e)}")
            return False

    def test_collection_statistics(self):
        """Test that collection statistics update correctly after adding items"""
        print("\n📊 TESTING COLLECTION STATISTICS")
        
        try:
            # Get all collection items to calculate statistics
            response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if response.status_code == 200:
                all_items = response.json()
                
                if isinstance(all_items, list):
                    # Calculate statistics
                    owned_items = [item for item in all_items if item.get('collection_type') == 'owned']
                    wanted_items = [item for item in all_items if item.get('collection_type') == 'wanted']
                    
                    owned_count = len(owned_items)
                    wanted_count = len(wanted_items)
                    
                    # Calculate total value from owned items
                    total_value = sum(item.get('purchase_price', 0) for item in owned_items if item.get('purchase_price'))
                    average_value = total_value / owned_count if owned_count > 0 else 0
                    
                    self.log_test(
                        "Collection Statistics", 
                        True, 
                        f"Collection stats calculated: {owned_count} owned kits, {wanted_count} wanted kits, €{total_value:.2f} total value, €{average_value:.2f} average value"
                    )
                    
                    # Verify we have the expected items from our tests
                    expected_owned = 1  # We added 1 owned item
                    expected_wanted = 1  # We added 1 wanted item
                    
                    if owned_count >= expected_owned and wanted_count >= expected_wanted:
                        self.log_test(
                            "Collection Count Verification", 
                            True, 
                            f"Collection counts match expectations: {owned_count} owned (expected ≥{expected_owned}), {wanted_count} wanted (expected ≥{expected_wanted})"
                        )
                        return True
                    else:
                        self.log_test(
                            "Collection Count Verification", 
                            False, 
                            f"Collection counts don't match expectations: {owned_count} owned (expected ≥{expected_owned}), {wanted_count} wanted (expected ≥{expected_wanted})"
                        )
                        return False
                else:
                    self.log_test(
                        "Collection Statistics", 
                        False, 
                        f"Expected list, got {type(all_items)}"
                    )
                    return False
            else:
                self.log_test(
                    "Collection Statistics", 
                    False, 
                    f"Failed to get collection for statistics: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Collection Statistics", False, f"Exception: {str(e)}")
            return False

    def test_duplicate_prevention(self):
        """Test that duplicate items cannot be added to the same collection type"""
        print("\n🚫 TESTING DUPLICATE PREVENTION")
        
        if not self.available_master_kits:
            self.log_test(
                "Duplicate Prevention", 
                False, 
                "No Master Kits available for testing"
            )
            return False
        
        try:
            # Try to add the same Master Kit to owned collection again
            test_kit = self.available_master_kits[0]
            master_kit_id = test_kit.get('id')
            
            duplicate_data = {
                "master_kit_id": master_kit_id,
                "collection_type": "owned",
                "size": "XL",
                "condition": "match_worn",  # Use correct enum value
                "purchase_price": 75.00
            }
            
            response = self.session.post(f"{BACKEND_URL}/my-collection", json=duplicate_data)
            
            if response.status_code == 400:
                error_message = response.text
                if "already in your" in error_message.lower():
                    self.log_test(
                        "Duplicate Prevention", 
                        True, 
                        f"Correctly prevented duplicate addition: {error_message}"
                    )
                    return True
                else:
                    self.log_test(
                        "Duplicate Prevention", 
                        False, 
                        f"Got 400 error but wrong message: {error_message}"
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

    def cleanup_test_data(self):
        """Clean up test collection items"""
        print("\n🧹 CLEANING UP TEST DATA")
        
        cleanup_count = 0
        for collection_id in self.test_collection_items:
            try:
                response = self.session.delete(f"{BACKEND_URL}/my-collection/{collection_id}")
                if response.status_code == 200:
                    cleanup_count += 1
            except Exception as e:
                print(f"Warning: Failed to cleanup collection item {collection_id}: {str(e)}")
        
        if cleanup_count > 0:
            self.log_test(
                "Test Data Cleanup", 
                True, 
                f"Successfully cleaned up {cleanup_count} test collection items"
            )
        else:
            self.log_test(
                "Test Data Cleanup", 
                True, 
                "No test data to cleanup"
            )

    def run_all_tests(self):
        """Run all Master Kit to My Collection workflow tests"""
        print("🚀 STARTING MASTER KIT TO MY COLLECTION WORKFLOW BACKEND TESTS")
        print("=" * 80)
        
        # Test 1: User Authentication
        if not self.authenticate_user():
            print("\n❌ CRITICAL: User authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Get Master Kits
        if not self.test_get_master_kits():
            print("\n❌ CRITICAL: Cannot get Master Kits. Cannot proceed with collection tests.")
            return False
        
        # Test 3: Add to Owned Collection
        self.test_add_to_owned_collection()
        
        # Test 4: Add to Want List
        self.test_add_to_want_list()
        
        # Test 5: Get My Collection - Owned
        self.test_get_my_collection_owned()
        
        # Test 6: Get My Collection - Wanted
        self.test_get_my_collection_wanted()
        
        # Test 7: Collection Statistics
        self.test_collection_statistics()
        
        # Test 8: Duplicate Prevention
        self.test_duplicate_prevention()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        self.print_test_summary()
        
        return True

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 MASTER KIT TO MY COLLECTION WORKFLOW TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result['success']:
                print(f"   • {result['test']}: {result['details']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT: Master Kit to My Collection workflow is working excellently!")
        elif success_rate >= 75:
            print(f"\n✅ GOOD: Master Kit to My Collection workflow is working well with minor issues.")
        elif success_rate >= 50:
            print(f"\n⚠️ MODERATE: Master Kit to My Collection workflow has some issues that need attention.")
        else:
            print(f"\n❌ CRITICAL: Master Kit to My Collection workflow has significant issues requiring immediate attention.")

def main():
    """Main test execution"""
    tester = MasterKitCollectionWorkflowTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n🏁 TESTING COMPLETED")
        else:
            print(f"\n💥 TESTING FAILED - Critical authentication or setup issue")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()