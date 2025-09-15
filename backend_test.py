#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - Price Estimation Focus
Testing the new price estimation endpoints and master kit verification
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

# Test kit IDs from the review request
PSG_2015_KIT_ID = "802f4f1d-7b3c-47fe-969f-5d45ed615257"
PSG_2023_KIT_ID = "1fe4787a-a0c0-4bb3-959d-931857745a2b"

# Expected price calculations from review request
EXPECTED_PRICES = {
    PSG_2015_KIT_ID: 280.0,  # 2015 kit (authentic, 10 years) = €280
    PSG_2023_KIT_ID: 108.0   # 2023 kit (replica, 2 years) = €108
}

class TopKitTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
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
    
    def test_master_kits_endpoint(self):
        """Test the master kits endpoint to verify test kits exist"""
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if response.status_code == 200:
                master_kits = response.json()
                self.log_test("Master Kits Endpoint", True, f"Retrieved {len(master_kits)} master kits")
                
                # Check if our test kits exist
                kit_ids = [kit.get('id') for kit in master_kits]
                
                psg_2015_found = PSG_2015_KIT_ID in kit_ids
                psg_2023_found = PSG_2023_KIT_ID in kit_ids
                
                self.log_test("PSG 2015-2016 Kit Exists", psg_2015_found, 
                             f"PSG 2015-2016 kit {'found' if psg_2015_found else 'NOT FOUND'} in master kits")
                
                self.log_test("PSG 2023-2024 Kit Exists", psg_2023_found,
                             f"PSG 2023-2024 kit {'found' if psg_2023_found else 'NOT FOUND'} in master kits")
                
                # Return details of our test kits if found
                test_kits = {}
                for kit in master_kits:
                    if kit.get('id') in [PSG_2015_KIT_ID, PSG_2023_KIT_ID]:
                        test_kits[kit.get('id')] = kit
                
                return test_kits
                
            else:
                self.log_test("Master Kits Endpoint", False, f"Failed with status {response.status_code}", response.text)
                return {}
                
        except Exception as e:
            self.log_test("Master Kits Endpoint", False, f"Exception: {str(e)}")
            return {}
    
    def test_individual_master_kit(self, kit_id, expected_name):
        """Test getting individual master kit details"""
        try:
            response = self.session.get(f"{BACKEND_URL}/master-kits/{kit_id}", timeout=10)
            
            if response.status_code == 200:
                kit_data = response.json()
                self.log_test(f"Individual Master Kit ({expected_name})", True, 
                             f"Retrieved kit details: {kit_data.get('club')} {kit_data.get('season')} {kit_data.get('kit_type')}")
                return kit_data
            elif response.status_code == 404:
                self.log_test(f"Individual Master Kit ({expected_name})", False, 
                             f"Kit not found (404)", f"Kit ID {kit_id} does not exist")
                return None
            else:
                self.log_test(f"Individual Master Kit ({expected_name})", False, 
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"Individual Master Kit ({expected_name})", False, f"Exception: {str(e)}")
            return None
    
    def test_price_estimation(self, kit_id, expected_price, kit_name):
        """Test price estimation endpoint for a specific kit"""
        try:
            response = self.session.get(f"{BACKEND_URL}/price-estimation/{kit_id}", timeout=10)
            
            if response.status_code == 200:
                price_data = response.json()
                estimated_price = price_data.get('estimated_price', 0)
                base_price = price_data.get('base_price', 0)
                model = price_data.get('model', 'unknown')
                
                # Check if price matches expected value (with some tolerance for rounding)
                price_match = abs(estimated_price - expected_price) < 1.0
                
                self.log_test(f"Price Estimation ({kit_name})", price_match,
                             f"Estimated: €{estimated_price}, Expected: €{expected_price}, Model: {model}",
                             price_data.get('calculation_details'))
                
                return price_data
                
            elif response.status_code == 404:
                self.log_test(f"Price Estimation ({kit_name})", False,
                             f"Kit not found for price estimation", f"Kit ID {kit_id} not found")
                return None
            else:
                self.log_test(f"Price Estimation ({kit_name})", False,
                             f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_test(f"Price Estimation ({kit_name})", False, f"Exception: {str(e)}")
            return None
    
    def verify_price_calculation_logic(self, kit_data, price_data):
        """Verify the price calculation logic matches the expected formula"""
        if not kit_data or not price_data:
            return
            
        try:
            # Extract data
            model = kit_data.get('model', 'replica')
            season = kit_data.get('season', '')
            estimated_price = price_data.get('estimated_price', 0)
            
            # Calculate expected price using the formula from server.py
            base_price = 140.0 if model == 'authentic' else 90.0
            coefficients = 0.0
            
            # Age calculation
            if season and '-' in season:
                try:
                    start_year = int(season.split('-')[0])
                    current_year = 2025
                    age_years = current_year - start_year
                    age_coefficient = min(age_years * 0.1, 3.0)
                    coefficients += age_coefficient
                except:
                    pass
            
            expected_calculated_price = base_price * (1 + coefficients)
            
            # Check if calculation matches
            calculation_match = abs(estimated_price - expected_calculated_price) < 0.01
            
            self.log_test(f"Price Calculation Logic ({kit_data.get('club', 'Unknown')} {season})", 
                         calculation_match,
                         f"Server: €{estimated_price}, Manual calc: €{expected_calculated_price:.2f}",
                         {
                             "base_price": base_price,
                             "model": model,
                             "age_coefficient": coefficients,
                             "season": season
                         })
            
        except Exception as e:
            self.log_test("Price Calculation Logic", False, f"Exception during verification: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting TopKit Backend Testing - Price Estimation Focus")
        print("=" * 60)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        print()
        
        # Step 2: Test master kits endpoint
        print("📋 Testing Master Kits Endpoint...")
        test_kits = self.test_master_kits_endpoint()
        print()
        
        # Step 3: Test individual master kit retrieval
        print("🔍 Testing Individual Master Kit Retrieval...")
        psg_2015_data = self.test_individual_master_kit(PSG_2015_KIT_ID, "PSG 2015-2016")
        psg_2023_data = self.test_individual_master_kit(PSG_2023_KIT_ID, "PSG 2023-2024")
        print()
        
        # Step 4: Test price estimation endpoints
        print("💰 Testing Price Estimation Endpoints...")
        psg_2015_price = self.test_price_estimation(PSG_2015_KIT_ID, EXPECTED_PRICES[PSG_2015_KIT_ID], "PSG 2015-2016")
        psg_2023_price = self.test_price_estimation(PSG_2023_KIT_ID, EXPECTED_PRICES[PSG_2023_KIT_ID], "PSG 2023-2024")
        print()
        
        # Step 5: Verify price calculation logic
        print("🧮 Verifying Price Calculation Logic...")
        if psg_2015_data and psg_2015_price:
            self.verify_price_calculation_logic(psg_2015_data, psg_2015_price)
        if psg_2023_data and psg_2023_price:
            self.verify_price_calculation_logic(psg_2023_data, psg_2023_price)
        print()
        
        # Summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
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
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    tester = TopKitTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()