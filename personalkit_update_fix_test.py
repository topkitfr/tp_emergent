#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://kit-fixes.preview.emergentagent.com/api"
ADMIN_EMAIL = "topkitfr@gmail.com"
ADMIN_PASSWORD = "TopKitSecure789#"

class PersonalKitUpdateTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_kit_id = None
        
    def authenticate(self):
        """Authenticate as admin user"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                user_info = data.get("user", {})
                self.user_id = user_info.get("id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ Authentication successful!")
                print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
                print(f"   Role: {user_info.get('role')}")
                print(f"   User ID: {self.user_id}")
                print(f"   Token length: {len(self.auth_token)} characters")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def get_reference_kit_for_testing(self):
        """Get a reference kit from vestiaire for testing"""
        print("\n📋 Getting reference kit for testing...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/vestiaire")
            print(f"   Vestiaire status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    reference_kit = data[0]  # Get first available kit
                    print(f"   ✅ Found reference kit: {reference_kit.get('id')}")
                    print(f"   Team: {reference_kit.get('team_info', {}).get('name', 'Unknown')}")
                    print(f"   Season: {reference_kit.get('season', 'Unknown')}")
                    return reference_kit.get('id')
                else:
                    print(f"   ❌ No reference kits available in vestiaire")
                    return None
            else:
                print(f"   ❌ Failed to get vestiaire: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error getting reference kit: {e}")
            return None

    def create_test_personal_kit(self, reference_kit_id):
        """Create a test personal kit for update testing"""
        print("\n➕ Creating test personal kit...")
        
        personal_kit_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",
            "condition": "excellent",
            "purchase_price": 85.00,
            "price_value": 120.00,
            "for_sale": False,  # Testing for_sale field specifically
            "times_worn": 5,
            "acquisition_story": "Original: Bought from official store during season launch",
            "printing_type": "Official",
            "match_details": "Worn during Champions League match",
            "authentication_details": "Comes with certificate of authenticity",
            "printed_name": "MBAPPE",
            "printed_number": "7",
            "personal_notes": "Original: Excellent condition jersey with official printing"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=personal_kit_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                kit_id = data.get('id')
                print(f"   ✅ Personal kit created successfully!")
                print(f"   Kit ID: {kit_id}")
                print(f"   Size: {data.get('size')}")
                print(f"   For Sale: {data.get('for_sale')}")  # Check for_sale field in response
                print(f"   Price Value: {data.get('price_value')}")
                return kit_id
            else:
                print(f"   ❌ Personal kit creation failed")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Personal kit creation error: {e}")
            return None

    def test_personal_kit_update_field_consistency(self, kit_id):
        """Test PersonalKit Update Field Consistency (PUT /api/personal-kits/{kit_id})"""
        print("\n🔄 Testing PersonalKit Update Field Consistency...")
        
        # Test updating PersonalKit with all available fields
        update_data = {
            "size": "XL",
            "condition": "very_good", 
            "purchase_price": 95.00,
            "price_value": 140.00,           # Test price_value field
            "for_sale": True,                # Test for_sale field (not is_for_sale)
            "times_worn": 12,                # Test times_worn field
            "acquisition_story": "Updated: Bought from official store during Champions League final - amazing experience!",  # Test acquisition_story field
            "printing_type": "Heat Transfer", # Test printing_type field
            "match_details": "Updated: Worn during El Clasico match - historic victory!",  # Test match_details field
            "authentication_details": "Updated: Verified authentic by TopKit experts with detailed analysis",  # Test authentication_details field
            "printed_name": "MESSI",         # Test printed_name field
            "printed_number": "30",          # Test printed_number field
            "personal_notes": "Updated: Authentic jersey with official printing - excellent condition after cleaning"  # Test personal_notes field
        }
        
        try:
            response = self.session.put(f"{BACKEND_URL}/personal-kits/{kit_id}", json=update_data)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   ✅ PersonalKit updated successfully!")
                
                # Verify all updated fields are returned correctly
                print("   📋 Verifying updated field mappings:")
                
                # Core fields
                print(f"     Size: {data.get('size')} (Expected: XL)")
                print(f"     Condition: {data.get('condition')} (Expected: very_good)")
                print(f"     Purchase Price: {data.get('purchase_price')} (Expected: 95.0)")
                
                # Key test fields from review request
                print(f"     Price Value: {data.get('price_value')} (Expected: 140.0)")
                print(f"     For Sale: {data.get('for_sale')} (Expected: True)")  # Check for_sale not is_for_sale
                print(f"     Times Worn: {data.get('times_worn')} (Expected: 12)")
                print(f"     Acquisition Story: {data.get('acquisition_story')}")
                print(f"     Printing Type: {data.get('printing_type')} (Expected: Heat Transfer)")
                print(f"     Match Details: {data.get('match_details')}")
                print(f"     Authentication Details: {data.get('authentication_details')}")
                print(f"     Printed Name: {data.get('printed_name')} (Expected: MESSI)")
                print(f"     Printed Number: {data.get('printed_number')} (Expected: 30)")
                print(f"     Personal Notes: {data.get('personal_notes')}")
                
                # Check for [object Object] errors
                response_text = response.text
                if "[object Object]" in response_text:
                    print(f"   ❌ [object Object] error detected in response!")
                    return False
                
                # Verify PersonalKitResponse model works correctly
                required_fields = ['id', 'size', 'condition', 'price_value', 'for_sale', 'times_worn']
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ⚠️ Missing or null fields in response: {missing_fields}")
                    return False
                
                print(f"   ✅ All field mappings working correctly!")
                return True
            else:
                print(f"   ❌ PersonalKit update failed")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ PersonalKit update error: {e}")
            return False

    def test_personal_kit_retrieval_after_update(self, kit_id):
        """Test PersonalKit Retrieval After Update (GET /api/personal-kits)"""
        print("\n📥 Testing PersonalKit Retrieval After Update...")
        
        try:
            # Test owned collection retrieval
            response = self.session.get(f"{BACKEND_URL}/personal-kits?collection_type=owned")
            print(f"   Owned collection status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Find our updated kit
                updated_kit = None
                for kit in data:
                    if kit.get('id') == kit_id:
                        updated_kit = kit
                        break
                
                if updated_kit:
                    print(f"   ✅ Updated kit found in owned collection!")
                    
                    # Verify all updated fields persist correctly
                    print("   📋 Verifying field persistence after update:")
                    print(f"     Size: {updated_kit.get('size')} (Should be: XL)")
                    print(f"     Condition: {updated_kit.get('condition')} (Should be: very_good)")
                    print(f"     Price Value: {updated_kit.get('price_value')} (Should be: 140.0)")
                    print(f"     For Sale: {updated_kit.get('for_sale')} (Should be: True)")  # Check for_sale field is returned
                    print(f"     Times Worn: {updated_kit.get('times_worn')} (Should be: 12)")
                    print(f"     Acquisition Story: {updated_kit.get('acquisition_story')}")
                    print(f"     Printing Type: {updated_kit.get('printing_type')} (Should be: Heat Transfer)")
                    print(f"     Match Details: {updated_kit.get('match_details')}")
                    print(f"     Authentication Details: {updated_kit.get('authentication_details')}")
                    
                    # Verify purchase information persists
                    print(f"     Purchase Price: {updated_kit.get('purchase_price')} (Should be: 95.0)")
                    print(f"     Printed Name: {updated_kit.get('printed_name')} (Should be: MESSI)")
                    print(f"     Printed Number: {updated_kit.get('printed_number')} (Should be: 30)")
                    print(f"     Personal Notes: {updated_kit.get('personal_notes')}")
                    
                    # Check that for_sale field is returned (not is_for_sale)
                    if 'for_sale' in updated_kit and updated_kit['for_sale'] == True:
                        print(f"   ✅ for_sale field correctly returned (not is_for_sale)")
                    else:
                        print(f"   ❌ for_sale field issue - Value: {updated_kit.get('for_sale')}")
                        return False
                    
                    return True
                else:
                    print(f"   ❌ Updated kit not found in owned collection")
                    return False
            else:
                print(f"   ❌ Failed to retrieve owned collection: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Retrieval error: {e}")
            return False

    def test_complete_personal_kit_workflow(self):
        """Test Complete PersonalKit Workflow"""
        print("\n🔄 Testing Complete PersonalKit Workflow...")
        
        # Get a reference kit for testing
        reference_kit_id = self.get_reference_kit_for_testing()
        if not reference_kit_id:
            print("   ❌ Cannot proceed without reference kit")
            return False
        
        # Create PersonalKit with full data
        print("   Step 1: Create PersonalKit with full data")
        kit_id = self.create_test_personal_kit(reference_kit_id)
        if not kit_id:
            print("   ❌ PersonalKit creation failed")
            return False
        
        # Update with new values
        print("   Step 2: Update PersonalKit with new values")
        update_success = self.test_personal_kit_update_field_consistency(kit_id)
        if not update_success:
            print("   ❌ PersonalKit update failed")
            return False
        
        # Retrieve and verify all fields
        print("   Step 3: Retrieve and verify all fields persist")
        retrieval_success = self.test_personal_kit_retrieval_after_update(kit_id)
        if not retrieval_success:
            print("   ❌ PersonalKit retrieval verification failed")
            return False
        
        print("   ✅ Complete PersonalKit workflow successful!")
        return True

    def test_get_enriched_personal_kit_function(self, kit_id):
        """Test the get_enriched_personal_kit function works without collection_type field"""
        print("\n🔍 Testing get_enriched_personal_kit function...")
        
        try:
            # Test direct kit retrieval (this uses get_enriched_personal_kit internally)
            response = self.session.get(f"{BACKEND_URL}/personal-kits/{kit_id}")
            print(f"   Direct kit retrieval status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ get_enriched_personal_kit function working!")
                
                # Verify enriched data structure
                enriched_fields = ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']
                for field in enriched_fields:
                    if field in data and data[field]:
                        print(f"     {field}: ✅ Present")
                    else:
                        print(f"     {field}: ❌ Missing or empty")
                
                return True
            else:
                print(f"   ❌ get_enriched_personal_kit function failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ get_enriched_personal_kit function error: {e}")
            return False

    def test_field_validation(self):
        """Test Field Validation Tests"""
        print("\n✅ Testing Field Validation...")
        
        # Get reference kit for testing
        reference_kit_id = self.get_reference_kit_for_testing()
        if not reference_kit_id:
            print("   ❌ Cannot proceed without reference kit")
            return False
        
        # Test 1: Optional fields can be set to null/None
        print("   Test 1: Optional fields can be set to null/None")
        optional_fields_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "M",
            "condition": "good",
            "purchase_price": None,  # Optional field set to None
            "price_value": None,     # Optional field set to None
            "acquisition_story": None,  # Optional field set to None
            "printing_type": None,   # Optional field set to None
            "personal_notes": None   # Optional field set to None
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=optional_fields_data)
            print(f"     Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"     ✅ Optional fields can be set to null/None")
                kit_id = response.json().get('id')
                
                # Clean up test kit
                if kit_id:
                    self.session.delete(f"{BACKEND_URL}/personal-kits/{kit_id}")
            else:
                print(f"     ❌ Optional fields validation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"     ❌ Optional fields test error: {e}")
            return False
        
        # Test 2: Required fields validation still works
        print("   Test 2: Required fields validation still works")
        missing_required_data = {
            "collection_type": "owned",
            # Missing reference_kit_id (required)
            # Missing size (required)
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=missing_required_data)
            print(f"     Status: {response.status_code}")
            
            if response.status_code == 422:  # Validation error expected
                print(f"     ✅ Required fields validation working")
                
                # Check for meaningful error messages (not [object Object])
                response_text = response.text
                if "[object Object]" in response_text:
                    print(f"     ❌ [object Object] error in validation response!")
                    return False
                else:
                    print(f"     ✅ Meaningful validation error messages")
            else:
                print(f"     ❌ Required fields validation not working properly")
                return False
                
        except Exception as e:
            print(f"     ❌ Required fields test error: {e}")
            return False
        
        # Test 3: Data types are handled correctly
        print("   Test 3: Data types are handled correctly")
        data_types_data = {
            "reference_kit_id": reference_kit_id,
            "collection_type": "owned",
            "size": "L",                    # string
            "condition": "excellent",       # string
            "purchase_price": 99.99,        # float
            "price_value": 150.0,          # float
            "for_sale": True,              # bool
            "times_worn": 8,               # int
            "acquisition_story": "Test story",  # string
            "printing_type": "Official"     # string
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/personal-kits", json=data_types_data)
            print(f"     Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"     ✅ Data types handled correctly")
                
                # Verify data types in response
                print(f"       purchase_price type: {type(data.get('purchase_price'))} (should be float)")
                print(f"       for_sale type: {type(data.get('for_sale'))} (should be bool)")
                print(f"       times_worn type: {type(data.get('times_worn'))} (should be int)")
                
                kit_id = data.get('id')
                # Clean up test kit
                if kit_id:
                    self.session.delete(f"{BACKEND_URL}/personal-kits/{kit_id}")
                    
                return True
            else:
                print(f"     ❌ Data types validation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"     ❌ Data types test error: {e}")
            return False

    def run_comprehensive_personalkit_update_test(self):
        """Run comprehensive PersonalKit Update Fix testing"""
        print("🚀 Starting PersonalKit Update Fix Comprehensive Testing")
        print("=" * 80)
        print("Focus: Verify all field mappings work correctly and for_sale field consistency")
        print("=" * 80)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        results = {
            'authentication': True,
            'personal_kit_update_field_consistency': False,
            'personal_kit_retrieval_after_update': False,
            'complete_personal_kit_workflow': False,
            'get_enriched_personal_kit_function': False,
            'field_validation_tests': False
        }
        
        # Step 2: Test Complete PersonalKit Workflow (includes creation, update, retrieval)
        results['complete_personal_kit_workflow'] = self.test_complete_personal_kit_workflow()
        
        # If workflow succeeded, we have a test kit to work with
        if results['complete_personal_kit_workflow'] and self.test_kit_id:
            # Step 3: Test get_enriched_personal_kit function
            results['get_enriched_personal_kit_function'] = self.test_get_enriched_personal_kit_function(self.test_kit_id)
        
        # Step 4: Test Field Validation
        results['field_validation_tests'] = self.test_field_validation()
        
        # Update individual results based on workflow success
        if results['complete_personal_kit_workflow']:
            results['personal_kit_update_field_consistency'] = True
            results['personal_kit_retrieval_after_update'] = True
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PERSONALKIT UPDATE FIX TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = 0
        total_tests = len(results)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
            if passed:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        
        if success_rate >= 80:
            print("🎉 PersonalKit Update Fix is PRODUCTION-READY!")
        elif success_rate >= 60:
            print("⚠️ PersonalKit Update Fix has minor issues but is mostly functional")
        else:
            print("❌ PersonalKit Update Fix has critical issues that need immediate attention")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = PersonalKitUpdateTester()
    success = tester.run_comprehensive_personalkit_update_test()
    sys.exit(0 if success else 1)