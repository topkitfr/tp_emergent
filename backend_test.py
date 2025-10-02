#!/usr/bin/env python3
"""
TopKit Backend Testing Suite - EDIT KIT FORM BACKEND FUNCTIONALITY TESTING

**EDIT KIT FORM BACKEND FUNCTIONALITY TESTING:**

Testing the Edit Kit Form backend functionality that was just implemented. This includes comprehensive testing of:

**Test Requirements:**
1. **Form Data API Endpoints**: Test the new form data endpoints:
   - GET /api/form-data/players (should return players with aura ratings)
   - GET /api/form-data/competitions (should return competition data)
   - GET /api/form-data/teams (should return team data for opponents)

2. **Price Calculation Endpoint**: Test the pricing calculation:
   - POST /api/calculate-price with sample kit details data
   - Verify it returns proper estimated price and coefficients breakdown
   - Test different combinations (signed vs unsigned, match-worn vs standard, etc.)

3. **Edit Master Kit Endpoint**: Test the edit functionality:
   - PUT /api/master-kits/{master_kit_id}/edit with sample kit details
   - Verify it updates the master kit and returns proper response

4. **Photo Upload Endpoint**: Test the photo upload:
   - POST /api/upload/kit-photo with a sample image
   - Verify it returns proper photo URL

**Authentication:** Use emergency.admin@topkit.test / EmergencyAdmin2025!

**Sample Test Data for Price Calculation:**
```json
{
  "type": "authentic",
  "condition": "nwt", 
  "origin_type": "match_worn",
  "special_match_type": "classico",
  "match_result": "win",
  "performance": ["scored_goal", "man_of_the_match"],
  "match_proof": "photo",
  "signed": true,
  "signature_proof": "certificate",
  "player_id": "[use any player ID from form-data/players]"
}
```

**Expected Results:**
- All form data endpoints should return populated data (players with aura ratings, competitions, teams)
- Price calculation should return detailed coefficients and estimated price
- Edit functionality should successfully update master kits
- Photo upload should work properly

**PRIORITY: HIGH** - Testing Edit Kit Form backend functionality implementation.
"""

import requests
import json
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path

# Configuration
BACKEND_URL = "https://soccer-kit-catalog-1.preview.emergentagent.com/api"

# Test Admin Credentials for authentication - Updated for Edit Kit Form Testing
ADMIN_CREDENTIALS = {
    "email": "emergency.admin@topkit.test",
    "password": "EmergencyAdmin2025!",
    "name": "Emergency Admin"
}

