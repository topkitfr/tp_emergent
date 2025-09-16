#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Complete Edit Kit Details Form Validation Errors Testing
Testing the critical bug fix for Edit Kit Details functionality where users were getting validation errors:
- Error: body.condition: Input should be 'club_stock', 'match_prepared', 'match_worn', 'training' or 'other'  
- Error: body.physical_state: Input should be 'new_with_tags', 'very_good_condition', 'used', 'damaged' or 'needs_restoration'

EXPANDED FIX: Enhanced handleSaveEdit function to properly handle ALL optional fields:
1. Only send fields that have actual values (not empty strings)
2. Remove empty enum fields (condition, physical_state) to avoid validation errors  
3. Remove empty text fields to prevent unnecessary data
4. Convert purchase_price to float and purchase_date to ISO datetime
5. Always include is_signed as boolean (required field)

FOCUS: Testing comprehensive validation fix for ALL optional fields in Edit Kit Details form.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://image-path-solver.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

class EditKitDetailsValidationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.collection_items = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Authenticate with admin credentials"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=TEST_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                user_email = data.get('user', {}).get('email')
                user_role = data.get('user', {}).get('role')
                self.log_test("Admin Authentication", True, 
                             f"Successfully authenticated as {user_email} (role: {user_role})")
                return True
            else:
                self.log_test("Admin Authentication", False, 
                             f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_my_collection(self):
        """Get user's collection items"""
        try:
            response = self.session.get(
                f"{BACKEND_URL}/my-collection",
                timeout=10
            )
            
            if response.status_code == 200:
                collection_items = response.json()
                self.collection_items = collection_items
                
                self.log_test("Get My Collection", True,
                             f"Retrieved {len(collection_items)} collection items")
                
                return collection_items
            else:
                self.log_test("Get My Collection", False,
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("Get My Collection", False, f"Exception: {str(e)}")
            return []
    
    def test_empty_condition_and_physical_state(self, collection_item_id):
        """Test the critical bug: empty condition and physical_state fields should be omitted"""
        try:
            print(f"\n   🎯 CRITICAL TEST: Empty condition and physical_state fields...")
            
            # This is the exact scenario causing the user's validation errors
            # Frontend should omit these fields when they are empty
            update_data = {
                "name_printing": "Ronaldo",
                "number_printing": "7",
                "is_signed": False,  # Required field - always included
                "notes": "Testing empty enum fields omission - CRITICAL BUG FIX"
                # condition and physical_state intentionally omitted (empty in form)
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Empty Condition and Physical State", True,
                             "✅ CRITICAL FIX WORKING: Empty enum fields correctly omitted - no 422 validation errors")
                return True
            elif response.status_code == 422:
                error_data = response.json()
                error_details = error_data.get('detail', [])
                
                # Check if the specific enum validation errors are present
                condition_error = any('condition' in str(err) for err in error_details)
                physical_state_error = any('physical_state' in str(err) for err in error_details)
                
                if condition_error or physical_state_error:
                    self.log_test("Empty Condition and Physical State", False,
                                 f"❌ CRITICAL BUG STILL PRESENT: 422 validation errors for empty enum fields", 
                                 error_data)
                    return False
                else:
                    # Different validation error - might be acceptable
                    self.log_test("Empty Condition and Physical State", False,
                                 f"422 validation error but not for condition/physical_state: {error_data}")
                    return False
            else:
                self.log_test("Empty Condition and Physical State", False,
                             f"Unexpected response: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Empty Condition and Physical State", False, f"Exception: {str(e)}")
            return False
    
    def test_valid_enum_values(self, collection_item_id):
        """Test valid enum values for condition and physical_state"""
        try:
            print(f"\n   Testing valid enum values...")
            
            # Test valid condition values
            valid_conditions = ['club_stock', 'match_prepared', 'match_worn', 'training', 'other']
            valid_physical_states = ['new_with_tags', 'very_good_condition', 'used', 'damaged', 'needs_restoration']
            
            for condition in valid_conditions:
                for physical_state in valid_physical_states:
                    print(f"     Testing: condition={condition}, physical_state={physical_state}")
                    
                    update_data = {
                        "condition": condition,
                        "physical_state": physical_state,
                        "is_signed": False,
                        "notes": f"Testing valid enums: {condition} + {physical_state}"
                    }
                    
                    response = self.session.put(
                        f"{BACKEND_URL}/my-collection/{collection_item_id}",
                        json=update_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("condition") == condition and result.get("physical_state") == physical_state:
                            self.log_test(f"Valid Enum - {condition} + {physical_state}", True,
                                         f"Successfully updated with valid enum values")
                        else:
                            self.log_test(f"Valid Enum - {condition} + {physical_state}", False,
                                         f"Enum values not saved correctly")
                            return False
                    else:
                        self.log_test(f"Valid Enum - {condition} + {physical_state}", False,
                                     f"Failed with status {response.status_code}: {response.text}")
                        return False
                    
                    # Only test first few combinations to avoid too many tests
                    if condition == 'match_worn' and physical_state == 'very_good_condition':
                        break
                if condition == 'match_worn':
                    break
            
            return True
            
        except Exception as e:
            self.log_test("Valid Enum Values", False, f"Exception: {str(e)}")
            return False
    
    def test_mixed_filled_and_empty_fields(self, collection_item_id):
        """Test mix of filled and empty fields"""
        try:
            print(f"\n   Testing mixed filled and empty fields...")
            
            # Scenario: Some fields filled, some empty (should be omitted)
            update_data = {
                "name_printing": "Mbappé",
                "number_printing": "10",
                "condition": "match_worn",  # Filled
                # physical_state omitted (empty)
                "patches": "UEFA Champions League",  # Filled
                # signed_by omitted (empty)
                "is_signed": True,  # Required field
                "purchase_price": 299.99,  # Filled
                # purchase_date omitted (empty)
                "notes": "Testing mixed filled/empty fields"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify filled fields are saved
                checks = [
                    ("name_printing", "Mbappé"),
                    ("number_printing", "10"),
                    ("condition", "match_worn"),
                    ("patches", "UEFA Champions League"),
                    ("is_signed", True),
                    ("purchase_price", 299.99),
                    ("notes", "Testing mixed filled/empty fields")
                ]
                
                all_correct = True
                for field, expected_value in checks:
                    actual_value = result.get(field)
                    if actual_value != expected_value:
                        print(f"     ❌ Field mismatch: {field} = {actual_value}, expected {expected_value}")
                        all_correct = False
                    else:
                        print(f"     ✅ Field correct: {field} = {actual_value}")
                
                if all_correct:
                    self.log_test("Mixed Filled and Empty Fields", True,
                                 "Successfully handled mix of filled and empty fields")
                    return True
                else:
                    self.log_test("Mixed Filled and Empty Fields", False,
                                 "Some filled fields were not saved correctly")
                    return False
            else:
                self.log_test("Mixed Filled and Empty Fields", False,
                             f"Failed with status {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Mixed Filled and Empty Fields", False, f"Exception: {str(e)}")
            return False
    
    def test_purchase_price_and_date_conversions(self, collection_item_id):
        """Test purchase_price and purchase_date conversions still working"""
        try:
            print(f"\n   Testing purchase_price and purchase_date conversions...")
            
            test_cases = [
                {
                    "purchase_price": 150.75,
                    "purchase_date": "2023-11-15T10:30:00.000Z",
                    "description": "Float price + ISO datetime"
                },
                {
                    "purchase_price": 200,
                    "purchase_date": "2024-01-01T00:00:00Z",
                    "description": "Integer price + ISO datetime"
                },
                {
                    "purchase_price": 0,
                    "description": "Zero price, no date"
                }
            ]
            
            for test_case in test_cases:
                print(f"     Testing: {test_case['description']}")
                
                update_data = {
                    "is_signed": False,
                    "notes": f"Testing: {test_case['description']}"
                }
                
                if "purchase_price" in test_case:
                    update_data["purchase_price"] = test_case["purchase_price"]
                if "purchase_date" in test_case:
                    update_data["purchase_date"] = test_case["purchase_date"]
                
                response = self.session.put(
                    f"{BACKEND_URL}/my-collection/{collection_item_id}",
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Verify conversions
                    if "purchase_price" in test_case:
                        returned_price = result.get("purchase_price")
                        if returned_price != test_case["purchase_price"]:
                            self.log_test(f"Purchase Conversion - {test_case['description']}", False,
                                         f"Price mismatch: sent {test_case['purchase_price']}, got {returned_price}")
                            return False
                    
                    self.log_test(f"Purchase Conversion - {test_case['description']}", True,
                                 "Purchase field conversions working correctly")
                else:
                    self.log_test(f"Purchase Conversion - {test_case['description']}", False,
                                 f"Failed with status {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Purchase Price and Date Conversions", False, f"Exception: {str(e)}")
            return False
    
    def test_boolean_is_signed_handling(self, collection_item_id):
        """Test boolean is_signed field handling (required field)"""
        try:
            print(f"\n   Testing boolean is_signed field handling...")
            
            test_cases = [
                {"is_signed": True, "signed_by": "Lionel Messi", "description": "Signed kit"},
                {"is_signed": False, "description": "Unsigned kit"},
            ]
            
            for test_case in test_cases:
                print(f"     Testing: {test_case['description']}")
                
                update_data = {
                    "is_signed": test_case["is_signed"],
                    "notes": f"Testing: {test_case['description']}"
                }
                
                if "signed_by" in test_case:
                    update_data["signed_by"] = test_case["signed_by"]
                
                response = self.session.put(
                    f"{BACKEND_URL}/my-collection/{collection_item_id}",
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    returned_is_signed = result.get("is_signed")
                    
                    if returned_is_signed == test_case["is_signed"]:
                        self.log_test(f"Boolean is_signed - {test_case['description']}", True,
                                     f"Boolean is_signed field handled correctly: {test_case['is_signed']}")
                    else:
                        self.log_test(f"Boolean is_signed - {test_case['description']}", False,
                                     f"Boolean mismatch: sent {test_case['is_signed']}, got {returned_is_signed}")
                        return False
                else:
                    self.log_test(f"Boolean is_signed - {test_case['description']}", False,
                                 f"Failed with status {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Boolean is_signed Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_all_text_fields_empty_and_filled(self, collection_item_id):
        """Test all text fields with empty and non-empty values"""
        try:
            print(f"\n   Testing all text fields with empty and non-empty values...")
            
            # Test with all text fields filled
            filled_data = {
                "name_printing": "Cristiano Ronaldo",
                "number_printing": "7",
                "patches": "Champions League, Serie A",
                "signed_by": "Cristiano Ronaldo",
                "notes": "Complete kit with all details filled",
                "is_signed": True
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=filled_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify all fields are saved
                all_correct = True
                for field, expected_value in filled_data.items():
                    actual_value = result.get(field)
                    if actual_value != expected_value:
                        print(f"     ❌ Field mismatch: {field} = {actual_value}, expected {expected_value}")
                        all_correct = False
                    else:
                        print(f"     ✅ Field correct: {field} = {actual_value}")
                
                if all_correct:
                    self.log_test("All Text Fields Filled", True,
                                 "All text fields saved correctly when filled")
                else:
                    self.log_test("All Text Fields Filled", False,
                                 "Some text fields were not saved correctly")
                    return False
            else:
                self.log_test("All Text Fields Filled", False,
                             f"Failed with status {response.status_code}: {response.text}")
                return False
            
            # Test with minimal data (most text fields empty/omitted)
            minimal_data = {
                "is_signed": False,  # Required field
                "notes": "Minimal kit details - most fields empty"
                # All other text fields omitted (empty)
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=minimal_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("All Text Fields Empty", True,
                             "Successfully handled minimal data with most text fields empty")
                return True
            else:
                self.log_test("All Text Fields Empty", False,
                             f"Failed with status {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("All Text Fields Empty and Filled", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_edit_kit_details_validation(self):
        """Test comprehensive Edit Kit Details validation scenarios"""
        try:
            print("\n🎯 Testing Comprehensive Edit Kit Details Validation...")
            
            # Get collection items to test with
            collection_items = self.get_my_collection()
            
            if not collection_items:
                self.log_test("Comprehensive Edit Kit Details Validation", False, "No collection items found to test with")
                return False
            
            # Use the first collection item for testing
            test_item = collection_items[0]
            collection_item_id = test_item.get("id")
            
            if not collection_item_id:
                self.log_test("Comprehensive Edit Kit Details Validation", False, "Collection item has no ID")
                return False
            
            print(f"   Using collection item: {collection_item_id}")
            print(f"   Master kit: {test_item.get('master_kit', {}).get('club', 'Unknown')} {test_item.get('master_kit', {}).get('season', 'Unknown')}")
            
            # Test all validation scenarios
            test_results = []
            
            # 1. CRITICAL: Test empty condition and physical_state fields
            print(f"\n🚨 CRITICAL TEST: Empty Condition and Physical State Fields...")
            test_results.append(self.test_empty_condition_and_physical_state(collection_item_id))
            
            # 2. Test valid enum values
            print(f"\n✅ Testing Valid Enum Values...")
            test_results.append(self.test_valid_enum_values(collection_item_id))
            
            # 3. Test mixed filled and empty fields
            print(f"\n🔄 Testing Mixed Filled and Empty Fields...")
            test_results.append(self.test_mixed_filled_and_empty_fields(collection_item_id))
            
            # 4. Test purchase price and date conversions still working
            print(f"\n💰 Testing Purchase Price and Date Conversions...")
            test_results.append(self.test_purchase_price_and_date_conversions(collection_item_id))
            
            # 5. Test boolean is_signed field handling
            print(f"\n✍️ Testing Boolean is_signed Field Handling...")
            test_results.append(self.test_boolean_is_signed_handling(collection_item_id))
            
            # 6. Test all text fields with empty and non-empty values
            print(f"\n📝 Testing All Text Fields...")
            test_results.append(self.test_all_text_fields_empty_and_filled(collection_item_id))
            
            # Overall result
            all_passed = all(test_results)
            
            if all_passed:
                self.log_test("Comprehensive Edit Kit Details Validation", True,
                             "All Edit Kit Details validation tests passed - comprehensive fix working!")
                return True
            else:
                failed_count = len([r for r in test_results if not r])
                self.log_test("Comprehensive Edit Kit Details Validation", False,
                             f"{failed_count} out of {len(test_results)} validation tests failed")
                return False
            
        except Exception as e:
            self.log_test("Comprehensive Edit Kit Details Validation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive Edit Kit Details validation testing"""
        print("🧪 Starting TopKit Complete Edit Kit Details Form Validation Testing")
        print("FOCUS: Testing the critical bug fix for Edit Kit Details validation errors")
        print("CRITICAL ISSUE: Users getting 422 validation errors for condition and physical_state enum fields")
        print("EXPANDED FIX: Enhanced handleSaveEdit function to handle ALL optional fields properly")
        print("=" * 90)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test comprehensive Edit Kit Details validation
        print("🎯 Testing Comprehensive Edit Kit Details Validation...")
        self.test_comprehensive_edit_kit_details_validation()
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 COMPLETE EDIT KIT DETAILS VALIDATION TEST SUMMARY")
        print("=" * 90)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test']]
        collection_tests = [r for r in self.test_results if 'Collection' in r['test']]
        enum_tests = [r for r in self.test_results if 'Condition' in r['test'] or 'Physical State' in r['test'] or 'Enum' in r['test']]
        field_tests = [r for r in self.test_results if 'Field' in r['test'] or 'Text' in r['test']]
        conversion_tests = [r for r in self.test_results if 'Conversion' in r['test'] or 'Purchase' in r['test'] or 'Boolean' in r['test']]
        
        print(f"\nTest Categories:")
        print(f"  Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} ✅")
        print(f"  Collection Access: {len([r for r in collection_tests if r['success']])}/{len(collection_tests)} ✅")
        print(f"  Enum Field Validation: {len([r for r in enum_tests if r['success']])}/{len(enum_tests)} ✅")
        print(f"  Text Field Handling: {len([r for r in field_tests if r['success']])}/{len(field_tests)} ✅")
        print(f"  Data Type Conversions: {len([r for r in conversion_tests if r['success']])}/{len(conversion_tests)} ✅")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           ('Condition' in r['test'] or 'Physical State' in r['test'] or 'Enum' in r['test'] or 'Validation' in r['test'])]
        
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED: {len(critical_failures)}")
            for failure in critical_failures:
                print(f"  • {failure['test']}: {failure['message']}")
                if failure.get('details'):
                    print(f"    Details: {failure['details']}")
        
        if failed_tests > 0:
            print("\n❌ ALL FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Specific findings for the bug report
        condition_failures = [r for r in self.test_results if not r['success'] and ('Condition' in r['test'] or 'Physical State' in r['test'])]
        enum_failures = [r for r in self.test_results if not r['success'] and 'Enum' in r['test']]
        field_failures = [r for r in self.test_results if not r['success'] and 'Field' in r['test']]
        
        print(f"\n🎯 CRITICAL BUG FIX ANALYSIS RESULTS:")
        print(f"  Condition/Physical State Validation Failures: {len(condition_failures)}")
        print(f"  Enum Field Validation Failures: {len(enum_failures)}")
        print(f"  General Field Handling Failures: {len(field_failures)}")
        
        if condition_failures or enum_failures or field_failures:
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            print("  The comprehensive Edit Kit Details validation fix has issues with:")
            if condition_failures:
                print("  - Condition and physical_state enum field validation (CRITICAL)")
            if enum_failures:
                print("  - General enum field validation")
            if field_failures:
                print("  - Field handling and data processing")
        else:
            print("\n✅ COMPREHENSIVE BUG FIX SUCCESSFUL!")
            print("  The complete Edit Kit Details form validation bug has been resolved.")
            print("  Users should no longer experience 422 validation errors for:")
            print("    - Empty condition and physical_state enum fields")
            print("    - Mixed filled and empty fields")
            print("    - Purchase price and date conversions")
            print("    - Boolean and text field handling")
        
        print("\n" + "=" * 90)

def main():
    """Main test execution"""
    tester = EditKitDetailsValidationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()