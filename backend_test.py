#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - My Collection Focus
Testing the My Collection functionality after Pydantic validation fixes
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://jerseydb-clean.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

# Test kit IDs from the review request - PSG collection items
PSG_2015_KIT_ID = "802f4f1d-7b3c-47fe-969f-5d45ed615257"
PSG_2023_KIT_ID = "1fe4787a-a0c0-4bb3-959d-931857745a2b"

# Expected price calculations from review request
EXPECTED_PRICES = {
    PSG_2015_KIT_ID: 952.0,  # PSG 2015 kit with Mbappé signature = €952
    PSG_2023_KIT_ID: 108.0   # PSG 2023 basic kit = €108
}

class TopKitTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.collection_items = []  # Store collection items for testing
        
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
        """Authenticate with the backend"""
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
                self.log_test("Authentication", True, f"Successfully authenticated as {data.get('user', {}).get('email')}")
                return True
            else:
                self.log_test("Authentication", False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception during authentication: {str(e)}")
            return False
    
    def test_my_collection_endpoint(self):
        """Test the My Collection endpoint - main focus of this test"""
        try:
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_data = response.json()
                self.collection_items = collection_data  # Store for later tests
                
                self.log_test("My Collection Endpoint", True, 
                             f"Retrieved {len(collection_data)} collection items successfully")
                
                # Check if we have the expected PSG items
                psg_items = [item for item in collection_data if item.get('master_kit', {}).get('id') in [PSG_2015_KIT_ID, PSG_2023_KIT_ID]]
                
                self.log_test("PSG Collection Items Found", len(psg_items) == 2,
                             f"Found {len(psg_items)} PSG items (expected 2)")
                
                # Verify no Pydantic validation errors by checking structure
                for i, item in enumerate(collection_data):
                    required_fields = ['id', 'master_kit_id', 'user_id', 'master_kit']
                    missing_fields = [field for field in required_fields if field not in item]
                    
                    if missing_fields:
                        self.log_test(f"Collection Item {i+1} Structure", False,
                                     f"Missing required fields: {missing_fields}")
                    else:
                        self.log_test(f"Collection Item {i+1} Structure", True,
                                     "All required fields present")
                
                return collection_data
                
            elif response.status_code == 401:
                self.log_test("My Collection Endpoint", False, 
                             "Authentication failed - token may be invalid", response.text)
                return []
            else:
                self.log_test("My Collection Endpoint", False, 
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("My Collection Endpoint", False, f"Exception: {str(e)}")
            return []
    
    def test_collection_price_estimation(self, collection_item, expected_price):
        """Test price estimation for a collection item"""
        try:
            collection_id = collection_item.get('id')
            master_kit = collection_item.get('master_kit', {})
            kit_name = f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')}"
            
            response = self.session.get(f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                estimated_price = price_data.get('estimated_price', 0)
                
                # Check if price matches expected value (with some tolerance for rounding)
                price_match = abs(estimated_price - expected_price) < 5.0  # Allow €5 tolerance
                
                self.log_test(f"Price Estimation ({kit_name})", price_match,
                             f"Estimated: €{estimated_price}, Expected: €{expected_price}",
                             price_data)
                
                return price_data
                
            elif response.status_code == 404:
                self.log_test(f"Price Estimation ({kit_name})", False,
                             f"Collection item not found for price estimation", f"Collection ID {collection_id} not found")
                return None
            else:
                self.log_test(f"Price Estimation ({kit_name})", False,
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"Price Estimation ({kit_name})", False, f"Exception: {str(e)}")
            return None
    
    def test_update_collection_item(self, collection_item):
        """Test updating a collection item with new details"""
        try:
            collection_id = collection_item.get('id')
            master_kit = collection_item.get('master_kit', {})
            kit_name = f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')}"
            
            # Test update data
            update_data = {
                "name_printing": "Mbappé",
                "number_printing": "7",
                "patches": "Champions League",
                "is_signed": True,
                "signed_by": "Kylian Mbappé",
                "size": "L",
                "purchase_price": 150.0,
                "personal_notes": "Updated via testing - signature verified"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                updated_item = response.json()
                
                # Verify the update was successful
                update_success = (
                    updated_item.get('name_printing') == update_data['name_printing'] and
                    updated_item.get('number_printing') == update_data['number_printing'] and
                    updated_item.get('is_signed') == update_data['is_signed']
                )
                
                self.log_test(f"Update Collection Item ({kit_name})", update_success,
                             f"Successfully updated collection item with new details",
                             {
                                 "name_printing": updated_item.get('name_printing'),
                                 "number_printing": updated_item.get('number_printing'),
                                 "is_signed": updated_item.get('is_signed'),
                                 "signed_by": updated_item.get('signed_by')
                             })
                
                return updated_item
                
            elif response.status_code == 404:
                self.log_test(f"Update Collection Item ({kit_name})", False,
                             f"Collection item not found for update", f"Collection ID {collection_id} not found")
                return None
            else:
                self.log_test(f"Update Collection Item ({kit_name})", False,
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"Update Collection Item ({kit_name})", False, f"Exception: {str(e)}")
            return None
    
    def verify_pydantic_validation_fixes(self, collection_data):
        """Verify that Pydantic validation issues have been resolved"""
        try:
            validation_issues = []
            
            for item in collection_data:
                # Check for previously problematic fields
                master_kit = item.get('master_kit', {})
                
                # These fields were causing validation errors before
                problematic_fields = {
                    'certificate_url': item.get('certificate_url'),
                    'condition_other': item.get('condition_other'), 
                    'proof_of_purchase_url': item.get('proof_of_purchase_url'),
                    'updated_at': item.get('updated_at')
                }
                
                # Check if fields are properly handled (None is acceptable)
                for field_name, field_value in problematic_fields.items():
                    if field_value is not None and not isinstance(field_value, (str, type(None))):
                        validation_issues.append(f"Field {field_name} has invalid type: {type(field_value)}")
                
                # Check master_kit structure
                if not master_kit:
                    validation_issues.append("Missing master_kit data")
                elif not master_kit.get('id'):
                    validation_issues.append("Missing master_kit.id")
            
            if validation_issues:
                self.log_test("Pydantic Validation Fixes", False,
                             f"Found {len(validation_issues)} validation issues", validation_issues)
            else:
                self.log_test("Pydantic Validation Fixes", True,
                             "No Pydantic validation issues detected - fixes successful")
            
            return len(validation_issues) == 0
            
        except Exception as e:
            self.log_test("Pydantic Validation Fixes", False, f"Exception during validation check: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests focusing on My Collection functionality"""
        print("🧪 Starting TopKit Backend Testing - My Collection Focus")
        print("Testing My Collection functionality after Pydantic validation fixes")
        print("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test My Collection endpoint (main focus)
        print("📋 Testing My Collection Endpoint...")
        collection_data = self.test_my_collection_endpoint()
        print()
        
        if not collection_data:
            print("❌ No collection data retrieved. Cannot proceed with further tests.")
            return False
        
        # Step 3: Verify Pydantic validation fixes
        print("🔧 Verifying Pydantic Validation Fixes...")
        self.verify_pydantic_validation_fixes(collection_data)
        print()
        
        # Step 4: Test price estimation for collection items
        print("💰 Testing Price Estimation for Collection Items...")
        psg_items = [item for item in collection_data if item.get('master_kit', {}).get('id') in [PSG_2015_KIT_ID, PSG_2023_KIT_ID]]
        
        for item in psg_items:
            master_kit_id = item.get('master_kit', {}).get('id')
            expected_price = EXPECTED_PRICES.get(master_kit_id, 0)
            if expected_price > 0:
                self.test_collection_price_estimation(item, expected_price)
        print()
        
        # Step 5: Test updating collection items
        print("✏️ Testing Collection Item Updates...")
        if psg_items:
            # Test updating the first PSG item
            self.test_update_collection_item(psg_items[0])
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
            print("My Collection functionality is working correctly after Pydantic validation fixes.")
        
        print("\n" + "=" * 70)

def main():
    """Main test execution"""
    tester = TopKitTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()