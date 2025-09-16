#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Updated Pricing Coefficients System
Testing the new TOPKIT pricing formula with updated coefficients
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://topkit-preview.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "topkitfr@gmail.com",
    "password": "TopKitSecure789#"
}

# Test kit IDs from the review request - PSG collection items
PSG_2015_KIT_ID = "802f4f1d-7b3c-47fe-969f-5d45ed615257"
PSG_2023_KIT_ID = "1fe4787a-a0c0-4bb3-959d-931857745a2b"

# New coefficient values to test (from review request)
NEW_COEFFICIENTS = {
    "condition": {
        "club_stock": 1.2,
        "match_prepared": 0.8,
        "match_worn": 1.5,
        "training": 0.2
    },
    "physical_state": {
        "new_with_tags": 0.3,
        "very_good_condition": 0.15,
        "used": 0.0,
        "damaged": -0.25,
        "needs_restoration": -0.4
    },
    "flocking": {
        "name_only": 0.15,
        "number_only": 0.1,
        "full_flocking": 0.2
    },
    "additional_features": {
        "patches": 0.15,
        "signed": 1.0
    },
    "age_per_year": 0.03,
    "age_max": 0.6
}

# Expected calculation example from review request:
# PSG 2015 authentic with full flocking, patches, match worn, signed, 10 years old
# Expected: €140 × (1 + 0.2 flocking + 0.15 patches + 1.5 match_worn + 1.0 signed + 0.6 age) = €140 × 4.45 = €623

