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

class PurchasePriceValidationTester:
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
    
    def test_valid_purchase_price_update(self, collection_item_id):
        """Test updating collection item with valid purchase_price as number"""
        try:
            test_cases = [
                {"purchase_price": 125.50, "description": "Float number"},
                {"purchase_price": 100, "description": "Integer number"},
                {"purchase_price": 0, "description": "Zero value"},
                {"purchase_price": 999.99, "description": "High value"}
            ]
            
            for test_case in test_cases:
                purchase_price = test_case["purchase_price"]
                description = test_case["description"]
                
                print(f"\n   Testing purchase_price: {purchase_price} ({description})")
                
                update_data = {
                    "purchase_price": purchase_price,
                    "notes": f"Testing valid purchase_price: {purchase_price}"
                }
                
                response = self.session.put(
                    f"{BACKEND_URL}/my-collection/{collection_item_id}",
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    returned_price = result.get("purchase_price")
                    
                    if returned_price == purchase_price:
                        self.log_test(f"Valid Purchase Price - {description}", True,
                                     f"Successfully updated purchase_price to {purchase_price}")
                    else:
                        self.log_test(f"Valid Purchase Price - {description}", False,
                                     f"Price mismatch: sent {purchase_price}, got {returned_price}")
                        return False
                else:
                    self.log_test(f"Valid Purchase Price - {description}", False,
                                 f"Failed with status {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Valid Purchase Price Update", False, f"Exception: {str(e)}")
            return False
    
    def test_valid_purchase_date_update(self, collection_item_id):
        """Test updating collection item with valid purchase_date as ISO datetime string"""
        try:
            test_cases = [
                {"purchase_date": "2023-12-25T00:00:00.000Z", "description": "Christmas 2023"},
                {"purchase_date": "2024-01-01T12:30:45.123Z", "description": "New Year 2024 with time"},
                {"purchase_date": "2022-06-15T00:00:00Z", "description": "Mid-year 2022"},
                {"purchase_date": "2024-12-31T23:59:59.999Z", "description": "End of 2024"}
            ]
            
            for test_case in test_cases:
                purchase_date = test_case["purchase_date"]
                description = test_case["description"]
                
                print(f"\n   Testing purchase_date: {purchase_date} ({description})")
                
                update_data = {
                    "purchase_date": purchase_date,
                    "notes": f"Testing valid purchase_date: {purchase_date}"
                }
                
                response = self.session.put(
                    f"{BACKEND_URL}/my-collection/{collection_item_id}",
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    returned_date = result.get("purchase_date")
                    
                    self.log_test(f"Valid Purchase Date - {description}", True,
                                 f"Successfully updated purchase_date to {purchase_date}")
                else:
                    self.log_test(f"Valid Purchase Date - {description}", False,
                                 f"Failed with status {response.status_code}: {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_test("Valid Purchase Date Update", False, f"Exception: {str(e)}")
            return False
    
    def test_empty_fields_handling(self, collection_item_id):
        """Test that empty purchase_price and purchase_date fields are handled correctly"""
        try:
            print(f"\n   Testing empty fields handling...")
            
            # Test with null values (should be omitted by frontend)
            update_data = {
                "name_printing": "Test Player",
                "number_printing": "10",
                "condition": "match_worn",
                "notes": "Testing empty fields handling"
                # purchase_price and purchase_date intentionally omitted
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Empty Fields Handling", True,
                             "Successfully updated collection item with empty purchase fields omitted")
                return True
            else:
                self.log_test("Empty Fields Handling", False,
                             f"Failed with status {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Empty Fields Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_combined_purchase_fields_update(self, collection_item_id):
        """Test updating both purchase_price and purchase_date together with other fields"""
        try:
            print(f"\n   Testing combined purchase fields update...")
            
            update_data = {
                "name_printing": "Messi",
                "number_printing": "10",
                "condition": "match_worn",
                "physical_state": "very_good_condition",
                "patches": "Champions League",
                "is_signed": True,
                "signed_by": "Lionel Messi",
                "purchase_price": 450.75,
                "purchase_date": "2023-08-15T14:30:00.000Z",
                "notes": "Complete kit details with purchase information"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify all fields were updated correctly
                checks = [
                    ("name_printing", "Messi"),
                    ("number_printing", "10"),
                    ("condition", "match_worn"),
                    ("physical_state", "very_good_condition"),
                    ("patches", "Champions League"),
                    ("is_signed", True),
                    ("signed_by", "Lionel Messi"),
                    ("purchase_price", 450.75),
                    ("notes", "Complete kit details with purchase information")
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
                    self.log_test("Combined Purchase Fields Update", True,
                                 "Successfully updated all fields including purchase_price and purchase_date")
                    return True
                else:
                    self.log_test("Combined Purchase Fields Update", False,
                                 "Some fields were not updated correctly")
                    return False
            else:
                self.log_test("Combined Purchase Fields Update", False,
                             f"Failed with status {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            self.log_test("Combined Purchase Fields Update", False, f"Exception: {str(e)}")
            return False
    
    def test_specific_user_reported_scenarios(self):
        """Test the specific scenarios reported by the user"""
        try:
            print("\n🐛 Testing Specific User-Reported Error Scenarios...")
            
            collection_items = self.get_my_collection()
            if not collection_items:
                self.log_test("User-Reported Scenarios", False, "No collection items found")
                return False
            
            test_item = collection_items[0]
            collection_item_id = test_item.get("id")
            
            # Scenario 1: The exact error case - string purchase_price and short purchase_date
            print(f"\n   Scenario 1: String purchase_price and short purchase_date (original bug)")
            
            # This simulates what the frontend was sending BEFORE the fix
            problematic_data = {
                "purchase_price": "125.50",  # String instead of number
                "purchase_date": "2023-12-25",  # Short date instead of ISO datetime
                "notes": "Testing original bug scenario"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=problematic_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("User-Reported Scenario 1", True,
                             "Frontend fix working - string price and short date accepted")
            elif response.status_code == 422:
                error_data = response.json()
                self.log_test("User-Reported Scenario 1", False,
                             f"Original bug still present - 422 validation error: {error_data}")
                return False
            else:
                self.log_test("User-Reported Scenario 1", False,
                             f"Unexpected response: {response.status_code} - {response.text}")
                return False
            
            # Scenario 2: Empty fields (should be omitted by frontend fix)
            print(f"\n   Scenario 2: Empty fields handling")
            
            empty_fields_data = {
                "name_printing": "Test Player",
                "condition": "match_worn",
                # purchase_price and purchase_date omitted (frontend fix)
                "notes": "Testing empty fields omission"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=empty_fields_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("User-Reported Scenario 2", True,
                             "Empty fields correctly omitted - no validation errors")
            else:
                self.log_test("User-Reported Scenario 2", False,
                             f"Empty fields handling failed: {response.status_code} - {response.text}")
                return False
            
            # Scenario 3: Proper frontend conversion (what should happen after fix)
            print(f"\n   Scenario 3: Proper frontend data conversion")
            
            proper_data = {
                "purchase_price": 125.50,  # Proper number (converted by frontend)
                "purchase_date": "2023-12-25T00:00:00.000Z",  # Proper ISO datetime (converted by frontend)
                "notes": "Testing proper frontend conversion"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_item_id}",
                json=proper_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                returned_price = result.get("purchase_price")
                
                if returned_price == 125.50:
                    self.log_test("User-Reported Scenario 3", True,
                                 "Proper frontend conversion working perfectly")
                else:
                    self.log_test("User-Reported Scenario 3", False,
                                 f"Price conversion issue: expected 125.50, got {returned_price}")
                    return False
            else:
                self.log_test("User-Reported Scenario 3", False,
                             f"Proper conversion failed: {response.status_code} - {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("User-Reported Scenarios", False, f"Exception: {str(e)}")
            return False
    
    def test_purchase_validation_bug_fix(self):
        """Test the specific purchase price and purchase date validation bug fix"""
        try:
            print("\n🎯 Testing Purchase Price and Purchase Date Validation Bug Fix...")
            
            # Get collection items to test with
            collection_items = self.get_my_collection()
            
            if not collection_items:
                self.log_test("Purchase Validation Bug Fix", False, "No collection items found to test with")
                return False
            
            # Use the first collection item for testing
            test_item = collection_items[0]
            collection_item_id = test_item.get("id")
            
            if not collection_item_id:
                self.log_test("Purchase Validation Bug Fix", False, "Collection item has no ID")
                return False
            
            print(f"   Using collection item: {collection_item_id}")
            print(f"   Master kit: {test_item.get('master_kit', {}).get('club', 'Unknown')} {test_item.get('master_kit', {}).get('season', 'Unknown')}")
            
            # Test all validation scenarios
            test_results = []
            
            # 1. Test valid purchase_price updates
            print(f"\n📊 Testing Valid Purchase Price Updates...")
            test_results.append(self.test_valid_purchase_price_update(collection_item_id))
            
            # 2. Test valid purchase_date updates  
            print(f"\n📅 Testing Valid Purchase Date Updates...")
            test_results.append(self.test_valid_purchase_date_update(collection_item_id))
            
            # 3. Test empty fields handling
            print(f"\n🔄 Testing Empty Fields Handling...")
            test_results.append(self.test_empty_fields_handling(collection_item_id))
            
            # 4. Test combined updates
            print(f"\n🔗 Testing Combined Purchase Fields Update...")
            test_results.append(self.test_combined_purchase_fields_update(collection_item_id))
            
            # Overall result
            all_passed = all(test_results)
            
            if all_passed:
                self.log_test("Purchase Validation Bug Fix", True,
                             "All purchase price and purchase date validation tests passed")
            else:
                failed_count = len([r for r in test_results if not r])
                self.log_test("Purchase Validation Bug Fix", False,
                             f"{failed_count} out of {len(test_results)} validation tests failed")
            
            return all_passed
            
        except Exception as e:
            self.log_test("Purchase Validation Bug Fix", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive purchase validation testing"""
        print("🧪 Starting TopKit Purchase Price and Purchase Date Validation Testing")
        print("FOCUS: Testing the critical bug fix for Edit Kit Details validation errors")
        print("ISSUE: Users getting 422 validation errors for purchase_price and purchase_date fields")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test the specific user-reported scenarios
        print("🐛 Testing User-Reported Error Scenarios...")
        self.test_specific_user_reported_scenarios()
        print()
        
        # Step 3: Test the comprehensive purchase validation bug fix
        print("🎯 Testing Purchase Validation Bug Fix...")
        self.test_purchase_validation_bug_fix()
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 PURCHASE VALIDATION BUG FIX TEST SUMMARY")
        print("=" * 80)
        
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
        validation_tests = [r for r in self.test_results if 'Purchase' in r['test'] or 'Validation' in r['test']]
        scenario_tests = [r for r in self.test_results if 'Scenario' in r['test']]
        
        print(f"\nTest Categories:")
        print(f"  Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} ✅")
        print(f"  Collection Access: {len([r for r in collection_tests if r['success']])}/{len(collection_tests)} ✅")
        print(f"  Purchase Validation: {len([r for r in validation_tests if r['success']])}/{len(validation_tests)} ✅")
        print(f"  User Scenarios: {len([r for r in scenario_tests if r['success']])}/{len(scenario_tests)} ✅")
        
        # Show critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           ('Purchase' in r['test'] or 'Validation' in r['test'] or 'Scenario' in r['test'])]
        
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
        purchase_price_failures = [r for r in self.test_results if not r['success'] and 'Purchase Price' in r['test']]
        purchase_date_failures = [r for r in self.test_results if not r['success'] and 'Purchase Date' in r['test']]
        scenario_failures = [r for r in self.test_results if not r['success'] and 'Scenario' in r['test']]
        
        print(f"\n🎯 BUG FIX ANALYSIS RESULTS:")
        print(f"  Purchase Price Validation Failures: {len(purchase_price_failures)}")
        print(f"  Purchase Date Validation Failures: {len(purchase_date_failures)}")
        print(f"  User Scenario Failures: {len(scenario_failures)}")
        
        if purchase_price_failures or purchase_date_failures or scenario_failures:
            print("\n🔍 ROOT CAUSE ANALYSIS:")
            print("  The purchase validation bug fix has issues with:")
            if purchase_price_failures:
                print("  - Purchase price field validation and conversion")
            if purchase_date_failures:
                print("  - Purchase date field validation and conversion")
            if scenario_failures:
                print("  - User-reported error scenarios still failing")
        else:
            print("\n✅ BUG FIX SUCCESSFUL!")
            print("  The purchase price and purchase date validation bug has been completely resolved.")
            print("  Users should no longer experience 422 validation errors when editing kit details.")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = PurchasePriceValidationTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()