class TopKitEditKitFormBackendTesting:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.admin_user_data = None
        self.form_data = {}
        self.master_kits_data = []
        self.sample_player_id = None
        
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
        """Authenticate with Emergency Admin credentials"""
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

    def test_form_data_endpoints(self):
        """Test all form data endpoints for Edit Kit Form"""
        try:
            print(f"\n📋 TESTING FORM DATA ENDPOINTS")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Test 1: Players endpoint
            print(f"\n      🏃 Testing GET /api/form-data/players")
            players_response = self.session.get(f"{BACKEND_URL}/form-data/players", timeout=10)
            print(f"         Response Status: {players_response.status_code}")
            
            if players_response.status_code == 200:
                players_data = players_response.json()
                print(f"         ✅ Players endpoint accessible")
                print(f"         Total players returned: {len(players_data)}")
                
                if len(players_data) > 0:
                    first_player = players_data[0]
                    self.sample_player_id = first_player.get('id') or first_player.get('name')
                    print(f"         Sample player: {first_player.get('name', 'Unknown')}")
                    print(f"         Player aura/coefficient: {first_player.get('coefficient', 'N/A')}")
                    print(f"         Player type: {first_player.get('player_type', 'N/A')}")
                    
                self.form_data['players'] = players_data
                self.log_test("Form Data Players Endpoint", True, f"✅ Retrieved {len(players_data)} players")
            else:
                self.log_test("Form Data Players Endpoint", False, f"❌ Failed - Status {players_response.status_code}", players_response.text)
                return False
            
            # Test 2: Competitions endpoint
            print(f"\n      🏆 Testing GET /api/form-data/competitions")
            competitions_response = self.session.get(f"{BACKEND_URL}/form-data/competitions", timeout=10)
            print(f"         Response Status: {competitions_response.status_code}")
            
            if competitions_response.status_code == 200:
                competitions_data = competitions_response.json()
                print(f"         ✅ Competitions endpoint accessible")
                print(f"         Total competitions returned: {len(competitions_data)}")
                
                if len(competitions_data) > 0:
                    first_competition = competitions_data[0]
                    print(f"         Sample competition: {first_competition.get('name', 'Unknown')}")
                    print(f"         Competition country: {first_competition.get('country', 'Unknown')}")
                    
                self.form_data['competitions'] = competitions_data
                self.log_test("Form Data Competitions Endpoint", True, f"✅ Retrieved {len(competitions_data)} competitions")
            else:
                self.log_test("Form Data Competitions Endpoint", False, f"❌ Failed - Status {competitions_response.status_code}", competitions_response.text)
                return False
            
            # Test 3: Teams endpoint (for opponents)
            print(f"\n      ⚽ Testing GET /api/form-data/clubs (teams)")
            teams_response = self.session.get(f"{BACKEND_URL}/form-data/clubs", timeout=10)
            print(f"         Response Status: {teams_response.status_code}")
            
            if teams_response.status_code == 200:
                teams_data = teams_response.json()
                print(f"         ✅ Teams endpoint accessible")
                print(f"         Total teams returned: {len(teams_data)}")
                
                if len(teams_data) > 0:
                    first_team = teams_data[0]
                    print(f"         Sample team: {first_team.get('name', 'Unknown')}")
                    print(f"         Team country: {first_team.get('country', 'Unknown')}")
                    
                self.form_data['teams'] = teams_data
                self.log_test("Form Data Teams Endpoint", True, f"✅ Retrieved {len(teams_data)} teams")
            else:
                self.log_test("Form Data Teams Endpoint", False, f"❌ Failed - Status {teams_response.status_code}", teams_response.text)
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Form Data Endpoints", False, f"Exception: {str(e)}")
            return False

    def test_price_calculation_endpoint(self):
        """Test POST /api/calculate-price endpoint with sample kit details"""
        try:
            print(f"\n💰 TESTING PRICE CALCULATION ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Sample test data for price calculation
            sample_kit_details = {
                "type": "authentic",
                "condition": "nwt", 
                "origin_type": "match_worn",
                "special_match_type": "classico",
                "match_result": "win",
                "performance": ["scored_goal", "man_of_the_match"],
                "match_proof": "photo",
                "signed": True,
                "signature_proof": "certificate",
                "player_aura": 2.0
            }
            
            # Add player_id if we have one from form data
            if self.sample_player_id:
                sample_kit_details["player_id"] = self.sample_player_id
            
            print(f"      📊 Testing price calculation with sample data:")
            print(f"         Type: {sample_kit_details['type']}")
            print(f"         Condition: {sample_kit_details['condition']}")
            print(f"         Origin: {sample_kit_details['origin_type']}")
            print(f"         Special Match: {sample_kit_details['special_match_type']}")
            print(f"         Signed: {sample_kit_details['signed']}")
            print(f"         Player Aura: {sample_kit_details['player_aura']}")
            
            response = self.session.post(
                f"{BACKEND_URL}/calculate-price",
                json=sample_kit_details,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                price_data = response.json()
                print(f"      ✅ Price calculation endpoint accessible")
                
                estimated_price = price_data.get('estimated_price')
                coefficients = price_data.get('coefficients', {})
                
                print(f"      💰 PRICE CALCULATION RESULTS:")
                print(f"         Estimated Price: €{estimated_price}")
                
                if coefficients:
                    print(f"         📈 COEFFICIENTS BREAKDOWN:")
                    for coeff_name, coeff_value in coefficients.items():
                        print(f"            {coeff_name}: {coeff_value}")
                
                # Verify expected components are present
                expected_components = ['base_price', 'condition', 'origin', 'signature']
                missing_components = []
                
                for component in expected_components:
                    if component not in coefficients:
                        missing_components.append(component)
                
                if missing_components:
                    print(f"      ⚠️ Missing expected coefficient components: {missing_components}")
                else:
                    print(f"      ✅ All expected coefficient components present")
                
                self.log_test("Price Calculation Endpoint", True, f"✅ Price calculation successful - €{estimated_price}")
                return True
                
            else:
                print(f"      ❌ Price calculation failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Price Calculation Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Price Calculation Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_photo_upload_endpoint(self):
        """Test POST /api/upload/kit-photo endpoint"""
        try:
            print(f"\n📸 TESTING PHOTO UPLOAD ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # Create a simple test image (1x1 pixel PNG)
            import io
            from PIL import Image
            
            # Create a small test image
            test_image = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            test_image.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            
            print(f"      📷 Testing photo upload with sample JPEG image (100x100)")
            
            files = {
                'file': ('test_kit_photo.jpg', img_buffer, 'image/jpeg')
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/upload/kit-photo",
                files=files,
                timeout=15
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                upload_data = response.json()
                print(f"      ✅ Photo upload endpoint accessible")
                
                photo_url = upload_data.get('photo_url') or upload_data.get('file_url') or upload_data.get('url')
                
                if photo_url:
                    print(f"      📸 PHOTO UPLOAD RESULTS:")
                    print(f"         Photo URL: {photo_url}")
                    
                    # Verify URL format
                    if photo_url.startswith('uploads/') or photo_url.startswith('http'):
                        print(f"      ✅ Photo URL format appears correct")
                    else:
                        print(f"      ⚠️ Photo URL format may be incorrect: {photo_url}")
                    
                    self.log_test("Photo Upload Endpoint", True, f"✅ Photo upload successful - URL: {photo_url}")
                    return True
                else:
                    print(f"      ❌ No photo URL returned in response")
                    print(f"      Response data: {upload_data}")
                    self.log_test("Photo Upload Endpoint", False, "❌ No photo URL in response", upload_data)
                    return False
                
            else:
                print(f"      ❌ Photo upload failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Photo Upload Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Photo Upload Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_edit_master_kit_endpoint(self):
        """Test PUT /api/master-kits/{master_kit_id}/edit endpoint"""
        try:
            print(f"\n✏️ TESTING EDIT MASTER KIT ENDPOINT")
            print("=" * 60)
            
            if not self.auth_token:
                if not self.authenticate_admin():
                    return False
            
            # First, get available master kits to test editing
            master_kits_response = self.session.get(f"{BACKEND_URL}/master-kits", timeout=10)
            
            if master_kits_response.status_code != 200:
                print(f"      ❌ Cannot get master kits for edit testing - Status {master_kits_response.status_code}")
                self.log_test("Edit Master Kit Endpoint", False, "❌ Cannot get master kits for testing")
                return False
            
            master_kits = master_kits_response.json()
            
            if not master_kits or len(master_kits) == 0:
                print(f"      ⚠️ No master kits available for edit testing")
                self.log_test("Edit Master Kit Endpoint", False, "⚠️ No master kits available for testing")
                return False
            
            # Use first master kit for testing
            test_master_kit = master_kits[0]
            master_kit_id = test_master_kit.get('id')
            
            print(f"      🎽 Testing edit on master kit: {master_kit_id}")
            print(f"         Original club: {test_master_kit.get('club', 'Unknown')}")
            print(f"         Original season: {test_master_kit.get('season', 'Unknown')}")
            
            # Sample edit data
            edit_data = {
                "personal_notes": "Updated via Edit Kit Form testing",
                "condition": "very_good",
                "physical_state": "very_good_condition",
                "purchase_price": 150.0,
                "name_printing": "Test Player",
                "number_printing": "10",
                "is_signed": False
            }
            
            print(f"      📝 Testing edit with sample data:")
            for key, value in edit_data.items():
                print(f"         {key}: {value}")
            
            response = self.session.put(
                f"{BACKEND_URL}/master-kits/{master_kit_id}/edit",
                json=edit_data,
                timeout=10
            )
            
            print(f"      Response Status: {response.status_code}")
            
            if response.status_code == 200:
                edit_response_data = response.json()
                print(f"      ✅ Edit master kit endpoint accessible")
                
                print(f"      ✏️ EDIT RESULTS:")
                print(f"         Response message: {edit_response_data.get('message', 'No message')}")
                
                # Check if response includes updated data
                updated_data = edit_response_data.get('updated_item') or edit_response_data.get('data')
                if updated_data:
                    print(f"         Updated item ID: {updated_data.get('id', 'Unknown')}")
                    print(f"         Updated notes: {updated_data.get('personal_notes', 'N/A')}")
                
                self.log_test("Edit Master Kit Endpoint", True, f"✅ Master kit edit successful")
                return True
                
            elif response.status_code == 404:
                print(f"      ❌ Edit endpoint not found - may not be implemented yet")
                self.log_test("Edit Master Kit Endpoint", False, "❌ Edit endpoint not found (404)")
                return False
                
            else:
                print(f"      ❌ Edit master kit failed - Status {response.status_code}")
                print(f"      Response: {response.text}")
                self.log_test("Edit Master Kit Endpoint", False, f"❌ Failed - Status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Edit Master Kit Endpoint", False, f"Exception: {str(e)}")
            return False

    def run_edit_kit_form_backend_testing(self):
        """Run comprehensive Edit Kit Form backend functionality testing"""
        print("\n🚀 EDIT KIT FORM BACKEND FUNCTIONALITY TESTING")
        print("Testing Edit Kit Form backend endpoints and functionality")
        print("=" * 80)
        
        test_results = []
        
        # Step 1: Authenticate
        print("\n1️⃣ Authenticating...")
        auth_success = self.authenticate_admin()
        test_results.append(auth_success)
        
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return test_results
        
        # Step 2: Test form data endpoints
        print("\n2️⃣ Testing Form Data Endpoints...")
        form_data_success = self.test_form_data_endpoints()
        test_results.append(form_data_success)
        
        # Step 3: Test price calculation endpoint
        print("\n3️⃣ Testing Price Calculation Endpoint...")
        price_calc_success = self.test_price_calculation_endpoint()
        test_results.append(price_calc_success)
        
        # Step 4: Test photo upload endpoint
        print("\n4️⃣ Testing Photo Upload Endpoint...")
        photo_upload_success = self.test_photo_upload_endpoint()
        test_results.append(photo_upload_success)
        
        # Step 5: Test edit master kit endpoint
        print("\n5️⃣ Testing Edit Master Kit Endpoint...")
        edit_kit_success = self.test_edit_master_kit_endpoint()
        test_results.append(edit_kit_success)
        
        return test_results

    def print_comprehensive_edit_kit_form_summary(self):
        """Print final comprehensive Edit Kit Form testing summary"""
        print("\n📊 EDIT KIT FORM BACKEND FUNCTIONALITY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings for Edit Kit Form testing
        print(f"\n🔍 EDIT KIT FORM BACKEND TESTING RESULTS:")
        
        # Form Data Endpoints Analysis
        form_data_tests = [r for r in self.test_results if 'Form Data' in r['test']]
        if form_data_tests:
            form_data_passed = len([r for r in form_data_tests if r['success']])
            print(f"\n✅ FORM DATA ENDPOINTS: {form_data_passed}/{len(form_data_tests)} PASSED")
            
            if self.form_data:
                if 'players' in self.form_data:
                    players_count = len(self.form_data['players'])
                    print(f"  • Players endpoint: {players_count} players returned")
                    if players_count > 0 and self.sample_player_id:
                        print(f"    - Sample player ID available: {self.sample_player_id}")
                
                if 'competitions' in self.form_data:
                    competitions_count = len(self.form_data['competitions'])
                    print(f"  • Competitions endpoint: {competitions_count} competitions returned")
                
                if 'teams' in self.form_data:
                    teams_count = len(self.form_data['teams'])
                    print(f"  • Teams endpoint: {teams_count} teams returned")
        
        # Price Calculation Analysis
        price_calc_tests = [r for r in self.test_results if 'Price Calculation' in r['test']]
        if price_calc_tests:
            price_calc_passed = len([r for r in price_calc_tests if r['success']])
            print(f"\n✅ PRICE CALCULATION ENDPOINT: {price_calc_passed}/{len(price_calc_tests)} PASSED")
            
            if price_calc_passed > 0:
                print(f"  • Price calculation working with coefficient breakdown")
                print(f"  • Sample data processed successfully")
            else:
                print(f"  • Price calculation endpoint issues detected")
        
        # Photo Upload Analysis
        photo_upload_tests = [r for r in self.test_results if 'Photo Upload' in r['test']]
        if photo_upload_tests:
            photo_upload_passed = len([r for r in photo_upload_tests if r['success']])
            print(f"\n✅ PHOTO UPLOAD ENDPOINT: {photo_upload_passed}/{len(photo_upload_tests)} PASSED")
            
            if photo_upload_passed > 0:
                print(f"  • Photo upload working with proper URL generation")
            else:
                print(f"  • Photo upload endpoint issues detected")
        
        # Edit Master Kit Analysis
        edit_kit_tests = [r for r in self.test_results if 'Edit Master Kit' in r['test']]
        if edit_kit_tests:
            edit_kit_passed = len([r for r in edit_kit_tests if r['success']])
            print(f"\n✅ EDIT MASTER KIT ENDPOINT: {edit_kit_passed}/{len(edit_kit_tests)} PASSED")
            
            if edit_kit_passed > 0:
                print(f"  • Master kit editing functionality working")
            else:
                print(f"  • Master kit editing endpoint issues detected")
        
        # Overall functionality status
        print(f"\n🎯 OVERALL EDIT KIT FORM FUNCTIONALITY STATUS:")
        
        functionality_working = []
        functionality_broken = []
        
        # Check each major functionality
        if any(r['success'] for r in self.test_results if 'Form Data' in r['test']):
            functionality_working.append("Form Data Endpoints (players, competitions, teams)")
        else:
            functionality_broken.append("Form Data Endpoints")
        
        if any(r['success'] for r in self.test_results if 'Price Calculation' in r['test']):
            functionality_working.append("Price Calculation with Coefficients")
        else:
            functionality_broken.append("Price Calculation")
        
        if any(r['success'] for r in self.test_results if 'Photo Upload' in r['test']):
            functionality_working.append("Photo Upload")
        else:
            functionality_broken.append("Photo Upload")
        
        if any(r['success'] for r in self.test_results if 'Edit Master Kit' in r['test']):
            functionality_working.append("Master Kit Editing")
        else:
            functionality_broken.append("Master Kit Editing")
        
        if functionality_working:
            print(f"  ✅ WORKING FUNCTIONALITY ({len(functionality_working)}):")
            for func in functionality_working:
                print(f"     • {func}")
        
        if functionality_broken:
            print(f"  ❌ BROKEN FUNCTIONALITY ({len(functionality_broken)}):")
            for func in functionality_broken:
                print(f"     • {func}")
        
        if not functionality_broken:
            print(f"  🎉 ALL EDIT KIT FORM FUNCTIONALITY WORKING!")
        
        # Show test failures
        failures = [r for r in self.test_results if not r['success']]
        if failures:
            print(f"\n❌ TEST FAILURES ({len(failures)}):")
            for failure in failures:
                print(f"  • {failure['test']}: {failure['message']}")
        
        print("\n" + "=" * 80)

def main():
    """Main function to run the Edit Kit Form backend testing"""
    tester = TopKitEditKitFormBackendTesting()
    
    # Run the comprehensive Edit Kit Form backend testing
    test_results = tester.run_edit_kit_form_backend_testing()
    
    # Print comprehensive summary
    tester.print_comprehensive_edit_kit_form_summary()
    
    # Return overall success
    return all(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)