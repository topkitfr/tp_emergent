#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Contribution Approval System Testing
Testing the contribution approval system specifically for image updates on master kits
to identify the bug where new photos are not showing up after approval.
"""

import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://topkit-preview.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "password123"
}

# Test focus: Contribution approval system for image updates
FOCUS_ENTITY_TYPE = "master_kit"

class ContributionApprovalTester:
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
    
    def test_get_specific_collection_item(self, collection_id):
        """Test getting a specific collection item by ID"""
        try:
            # First try to get the specific collection item from the failing ID
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_data = response.json()
                
                # Find the specific item
                target_item = None
                for item in collection_data:
                    if item.get('id') == collection_id:
                        target_item = item
                        break
                
                if target_item:
                    self.log_test("Get Specific Collection Item", True,
                                 f"Found collection item {collection_id}")
                    return target_item
                else:
                    # If specific ID not found, use any available item for testing
                    if collection_data:
                        target_item = collection_data[0]
                        self.log_test("Get Specific Collection Item", True,
                                     f"Specific ID {collection_id} not found, using {target_item.get('id')} for testing")
                        return target_item
                    else:
                        self.log_test("Get Specific Collection Item", False,
                                     "No collection items found")
                        return None
            else:
                self.log_test("Get Specific Collection Item", False,
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test("Get Specific Collection Item", False, f"Exception: {str(e)}")
            return None
    
    def get_my_collection(self):
        """Get user's collection items"""
        try:
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_data = response.json()
                self.collection_items = collection_data
                
                self.log_test("My Collection Retrieval", True,
                             f"Retrieved {len(collection_data)} collection items")
                
                return collection_data
                
            else:
                self.log_test("My Collection Retrieval", False,
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("My Collection Retrieval", False, f"Exception: {str(e)}")
            return []
    
    def test_edit_kit_details_validation_error(self, collection_item):
        """Test editing kit details to identify the 422 validation error"""
        try:
            collection_id = collection_item.get('id')
            master_kit = collection_item.get('master_kit', {})
            kit_name = f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')}"
            
            print(f"\n🔍 Testing Edit Kit Details for: {kit_name} (ID: {collection_id})")
            print(f"Current item data: {json.dumps(collection_item, indent=2, default=str)}")
            
            # Test with various update scenarios to identify validation issues
            test_scenarios = [
                {
                    "name": "Basic Update - Name and Number",
                    "data": {
                        "name_printing": "Messi",
                        "number_printing": "10"
                    }
                },
                {
                    "name": "Invalid Condition Value",
                    "data": {
                        "condition": "invalid_condition_value",
                        "physical_state": "very_good_condition"
                    }
                },
                {
                    "name": "Invalid Physical State Value",
                    "data": {
                        "condition": "match_worn",
                        "physical_state": "invalid_physical_state"
                    }
                },
                {
                    "name": "Invalid Data Types",
                    "data": {
                        "purchase_price": "not_a_number",
                        "is_signed": "not_a_boolean",
                        "purchase_date": "invalid_date_format"
                    }
                },
                {
                    "name": "Missing Required Fields Test",
                    "data": {
                        "master_kit_id": None,
                        "user_id": None
                    }
                },
                {
                    "name": "Full Update with All Fields",
                    "data": {
                        "name_printing": "Mbappé",
                        "number_printing": "7",
                        "condition": "match_prepared",
                        "physical_state": "new_with_tags",
                        "patches": "Champions League",
                        "is_signed": True,
                        "signed_by": "Kylian Mbappé",
                        "purchase_price": 150.0,
                        "purchase_date": "2023-01-15",
                        "notes": "Excellent condition jersey"
                    }
                },
                {
                    "name": "Minimal Update - Single Field",
                    "data": {
                        "notes": "Updated notes"
                    }
                }
            ]
            
            for scenario in test_scenarios:
                print(f"\n📝 Testing scenario: {scenario['name']}")
                print(f"Update data: {json.dumps(scenario['data'], indent=2)}")
                
                response = self.session.put(
                    f"{BACKEND_URL}/my-collection/{collection_id}",
                    json=scenario['data'],
                    timeout=10
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 422:
                    # This is the error we're looking for!
                    try:
                        error_data = response.json()
                        print(f"422 Validation Error Details: {json.dumps(error_data, indent=2)}")
                        
                        self.log_test(f"Edit Kit Details - {scenario['name']}", False,
                                     f"422 Validation Error: {error_data}",
                                     {
                                         "status_code": response.status_code,
                                         "error_details": error_data,
                                         "update_data": scenario['data']
                                     })
                    except:
                        error_text = response.text
                        print(f"422 Error Response Text: {error_text}")
                        
                        self.log_test(f"Edit Kit Details - {scenario['name']}", False,
                                     f"422 Validation Error (raw): {error_text}",
                                     {
                                         "status_code": response.status_code,
                                         "error_text": error_text,
                                         "update_data": scenario['data']
                                     })
                    
                    # Continue testing other scenarios to see if all fail or just specific ones
                    continue
                    
                elif response.status_code == 200:
                    updated_data = response.json()
                    self.log_test(f"Edit Kit Details - {scenario['name']}", True,
                                 f"Successfully updated collection item",
                                 {
                                     "updated_data": updated_data,
                                     "update_data": scenario['data']
                                 })
                else:
                    try:
                        error_data = response.json()
                        print(f"Error Response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"Error Response Text: {response.text}")
                    
                    self.log_test(f"Edit Kit Details - {scenario['name']}", False,
                                 f"Failed with status {response.status_code}",
                                 {
                                     "status_code": response.status_code,
                                     "response_text": response.text,
                                     "update_data": scenario['data']
                                 })
            
            return True
                
        except Exception as e:
            self.log_test(f"Edit Kit Details Testing", False, f"Exception: {str(e)}")
            return False
    
    def test_backend_model_validation(self):
        """Test backend model validation by examining the Pydantic models"""
        try:
            # Let's check what the backend expects for MyCollectionUpdate
            print("\n🔍 Analyzing Backend Model Validation...")
            
            # Try to get the OpenAPI schema to understand validation requirements
            response = self.session.get(f"{BACKEND_URL.replace('/api', '')}/docs", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Backend API Documentation Access", True, "Successfully accessed API docs")
            else:
                self.log_test("Backend API Documentation Access", False, f"Failed with status {response.status_code}")
            
            # Try to get the OpenAPI JSON schema
            schema_response = self.session.get(f"{BACKEND_URL.replace('/api', '')}/openapi.json", timeout=10)
            
            if schema_response.status_code == 200:
                schema_data = schema_response.json()
                
                # Look for MyCollectionUpdate schema
                schemas = schema_data.get('components', {}).get('schemas', {})
                
                if 'MyCollectionUpdate' in schemas:
                    update_schema = schemas['MyCollectionUpdate']
                    print(f"MyCollectionUpdate schema: {json.dumps(update_schema, indent=2)}")
                    
                    self.log_test("Backend Model Schema Analysis", True,
                                 "Found MyCollectionUpdate schema",
                                 {"schema": update_schema})
                else:
                    self.log_test("Backend Model Schema Analysis", False,
                                 "MyCollectionUpdate schema not found in OpenAPI spec")
                    
                    # List available schemas
                    available_schemas = list(schemas.keys())
                    print(f"Available schemas: {available_schemas}")
                    
            else:
                self.log_test("Backend OpenAPI Schema Access", False, 
                             f"Failed with status {schema_response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Backend Model Validation Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_curl_direct_api_calls(self, collection_item):
        """Test direct API calls using curl-like requests to capture exact errors"""
        try:
            collection_id = collection_item.get('id')
            
            print(f"\n🌐 Testing Direct API Calls for Collection ID: {collection_id}")
            
            # Test with raw requests to capture exact error responses
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Test minimal update that should work
            minimal_update = {"notes": "Test update"}
            
            print(f"Making PUT request to: {BACKEND_URL}/my-collection/{collection_id}")
            print(f"Headers: {headers}")
            print(f"Data: {json.dumps(minimal_update)}")
            
            response = requests.put(
                f"{BACKEND_URL}/my-collection/{collection_id}",
                headers=headers,
                json=minimal_update,
                timeout=10
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Content: {response.text}")
            
            if response.status_code == 422:
                try:
                    error_json = response.json()
                    print(f"422 Error JSON: {json.dumps(error_json, indent=2)}")
                    
                    # Check if this is a Pydantic validation error
                    if 'detail' in error_json:
                        detail = error_json['detail']
                        if isinstance(detail, list):
                            print("Pydantic validation errors found:")
                            for error in detail:
                                print(f"  - Field: {error.get('loc', 'unknown')}")
                                print(f"    Message: {error.get('msg', 'unknown')}")
                                print(f"    Type: {error.get('type', 'unknown')}")
                                print(f"    Input: {error.get('input', 'unknown')}")
                        
                        self.log_test("Direct API Call - 422 Analysis", True,
                                     "Successfully captured 422 validation error details",
                                     {"error_details": error_json})
                    
                except Exception as json_error:
                    print(f"Could not parse JSON response: {json_error}")
                    self.log_test("Direct API Call - 422 Analysis", True,
                                 f"422 error captured (raw text): {response.text}")
            
            elif response.status_code == 200:
                self.log_test("Direct API Call - Success", True,
                             "Update succeeded - no validation error")
            else:
                self.log_test("Direct API Call - Other Error", False,
                             f"Unexpected status {response.status_code}: {response.text}")
            
            return True
            
        except Exception as e:
            self.log_test("Direct API Call Testing", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive Edit Kit Details functionality tests"""
        print("🧪 Starting TopKit Edit Kit Details Testing")
        print("Testing the Edit Kit Details functionality that's failing with 422 Unprocessable Entity errors")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Get collection items
        print("📋 Retrieving My Collection...")
        collection_data = self.get_my_collection()
        print()
        
        if not collection_data:
            print("❌ No collection data retrieved. Cannot proceed with tests.")
            return False
        
        # Step 3: Test getting the specific failing collection item
        print(f"🎯 Testing Specific Collection Item: {FAILING_COLLECTION_ID}")
        target_item = self.test_get_specific_collection_item(FAILING_COLLECTION_ID)
        print()
        
        if not target_item:
            print("❌ Could not find target collection item. Using first available item.")
            target_item = collection_data[0] if collection_data else None
        
        if not target_item:
            print("❌ No collection items available for testing.")
            return False
        
        # Step 4: Test backend model validation analysis
        print("🔍 Analyzing Backend Model Validation...")
        self.test_backend_model_validation()
        print()
        
        # Step 5: Test direct API calls to capture exact errors
        print("🌐 Testing Direct API Calls...")
        self.test_curl_direct_api_calls(target_item)
        print()
        
        # Step 6: Test edit kit details with various scenarios
        print("✏️ Testing Edit Kit Details Validation Errors...")
        self.test_edit_kit_details_validation_error(target_item)
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 EDIT KIT DETAILS TEST SUMMARY")
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
        edit_tests = [r for r in self.test_results if 'Edit Kit Details' in r['test']]
        api_tests = [r for r in self.test_results if 'API Call' in r['test']]
        validation_tests = [r for r in self.test_results if 'Validation' in r['test'] or 'Model' in r['test']]
        
        print(f"\nTest Categories:")
        print(f"  Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} ✅")
        print(f"  Collection Access: {len([r for r in collection_tests if r['success']])}/{len(collection_tests)} ✅")
        print(f"  Edit Kit Details: {len([r for r in edit_tests if r['success']])}/{len(edit_tests)} ✅")
        print(f"  Direct API Calls: {len([r for r in api_tests if r['success']])}/{len(api_tests)} ✅")
        print(f"  Validation Analysis: {len([r for r in validation_tests if r['success']])}/{len(validation_tests)} ✅")
        
        # Show 422 errors specifically
        validation_errors = [r for r in self.test_results if '422' in r['message']]
        if validation_errors:
            print(f"\n🚨 422 VALIDATION ERRORS FOUND: {len(validation_errors)}")
            for error in validation_errors:
                print(f"  • {error['test']}: {error['message']}")
                if error.get('details'):
                    error_details = error['details']
                    if isinstance(error_details, dict) and 'error_details' in error_details:
                        print(f"    Details: {error_details['error_details']}")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success'] and '422' not in result['message']:
                    print(f"  • {result['test']}: {result['message']}")
        
        if validation_errors:
            print("\n🎯 VALIDATION ERROR ANALYSIS COMPLETE!")
            print("The 422 Unprocessable Entity errors have been captured and analyzed.")
        else:
            print("\n✅ NO VALIDATION ERRORS FOUND!")
            print("Edit Kit Details functionality appears to be working correctly.")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = EditKitDetailsTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()