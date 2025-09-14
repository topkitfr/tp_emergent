#!/usr/bin/env python3

"""
Reference Kit Collection Creation Workflow Backend Test
Testing the reference kit collection creation workflow that's failing in the frontend.

Test Requirements from Review Request:
1. AUTHENTICATION TEST: Login with admin credentials: topkitfr@gmail.com / TopKitSecure789#
2. REFERENCE KIT COLLECTION CREATION TEST: Test POST /api/reference-kit-collections endpoint
3. FORM DATA VALIDATION TEST: Test with required and optional fields
4. ERROR HANDLING TEST: Test various error scenarios

The user reports that the "Add Personal Details" form doesn't work after filling it out 
and clicking "Add to Collection". Previously it worked, so check if there are any 
validation issues or API changes that could be blocking the submission.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class ReferenceKitCollectionWorkflowTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.admin_user_id = None
        self.test_results = []
        self.available_reference_kits = []
        
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
            
            if response.status_code == 200:
                data = response.json()
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
    
    def get_available_reference_kits(self):
        """Get available reference kits from the database for testing"""
        print("\n📋 GETTING AVAILABLE REFERENCE KITS")
        print("=" * 60)
        
        try:
            # Get reference kits from vestiaire endpoint
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            
            if response.status_code == 200:
                data = response.json()
                self.available_reference_kits = data if isinstance(data, list) else []
                
                self.log_test(
                    "Reference Kits Retrieval", 
                    True, 
                    f"Retrieved {len(self.available_reference_kits)} reference kits from database"
                )
                
                # Log some details about available kits
                if self.available_reference_kits:
                    first_kit = self.available_reference_kits[0]
                    print(f"Sample reference kit ID: {first_kit.get('id', 'unknown')}")
                    print(f"Sample reference kit name: {first_kit.get('model_name', 'unknown')}")
                    print(f"Sample team: {first_kit.get('team_name', 'unknown')}")
                
                return len(self.available_reference_kits) > 0
            else:
                self.log_test("Reference Kits Retrieval", False, f"Failed to get reference kits: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Reference Kits Retrieval", False, f"Exception getting reference kits: {str(e)}")
            return False
    
    def test_reference_kit_collection_creation_basic(self):
        """Test 2: REFERENCE KIT COLLECTION CREATION TEST - Basic collection creation"""
        print("\n📝 TESTING BASIC REFERENCE KIT COLLECTION CREATION")
        print("=" * 60)
        
        if not self.available_reference_kits:
            self.log_test("Basic Collection Creation", False, "No reference kits available for testing")
            return False
        
        # Use the first available reference kit
        test_reference_kit = self.available_reference_kits[0]
        reference_kit_id = test_reference_kit.get('id')
        
        if not reference_kit_id:
            self.log_test("Basic Collection Creation", False, "No reference kit ID found")
            return False
        
        print(f"Testing with reference kit ID: {reference_kit_id}")
        
        # Test basic collection creation with minimal required fields
        basic_collection_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "excellent"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=basic_collection_data)
            
            print(f"Basic collection creation response status: {response.status_code}")
            print(f"Basic collection creation response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                collection_id = data.get('id')
                
                self.log_test(
                    "Basic Collection Creation", 
                    True, 
                    f"Successfully created basic collection with ID: {collection_id}"
                )
                return True
            else:
                self.log_test(
                    "Basic Collection Creation", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Basic Collection Creation", False, f"Exception during basic collection creation: {str(e)}")
            return False
    
    def test_reference_kit_collection_creation_detailed(self):
        """Test 3: DETAILED COLLECTION CREATION TEST - Test with all optional fields"""
        print("\n📋 TESTING DETAILED REFERENCE KIT COLLECTION CREATION")
        print("=" * 60)
        
        if not self.available_reference_kits:
            self.log_test("Detailed Collection Creation", False, "No reference kits available for testing")
            return False
        
        # Use the first available reference kit
        test_reference_kit = self.available_reference_kits[0]
        reference_kit_id = test_reference_kit.get('id')
        
        if not reference_kit_id:
            self.log_test("Detailed Collection Creation", False, "No reference kit ID found")
            return False
        
        print(f"Testing detailed collection with reference kit ID: {reference_kit_id}")
        
        # Test detailed collection creation with all optional fields
        detailed_collection_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "wanted",
            "size": "L",
            "condition": "excellent",
            "personal_description": "Looking for this specific kit for my collection",
            "purchase_price": 120.00,
            "estimated_value": 150.00,
            "player_name": "Leao",
            "player_number": "10",
            "worn": False,
            "worn_type": None,
            "signed": False,
            "signed_by": None
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=detailed_collection_data)
            
            print(f"Detailed collection creation response status: {response.status_code}")
            print(f"Detailed collection creation response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                collection_id = data.get('id')
                
                # Verify that optional fields were saved
                saved_player_name = data.get('player_name')
                saved_purchase_price = data.get('purchase_price')
                saved_worn = data.get('worn')
                saved_signed = data.get('signed')
                
                self.log_test(
                    "Detailed Collection Creation", 
                    True, 
                    f"Successfully created detailed collection with ID: {collection_id}. Player: {saved_player_name}, Price: {saved_purchase_price}, Worn: {saved_worn}, Signed: {saved_signed}"
                )
                return True
            else:
                self.log_test(
                    "Detailed Collection Creation", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Detailed Collection Creation", False, f"Exception during detailed collection creation: {str(e)}")
            return False
    
    def test_special_attributes_collection(self):
        """Test 4: SPECIAL ATTRIBUTES TEST - Test worn=true, signed=true"""
        print("\n⭐ TESTING SPECIAL ATTRIBUTES COLLECTION CREATION")
        print("=" * 60)
        
        if not self.available_reference_kits:
            self.log_test("Special Attributes Collection", False, "No reference kits available for testing")
            return False
        
        # Use the first available reference kit
        test_reference_kit = self.available_reference_kits[0]
        reference_kit_id = test_reference_kit.get('id')
        
        if not reference_kit_id:
            self.log_test("Special Attributes Collection", False, "No reference kit ID found")
            return False
        
        print(f"Testing special attributes with reference kit ID: {reference_kit_id}")
        
        # Test collection with special attributes
        special_collection_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "excellent",
            "personal_description": "Match-worn and signed by Leao",
            "purchase_price": 500.00,
            "player_name": "Leao",
            "player_number": "10",
            "worn": True,
            "worn_type": "match_worn",
            "signed": True,
            "signed_by": "Rafael Leao"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=special_collection_data)
            
            print(f"Special attributes collection response status: {response.status_code}")
            print(f"Special attributes collection response: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                collection_id = data.get('id')
                
                # Verify special attributes were saved
                saved_worn = data.get('worn')
                saved_worn_type = data.get('worn_type')
                saved_signed = data.get('signed')
                saved_signed_by = data.get('signed_by')
                
                special_attributes_correct = (
                    saved_worn == True and
                    saved_worn_type == "match_worn" and
                    saved_signed == True and
                    saved_signed_by == "Rafael Leao"
                )
                
                self.log_test(
                    "Special Attributes Collection", 
                    special_attributes_correct, 
                    f"Collection ID: {collection_id}. Worn: {saved_worn} ({saved_worn_type}), Signed: {saved_signed} by {saved_signed_by}"
                )
                return special_attributes_correct
            else:
                self.log_test(
                    "Special Attributes Collection", 
                    False, 
                    f"Failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Special Attributes Collection", False, f"Exception during special attributes collection: {str(e)}")
            return False
    
    def test_form_validation_errors(self):
        """Test 5: FORM DATA VALIDATION TEST - Test missing required fields"""
        print("\n⚠️ TESTING FORM VALIDATION ERRORS")
        print("=" * 60)
        
        validation_tests = []
        
        # Test 1: Missing reference_kit_id
        try:
            invalid_data = {
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent"
            }
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
            validation_tests.append({
                'test': 'Missing reference_kit_id',
                'expected_status': [400, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 422]
            })
        except Exception as e:
            validation_tests.append({
                'test': 'Missing reference_kit_id',
                'success': False,
                'error': str(e)
            })
        
        # Test 2: Missing size
        if self.available_reference_kits:
            try:
                invalid_data = {
                    "reference_kit_id": self.available_reference_kits[0].get('id'),
                    "collection_type": "owned",
                    "condition": "excellent"
                }
                response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
                validation_tests.append({
                    'test': 'Missing size',
                    'expected_status': [400, 422],
                    'actual_status': response.status_code,
                    'success': response.status_code in [400, 422]
                })
            except Exception as e:
                validation_tests.append({
                    'test': 'Missing size',
                    'success': False,
                    'error': str(e)
                })
        
        # Test 3: Missing condition
        if self.available_reference_kits:
            try:
                invalid_data = {
                    "reference_kit_id": self.available_reference_kits[0].get('id'),
                    "collection_type": "owned",
                    "size": "L"
                }
                response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
                validation_tests.append({
                    'test': 'Missing condition',
                    'expected_status': [400, 422],
                    'actual_status': response.status_code,
                    'success': response.status_code in [400, 422]
                })
            except Exception as e:
                validation_tests.append({
                    'test': 'Missing condition',
                    'success': False,
                    'error': str(e)
                })
        
        # Test 4: Invalid reference_kit_id
        try:
            invalid_data = {
                "reference_kit_id": "invalid-reference-kit-id",
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent"
            }
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
            validation_tests.append({
                'test': 'Invalid reference_kit_id',
                'expected_status': [400, 404, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 404, 422]
            })
        except Exception as e:
            validation_tests.append({
                'test': 'Invalid reference_kit_id',
                'success': False,
                'error': str(e)
            })
        
        # Log results
        successful_validation_tests = 0
        for test in validation_tests:
            if test['success']:
                successful_validation_tests += 1
                self.log_test(
                    f"Form Validation - {test['test']}", 
                    True, 
                    f"Proper validation error: {test.get('actual_status', 'N/A')}"
                )
            else:
                self.log_test(
                    f"Form Validation - {test['test']}", 
                    False, 
                    f"Unexpected response: {test.get('actual_status', test.get('error', 'Unknown'))}"
                )
        
        overall_success = successful_validation_tests >= 3  # At least 3 out of 4 validation tests should pass
        
        self.log_test(
            "Form Validation Overall", 
            overall_success, 
            f"Passed {successful_validation_tests}/{len(validation_tests)} validation tests"
        )
        
        return overall_success
    
    def test_duplicate_collection_handling(self):
        """Test 6: DUPLICATE COLLECTION TEST - Test duplicate collection entries"""
        print("\n🔄 TESTING DUPLICATE COLLECTION HANDLING")
        print("=" * 60)
        
        if not self.available_reference_kits:
            self.log_test("Duplicate Collection Handling", False, "No reference kits available for testing")
            return False
        
        # Use the first available reference kit
        test_reference_kit = self.available_reference_kits[0]
        reference_kit_id = test_reference_kit.get('id')
        
        if not reference_kit_id:
            self.log_test("Duplicate Collection Handling", False, "No reference kit ID found")
            return False
        
        print(f"Testing duplicate handling with reference kit ID: {reference_kit_id}")
        
        # Create first collection
        collection_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "M",
            "condition": "good"
        }
        
        try:
            # First creation should succeed
            first_response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=collection_data)
            
            if first_response.status_code in [200, 201]:
                print("First collection created successfully")
                
                # Second creation with same data should fail or handle duplicates
                second_response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=collection_data)
                
                print(f"Duplicate collection response status: {second_response.status_code}")
                print(f"Duplicate collection response: {second_response.text}")
                
                # Check if duplicate is properly handled (either rejected or allowed with different ID)
                if second_response.status_code == 400:
                    self.log_test(
                        "Duplicate Collection Handling", 
                        True, 
                        "Duplicate collection properly rejected with 400 status"
                    )
                    return True
                elif second_response.status_code in [200, 201]:
                    # If duplicates are allowed, check if they have different IDs
                    second_data = second_response.json()
                    first_data = first_response.json()
                    
                    if first_data.get('id') != second_data.get('id'):
                        self.log_test(
                            "Duplicate Collection Handling", 
                            True, 
                            "Duplicate collections allowed with different IDs"
                        )
                        return True
                    else:
                        self.log_test(
                            "Duplicate Collection Handling", 
                            False, 
                            "Duplicate collections have same ID - potential issue"
                        )
                        return False
                else:
                    self.log_test(
                        "Duplicate Collection Handling", 
                        False, 
                        f"Unexpected duplicate response: {second_response.status_code}"
                    )
                    return False
            else:
                self.log_test(
                    "Duplicate Collection Handling", 
                    False, 
                    f"First collection creation failed: {first_response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test("Duplicate Collection Handling", False, f"Exception during duplicate testing: {str(e)}")
            return False
    
    def test_error_handling_scenarios(self):
        """Test 7: ERROR HANDLING TEST - Test various error scenarios"""
        print("\n🚨 TESTING ERROR HANDLING SCENARIOS")
        print("=" * 60)
        
        error_tests = []
        
        # Test 1: Unauthenticated request
        try:
            unauthenticated_session = requests.Session()
            collection_data = {
                "reference_kit_id": "test-id",
                "collection_type": "owned",
                "size": "L",
                "condition": "excellent"
            }
            response = unauthenticated_session.post(f"{BACKEND_URL}/reference-kit-collections", json=collection_data)
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
        
        # Test 2: Invalid collection_type
        try:
            invalid_data = {
                "reference_kit_id": self.available_reference_kits[0].get('id') if self.available_reference_kits else "test-id",
                "collection_type": "invalid_type",
                "size": "L",
                "condition": "excellent"
            }
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
            error_tests.append({
                'test': 'Invalid Collection Type',
                'expected_status': [400, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 422]
            })
        except Exception as e:
            error_tests.append({
                'test': 'Invalid Collection Type',
                'success': False,
                'error': str(e)
            })
        
        # Test 3: Invalid size value
        try:
            invalid_data = {
                "reference_kit_id": self.available_reference_kits[0].get('id') if self.available_reference_kits else "test-id",
                "collection_type": "owned",
                "size": "INVALID_SIZE",
                "condition": "excellent"
            }
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
            error_tests.append({
                'test': 'Invalid Size Value',
                'expected_status': [400, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 422]
            })
        except Exception as e:
            error_tests.append({
                'test': 'Invalid Size Value',
                'success': False,
                'error': str(e)
            })
        
        # Test 4: Invalid condition value
        try:
            invalid_data = {
                "reference_kit_id": self.available_reference_kits[0].get('id') if self.available_reference_kits else "test-id",
                "collection_type": "owned",
                "size": "L",
                "condition": "invalid_condition"
            }
            response = self.session.post(f"{BACKEND_URL}/reference-kit-collections", json=invalid_data)
            error_tests.append({
                'test': 'Invalid Condition Value',
                'expected_status': [400, 422],
                'actual_status': response.status_code,
                'success': response.status_code in [400, 422]
            })
        except Exception as e:
            error_tests.append({
                'test': 'Invalid Condition Value',
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
        
        overall_success = successful_error_tests >= 3  # At least 3 out of 4 error tests should pass
        
        self.log_test(
            "Error Handling Overall", 
            overall_success, 
            f"Passed {successful_error_tests}/{len(error_tests)} error handling tests"
        )
        
        return overall_success
    
    def run_all_tests(self):
        """Run all reference kit collection workflow tests"""
        print("🚀 STARTING REFERENCE KIT COLLECTION CREATION WORKFLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Admin Email: {ADMIN_EMAIL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Test 1: Authentication
        if not self.authenticate_admin():
            print("\n❌ CRITICAL: Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Test 2: Get available reference kits
        if not self.get_available_reference_kits():
            print("\n❌ CRITICAL: No reference kits available. Cannot proceed with collection tests.")
            return False
        
        # Test 3: Basic collection creation
        basic_success = self.test_reference_kit_collection_creation_basic()
        
        # Test 4: Detailed collection creation
        detailed_success = self.test_reference_kit_collection_creation_detailed()
        
        # Test 5: Special attributes collection
        special_success = self.test_special_attributes_collection()
        
        # Test 6: Form validation
        validation_success = self.test_form_validation_errors()
        
        # Test 7: Duplicate handling
        duplicate_success = self.test_duplicate_collection_handling()
        
        # Test 8: Error handling
        error_handling_success = self.test_error_handling_scenarios()
        
        # Generate final report
        self.generate_final_report()
        
        return True
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📋 FINAL TEST REPORT - REFERENCE KIT COLLECTION CREATION WORKFLOW")
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
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Reference Kit Collection creation workflow is working well!")
        elif success_rate >= 60:
            print("⚠️ OVERALL ASSESSMENT: GOOD - Reference Kit Collection creation workflow is mostly working with minor issues.")
        elif success_rate >= 40:
            print("🔧 OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Reference Kit Collection creation workflow has significant issues.")
        else:
            print("🚨 OVERALL ASSESSMENT: CRITICAL ISSUES - Reference Kit Collection creation workflow is severely broken.")
        
        print("=" * 80)

def main():
    """Main function to run the tests"""
    tester = ReferenceKitCollectionWorkflowTester()
    
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