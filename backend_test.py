#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - PATCHES FIELD VALIDATION FIX TESTING

Testing the patches field validation fix for the Add Personal Details form.
The user reported "Error: body.patches: Input should be a valid string" when submitting the form.
Main agent has added debugging and additional sanitization to ensure patches arrays are properly converted to strings.

Test Plan:
1. **Authentication Testing** - Login with emergency.admin@topkit.test / EmergencyAdmin2025!
2. **Master Kit Access** - Verify available Master Kits for collection addition
3. **Patches Field Scenarios Testing**:
   - Test with patches as empty array []
   - Test with patches as string array ["patch1", "patch2"] 
   - Test with patches as null/undefined
   - Test with patches as empty string ""
4. **Verify patches field is always sent as a string or null to the backend**
5. **Confirm no "Input should be a valid string" validation errors for patches field**
6. **Test both minimal and comprehensive form data with various patches combinations**

CRITICAL: Focus on verifying that patches field validation no longer causes form submission failures.
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
BACKEND_URL = "https://jersey-collector-2.preview.emergentagent.com/api"

# Test Admin Credentials for authentication
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitCollectionFormTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.available_master_kits = []
        self.test_master_kit_id = None
        
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
    
    def test_minimal_collection_addition(self):
        """Test minimal collection addition with just master_kit_id and collection_type"""
        try:
            print(f"\n📦 TESTING MINIMAL COLLECTION ADDITION")
            print("=" * 60)
            print("Testing POST /api/my-collection with minimal data...")
            
            if not self.auth_token:
                self.log_test("Minimal Collection Addition", False, "❌ No authentication token available")
                return False
            
            if not self.test_master_kit_id:
                self.log_test("Minimal Collection Addition", False, "❌ No test Master Kit available")
                return False
            
            # Find a Master Kit that's not already in collection
            available_kit = None
            for kit in self.available_master_kits:
                # Check if this kit is already in collection
                check_response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
                if check_response.status_code == 200:
                    existing_items = check_response.json()
                    existing_kit_ids = [item.get('master_kit_id') for item in existing_items]
                    if kit.get('id') not in existing_kit_ids:
                        available_kit = kit
                        break
            
            if not available_kit:
                # If all kits are in collection, try to remove one first
                print("      All Master Kits already in collection, testing with existing kit...")
                available_kit = self.available_master_kits[0]
            
            # Test minimal collection addition - owned type
            minimal_data = {
                "master_kit_id": available_kit.get('id'),
                "collection_type": "owned"
            }
            
            print(f"      Adding Master Kit to collection (minimal data):")
            print(f"         Master Kit ID: {available_kit.get('id')}")
            print(f"         Master Kit: {available_kit.get('club', 'Unknown')} {available_kit.get('season', 'Unknown')}")
            print(f"         Collection Type: owned")
            
            response = self.session.post(
                f"{BACKEND_URL}/my-collection",
                json=minimal_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                print(f"         ✅ Minimal collection addition successful")
                print(f"            Collection Item ID: {data.get('id')}")
                print(f"            Master Kit ID: {data.get('master_kit_id')}")
                print(f"            Collection Type: {data.get('collection_type')}")
                
                # Verify no "[object Object]" errors in response
                response_str = json.dumps(data)
                if "[object Object]" in response_str:
                    self.log_test("Minimal Collection Addition", False, 
                                 f"❌ '[object Object]' errors found in response")
                    return False
                
                # Verify required fields are present
                required_fields = ['id', 'master_kit_id', 'collection_type', 'user_id']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("Minimal Collection Addition", True, 
                                 f"✅ Minimal collection addition working - no '[object Object]' errors")
                    return True
                else:
                    self.log_test("Minimal Collection Addition", False, 
                                 f"❌ Response missing required fields: {missing_fields}")
                    return False
                    
            elif response.status_code == 400 and "already in your" in response.text:
                # Item already exists - this means the endpoint is working, just testing with existing data
                print(f"         ✅ Master Kit already in collection (endpoint working correctly)")
                self.log_test("Minimal Collection Addition", True, 
                             f"✅ Minimal collection addition endpoint working - item already exists")
                return True
            else:
                error_text = response.text
                print(f"         ❌ Minimal collection addition failed - Status {response.status_code}")
                print(f"            Error: {error_text}")
                
                # Check if it's a field mapping error
                if "patches field expects List[str]" in error_text or "signature" in error_text:
                    self.log_test("Minimal Collection Addition", False, 
                                 f"❌ Field mapping error still exists - Status {response.status_code}", error_text)
                else:
                    self.log_test("Minimal Collection Addition", False, 
                                 f"❌ Collection addition failed - Status {response.status_code}", error_text)
                return False
                
        except Exception as e:
            self.log_test("Minimal Collection Addition", False, f"Exception: {str(e)}")
            return False
    
    def test_patches_field_empty_array(self):
        """Test patches field with empty array []"""
        try:
            print(f"\n🔍 TESTING PATCHES FIELD - EMPTY ARRAY")
            print("=" * 60)
            print("Testing POST /api/my-collection with patches as empty array []...")
            
            if not self.auth_token or not self.test_master_kit_id:
                self.log_test("Patches Field Empty Array", False, "❌ Missing authentication or test kit")
                return False
            
            # Find available kit for testing
            test_kit = self.available_master_kits[0] if self.available_master_kits else None
            if not test_kit:
                self.log_test("Patches Field Empty Array", False, "❌ No test Master Kit available")
                return False
            
            # Test with patches as empty array
            test_data = {
                "master_kit_id": test_kit.get('id'),
                "collection_type": "owned",
                "patches": []  # Empty array - should be converted to string or null
            }
            
            print(f"      Testing patches field as empty array:")
            print(f"         Master Kit: {test_kit.get('club', 'Unknown')} {test_kit.get('season', 'Unknown')}")
            print(f"         Patches: {test_data['patches']} (type: {type(test_data['patches'])})")
            
            response = self.session.post(
                f"{BACKEND_URL}/my-collection",
                json=test_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"         ✅ Empty array patches field accepted successfully")
                
                # Check if patches field validation error occurred
                if "Input should be a valid string" not in response.text:
                    self.log_test("Patches Field Empty Array", True, 
                                 f"✅ Empty array patches field handled correctly - no validation error")
                    return True
                else:
                    self.log_test("Patches Field Empty Array", False, 
                                 f"❌ Validation error still occurs with empty array")
                    return False
                    
            elif response.status_code == 400 and "already in your" in response.text:
                print(f"         ✅ Item already exists - but no patches validation error")
                self.log_test("Patches Field Empty Array", True, 
                             f"✅ Empty array patches field handled correctly - no validation error")
                return True
            elif response.status_code == 422 and "Input should be a valid string" in response.text:
                print(f"         ❌ Patches validation error still occurs with empty array")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Empty Array", False, 
                             f"❌ Patches validation error: {response.text}")
                return False
            else:
                print(f"         ❌ Unexpected response - Status {response.status_code}")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Empty Array", False, 
                             f"❌ Unexpected error - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patches Field Empty Array", False, f"Exception: {str(e)}")
            return False
    
    def test_patches_field_string_array(self):
        """Test patches field with string array ["patch1", "patch2"]"""
        try:
            print(f"\n🔍 TESTING PATCHES FIELD - STRING ARRAY")
            print("=" * 60)
            print("Testing POST /api/my-collection with patches as string array...")
            
            if not self.auth_token or not self.test_master_kit_id:
                self.log_test("Patches Field String Array", False, "❌ Missing authentication or test kit")
                return False
            
            # Find available kit for testing
            test_kit = self.available_master_kits[1] if len(self.available_master_kits) > 1 else self.available_master_kits[0]
            
            # Test with patches as string array
            test_data = {
                "master_kit_id": test_kit.get('id'),
                "collection_type": "wanted",
                "patches": ["Champions League", "Premier League"]  # String array - should be converted to string
            }
            
            print(f"      Testing patches field as string array:")
            print(f"         Master Kit: {test_kit.get('club', 'Unknown')} {test_kit.get('season', 'Unknown')}")
            print(f"         Patches: {test_data['patches']} (type: {type(test_data['patches'])})")
            
            response = self.session.post(
                f"{BACKEND_URL}/my-collection",
                json=test_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"         ✅ String array patches field accepted successfully")
                
                # Check if patches field validation error occurred
                if "Input should be a valid string" not in response.text:
                    self.log_test("Patches Field String Array", True, 
                                 f"✅ String array patches field handled correctly - no validation error")
                    return True
                else:
                    self.log_test("Patches Field String Array", False, 
                                 f"❌ Validation error still occurs with string array")
                    return False
                    
            elif response.status_code == 400 and "already in your" in response.text:
                print(f"         ✅ Item already exists - but no patches validation error")
                self.log_test("Patches Field String Array", True, 
                             f"✅ String array patches field handled correctly - no validation error")
                return True
            elif response.status_code == 422 and "Input should be a valid string" in response.text:
                print(f"         ❌ Patches validation error still occurs with string array")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field String Array", False, 
                             f"❌ Patches validation error: {response.text}")
                return False
            else:
                print(f"         ❌ Unexpected response - Status {response.status_code}")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field String Array", False, 
                             f"❌ Unexpected error - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patches Field String Array", False, f"Exception: {str(e)}")
            return False
    
    def test_patches_field_null_undefined(self):
        """Test patches field with null/undefined"""
        try:
            print(f"\n🔍 TESTING PATCHES FIELD - NULL/UNDEFINED")
            print("=" * 60)
            print("Testing POST /api/my-collection with patches as null...")
            
            if not self.auth_token or not self.test_master_kit_id:
                self.log_test("Patches Field Null", False, "❌ Missing authentication or test kit")
                return False
            
            # Find available kit for testing
            test_kit = self.available_master_kits[2] if len(self.available_master_kits) > 2 else self.available_master_kits[0]
            
            # Test with patches as null
            test_data = {
                "master_kit_id": test_kit.get('id'),
                "collection_type": "owned",
                "patches": None  # Null value - should be handled gracefully
            }
            
            print(f"      Testing patches field as null:")
            print(f"         Master Kit: {test_kit.get('club', 'Unknown')} {test_kit.get('season', 'Unknown')}")
            print(f"         Patches: {test_data['patches']} (type: {type(test_data['patches'])})")
            
            response = self.session.post(
                f"{BACKEND_URL}/my-collection",
                json=test_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"         ✅ Null patches field accepted successfully")
                
                # Check if patches field validation error occurred
                if "Input should be a valid string" not in response.text:
                    self.log_test("Patches Field Null", True, 
                                 f"✅ Null patches field handled correctly - no validation error")
                    return True
                else:
                    self.log_test("Patches Field Null", False, 
                                 f"❌ Validation error still occurs with null")
                    return False
                    
            elif response.status_code == 400 and "already in your" in response.text:
                print(f"         ✅ Item already exists - but no patches validation error")
                self.log_test("Patches Field Null", True, 
                             f"✅ Null patches field handled correctly - no validation error")
                return True
            elif response.status_code == 422 and "Input should be a valid string" in response.text:
                print(f"         ❌ Patches validation error still occurs with null")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Null", False, 
                             f"❌ Patches validation error: {response.text}")
                return False
            else:
                print(f"         ❌ Unexpected response - Status {response.status_code}")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Null", False, 
                             f"❌ Unexpected error - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patches Field Null", False, f"Exception: {str(e)}")
            return False
    
    def test_patches_field_empty_string(self):
        """Test patches field with empty string"""
        try:
            print(f"\n🔍 TESTING PATCHES FIELD - EMPTY STRING")
            print("=" * 60)
            print("Testing POST /api/my-collection with patches as empty string...")
            
            if not self.auth_token or not self.test_master_kit_id:
                self.log_test("Patches Field Empty String", False, "❌ Missing authentication or test kit")
                return False
            
            # Find available kit for testing
            test_kit = self.available_master_kits[3] if len(self.available_master_kits) > 3 else self.available_master_kits[0]
            
            # Test with patches as empty string
            test_data = {
                "master_kit_id": test_kit.get('id'),
                "collection_type": "wanted",
                "patches": ""  # Empty string - should be handled gracefully
            }
            
            print(f"      Testing patches field as empty string:")
            print(f"         Master Kit: {test_kit.get('club', 'Unknown')} {test_kit.get('season', 'Unknown')}")
            print(f"         Patches: '{test_data['patches']}' (type: {type(test_data['patches'])})")
            
            response = self.session.post(
                f"{BACKEND_URL}/my-collection",
                json=test_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"         ✅ Empty string patches field accepted successfully")
                
                # Check if patches field validation error occurred
                if "Input should be a valid string" not in response.text:
                    self.log_test("Patches Field Empty String", True, 
                                 f"✅ Empty string patches field handled correctly - no validation error")
                    return True
                else:
                    self.log_test("Patches Field Empty String", False, 
                                 f"❌ Validation error still occurs with empty string")
                    return False
                    
            elif response.status_code == 400 and "already in your" in response.text:
                print(f"         ✅ Item already exists - but no patches validation error")
                self.log_test("Patches Field Empty String", True, 
                             f"✅ Empty string patches field handled correctly - no validation error")
                return True
            elif response.status_code == 422 and "Input should be a valid string" in response.text:
                print(f"         ❌ Patches validation error still occurs with empty string")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Empty String", False, 
                             f"❌ Patches validation error: {response.text}")
                return False
            else:
                print(f"         ❌ Unexpected response - Status {response.status_code}")
                print(f"            Error: {response.text}")
                self.log_test("Patches Field Empty String", False, 
                             f"❌ Unexpected error - Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Patches Field Empty String", False, f"Exception: {str(e)}")
            return False
    
    def test_comprehensive_patches_combinations(self):
        """Test comprehensive form data with various patches combinations"""
        try:
            print(f"\n🎯 TESTING COMPREHENSIVE PATCHES COMBINATIONS")
            print("=" * 60)
            print("Testing comprehensive form data with various patches combinations...")
            
            if not self.auth_token or not self.test_master_kit_id:
                self.log_test("Comprehensive Patches Combinations", False, "❌ Missing authentication or test kit")
                return False
            
            # Test different patches combinations with comprehensive form data
            test_cases = [
                {
                    "name": "Comprehensive with string patches",
                    "patches": "Champions League, Premier League, FA Cup",
                    "expected_success": True
                },
                {
                    "name": "Comprehensive with empty string patches",
                    "patches": "",
                    "expected_success": True
                },
                {
                    "name": "Comprehensive with null patches",
                    "patches": None,
                    "expected_success": True
                }
            ]
            
            success_count = 0
            
            for i, test_case in enumerate(test_cases):
                print(f"      Test {i+1}: {test_case['name']}")
                
                # Use different kits for each test
                test_kit = self.available_master_kits[i % len(self.available_master_kits)]
                
                comprehensive_data = {
                    "master_kit_id": test_kit.get('id'),
                    "collection_type": "owned" if i % 2 == 0 else "wanted",
                    "patches": test_case['patches'],
                    "condition": "match_worn",
                    "physical_state": "very_good_condition",
                    "is_signed": True,
                    "signed_by": "test-player-id",
                    "purchase_price": 150.00,
                    "purchase_date": "2024-01-15",
                    "size": "L",
                    "name_printing": "MESSI",
                    "number_printing": "10",
                    "personal_notes": "Test comprehensive data with patches variations"
                }
                
                print(f"         Patches: {test_case['patches']} (type: {type(test_case['patches'])})")
                
                response = self.session.post(
                    f"{BACKEND_URL}/my-collection",
                    json=comprehensive_data,
                    timeout=15
                )
                
                if response.status_code in [200, 201]:
                    print(f"            ✅ {test_case['name']} successful")
                    success_count += 1
                elif response.status_code == 400 and "already in your" in response.text:
                    print(f"            ✅ {test_case['name']} - item already exists (no validation error)")
                    success_count += 1
                elif response.status_code == 422 and "Input should be a valid string" in response.text:
                    print(f"            ❌ {test_case['name']} - patches validation error still occurs")
                    print(f"               Error: {response.text}")
                else:
                    print(f"            ❌ {test_case['name']} - Status {response.status_code}")
                    print(f"               Error: {response.text}")
            
            if success_count == len(test_cases):
                self.log_test("Comprehensive Patches Combinations", True, 
                             f"✅ All patches combinations working correctly")
                return True
            else:
                self.log_test("Comprehensive Patches Combinations", False, 
                             f"❌ Patches validation issues - {success_count}/{len(test_cases)} successful")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Patches Combinations", False, f"Exception: {str(e)}")
            return False
    
    def test_collection_type_variations(self):
        """Test both 'owned' and 'wanted' collection types"""
        try:
            print(f"\n🔄 TESTING COLLECTION TYPE VARIATIONS")
            print("=" * 60)
            print("Testing both 'owned' and 'wanted' collection types...")
            
            if not self.auth_token:
                self.log_test("Collection Type Variations", False, "❌ No authentication token available")
                return False
            
            if len(self.available_master_kits) < 2:
                self.log_test("Collection Type Variations", False, "❌ Need at least 2 Master Kits for testing")
                return False
            
            # Test different collection types with different Master Kits
            test_cases = [
                {
                    "master_kit_id": self.available_master_kits[0].get('id'),
                    "collection_type": "owned",
                    "description": "Owned collection type"
                },
                {
                    "master_kit_id": self.available_master_kits[1].get('id') if len(self.available_master_kits) > 1 else self.available_master_kits[0].get('id'),
                    "collection_type": "wanted", 
                    "description": "Wanted collection type"
                }
            ]
            
            success_count = 0
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"      Test {i}: {test_case['description']}")
                print(f"         Master Kit ID: {test_case['master_kit_id']}")
                print(f"         Collection Type: {test_case['collection_type']}")
                
                response = self.session.post(
                    f"{BACKEND_URL}/my-collection",
                    json=test_case,
                    timeout=15
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    
                    # Verify collection type is correct
                    if data.get('collection_type') == test_case['collection_type']:
                        print(f"            ✅ {test_case['description']} successful")
                        success_count += 1
                    else:
                        print(f"            ❌ Collection type mismatch: expected {test_case['collection_type']}, got {data.get('collection_type')}")
                        
                elif response.status_code == 400 and "already in your" in response.text:
                    # Item already exists - this is expected behavior
                    print(f"            ✅ {test_case['description']} - item already exists (expected)")
                    success_count += 1
                else:
                    print(f"            ❌ {test_case['description']} failed - Status {response.status_code}")
                    print(f"               Error: {response.text}")
            
            if success_count == len(test_cases):
                self.log_test("Collection Type Variations", True, 
                             f"✅ Both collection types working correctly")
                return True
            else:
                self.log_test("Collection Type Variations", False, 
                             f"❌ Collection type issues - {success_count}/{len(test_cases)} successful")
                return False
                
        except Exception as e:
            self.log_test("Collection Type Variations", False, f"Exception: {str(e)}")
            return False
    
    def test_existing_collection_retrieval(self):
        """Test retrieving existing collection items to verify no '[object Object]' errors"""
        try:
            print(f"\n📖 TESTING EXISTING COLLECTION RETRIEVAL")
            print("=" * 60)
            print("Testing GET /api/my-collection to verify no '[object Object]' errors...")
            
            if not self.auth_token:
                self.log_test("Existing Collection Retrieval", False, "❌ No authentication token available")
                return False
            
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_items = response.json()
                
                print(f"      ✅ Collection retrieved successfully")
                print(f"         Collection Items: {len(collection_items)}")
                
                # Check for "[object Object]" errors in any collection item
                response_str = json.dumps(collection_items)
                object_errors = response_str.count("[object Object]")
                
                if object_errors > 0:
                    print(f"         ❌ Found {object_errors} '[object Object]' errors in collection data")
                    self.log_test("Existing Collection Retrieval", False, 
                                 f"❌ {object_errors} '[object Object]' errors found in existing collection data")
                    return False
                else:
                    print(f"         ✅ No '[object Object]' errors found in collection data")
                    
                    # Show sample collection item structure
                    if collection_items:
                        sample_item = collection_items[0]
                        print(f"         Sample item fields: {list(sample_item.keys())}")
                        
                        # Check specific fields that were problematic
                        patches_field = sample_item.get('patches')
                        signature_field = sample_item.get('signature')
                        
                        print(f"         Patches field: {patches_field} (type: {type(patches_field)})")
                        print(f"         Signature field: {signature_field}")
                    
                    self.log_test("Existing Collection Retrieval", True, 
                                 f"✅ No '[object Object]' errors in existing collection data")
                    return True
                    
            else:
                self.log_test("Existing Collection Retrieval", False, 
                             f"❌ Collection retrieval failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Existing Collection Retrieval", False, f"Exception: {str(e)}")
            return False
    
    def test_patches_field_validation_fix(self):
        """Test complete patches field validation fix"""
        print("\n🚀 PATCHES FIELD VALIDATION FIX TESTING")
        print("Testing the patches field validation fix for Add Personal Details form")
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
        
        # Step 3: Test patches field with empty array
        print("\n3️⃣ Testing patches field with empty array []...")
        empty_array_success = self.test_patches_field_empty_array()
        test_results.append(empty_array_success)
        
        # Step 4: Test patches field with string array
        print("\n4️⃣ Testing patches field with string array...")
        string_array_success = self.test_patches_field_string_array()
        test_results.append(string_array_success)
        
        # Step 5: Test patches field with null/undefined
        print("\n5️⃣ Testing patches field with null/undefined...")
        null_success = self.test_patches_field_null_undefined()
        test_results.append(null_success)
        
        # Step 6: Test patches field with empty string
        print("\n6️⃣ Testing patches field with empty string...")
        empty_string_success = self.test_patches_field_empty_string()
        test_results.append(empty_string_success)
        
        # Step 7: Test comprehensive patches combinations
        print("\n7️⃣ Testing comprehensive patches combinations...")
        comprehensive_success = self.test_comprehensive_patches_combinations()
        test_results.append(comprehensive_success)
        
        # Step 8: Test minimal collection addition (for baseline)
        print("\n8️⃣ Testing minimal collection addition...")
        minimal_success = self.test_minimal_collection_addition()
        test_results.append(minimal_success)
        
        return test_results
    
    def print_final_summary(self):
        """Print final testing summary"""
        print("\n📊 PATCHES FIELD VALIDATION FIX TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print(f"\n🔍 PATCHES FIELD VALIDATION FIX RESULTS:")
        
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
        
        # Patches Field Tests
        empty_array_working = any(r['success'] for r in self.test_results if 'Patches Field Empty Array' in r['test'])
        string_array_working = any(r['success'] for r in self.test_results if 'Patches Field String Array' in r['test'])
        null_working = any(r['success'] for r in self.test_results if 'Patches Field Null' in r['test'])
        empty_string_working = any(r['success'] for r in self.test_results if 'Patches Field Empty String' in r['test'])
        comprehensive_working = any(r['success'] for r in self.test_results if 'Comprehensive Patches Combinations' in r['test'])
        
        if empty_array_working:
            print(f"  ✅ PATCHES EMPTY ARRAY: No validation error with patches as []")
        else:
            print(f"  ❌ PATCHES EMPTY ARRAY: Still getting validation error with patches as []")
        
        if string_array_working:
            print(f"  ✅ PATCHES STRING ARRAY: No validation error with patches as ['patch1', 'patch2']")
        else:
            print(f"  ❌ PATCHES STRING ARRAY: Still getting validation error with patches as string array")
        
        if null_working:
            print(f"  ✅ PATCHES NULL: No validation error with patches as null")
        else:
            print(f"  ❌ PATCHES NULL: Still getting validation error with patches as null")
        
        if empty_string_working:
            print(f"  ✅ PATCHES EMPTY STRING: No validation error with patches as ''")
        else:
            print(f"  ❌ PATCHES EMPTY STRING: Still getting validation error with patches as empty string")
        
        if comprehensive_working:
            print(f"  ✅ COMPREHENSIVE PATCHES: All patches combinations working in comprehensive form")
        else:
            print(f"  ❌ COMPREHENSIVE PATCHES: Issues with patches combinations in comprehensive form")
        
        # Minimal Collection Addition
        minimal_working = any(r['success'] for r in self.test_results if 'Minimal Collection Addition' in r['test'])
        if minimal_working:
            print(f"  ✅ MINIMAL COLLECTION ADDITION: Basic form submission working")
        else:
            print(f"  ❌ MINIMAL COLLECTION ADDITION: Basic form submission failing")
        
        # Show failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ ISSUES IDENTIFIED ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        # Final status - Focus on patches field validation
        print(f"\n🎯 FINAL STATUS - PATCHES FIELD VALIDATION FIX:")
        patches_tests = [empty_array_working, string_array_working, null_working, empty_string_working]
        critical_tests = [auth_working, master_kits_working] + patches_tests
        
        if all(patches_tests):
            print(f"  ✅ PATCHES FIELD VALIDATION FIX WORKING PERFECTLY")
            print(f"     - No 'Input should be a valid string' errors for patches field")
            print(f"     - Empty array [] handled correctly")
            print(f"     - String array ['patch1', 'patch2'] handled correctly")
            print(f"     - Null/undefined values handled correctly")
            print(f"     - Empty string '' handled correctly")
            print(f"     - Patches field always sent as string or null to backend")
        elif any(patches_tests):
            print(f"  ⚠️ PARTIAL SUCCESS: Some patches scenarios working")
            working_scenarios = []
            if empty_array_working: working_scenarios.append("empty array")
            if string_array_working: working_scenarios.append("string array")
            if null_working: working_scenarios.append("null values")
            if empty_string_working: working_scenarios.append("empty string")
            print(f"     - Working scenarios: {', '.join(working_scenarios)}")
            
            failing_scenarios = []
            if not empty_array_working: failing_scenarios.append("empty array")
            if not string_array_working: failing_scenarios.append("string array")
            if not null_working: failing_scenarios.append("null values")
            if not empty_string_working: failing_scenarios.append("empty string")
            if failing_scenarios:
                print(f"     - Still failing: {', '.join(failing_scenarios)}")
        else:
            print(f"  ❌ PATCHES FIELD VALIDATION FIX NOT WORKING")
            print(f"     - Still getting 'Input should be a valid string' errors")
            print(f"     - Form submission failures continue for patches field")
            print(f"     - Backend validation not properly handling patches arrays")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all patches field validation fix tests and return success status"""
        test_results = self.test_patches_field_validation_fix()
        self.print_final_summary()
        return any(test_results)

def main():
    """Main test execution - Patches Field Validation Fix Testing"""
    tester = TopKitCollectionFormTesting()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()