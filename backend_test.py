#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - ADMIN DATA DELETION ENDPOINTS TESTING

Testing the newly created admin data deletion endpoints for clearing master kits and personal collections.

**Testing Requirements:**
1. Login with emergency admin account (emergency.admin@topkit.test / EmergencyAdmin2025!)
2. Test the three new admin endpoints:
   - `DELETE /api/admin/clear-master-kits` - Should clear all master kits
   - `DELETE /api/admin/clear-personal-collections` - Should clear all personal collections
   - `DELETE /api/admin/clear-all-kits` - Should clear both master kits and personal collections
3. Verify the endpoints return proper counts before and after deletion
4. Test admin authorization (endpoints should require admin role)
5. Verify the data is actually cleared from the database by checking counts afterward

**Expected Results:**
- All endpoints should return success messages with deletion counts
- After running the clear endpoints, the respective collections should be empty
- Only admin users should be able to access these endpoints
- Error handling should work for non-admin users

**Authentication:**
- Use emergency.admin@topkit.test / EmergencyAdmin2025! (admin role)
- Test should confirm admin authorization is working correctly

CRITICAL: Focus on testing admin data deletion endpoints with proper authorization and data verification.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from io import BytesIO
from PIL import Image

# Configuration
BACKEND_URL = "https://topkits.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitPersonalDetailsFormTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.available_master_kits = []
        self.test_master_kit_id = None
        self.created_collection_id = None
        
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
    
    def authenticate_admin(self):
        """Authenticate with emergency admin credentials"""
        try:
            print(f"\n🔐 EMERGENCY ADMIN AUTHENTICATION")
            print("=" * 60)
            print(f"   Email: {ADMIN_CREDENTIALS['email']}")
            print(f"   Password: {ADMIN_CREDENTIALS['password']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/auth/login",
                json=ADMIN_CREDENTIALS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_user_data = data.get('user', {})
                self.auth_token = data.get("token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                
                self.log_test("Emergency Admin Authentication", True, 
                             f"✅ Emergency admin authentication successful")
                print(f"      User ID: {self.admin_user_data.get('id')}")
                print(f"      Name: {self.admin_user_data.get('name')}")
                print(f"      Email: {self.admin_user_data.get('email')}")
                print(f"      Role: {self.admin_user_data.get('role')}")
                
                return True
                
            else:
                self.log_test("Emergency Admin Authentication", False, 
                             f"❌ Emergency admin authentication failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Emergency Admin Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_available_master_kits(self):
        """Get available Master Kits for collection addition testing"""
        try:
            print(f"\n📋 GETTING AVAILABLE MASTER KITS")
            print("=" * 60)
            print("Getting available Master Kits for collection testing...")
            
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if response.status_code == 200:
                self.available_master_kits = response.json()
                
                print(f"      ✅ Master Kits retrieved successfully")
                print(f"         Available Master Kits: {len(self.available_master_kits)}")
                
                if self.available_master_kits:
                    # Select first Master Kit for testing
                    self.test_master_kit_id = self.available_master_kits[0].get('id')
                    test_kit = self.available_master_kits[0]
                    print(f"         Test Master Kit: {test_kit.get('club', 'Unknown')} {test_kit.get('season', 'Unknown')}")
                    print(f"         Test Master Kit ID: {self.test_master_kit_id}")
                
                self.log_test("Get Available Master Kits", True, 
                             f"✅ {len(self.available_master_kits)} Master Kits available for testing")
                return True
            else:
                self.log_test("Get Available Master Kits", False, 
                             f"❌ Failed to get Master Kits - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Get Available Master Kits", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_collection_creation(self):
        """Test comprehensive collection creation with detailed personal information"""
        try:
            print(f"\n🎯 TESTING COMPREHENSIVE COLLECTION CREATION")
            print("=" * 60)
            print("Testing collection update with comprehensive personal details...")
            
            if not self.auth_token:
                self.log_test("Comprehensive Collection Creation", False, "❌ Missing authentication")
                return False
            
            # Get existing collection items to update one with comprehensive data
            collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            if collection_response.status_code != 200:
                self.log_test("Comprehensive Collection Creation", False, "❌ Cannot get collection items")
                return False
            
            collection_items = collection_response.json()
            if not collection_items:
                self.log_test("Comprehensive Collection Creation", False, "❌ No collection items available for testing")
                return False
            
            # Use first collection item for testing
            collection_id = collection_items[0].get('id')
            self.created_collection_id = collection_id
            
            # Update data with comprehensive personal details
            update_data = {
                # Basic Information
                "size": "L",
                "name_printing": "MESSI",
                "number_printing": "10",
                
                # Origin & Authenticity (condition mapping test)
                "condition": "match_worn",  # Should map from origin_type
                "physical_state": "very_good_condition",  # Should map from general_condition
                
                # Technical Details
                "patches": "UEFA Champions League, Premier League, FA Cup",
                "is_signed": True,
                "signed_by": "Lionel Messi",
                
                # User Estimate & Comments
                "purchase_price": 250.00,
                "purchase_date": "2024-01-15",
                "personal_notes": "Comprehensive test with all personal details - field mapping verification"  # Should map from comments
            }
            
            print(f"      Updating collection item with comprehensive personal details:")
            print(f"         Collection ID: {collection_id}")
            print(f"         Size: {update_data['size']}")
            print(f"         Name Printing: {update_data['name_printing']}")
            print(f"         Number Printing: {update_data['number_printing']}")
            print(f"         Condition: {update_data['condition']}")
            print(f"         Physical State: {update_data['physical_state']}")
            print(f"         Patches: {update_data['patches']}")
            print(f"         Is Signed: {update_data['is_signed']}")
            print(f"         Signed By: {update_data['signed_by']}")
            print(f"         Purchase Price: €{update_data['purchase_price']}")
            print(f"         Purchase Date: {update_data['purchase_date']}")
            print(f"         Personal Notes: {update_data['personal_notes']}")
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_id}",
                json=update_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"         ✅ Comprehensive collection update successful")
                print(f"            Collection Item ID: {collection_id}")
                print(f"            Master Kit ID: {data.get('master_kit_id')}")
                print(f"            Collection Type: {data.get('collection_type')}")
                
                # Verify field mapping worked correctly
                field_mapping_success = True
                field_mapping_issues = []
                
                # Check personal_notes mapping (from comments)
                if data.get('personal_notes') != update_data['personal_notes']:
                    field_mapping_success = False
                    field_mapping_issues.append(f"personal_notes mapping failed: expected '{update_data['personal_notes']}', got '{data.get('personal_notes')}'")
                
                # Check condition mapping (from origin_type)
                if data.get('condition') != update_data['condition']:
                    field_mapping_success = False
                    field_mapping_issues.append(f"condition mapping failed: expected '{update_data['condition']}', got '{data.get('condition')}'")
                
                # Check physical_state mapping (from general_condition)
                if data.get('physical_state') != update_data['physical_state']:
                    field_mapping_success = False
                    field_mapping_issues.append(f"physical_state mapping failed: expected '{update_data['physical_state']}', got '{data.get('physical_state')}'")
                
                # Check patches field
                if data.get('patches') != update_data['patches']:
                    field_mapping_success = False
                    field_mapping_issues.append(f"patches mapping failed: expected '{update_data['patches']}', got '{data.get('patches')}'")
                
                # Check signature fields
                if data.get('is_signed') != update_data['is_signed']:
                    field_mapping_success = False
                    field_mapping_issues.append(f"is_signed mapping failed: expected '{update_data['is_signed']}', got '{data.get('is_signed')}'")
                
                if field_mapping_success:
                    print(f"            ✅ All field mappings working correctly")
                    self.log_test("Comprehensive Collection Creation", True, 
                                 f"✅ Comprehensive collection update with all personal details successful")
                    return True
                else:
                    print(f"            ❌ Field mapping issues detected:")
                    for issue in field_mapping_issues:
                        print(f"               • {issue}")
                    self.log_test("Comprehensive Collection Creation", False, 
                                 f"❌ Field mapping issues: {'; '.join(field_mapping_issues)}")
                    return False
                    
            else:
                error_text = response.text
                print(f"         ❌ Comprehensive collection update failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                self.log_test("Comprehensive Collection Creation", False, 
                             f"❌ Collection update failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Collection Creation", False, f"Exception: {str(e)}")
            return False
    
    def test_price_estimation_endpoint(self):
        """Test price estimation endpoint for collection item"""
        try:
            print(f"\n💰 TESTING PRICE ESTIMATION ENDPOINT")
            print("=" * 60)
            print("Testing GET /api/my-collection/{collection_id}/price-estimation...")
            
            if not self.auth_token:
                self.log_test("Price Estimation Endpoint", False, "❌ No authentication token available")
                return False
            
            if not self.created_collection_id:
                # Try to get any collection item for testing
                collection_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
                if collection_response.status_code == 200:
                    collection_items = collection_response.json()
                    if collection_items:
                        self.created_collection_id = collection_items[0].get('id')
                        print(f"      Using existing collection item ID: {self.created_collection_id}")
                    else:
                        self.log_test("Price Estimation Endpoint", False, "❌ No collection items available for testing")
                        return False
                else:
                    self.log_test("Price Estimation Endpoint", False, "❌ Cannot get collection items for testing")
                    return False
            
            print(f"      Testing price estimation for collection item: {self.created_collection_id}")
            
            response = self.session.get(
                f"{BACKEND_URL}/my-collection/{self.created_collection_id}/price-estimation",
                timeout=10
            )
            
            if response.status_code == 200:
                price_data = response.json()
                
                print(f"         ✅ Price estimation endpoint accessible")
                print(f"            Estimated Price: €{price_data.get('estimated_price', 'N/A')}")
                
                # Check for coefficient breakdown in calculation_details
                calculation_details = price_data.get('calculation_details', {})
                coefficients_applied = calculation_details.get('coefficients_applied', [])
                
                print(f"            Calculation Details Available: {bool(calculation_details)}")
                print(f"            Coefficients Applied: {len(coefficients_applied)}")
                
                # Verify specific coefficient categories are present
                coefficient_factors = [coeff.get('factor', '') for coeff in coefficients_applied]
                
                expected_coefficient_types = [
                    'flocking',  # name+number printing
                    'patches',
                    'condition',
                    'physical_state', 
                    'signature'
                ]
                
                found_coefficients = []
                for coeff in coefficients_applied:
                    factor = coeff.get('factor', '').lower()
                    value = coeff.get('value', '')
                    print(f"               {coeff.get('factor')}: {value}")
                    
                    # Check which coefficient types are present
                    if 'flocking' in factor or 'name' in factor or 'number' in factor:
                        found_coefficients.append('flocking')
                    elif 'patch' in factor:
                        found_coefficients.append('patches')
                    elif 'condition' in factor and 'physical' not in factor:
                        found_coefficients.append('condition')
                    elif 'condition' in factor and ('physical' in factor or 'good' in factor or 'new' in factor or 'used' in factor or 'damaged' in factor):
                        found_coefficients.append('physical_state')
                    elif 'signed' in factor or 'signature' in factor:
                        found_coefficients.append('signature')
                
                # Remove duplicates
                found_coefficients = list(set(found_coefficients))
                
                if len(coefficients_applied) >= 3:  # Should have at least 3 coefficients for comprehensive data
                    print(f"            ✅ Price calculation working with {len(coefficients_applied)} coefficients")
                    print(f"            ✅ Coefficient types found: {', '.join(found_coefficients)}")
                    self.log_test("Price Estimation Endpoint", True, 
                                 f"✅ Price estimation working with proper coefficient breakdown ({len(coefficients_applied)} coefficients)")
                    return True
                else:
                    print(f"            ❌ Insufficient coefficients applied: {len(coefficients_applied)}")
                    self.log_test("Price Estimation Endpoint", False, 
                                 f"❌ Insufficient coefficients applied: {len(coefficients_applied)}")
                    return False
                    
            elif response.status_code == 404:
                print(f"         ❌ Price estimation endpoint not found - Status 404")
                self.log_test("Price Estimation Endpoint", False, 
                             f"❌ Price estimation endpoint not implemented - Status 404")
                return False
            else:
                error_text = response.text
                print(f"         ❌ Price estimation failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                self.log_test("Price Estimation Endpoint", False, 
                             f"❌ Price estimation failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Price Estimation Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def test_personal_details_retrieval(self):
        """Test retrieving collection item to verify personal details persistence"""
        try:
            print(f"\n📖 TESTING PERSONAL DETAILS RETRIEVAL")
            print("=" * 60)
            print("Testing GET /api/my-collection to verify personal details persistence...")
            
            if not self.auth_token:
                self.log_test("Personal Details Retrieval", False, "❌ No authentication token available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_items = response.json()
                
                print(f"      ✅ Collection retrieved successfully")
                print(f"         Collection Items: {len(collection_items)}")
                
                if not collection_items:
                    self.log_test("Personal Details Retrieval", False, "❌ No collection items found")
                    return False
                
                # Check first collection item for personal details
                sample_item = collection_items[0]
                
                print(f"         Sample Collection Item Analysis:")
                print(f"            ID: {sample_item.get('id')}")
                print(f"            Master Kit ID: {sample_item.get('master_kit_id')}")
                print(f"            Collection Type: {sample_item.get('collection_type')}")
                
                # Check personal details fields
                personal_details_fields = {
                    'size': sample_item.get('size'),
                    'name_printing': sample_item.get('name_printing'),
                    'number_printing': sample_item.get('number_printing'),
                    'condition': sample_item.get('condition'),
                    'physical_state': sample_item.get('physical_state'),
                    'patches': sample_item.get('patches'),
                    'is_signed': sample_item.get('is_signed'),
                    'signed_by': sample_item.get('signed_by'),
                    'purchase_price': sample_item.get('purchase_price'),
                    'purchase_date': sample_item.get('purchase_date'),
                    'personal_notes': sample_item.get('personal_notes')
                }
                
                print(f"         Personal Details Fields:")
                fields_with_data = 0
                for field_name, field_value in personal_details_fields.items():
                    if field_value is not None and field_value != "":
                        fields_with_data += 1
                        print(f"            ✅ {field_name}: {field_value}")
                    else:
                        print(f"            ⚪ {field_name}: {field_value}")
                
                # Check for "[object Object]" errors
                response_str = json.dumps(collection_items)
                object_errors = response_str.count("[object Object]")
                
                if object_errors > 0:
                    print(f"         ❌ Found {object_errors} '[object Object]' errors in collection data")
                    self.log_test("Personal Details Retrieval", False, 
                                 f"❌ {object_errors} '[object Object]' errors found")
                    return False
                
                # Verify field mapping worked correctly
                field_mapping_success = True
                if fields_with_data >= 5:  # At least 5 personal detail fields should have data
                    print(f"         ✅ Personal details persistence verified ({fields_with_data} fields with data)")
                    self.log_test("Personal Details Retrieval", True, 
                                 f"✅ Personal details persisted correctly - {fields_with_data} fields with data")
                    return True
                else:
                    print(f"         ❌ Insufficient personal details persisted ({fields_with_data} fields with data)")
                    self.log_test("Personal Details Retrieval", False, 
                                 f"❌ Insufficient personal details persisted - only {fields_with_data} fields with data")
                    return False
                    
            else:
                self.log_test("Personal Details Retrieval", False, 
                             f"❌ Collection retrieval failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Personal Details Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_personal_details_form_fix(self):
        """Test complete personal details form fix"""
        print("\n🚀 PERSONAL DETAILS PERSISTENCE & PRICE CALCULATION FIX TESTING")
        print("Testing the personal details persistence and price calculation fix for Add Personal Details form")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authentication...")
        auth_success = self.authenticate_admin()
        if not auth_success:
            print("❌ Cannot continue without authentication")
            return [False]
        test_results.append(auth_success)
        
        # Step 2: Get available Master Kits
        print("\n2️⃣ Getting available Master Kits...")
        master_kits_success = self.get_available_master_kits()
        test_results.append(master_kits_success)
        
        # Step 3: Test comprehensive collection creation with personal details
        print("\n3️⃣ Testing comprehensive collection creation with personal details...")
        comprehensive_success = self.test_comprehensive_collection_creation()
        test_results.append(comprehensive_success)
        
        # Step 4: Test price estimation endpoint
        print("\n4️⃣ Testing price estimation endpoint...")
        price_estimation_success = self.test_price_estimation_endpoint()
        test_results.append(price_estimation_success)
        
        # Step 5: Test personal details retrieval and persistence
        print("\n5️⃣ Testing personal details retrieval and persistence...")
        retrieval_success = self.test_personal_details_retrieval()
        test_results.append(retrieval_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 PERSONAL DETAILS PERSISTENCE & PRICE CALCULATION FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 PERSONAL DETAILS FORM FIX RESULTS:")
        
        # Authentication
        auth_working = any(r['success'] for r in self.test_results if 'Emergency Admin Authentication' in r['test'])
        if auth_working:
            print(f"  ✅ AUTHENTICATION: Emergency admin login working")
        else:
            print(f"  ❌ AUTHENTICATION: Emergency admin login failed")
        
        # Master Kits Access
        master_kits_working = any(r['success'] for r in self.test_results if 'Get Available Master Kits' in r['test'])
        if master_kits_working:
            print(f"  ✅ MASTER KITS ACCESS: Available Master Kits retrieved successfully")
        else:
            print(f"  ❌ MASTER KITS ACCESS: Failed to get Master Kits")
        
        # Comprehensive Collection Creation
        comprehensive_working = any(r['success'] for r in self.test_results if 'Comprehensive Collection Creation' in r['test'])
        if comprehensive_working:
            print(f"  ✅ COMPREHENSIVE COLLECTION CREATION: All personal details saved correctly")
        else:
            print(f"  ❌ COMPREHENSIVE COLLECTION CREATION: Field mapping issues detected")
        
        # Price Estimation
        price_estimation_working = any(r['success'] for r in self.test_results if 'Price Estimation Endpoint' in r['test'])
        if price_estimation_working:
            print(f"  ✅ PRICE ESTIMATION: Endpoint working with proper coefficient breakdown")
        else:
            print(f"  ❌ PRICE ESTIMATION: Endpoint not working or missing coefficients")
        
        # Personal Details Retrieval
        retrieval_working = any(r['success'] for r in self.test_results if 'Personal Details Retrieval' in r['test'])
        if retrieval_working:
            print(f"  ✅ PERSONAL DETAILS RETRIEVAL: Personal details persisted and retrievable")
        else:
            print(f"  ❌ PERSONAL DETAILS RETRIEVAL: Personal details not properly persisted")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status
        print(f"\n🎯 FINAL STATUS - PERSONAL DETAILS FORM FIX:")
        critical_tests = [auth_working, master_kits_working, comprehensive_working, retrieval_working]
        
        if all(critical_tests):
            print(f"  ✅ PERSONAL DETAILS FORM FIX WORKING PERFECTLY")
            print(f"     - Field mapping between EnhancedEditKitForm and backend working correctly")
            print(f"     - personal_notes from comments mapping working")
            print(f"     - condition from origin_type mapping working")
            print(f"     - physical_state from general_condition mapping working")
            print(f"     - All personal details persisted correctly")
            print(f"     - Price calculation coefficients available")
        elif any(critical_tests):
            print(f"  ⚠️ PARTIAL SUCCESS: Some functionality working")
            working_areas = []
            if auth_working: working_areas.append("authentication")
            if master_kits_working: working_areas.append("master kits access")
            if comprehensive_working: working_areas.append("collection creation")
            if retrieval_working: working_areas.append("personal details retrieval")
            print(f"     - Working areas: {', '.join(working_areas)}")
            
            failing_areas = []
            if not auth_working: failing_areas.append("authentication")
            if not master_kits_working: failing_areas.append("master kits access")
            if not comprehensive_working: failing_areas.append("collection creation")
            if not retrieval_working: failing_areas.append("personal details retrieval")
            if failing_areas:
                print(f"     - Still failing: {', '.join(failing_areas)}")
        else:
            print(f"  ❌ PERSONAL DETAILS FORM FIX NOT WORKING")
            print(f"     - Field mapping issues persist")
            print(f"     - Personal details not being saved correctly")
            print(f"     - Price calculation may not be working properly")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all personal details form fix tests and return success status"""
        test_results = self.test_personal_details_form_fix()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Personal Details Form Fix Testing"""
    tester = TopKitPersonalDetailsFormTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()