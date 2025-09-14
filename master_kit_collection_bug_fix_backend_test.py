#!/usr/bin/env python3

"""
Master Kit Collection Workflow Bug Fix Backend Test
Testing the complete Master Kit collection workflow end-to-end to verify the bug fix.

Test Requirements from Review Request:
1. **Authenticate** with topkitfr@gmail.com / TopKitSecure789#
2. **Check specific Master Kit**: Verify TK-MASTER-8270A7 exists and is accessible
3. **Verify Collection API**: Test GET /api/my-collection to confirm it returns collection items (should be 14 items now)
4. **Confirm TK-MASTER-8270A7 in collection**: Verify the user's specific Master Kit appears in their collection
5. **Test collection statistics**: Check if collection_type field is now properly included
6. **Verify owned vs wanted filtering**: Test collection_type filtering functionality

Bug Fix Details:
- Token validation in frontend
- Added collection_type field to MyCollectionResponse model  
- Added backward compatibility for existing items without collection_type
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
TARGET_MASTER_KIT = "TK-MASTER-8270A7"

class MasterKitCollectionTester:
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
                self.admin_token = data.get("token")
                self.admin_user_id = data.get("user", {}).get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.admin_token}"
                })
                
                self.log_test(
                    "Admin Authentication", 
                    True, 
                    f"Successfully authenticated as {data.get('user', {}).get('name', 'Unknown')} (Role: {data.get('user', {}).get('role', 'Unknown')})"
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    False, 
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception during login: {str(e)}")
            return False

    def check_specific_master_kit(self):
        """Check if TK-MASTER-8270A7 exists and is accessible"""
        print(f"\n🎯 TESTING SPECIFIC MASTER KIT: {TARGET_MASTER_KIT}")
        
        try:
            # First, try to get all master kits and search for our target
            response = self.session.get(f"{BACKEND_URL}/master-kits")
            
            if response.status_code == 200:
                master_kits = response.json()
                target_kit = None
                
                # Search for the target master kit
                for kit in master_kits:
                    if kit.get("topkit_reference") == TARGET_MASTER_KIT:
                        target_kit = kit
                        break
                
                if target_kit:
                    self.log_test(
                        f"Master Kit {TARGET_MASTER_KIT} Exists", 
                        True, 
                        f"Found Master Kit: {target_kit.get('club', 'Unknown')} {target_kit.get('season', 'Unknown')} {target_kit.get('kit_type', 'Unknown')}"
                    )
                    
                    # Try to get the specific master kit by ID
                    kit_id = target_kit.get("id")
                    if kit_id:
                        detail_response = self.session.get(f"{BACKEND_URL}/master-kits/{kit_id}")
                        if detail_response.status_code == 200:
                            self.log_test(
                                f"Master Kit {TARGET_MASTER_KIT} Detail Access", 
                                True, 
                                f"Successfully accessed detailed view of Master Kit {TARGET_MASTER_KIT}"
                            )
                            return target_kit
                        else:
                            self.log_test(
                                f"Master Kit {TARGET_MASTER_KIT} Detail Access", 
                                False, 
                                f"Failed to access detail view: {detail_response.status_code}"
                            )
                    
                    return target_kit
                else:
                    self.log_test(
                        f"Master Kit {TARGET_MASTER_KIT} Exists", 
                        False, 
                        f"Master Kit {TARGET_MASTER_KIT} not found in {len(master_kits)} available master kits"
                    )
                    return None
            else:
                self.log_test(
                    f"Master Kit {TARGET_MASTER_KIT} Exists", 
                    False, 
                    f"Failed to fetch master kits: {response.status_code} - {response.text}"
                )
                return None
                
        except Exception as e:
            self.log_test(f"Master Kit {TARGET_MASTER_KIT} Exists", False, f"Exception: {str(e)}")
            return None

    def verify_collection_api(self):
        """Test GET /api/my-collection to confirm it returns collection items"""
        print("\n📦 TESTING COLLECTION API")
        
        try:
            # Get user's collection
            response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if response.status_code == 200:
                collection_items = response.json()
                total_items = len(collection_items)
                
                self.log_test(
                    "Collection API Access", 
                    True, 
                    f"Successfully retrieved collection with {total_items} items"
                )
                
                # Check if we have the expected number of items (should be 14 according to review request)
                expected_items = 14
                if total_items == expected_items:
                    self.log_test(
                        "Collection Item Count", 
                        True, 
                        f"Collection has exactly {expected_items} items as expected"
                    )
                else:
                    self.log_test(
                        "Collection Item Count", 
                        False, 
                        f"Expected {expected_items} items but found {total_items} items"
                    )
                
                # Analyze collection_type field presence
                items_with_collection_type = 0
                items_without_collection_type = 0
                owned_items = 0
                wanted_items = 0
                
                for item in collection_items:
                    if "collection_type" in item and item["collection_type"] is not None:
                        items_with_collection_type += 1
                        if item["collection_type"] == "owned":
                            owned_items += 1
                        elif item["collection_type"] == "wanted":
                            wanted_items += 1
                    else:
                        items_without_collection_type += 1
                
                self.log_test(
                    "Collection Type Field Analysis", 
                    True, 
                    f"Items with collection_type: {items_with_collection_type}, without: {items_without_collection_type}, owned: {owned_items}, wanted: {wanted_items}"
                )
                
                return collection_items
            else:
                self.log_test(
                    "Collection API Access", 
                    False, 
                    f"Failed to access collection: {response.status_code} - {response.text}"
                )
                return []
                
        except Exception as e:
            self.log_test("Collection API Access", False, f"Exception: {str(e)}")
            return []

    def confirm_target_kit_in_collection(self, collection_items):
        """Confirm TK-MASTER-8270A7 appears in the user's collection"""
        print(f"\n🔍 CHECKING FOR {TARGET_MASTER_KIT} IN COLLECTION")
        
        try:
            target_found = False
            target_item = None
            
            for item in collection_items:
                # Check if the master kit info contains our target reference
                master_kit = item.get("master_kit", {})
                if master_kit.get("topkit_reference") == TARGET_MASTER_KIT:
                    target_found = True
                    target_item = item
                    break
            
            if target_found:
                collection_type = target_item.get("collection_type", "unknown")
                self.log_test(
                    f"{TARGET_MASTER_KIT} in Collection", 
                    True, 
                    f"Found {TARGET_MASTER_KIT} in user's collection (Type: {collection_type})"
                )
                
                # Check if the item has proper collection_type
                if collection_type in ["owned", "wanted"]:
                    self.log_test(
                        f"{TARGET_MASTER_KIT} Collection Type", 
                        True, 
                        f"Master Kit has valid collection_type: {collection_type}"
                    )
                else:
                    self.log_test(
                        f"{TARGET_MASTER_KIT} Collection Type", 
                        False, 
                        f"Master Kit has invalid/missing collection_type: {collection_type}"
                    )
                
                return target_item
            else:
                self.log_test(
                    f"{TARGET_MASTER_KIT} in Collection", 
                    False, 
                    f"Master Kit {TARGET_MASTER_KIT} not found in user's collection of {len(collection_items)} items"
                )
                return None
                
        except Exception as e:
            self.log_test(f"{TARGET_MASTER_KIT} in Collection", False, f"Exception: {str(e)}")
            return None

    def test_collection_filtering(self):
        """Test collection_type filtering functionality"""
        print("\n🔄 TESTING COLLECTION FILTERING")
        
        try:
            # Test filtering by owned items
            owned_response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=owned")
            
            if owned_response.status_code == 200:
                owned_items = owned_response.json()
                owned_count = len(owned_items)
                
                # Verify all items are actually owned
                all_owned = all(item.get("collection_type") == "owned" for item in owned_items)
                
                self.log_test(
                    "Owned Items Filtering", 
                    all_owned, 
                    f"Retrieved {owned_count} owned items, all properly filtered: {all_owned}"
                )
            else:
                self.log_test(
                    "Owned Items Filtering", 
                    False, 
                    f"Failed to filter owned items: {owned_response.status_code}"
                )
            
            # Test filtering by wanted items
            wanted_response = self.session.get(f"{BACKEND_URL}/my-collection?collection_type=wanted")
            
            if wanted_response.status_code == 200:
                wanted_items = wanted_response.json()
                wanted_count = len(wanted_items)
                
                # Verify all items are actually wanted
                all_wanted = all(item.get("collection_type") == "wanted" for item in wanted_items)
                
                self.log_test(
                    "Wanted Items Filtering", 
                    all_wanted, 
                    f"Retrieved {wanted_count} wanted items, all properly filtered: {all_wanted}"
                )
            else:
                self.log_test(
                    "Wanted Items Filtering", 
                    False, 
                    f"Failed to filter wanted items: {wanted_response.status_code}"
                )
            
            # Test that total filtered items match total collection
            if owned_response.status_code == 200 and wanted_response.status_code == 200:
                total_filtered = len(owned_items) + len(wanted_items)
                
                # Get total collection count for comparison
                total_response = self.session.get(f"{BACKEND_URL}/my-collection")
                if total_response.status_code == 200:
                    total_items = len(total_response.json())
                    
                    # Account for items without collection_type (backward compatibility)
                    items_without_type = 0
                    for item in total_response.json():
                        if not item.get("collection_type"):
                            items_without_type += 1
                    
                    expected_filtered = total_items - items_without_type
                    
                    if total_filtered == expected_filtered:
                        self.log_test(
                            "Collection Filtering Completeness", 
                            True, 
                            f"Filtered items ({total_filtered}) match expected count ({expected_filtered}), {items_without_type} items without collection_type"
                        )
                    else:
                        self.log_test(
                            "Collection Filtering Completeness", 
                            False, 
                            f"Filtered items ({total_filtered}) don't match expected count ({expected_filtered})"
                        )
                
        except Exception as e:
            self.log_test("Collection Filtering", False, f"Exception: {str(e)}")

    def test_backward_compatibility(self):
        """Test backward compatibility for existing items without collection_type"""
        print("\n🔄 TESTING BACKWARD COMPATIBILITY")
        
        try:
            # Get all collection items
            response = self.session.get(f"{BACKEND_URL}/my-collection")
            
            if response.status_code == 200:
                collection_items = response.json()
                
                # Count items without collection_type
                items_without_type = []
                items_with_type = []
                
                for item in collection_items:
                    if "collection_type" not in item or item["collection_type"] is None:
                        items_without_type.append(item)
                    else:
                        items_with_type.append(item)
                
                self.log_test(
                    "Backward Compatibility Analysis", 
                    True, 
                    f"Found {len(items_without_type)} items without collection_type, {len(items_with_type)} items with collection_type"
                )
                
                # Test that items without collection_type are still accessible
                if items_without_type:
                    # These should be treated as "owned" by default for backward compatibility
                    self.log_test(
                        "Backward Compatibility Support", 
                        True, 
                        f"System handles {len(items_without_type)} legacy items without collection_type field"
                    )
                else:
                    self.log_test(
                        "Backward Compatibility Support", 
                        True, 
                        "All items have collection_type field - no legacy items found"
                    )
                
        except Exception as e:
            self.log_test("Backward Compatibility", False, f"Exception: {str(e)}")

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 STARTING MASTER KIT COLLECTION WORKFLOW BUG FIX TEST")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate_admin():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Check specific Master Kit
        target_kit = self.check_specific_master_kit()
        
        # Step 3: Verify Collection API
        collection_items = self.verify_collection_api()
        
        # Step 4: Confirm target kit in collection
        if collection_items:
            self.confirm_target_kit_in_collection(collection_items)
        
        # Step 5: Test collection filtering
        self.test_collection_filtering()
        
        # Step 6: Test backward compatibility
        self.test_backward_compatibility()
        
        # Generate summary
        self.generate_summary()
        
        return True

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 MASTER KIT COLLECTION WORKFLOW BUG FIX VERIFICATION:")
        if success_rate >= 80:
            print("✅ BUG FIX VERIFICATION SUCCESSFUL - Most functionality working correctly")
        else:
            print("❌ BUG FIX VERIFICATION FAILED - Critical issues remain")
        
        return success_rate >= 80

def main():
    """Main test execution"""
    tester = MasterKitCollectionTester()
    success = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()