class TopKitPricingTester:
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
    
    def test_basic_master_kit_price_estimation(self):
        """Test basic Master Kit price estimation endpoints"""
        try:
            # Test PSG 2015 kit
            response = self.session.get(f"{BACKEND_URL}/price-estimation/{PSG_2015_KIT_ID}", timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                estimated_price = price_data.get('estimated_price', 0)
                base_price = price_data.get('base_price', 0)
                model = price_data.get('model', '')
                
                # PSG 2015 should be authentic (€140 base) with age coefficient
                expected_base = 140.0  # Authentic
                age_years = 2025 - 2015  # 10 years
                age_coefficient = min(age_years * 0.03, 0.6)  # Should be 0.3 (10 * 0.03 = 0.3)
                expected_price = expected_base * (1 + age_coefficient)
                
                price_match = abs(estimated_price - expected_price) < 5.0
                
                self.log_test("PSG 2015 Basic Price Estimation", price_match,
                             f"Estimated: €{estimated_price}, Expected: €{expected_price:.2f} (base: €{base_price}, model: {model})",
                             price_data)
                
                # Test PSG 2023 kit
                response2 = self.session.get(f"{BACKEND_URL}/price-estimation/{PSG_2023_KIT_ID}", timeout=10)
                
                if response2.status_code == 200:
                    price_data2 = response2.json()
                    estimated_price2 = price_data2.get('estimated_price', 0)
                    base_price2 = price_data2.get('base_price', 0)
                    model2 = price_data2.get('model', '')
                    
                    # PSG 2023 should be replica (€90 base) with age coefficient
                    expected_base2 = 90.0  # Replica
                    age_years2 = 2025 - 2023  # 2 years
                    age_coefficient2 = min(age_years2 * 0.03, 0.6)  # Should be 0.06 (2 * 0.03 = 0.06)
                    expected_price2 = expected_base2 * (1 + age_coefficient2)
                    
                    price_match2 = abs(estimated_price2 - expected_price2) < 5.0
                    
                    self.log_test("PSG 2023 Basic Price Estimation", price_match2,
                                 f"Estimated: €{estimated_price2}, Expected: €{expected_price2:.2f} (base: €{base_price2}, model: {model2})",
                                 price_data2)
                    
                    return True
                else:
                    self.log_test("PSG 2023 Basic Price Estimation", False,
                                 f"Failed with status {response2.status_code}", response2.text)
                    return False
                    
            else:
                self.log_test("PSG 2015 Basic Price Estimation", False,
                             f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Basic Price Estimation", False, f"Exception: {str(e)}")
            return False
    
    def get_my_collection(self):
        """Get user's collection items"""
        try:
            response = self.session.get(f"{BACKEND_URL}/my-collection", timeout=10)
            
            if response.status_code == 200:
                collection_data = response.json()
                self.collection_items = collection_data
                
                psg_items = [item for item in collection_data 
                           if item.get('master_kit', {}).get('id') in [PSG_2015_KIT_ID, PSG_2023_KIT_ID]]
                
                self.log_test("My Collection Retrieval", True,
                             f"Retrieved {len(collection_data)} items, {len(psg_items)} PSG items found")
                
                return collection_data
                
            else:
                self.log_test("My Collection Retrieval", False,
                             f"Failed with status {response.status_code}", response.text)
                return []
                
        except Exception as e:
            self.log_test("My Collection Retrieval", False, f"Exception: {str(e)}")
            return []
    
    def test_detailed_collection_price_estimation(self, collection_item):
        """Test detailed price estimation with new coefficients"""
        try:
            collection_id = collection_item.get('id')
            master_kit = collection_item.get('master_kit', {})
            kit_name = f"{master_kit.get('club', 'Unknown')} {master_kit.get('season', 'Unknown')}"
            
            response = self.session.get(f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                estimated_price = price_data.get('estimated_price', 0)
                base_price = price_data.get('base_price', 0)
                coefficients_applied = price_data.get('calculation_details', {}).get('coefficients_applied', [])
                
                # Verify coefficient breakdown is present and detailed
                has_detailed_breakdown = len(coefficients_applied) > 0
                
                self.log_test(f"Detailed Price Estimation ({kit_name})", has_detailed_breakdown,
                             f"Price: €{estimated_price}, Base: €{base_price}, Coefficients: {len(coefficients_applied)}",
                             {
                                 "estimated_price": estimated_price,
                                 "coefficients": coefficients_applied,
                                 "formula": price_data.get('calculation_details', {}).get('formula', '')
                             })
                
                # Test specific coefficient values if present
                self.verify_coefficient_values(coefficients_applied, collection_item)
                
                return price_data
                
            else:
                self.log_test(f"Detailed Price Estimation ({kit_name})", False,
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"Detailed Price Estimation", False, f"Exception: {str(e)}")
            return None
    
    def verify_coefficient_values(self, coefficients_applied, collection_item):
        """Verify that the new coefficient values are correctly applied"""
        try:
            coefficient_checks = []
            
            for coeff in coefficients_applied:
                factor = coeff.get('factor', '')
                value = coeff.get('value', '')
                
                # Check condition coefficients
                if 'Club Stock' in factor:
                    expected = "+1.2"
                    coefficient_checks.append(("Club Stock", value == expected, f"Expected {expected}, got {value}"))
                elif 'Match Prepared' in factor:
                    expected = "+0.8"
                    coefficient_checks.append(("Match Prepared", value == expected, f"Expected {expected}, got {value}"))
                elif 'Match Worn' in factor:
                    expected = "+1.5"
                    coefficient_checks.append(("Match Worn", value == expected, f"Expected {expected}, got {value}"))
                elif 'Training' in factor:
                    expected = "+0.2"
                    coefficient_checks.append(("Training", value == expected, f"Expected {expected}, got {value}"))
                
                # Check physical state coefficients
                elif 'New with tags' in factor:
                    expected = "+0.3"
                    coefficient_checks.append(("New with tags", value == expected, f"Expected {expected}, got {value}"))
                elif 'Very good condition' in factor:
                    expected = "+0.15"
                    coefficient_checks.append(("Very good", value == expected, f"Expected {expected}, got {value}"))
                elif 'Used condition' in factor:
                    expected = "0"
                    coefficient_checks.append(("Used", value == expected, f"Expected {expected}, got {value}"))
                elif 'Damaged condition' in factor:
                    expected = "-0.25"
                    coefficient_checks.append(("Damaged", value == expected, f"Expected {expected}, got {value}"))
                elif 'Needs restoration' in factor:
                    expected = "-0.4"
                    coefficient_checks.append(("Restoration", value == expected, f"Expected {expected}, got {value}"))
                
                # Check flocking coefficients
                elif 'Full flocking' in factor:
                    expected = "+0.2"
                    coefficient_checks.append(("Full flocking", value == expected, f"Expected {expected}, got {value}"))
                elif 'Official name flocking' in factor:
                    expected = "+0.15"
                    coefficient_checks.append(("Name flocking", value == expected, f"Expected {expected}, got {value}"))
                elif 'Official number flocking' in factor:
                    expected = "+0.1"
                    coefficient_checks.append(("Number flocking", value == expected, f"Expected {expected}, got {value}"))
                
                # Check additional features
                elif 'Competition patches' in factor:
                    expected = "+0.15"
                    coefficient_checks.append(("Patches", value == expected, f"Expected {expected}, got {value}"))
                elif 'Signed by' in factor:
                    expected = "+1.0"
                    coefficient_checks.append(("Signature", value == expected, f"Expected {expected}, got {value}"))
                
                # Check age coefficient (should be max +0.6)
                elif 'Age' in factor:
                    # Extract numeric value from string like "+0.30"
                    try:
                        numeric_value = float(value.replace('+', ''))
                        age_valid = 0 <= numeric_value <= 0.6
                        coefficient_checks.append(("Age coefficient", age_valid, f"Age coefficient {value} within range [0, +0.6]"))
                    except:
                        coefficient_checks.append(("Age coefficient", False, f"Could not parse age coefficient: {value}"))
            
            # Log coefficient verification results
            for check_name, success, message in coefficient_checks:
                self.log_test(f"Coefficient Verification - {check_name}", success, message)
            
        except Exception as e:
            self.log_test("Coefficient Verification", False, f"Exception: {str(e)}")
    
    def test_example_calculation(self):
        """Test the specific example from the review request"""
        try:
            # Find a PSG 2015 item to update with the example configuration
            psg_2015_items = [item for item in self.collection_items 
                            if item.get('master_kit', {}).get('id') == PSG_2015_KIT_ID]
            
            if not psg_2015_items:
                self.log_test("Example Calculation Setup", False, "No PSG 2015 items found in collection")
                return False
            
            collection_item = psg_2015_items[0]
            collection_id = collection_item.get('id')
            
            # Update the item with the example configuration:
            # Full flocking, patches, match worn, signed, 10 years old
            update_data = {
                "name_printing": "Mbappé",
                "number_printing": "10",
                "patches": "Champions League",
                "condition": "match_worn",
                "physical_state": "used",
                "is_signed": True,
                "signed_by": "Kylian Mbappé"
            }
            
            response = self.session.put(
                f"{BACKEND_URL}/my-collection/{collection_id}",
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_test("Example Configuration Update", True, "Updated PSG 2015 item with example configuration")
                
                # Now test the price estimation
                price_response = self.session.get(f"{BACKEND_URL}/my-collection/{collection_id}/price-estimation", timeout=10)
                
                if price_response.status_code == 200:
                    price_data = price_response.json()
                    estimated_price = price_data.get('estimated_price', 0)
                    
                    # Expected calculation: €140 × (1 + 0.2 flocking + 0.15 patches + 1.5 match_worn + 1.0 signed + 0.6 age)
                    # = €140 × (1 + 3.45) = €140 × 4.45 = €623
                    expected_price = 623.0
                    
                    price_match = abs(estimated_price - expected_price) < 50.0  # Allow €50 tolerance for this complex calculation
                    
                    self.log_test("Example Calculation Verification", price_match,
                                 f"Estimated: €{estimated_price}, Expected: €{expected_price} (tolerance: €50)",
                                 {
                                     "calculation_details": price_data.get('calculation_details', {}),
                                     "coefficients": price_data.get('calculation_details', {}).get('coefficients_applied', [])
                                 })
                    
                    return price_match
                else:
                    self.log_test("Example Calculation Verification", False,
                                 f"Price estimation failed with status {price_response.status_code}")
                    return False
            else:
                self.log_test("Example Configuration Update", False,
                             f"Update failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Example Calculation", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive pricing coefficient tests"""
        print("🧪 Starting TopKit Pricing Coefficients Testing")
        print("Testing the updated TOPKIT pricing formula with new coefficients")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test basic Master Kit price estimation
        print("💰 Testing Basic Master Kit Price Estimation...")
        self.test_basic_master_kit_price_estimation()
        print()
        
        # Step 3: Get collection items
        print("📋 Retrieving My Collection...")
        collection_data = self.get_my_collection()
        print()
        
        if not collection_data:
            print("❌ No collection data retrieved. Cannot proceed with detailed tests.")
            return False
        
        # Step 4: Test detailed collection price estimations
        print("🔍 Testing Detailed Collection Price Estimations...")
        psg_items = [item for item in collection_data 
                    if item.get('master_kit', {}).get('id') in [PSG_2015_KIT_ID, PSG_2023_KIT_ID]]
        
        for item in psg_items:
            self.test_detailed_collection_price_estimation(item)
        print()
        
        # Step 5: Test the specific example calculation
        print("🎯 Testing Example Calculation from Review Request...")
        self.test_example_calculation()
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("📊 PRICING COEFFICIENTS TEST SUMMARY")
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
        price_tests = [r for r in self.test_results if 'Price Estimation' in r['test']]
        coeff_tests = [r for r in self.test_results if 'Coefficient' in r['test']]
        example_tests = [r for r in self.test_results if 'Example' in r['test']]
        
        print(f"\nTest Categories:")
        print(f"  Authentication: {len([r for r in auth_tests if r['success']])}/{len(auth_tests)} ✅")
        print(f"  Price Estimation: {len([r for r in price_tests if r['success']])}/{len(price_tests)} ✅")
        print(f"  Coefficient Verification: {len([r for r in coeff_tests if r['success']])}/{len(coeff_tests)} ✅")
        print(f"  Example Calculation: {len([r for r in example_tests if r['success']])}/{len(example_tests)} ✅")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        else:
            print("\n🎉 ALL PRICING COEFFICIENT TESTS PASSED!")
            print("The new TOPKIT pricing formula is working correctly with updated coefficients.")
        
        print("\n" + "=" * 80)

def main():
    """Main test execution"""
    tester = TopKitPricingTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()